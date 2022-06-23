from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from characters import upper_alphabet_list, lower_alphabet_list, numbers
import random
import webbrowser

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url-data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class UrlForm(FlaskForm):
    long_url = StringField(label="Enter your url", validators=[DataRequired()])
    submit = SubmitField(label="Shorten Url")


class UrlData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_url = db.Column(db.String, nullable=False)
    shortened_url = db.Column(db.String)


def generate_shortened_url():
    character_list = [random.choice(upper_alphabet_list) for _ in range(2)]
    for char in range(2):
        letter = random.choice(lower_alphabet_list)
        character_list.append(letter)
    for num in range(2):
        number = str(random.choice(numbers))
        character_list.append(number)

    random.shuffle(character_list)
    shortened_url = ""
    for char in character_list:
        shortened_url += char

    return shortened_url


def validate_shortened_url(url):
    checked_url = UrlData.query.filter_by(shortened_url=url).first()
    if checked_url:
        return True
    else:
        return False


@app.route("/", methods=["POST", "GET"])
def home():
    form = UrlForm(request.form)
    user_url = form.long_url.data
    if form.validate_on_submit() and request.method == "POST":
        new_url = generate_shortened_url()
        while validate_shortened_url(new_url):
            new_url = generate_shortened_url()
        else:
            new_data = UrlData(client_url=user_url, shortened_url=new_url)
            db.session.add(new_data)
            db.session.commit()
            return render_template("index.html", new_url=new_url, form=form)
    return render_template("index.html", form=form)


@app.route("/go-to", methods=["POST", "GET"])
def go_to():
    url_code = request.args.get("url_code")
    data = UrlData.query.filter_by(shortened_url=url_code).first()
    website = data.client_url
    return webbrowser.open(f'http://{website}')


@app.route("/<short_code>")
def redirect_to(short_code):
    data = UrlData.query.filter_by(shortened_url=short_code).first()
    website = data.client_url
    return webbrowser.open(f"http://{website}")

if __name__ == '__main__':
    app.run(debug=True)