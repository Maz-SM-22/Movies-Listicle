from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

MOVIE_API_KEY = os.environ['THEMOVIEDB_API_KEY']

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return '<Movie %r>' % self.title

# db.create_all()
# db.session.commit()


class EditForm(FlaskForm):
    rating = StringField('Your Rating Out Of 10')
    review = TextAreaField('Your Review')
    submit = SubmitField('Submit')

class AddForm(FlaskForm): 
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


@app.route('/')
def home():
    movies = db.session.query(Movie).order_by(Movie.rating).all()
    for i in range(len(movies)): 
        movies[i].ranking = len(movies) - i 
    db.session.commit()
    return render_template('index.html', movies=movies)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = EditForm()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit(): 
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit(): 
        movie_title = form.title.data
        movie_data = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={MOVIE_API_KEY}&query={movie_title}').json()['results']
        return render_template('select.html', movies=movie_data)
    return render_template('add.html', form=form)


@app.route('/details')
def get_movie_details(): 
    movie_data = requests.get(f"https://api.themoviedb.org/3/movie/{request.args.get('id')}?api_key={MOVIE_API_KEY}").json()
    new_movie = Movie(
        title = movie_data['original_title'], 
        year = movie_data['release_date'][0:4],
        description = movie_data['overview'],
        img_url = 'https://image.tmdb.org/t/p/w500/' + movie_data['poster_path'] 
    )
    db.session.add(new_movie)
    db.session.commit()

    return redirect(url_for('edit', id=new_movie.id))


@app.route('/delete', methods=['GET', 'POST'])
def delete(): 
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='1300')
