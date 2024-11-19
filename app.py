from fastapi import FastAPI, Depends
from typing import Annotated, List
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select, func, desc
from models import Movie, Genre, Movie_rating, Movie_genre, Played_in, Actor
from data_validation import Movie_per_year, Movie_per_genre, Rating_ranking, Actor_rating
import requests


path = 'sqlite:///database.db'
connect_args = {"check_same_thread": False}
engine = create_engine(path, connect_args=connect_args)
Session = sessionmaker(engine)

app = FastAPI()
 
def get_session():
    with Session() as session:
        yield session

# In function args, this variable allows to open and close a session
SessionDep = Annotated[Session, Depends(get_session)] 

def get_data(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print('Data collected')
        return data
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return None


@app.get("/perYear")
def movie_per_year(session: SessionDep)-> List[Movie_per_year]:
    data = (
        session.query(
            Movie.start_year.label("year"), func.count(Movie.primary_title).label("movie_number"))
            .group_by(Movie.start_year)
            .having(Movie.start_year <= 2024)
        )
    return data.all()


@app.get("/perGenre")
def movie_per_genre(session: SessionDep)-> List[Movie_per_genre]:
    data = (
        session.query(
            Genre.name.label("genre"), func.count(Movie_genre.c.movie).label("movie_number"))
            .join(Movie_genre, Genre.id == Movie_genre.c.genre)
            .group_by(Genre.id)
            .having(func.count(Movie_genre.c.movie)>15000)
        )

    return data.all()

@app.get("/movieRating")
def rating_ranking(session: SessionDep)-> List[Rating_ranking]:
    data = (
    session.query(
        Movie.primary_title.label("title"), (Movie_rating.num_votes*Movie_rating.average_rating).label('score'), 
        Movie_rating.average_rating.label("rating"), Movie_rating.num_votes.label("num_votes") )
        .join(Movie, Movie_rating.tconst == Movie.tconst)
        .order_by(desc(Movie_rating.num_votes*Movie_rating.average_rating))
        .limit(10)
    )

    return data.all()


@app.get("/actorRanking")
def rating_ranking(session: SessionDep)-> List[Actor_rating]:
    data = (
    session.query(
        Actor.primary_name.label("actor"), func.sum(Movie_rating.average_rating*Movie_rating.num_votes).label('score'),
        func.avg(Movie_rating.average_rating).label("average_rating"), func.avg(Movie_rating.num_votes).label("num_votes"))
        .join(Played_in, Actor.nconst == Played_in.c.actor)
        .join(Movie_rating, Played_in.c.movie == Movie_rating.tconst)
        .group_by(Played_in.c.actor)
        .having(func.count(Actor.primary_name) >= 4)
        .order_by(desc(func.avg(Movie_rating.average_rating*Movie_rating.num_votes)))
        .limit(10)
    )

    return data.all()