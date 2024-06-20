from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie-list.db"
Bootstrap5(app)

# CREATE DB
db = SQLAlchemy(app)

# CREATE TABLE
class MovieList(db.Model):
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    title : Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year : Mapped[int] = mapped_column(Integer,nullable=True)
    description : Mapped[str] = mapped_column(String(250), nullable=True)
    rating : Mapped[float] = mapped_column(Float, nullable=True)
    ranking : Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_movies = db.session.execute(
        db.select(MovieList).order_by(MovieList.ranking)).scalars()
    return render_template("index.html", all_movies=all_movies)

if __name__ == '__main__':
    app.run(debug=True)
