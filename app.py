from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from random import choice
from string import ascii_letters, digits
import re

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def home():
    return render_template('index.html', URL="The shortened URL will appear here", scroll="no")

def is_slug_used(slug:str) -> bool:
    """
    Returns a boolean value whether the given slug has been used or not.
    """
    conn = sqlite3.connect("./urls.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS urls(original_url text, slug text)")
    c.execute("SELECT (slug) FROM urls")
    used_slugs = {i[0] for i in c.fetchall()}

    return slug in used_slugs


@app.route("/shorten", methods=['GET'])
def shorten():
    try:
        url = request.headers["original-url"]
        alias_type = request.headers["alias-type"]
        print("URL", url)
        print("Alias Type", alias_type)

        if len(re.findall(r"^[http|https|ftp|ftps]://\w", url)) == 0:
            return jsonify({
                "ok": False,
                "message": "The entered URL is invalid."
            })

        if alias_type == "random":
            slug = "".join([choice([choice(digits), choice(ascii_letters)]) for _ in range(6)])
    
            slug_used = is_slug_used(slug)
            while slug_used:
                slug = "".join([choice([choice(digits), choice(ascii_letters)]) for _ in range(6)])
                slug_used = is_slug_used(slug)

        elif alias_type == "custom":
            slug = request.headers["slug"]
            if is_slug_used(slug):
                return jsonify({
                    "ok": False,
                    "message": "This custom alias is already used! Try another one."
                })

        else:
            return jsonify({
                "ok": False,
                "message": "Invalid slug type!"
            })

        print("SLUG", slug)

        conn = sqlite3.connect("./urls.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS urls(original_url text, slug text)")
        c.execute("INSERT INTO urls VALUES(:url, :slug)",
                  {"url": url, "slug": slug})
        conn.commit()
        conn.close()

        return jsonify({
            "ok": True,
            "message": f"{request.host_url}{slug}"
        })

    except Exception as e:
        print(e)
        return render_template('404.html')


@app.route("/<string:slug>")
def get(slug):
    conn = sqlite3.connect("./urls.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS urls(original_url text, slug text)")
    c.execute("SELECT * FROM urls WHERE slug = :slug", {"slug": slug})
    try:
        url = c.fetchone()[0]
        print(url)
        return redirect(url)
    except Exception as e:
        print(e)
        return render_template("404.html")
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
