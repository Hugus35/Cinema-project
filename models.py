from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine, Boolean, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Several-several relationshop managing
Played_in = Table(
    'played_in', Base.metadata,
    Column('actor', String, ForeignKey('actors.nconst'), primary_key = True, index = True),
    Column('movie', String, ForeignKey('movies.tconst'), primary_key = True, index = True)
)

Movie_genre = Table(
    'movie_genre', Base.metadata,
    Column('movie', String, ForeignKey('movies.tconst'), primary_key = True, index = True),
    Column('genre', Integer, ForeignKey('genres.id'), primary_key = True, index = True)
)

# Definition of every table with SQLAlchemy ORM
class Actor(Base):
    __tablename__ = 'actors'

    nconst = Column(String, primary_key = True, index = True)
    primary_name = Column(String, index = True)
    birth_year = Column(Integer, index = True)
    death_year = Column(Integer, index = False, nullable = True)

    movies = relationship("Movie", secondary = Played_in, back_populates = 'actors')


class Movie(Base):
    __tablename__ = 'movies'

    tconst = Column(String, primary_key = True, index = True)
    primary_title = Column(String)
    original_title = Column(String, index = True)
    is_adult = Column(Boolean)
    start_year = Column(Integer, index = True)
    run_time_minutes = Column(Integer, nullable = True)

    actors = relationship("Actor", secondary = Played_in, back_populates = 'movies')
    genres = relationship('Genre', secondary = Movie_genre, back_populates = 'movies')
    movie_rating = relationship("Movie_rating", back_populates = "movie")


class Movie_rating(Base):
    __tablename__ = 'movie_ratings'

    tconst = Column(String, ForeignKey('movies.tconst'), primary_key = True, index = True)
    average_rating = Column(Float, index = True)
    num_votes = Column(Integer, index = False)

    movie = relationship("Movie", back_populates = "movie_rating")


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String, unique = True)

    movies = relationship("Movie", secondary = Movie_genre, back_populates = 'genres')