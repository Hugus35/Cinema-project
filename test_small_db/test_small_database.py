import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Base, Movie, Actor, Movie_rating, Movie_genre
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select, func, desc
from db_functions import *

import pandas as pd

import time

start = time.time()
path = 'sqlite:///test_small_db/small_db.db'

engine = create_engine(path)

Base.metadata.drop_all(bind = engine)
Base.metadata.create_all(bind = engine)

load_movies(engine, test = True)
load_ratings(engine, test = True)
load_actors(engine, test = True)
load_played_in(engine, test = True)

end = time.time()
print(f"Total time : {(end-start):.2f} s") 


