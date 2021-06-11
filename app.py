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


@app.route("/shorten/", methods=['GET'])
def shorten():
	try:
		url = request.args.get("url")
		print("URL", url)
		# alias_type = request.form['alias-type']

		if len(re.findall(r"[http|https|ftp]://\w", url)) == 0:
			return jsonify({
				"ok":  False,
				"message": "The URL you entered is not valid."
			})

		slug = ""
		for _ in range(6):
			slug += choice([choice(digits), choice(ascii_letters)])
		print("SLUG",slug)
		conn = sqlite3.connect("./urls.db")
		c = conn.cursor()
		c.execute("CREATE TABLE IF NOT EXISTS urls(original_url text, slug text)")
		c.execute("INSERT INTO urls VALUES(:url, :slug)", {"url":url, "slug":slug})
		conn.commit()
		conn.close()

		return jsonify({
			"ok": True,
			"message": f"{request.host_url}{slug}"
		})

	except Exception as e:
		print(e)
		return jsonify({
			"ok": False,
			"message": "An internal server error occured!"
		})

@app.route("/<string:slug>")
def get(slug):
	conn = sqlite3.connect("./urls.db")
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS urls(original_url text, slug text)")
	c.execute("SELECT * FROM urls WHERE slug = :slug", {"slug":slug})
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
	app.run(debug=True, use_reloader=False)