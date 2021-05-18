from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from random import randint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@app.route("/")
def home():
	return render_template('index.html')


class URLForm(db.Model):
	sno = db.Column(db.Integer, primary_key=True)
	original_url = db.Column(db.String(1000), nullable=False)
	alias_type = db.Column(db.String(6), nullable=False)
	shortened_url = db.Column(db.String(100))

	def __repr__(self) -> str:
		return f"{self.original_url}: {self.alias_type} = {self.shortened_url} "

@app.route("/shorten")
def shorten():
	url = request.form['original-url']
	alias_type = request.form['alias-type']

	if alias_type == "custom":
		slug = request.form['slug']
		shortened_url = "/{}".format(slug)
		data = URLForm(original_url=url, alias_type=alias_type, shortened_url=shortened_url)
		db.session.add(data)
		db.session.commit()

	elif alias_type == "random":
		slug = str(randint(100000, 1000000))
		shortened_url = "/{}".format(slug)
		data = URLForm(original_url=url, alias_type=alias_type, shortened_url=shortened_url)
		db.session.add(data)
		db.session.commit()

	else:
		print('error')

@app.route("/<string:slug>")
def main(slug):
	results = URLForm.query_all()
	for item in results:
		if item.shortened_url[1:] == slug:
			return redirect(item.original_url)

	else:
		return render_template("404.html")

if __name__ == "__main__":
	app.run(debug=True)