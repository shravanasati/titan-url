from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from random import choice
from string import ascii_letters, digits

app = Flask(__name__)

@app.route("/")
def home():
	return render_template('index.html')


@app.route("/shorten")
def shorten(url):
	try:
		url = request.form['original-url']
		print(url)
		# alias_type = request.form['alias-type']

		slug = ""
		for _ in range(6):
			slug += choice(choice(digits), choice(ascii_letters), choice("-_-"))
		print(slug)
		conn = sqlite3.connect("urls.db")
		c = conn.cursor()
		c.execute("CREATE TABLE IF NOT EXISTS urls(original_url text, slug text)")
		c.execute("INSERT INTO urls VALUES(:url, :slug)", {"url":url, "slug":slug})
		conn.commit()
		conn.close()
		return jsonify({
			"ok": True,
			"shortened_url": f"/{slug}"
		})


	except Exception as e:
		print(e)
		return jsonify({
			"ok": False,
			"shortened_url": "none"
		})

@app.route("/<string:slug>")
def get(slug):
	conn = sqlite3.connect("urls.db")
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS urls(original_url text, slug text)")
	c.execute("SELECT * FROM urls WHERE slug = :slug", {"slug":slug})
	try:
		url = c.fetchall()[0][1]
		return redirect(url)
	except Exception as e:
		print(e)
		return render_template("404.html")
	finally:
		conn.close()

if __name__ == "__main__":
	app.run(debug=True)