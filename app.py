import logging
import os
import random
import re
import string
from threading import Thread
import time

import sqlalchemy
import sqlalchemy.exc
import werkzeug
import werkzeug.exceptions

from database import db_session, init_db
from models import URL as URLModel

from dotenv import load_dotenv
from flask import Flask, abort, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from requests.exceptions import MissingSchema
from requests.models import PreparedRequest
import segno

load_dotenv()
init_db()

app = Flask(__name__)
app.config["POSTGRES_URL"] = os.environ["POSTGRES_URL"]
if app.config["POSTGRES_URL"].endswith("sslmode"):
    app.config["POSTGRES_URL"] += "=require"

limiter = Limiter(
    get_remote_address,
    app=app,
    headers_enabled=True,
    storage_uri=os.environ["FLASK_LIMITER_STORAGE_URI"],
    default_limits=["300/minute", "6/second"],
)

ALIAS_REGEX = re.compile(r"^(?=.*[A-Za-z0-9])[\w\-]{1,50}$")
BLACKLISTED_ALIASES = {"shorten", "analytics"}


def check_url(url: str) -> bool:
    prepared_request = PreparedRequest()
    try:
        prepared_request.prepare_url(url, None)
        return True
    except MissingSchema:
        return False


@app.route("/")
def home():
    return render_template("index.html")


def is_slug_used(slug: str) -> bool:
    """
    Returns a boolean value whether the given slug has been used or not.
    """
    return bool(db_session.query(URLModel).filter_by(slug=slug).first())


def is_analytics_id_used(analytics_id: str) -> bool:
    """
    Returns a boolean value whether the given analytics ID has been used or not.
    """
    return bool(db_session.query(URLModel).filter_by(analytics_id=analytics_id).first())


def generate_random_string(length: int):
    charset = string.ascii_letters + string.digits
    return "".join((random.choice(charset) for _ in range(length)))


def construct_url_path(path: str):
    """
    Returns the full URL to the /path. Do NOT prepend `path` with `/`.
    """
    return f"{url_for('home', _external=True)}{path}"


@app.route("/shorten", methods=["GET", "POST"])
def shorten():
    try:
        if request.method == "GET":
            return render_template("index.html")

        data = request.json
        if data is None:
            return (
                ({"ok": False, "message": "Please provide a valid JSON object."}),
                400,
            )

        url = data.get("original-url")
        alias_type = data.get("alias-type")
        if url is None or alias_type is None:
            return (
                (
                    {
                        "ok": False,
                        "message": "Missing fields `original-url` or `alias-type`.",
                    }
                ),
                400,
            )

        if not check_url(url):
            return ({"ok": False, "message": "The entered URL is invalid."}), 400

        if alias_type == "random":
            slug = generate_random_string(6)
            slug_used = is_slug_used(slug)
            while slug_used:
                slug = generate_random_string(6)
                slug_used = is_slug_used(slug)

        elif alias_type == "custom":
            slug = data.get("alias")
            if slug is None:
                return {"ok": False, "message": "Missing field `slug`."}, 400

            if slug in BLACKLISTED_ALIASES:
                return {
                    "ok": False,
                    "message": f"The alias {slug} is not allowed.",
                }, 400

            if not ALIAS_REGEX.match(slug):
                return (
                    (
                        {
                            "ok": False,
                            "message": "Invalid alias! It must only contain alphanumeric characters, hyphens (-), underscores (_), and not be longer than 50 characters.",
                        }
                    ),
                    400,
                )

            if is_slug_used(slug):
                return (
                    (
                        {
                            "ok": False,
                            "message": "This custom alias has already been used! Try another one.",
                        }
                    ),
                    400,
                )

        else:
            return ({"ok": False, "message": "Invalid alias type!"}), 400

        analytics_id = generate_random_string(6)
        analytics_id_used = is_analytics_id_used(analytics_id)
        while analytics_id_used:
            analytics_id = generate_random_string(6)
            analytics_id_used = is_analytics_id_used(analytics_id)

        url_entity = URLModel(url, slug, analytics_id)
        db_session.add(url_entity)
        db_session.commit()

        resp = {
            "ok": True,
            "message": construct_url_path(slug),
            "analytics_url": construct_url_path(f"analytics/{analytics_id}"),
        }

        try:
            # make a qr for the shortened URL
            qr = data.get("qr")
            if qr and isinstance(qr, bool):
                resp["qr_code"] = segno.make(resp["message"], micro=False).png_data_uri(
                    scale=7, border=2
                )
        except Exception as e:
            logging.exception(e)
        finally:
            return resp, 200

    except (werkzeug.exceptions.BadRequest, werkzeug.exceptions.UnsupportedMediaType):
        return ({"ok": False, "message": "Invalid/Missing JSON object."}, 422)

    except sqlalchemy.exc.PendingRollbackError:
        db_session.rollback()
        return (
            {
                "ok": False,
                "message": "Unable to fulfill this request, please try again.",
            }
        ), 500

    except Exception as e:
        logging.exception(e)
        return (
            {
                "ok": False,
                "message": "An internal server error occured, please try again later.",
            }
        ), 500


@app.route("/analytics/<string:analytics_id>", methods=["GET"])
def analytics(analytics_id: str):
    url_entity = db_session.query(URLModel).filter_by(analytics_id=analytics_id).first()
    if not url_entity:
        return render_template("404.html")

    return render_template("analytics.html", url_entity=url_entity)


def increment_clicks(slug: str):
    max_retries = 5
    for i in range(max_retries):
        try:
            # Fetch the current click count in a fresh query to avoid stale data
            current_clicks = (
                db_session.query(URLModel.clicks)
                .filter_by(slug=slug)
                .scalar()
            )
            # Update clicks with the new value
            db_session.query(URLModel).filter_by(slug=slug).update(
                {"clicks": current_clicks + 1}
            )
            db_session.commit()
            return
        except sqlalchemy.exc.PendingRollbackError:
            db_session.rollback()
            time.sleep(2 ** i)
        except Exception as e:
            print(f"Failed to increment clicks: {e}")
            db_session.rollback()
            time.sleep(2 ** i)


@app.route("/<string:slug>")
def get(slug):
    try:
        url_model = db_session.query(URLModel).filter_by(slug=slug).first()
        if url_model:
            t = Thread(target=increment_clicks, args=(url_model.slug,))
            t.start()
            return render_template("redirect.html", url=url_model.original_url)
        else:
            return render_template("404.html"), 404

    except sqlalchemy.exc.PendingRollbackError:
        db_session.rollback()
        abort(500)
