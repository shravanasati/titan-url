import logging
import os
from random import choice
from string import ascii_letters, digits

from database import db_session, init_db
from models import URL as URLModel

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request
from requests.exceptions import MissingSchema
from requests.models import PreparedRequest

load_dotenv()
init_db()

app = Flask(__name__)
app.config["POSTGRES_URL"] = os.environ["POSTGRES_URL"]
if app.config["POSTGRES_URL"].endswith("sslmode"):
    app.config["POSTGRES_URL"] += "=require"


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
            return jsonify(
                {"ok": False, "message": "Please provide a valid JSON object."}
            )

        url = data.get("original-url")
        alias_type = data.get("alias-type")
        if url is None or alias_type is None:
            return jsonify(
                {
                    "ok": False,
                    "message": "Missing fields `original-url` or `alias-type`.",
                }
            )

        if not check_url(url):
            return jsonify({"ok": False, "message": "The entered URL is invalid."})

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
                return jsonify({"ok": False, "message": "Missing field `slug`."})

            if is_slug_used(slug):
                return jsonify(
                    {
                        "ok": False,
                        "message": "This custom alias has already been used! Try another one.",
                    }
                )

        else:
            return jsonify({"ok": False, "message": "Invalid alias type!"})

        url_entity = URLModel(url, slug)
        db_session.add(url_entity)
        db_session.commit()
        return jsonify({"ok": True, "message": f"{request.host_url}{slug}"})

    except Exception as e:
        logging.exception(e)
        return render_template("404.html")


@app.route("/<string:slug>")
def get(slug):
    url = db_session.query(URLModel).filter_by(slug=slug).first()
    if url:
        return redirect(url.original_url)
    else:
        return render_template("404.html")
