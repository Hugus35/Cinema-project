from models import Base, Movie, Actor, Movie_rating
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import time
#import dask.dataframe as dd
import pandas as pd

start = time.time()
path = 'sqlite:///database.db'

engine = create_engine(path)
"""
#Base.metadata.drop_all(bind = engine)
Base.metadata.create_all(bind = engine)

#load_movies(engine, test = False)
#load_ratings(engine, test = False)
#load_actors(engine, test = False)

end = time.time()
print(f"Total time : {(end-start):.2f} s")
"""
