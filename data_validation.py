from pydantic import BaseModel
from typing import List, Optional

class Movie_per_year(BaseModel):
    year: int
    movie_number: int

    # Allow to transfer Python object
    class Config:
        from_attributes = True


class Movie_per_genre(BaseModel):
    genre: str
    movie_number: int

    class Config:
        from_attributes = True


class Rating_ranking(BaseModel):
    title: str
    score: float
    rating: float
    num_votes: int
    
    class Config:
        from_attributes = True

class Actor_rating(BaseModel):
    actor: str
    score: float
    average_rating: float
    num_votes: float

    class Config:
        from_attributes = True
