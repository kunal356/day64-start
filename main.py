from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from dotenv import load_dotenv
import os

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
load_dotenv()
API_KEY = os.environ['API_KEY']
ACCES_TOKEN = os.environ['ACCESS_TOKEN']


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie-list.db"
Bootstrap5(app)

# CREATE DB
db = SQLAlchemy(app)

# CREATE TABLE


class MovieList(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(
        String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    db.create_all()


class AddForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


class EditForm(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def home():
    all_movies = db.session.execute(
        db.select(MovieList).order_by(MovieList.ranking)).scalars()
    return render_template("index.html", all_movies=all_movies)


@app.route("/add", methods=["POST", "GET"])
def add():
    form = AddForm()
    if form.validate_on_submit():

        url = "https://api.themoviedb.org/3/search/movie"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {ACCES_TOKEN}"
        }
        q_params = {
            "query": form.title.data,
            "include_adult": False,
            "language": "en-US",
            "page": 1
        }

        response = requests.get(url, headers=headers, params=q_params)
        all_movies = response.json()

        return render_template('select.html', all_movies=all_movies)

    return render_template('add.html', form=form)


@app.route("/search", methods=["GET"])
def search():
    movie_id = request.args.get('movie_id')

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {ACCES_TOKEN}"
    }

    response = requests.get(url, headers=headers)
    movie = response.json()
    new_movie = MovieList(
        title=movie['title'],
        img_url=f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}",
        year=f"{movie['release_date'].split("-")[0]}",
        description=movie['overview']
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))
    


@app.route("/edit", methods=["POST", "GET"])
def edit():
    id = request.args.get('id')
    movie_to_update = db.get_or_404(MovieList, id)
    form = EditForm()
    if request.method == "GET":
        form.rating.data = movie_to_update.rating
        form.review.data = movie_to_update.review
    if form.validate_on_submit():
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, title=movie_to_update.title)


@app.route("/delete")
def delete():
    id = request.args.get('id')
    movie_to_delete = db.get_or_404(MovieList, id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
