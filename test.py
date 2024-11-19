from models import Base, Movie, Actor, Movie_rating, Movie_genre, Played_in
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select, func, desc
import time
#import dask.dataframe as dd
import pandas as pd

path = 'sqlite:///database.db'

engine = create_engine(path)
conn = engine.connect()


Session = sessionmaker(bind = engine)
session = Session()



# Let's verify that every film in played_in are well referenced in the movie table
# Thus, the following request should be empty
stmt = (select(Movie.primary_title, Played_in.c.actor)
        .outerjoin(Movie, Movie.tconst == Played_in.c.movie)
        .filter(Played_in.c.movie == None))

results = session.execute(stmt).fetchall()

for row in results:
    print(row)


# Let's do the same with ratings : every ids on the rating table must be referenced in the movie table
stmt = (select(Movie.primary_title, Movie_rating.num_votes)
        .outerjoin(Movie, Movie.tconst == Movie_rating.tconst)
        .filter(Movie.tconst == None))

results = session.execute(stmt).fetchall()

for row in results:
    print(row)


session.commit()
session.close()