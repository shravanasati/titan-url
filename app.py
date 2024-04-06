import logging
import os
from random import choice
import re
from string import ascii_letters, digits

import sqlalchemy
import sqlalchemy.exc

from database import db_session, init_db
from models import URL as URLModel

from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from requests.exceptions import MissingSchema
from requests.models import PreparedRequest

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
    default_limits=["60/minute", "1/second"],
)

ALIAS_REGEX = re.compile(r"^(?=.*[A-Za-z0-9])[\w\-]{1,50}$")


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


@app.route("/shorten", methods=["GET", "POST"])
def shorten():
    try:
        if request.method == "GET":
            return render_template("index.html")

        data = request.json
        if data is None:
            return (
                (
                    {"ok": False, "message": "Please provide a valid JSON object."}
                ),
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
            slug = "".join(
                [choice([choice(digits), choice(ascii_letters)]) for _ in range(6)]
            )

            slug_used = is_slug_used(slug)
            while slug_used:
                slug = "".join(
                    [choice([choice(digits), choice(ascii_letters)]) for _ in range(6)]
                )
                slug_used = is_slug_used(slug)

        elif alias_type == "custom":
            slug = data.get("alias")
            if slug is None:
                return ({"ok": False, "message": "Missing field `slug`."})

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

        url_entity = URLModel(url, slug)
        db_session.add(url_entity)
        db_session.commit()
        return ({"ok": True, "message": f"{request.host_url}{slug}"}), 200

    except sqlalchemy.exc.PendingRollbackError:
        db_session.rollback()
        return ({"ok": False, "message": "Unable to fulfill this request, please try again."}), 500

    except Exception as e:
        logging.exception(e)
        return ({"ok": False, "message": "An internal server error occured, please try again later."}), 500


@app.route("/<string:slug>")
def get(slug):
    url = db_session.query(URLModel).filter_by(slug=slug).first()
    if url:
        return render_template("redirect.html", url=url.original_url)
    else:
        return render_template("404.html")
