from models import Base, Movie, Actor, Movie_rating, Played_in, Genre
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tqdm import tqdm
import pandas as pd


def preprocess_actors(engine, test):
    """Load DataFrame from name.basics.tsv or test_name.csv, rename columns and filter only actors/actress born after 1940.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.
        test (bool): if True, use the test table in test_small_db repository. Allow to test functions on small database.

    Returns:
        pd.DataFrame: filtered and cleaned DataFrame
    """
    if test :
        name_basics = pd.read_csv('test_small_db/test_name.csv', sep = ';', na_values = '\\N')
    else :
        url = 'https://datasets.imdbws.com/name.basics.tsv.gz'
        name_basics = pd.read_csv(url, sep = '\t', na_values = '\\N', compression = "gzip")
    
    # Let's gather only actor and actress born after 1940 to limit the file size
    name_basics = name_basics[name_basics['birthYear'] >= 1940]
    name_basics = name_basics[
        name_basics['primaryProfession'].str.contains('actor|actress', na=False)
    ]
    name_basics = name_basics.drop(['primaryProfession'], axis = 1)

    name_basics = name_basics.rename(columns={
        'nconst': 'nconst',
        'primaryName': 'primary_name',
        'birthYear': 'birth_year',
        'deathYear': 'death_year'
    })
    return name_basics


def preprocess_movies(engine, test):
    """Load DataFrame from title.basics.tsv or test_title.csv, rename columns and filter only movie type.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.
        test (bool): if True, use the test table in test_small_db repository. Allow to test functions on small database.

    Returns:
        pd.DataFrame: filtered and cleaned DataFrame
    """

    if test :
        title_basics = pd.read_csv('test_small_db/test_title.csv', sep=';', na_values='\\N')
    else :
        url = 'https://datasets.imdbws.com/title.basics.tsv.gz'
        title_basics = pd.read_csv(url, sep='\t', na_values='\\N', dtype = {'runtimeMinutes': 'string'}, compression = "gzip")
    
    # Let's collect only the movies
    title_basics = title_basics[title_basics['titleType'] == 'movie']
    title_basics = title_basics.drop(['titleType', 'endYear'], axis = 1)
    
    # If not a number, convert into Nan
    title_basics['runtimeMinutes'] = pd.to_numeric(title_basics['runtimeMinutes'], errors = 'coerce')

    title_basics = title_basics.rename(columns={
        'tconst': 'tconst',
        'primaryTitle': 'primary_title',
        'originalTitle': 'original_title',
        'isAdult': 'is_adult',
        'startYear': 'start_year',
        'runtimeMinutes': 'run_time_minutes'
    })

    return title_basics


def preprocess_ratings(engine, test):
    """Load DataFrame from title.ratings.tsv or test_ratings.csv, rename columns and filter only movie type.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.
        test (bool): if True, use the test table in test_small_db repository. Allow to test functions on small database.

    Returns:
        pd.DataFrame: filtered and cleaned DataFrame
    """
    if test :
        title_ratings = pd.read_csv('test_small_db/test_rating.csv', sep = ';', na_values = '\\N')
    else : 
        url = "https://datasets.imdbws.com/title.ratings.tsv.gz"
        title_ratings = pd.read_csv(url, sep = '\t', na_values = '\\N', compression = "gzip")

    title_ratings = title_ratings.rename(columns={
        'tconst': 'tconst',
        'averageRating': 'average_rating',
        'numVotes': 'num_votes'
    })  

    return title_ratings


def preprocess_played_in(engine, test):
    """Load DataFrame from title.principals.tsv or test_ratings.csv, extract existing movies and actors from database.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.
        test (bool): if True, use the test table in test_small_db repository. Allow to test functions on small database.

    Returns:
        TextFileReader : DataFrames split in chunks
        list : List of existing movies from database
        list : List of existing actors from database
    """
    if test :
        chunksize = 3
        title_principals = pd.read_csv('test_small_db/test_played_in.csv', sep=';', na_values='\\N', chunksize = chunksize)
    else :
        chunksize = 100000
        title_principals = pd.read_csv('https://datasets.imdbws.com/title.principals.tsv.gz', compression = 'gzip', sep = '\t', na_values = '\\N', chunksize = chunksize)
    
    Session = sessionmaker(bind = engine)
    session = Session()

    existing_movie_ids = [movie[0] for movie in session.query(Movie.tconst).all()]
    existing_actor_ids = [actor[0] for actor in session.query(Actor.nconst).all()]

    session.close()

    return title_principals, existing_movie_ids, existing_actor_ids



def load_ratings(engine, test = False):
    """Load data to fill movie_ratings table.
    Check if the film is well referenced on the movies table before adding it to movie_ratings table.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.
        test (bool, optional): if True, use the test table in test_small_db repository. Allow to test functions on small database.
          Defaults to False.
    """

    # Use preprocessing function to set up the DataFrame
    title_ratings = preprocess_ratings(engine, test)

    Session = sessionmaker(bind = engine)
    session = Session()

    # We only want to add ratings for movie already presents on the table movie
    movie_ids = [row[0] for row in session.query(Movie.tconst).all()]
    title_ratings = title_ratings[title_ratings['tconst'].isin(movie_ids)]

    print("rating table creation...")
    title_ratings.to_sql('movie_ratings', con = engine, if_exists = 'append', index = False)

    session.commit()
    session.close()



def load_actors_not_used(engine, test = False):
    """Load data to fill actors table and played_in table.
   For each actor, extract movies from its attibutes to link actors and movies in played_in table.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.        
        test (bool, optional): if True, use the test table in test_small_db repository. Allow to test functions on small database.
          Defaults to False.
    """

    # Call preprocessing function to set up the DataFrame
    name_basics = preprocess_actors(engine, test)

    Session = sessionmaker(bind = engine)
    session = Session()

    # Using a cache to reduce interaction with the database
    existing_movie_ids = {movie.tconst: movie for movie in session.query(Movie).all()}

    # Movie extraction from actors : we only want to consider movies already referenced on the table movie. 
    # We compare its id with the previous dict.
    for i, row in tqdm(name_basics.iterrows(), desc = 'Association movie-actor', total = name_basics.shape[0]):
        acteur = Actor(nconst = row['nconst'], primary_name = row['primary_name'], 
                       birth_year = row['birth_year'], death_year = row['death_year'])
        if pd.notna(row['knownForTitles']): 
            film_ids = row['knownForTitles'].split(",")
            for film_id in film_ids:
                film_id = film_id.strip()
                existing_movie = existing_movie_ids.get(film_id)
                if existing_movie:
                    acteur.movies.append(existing_movie)
        
        session.add(acteur)

        # Commit data every 5000 iterations
        if i%5000 == 0 : 
            session.commit()
    
    session.commit()
    session.close()


def load_actors(engine, test = False):
    """Load data to fill actors table.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.
        test (bool, optional): if True, use the test table in test_small_db repository. Allow to test functions on small database.
          Defaults to False.
    """
    name_basics = preprocess_actors(engine, test)
    name_basics = name_basics.drop(['knownForTitles'], axis = 1)

    Session = sessionmaker(bind = engine)
    session = Session()

    name_basics.to_sql('actors', con = engine, if_exists = 'append', index = False)



def load_played_in(engine, test = False):
    """Load data to fill played_in table. Use of batches to fill the table since the raw file is too large.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.
        test (bool, optional): if True, use the test table in test_small_db repository. Allow to test functions on small database.
          Defaults to False.
    """
    title_principals, existing_movie_ids, existing_actor_ids = preprocess_played_in(engine, test)
    nb_errors = 0

    # Iteration on each batch with filtering actors/actress, movies and actors already referenced on corresponding tables
    for i, chunk in enumerate(tqdm(title_principals, desc = "Chunks treatment")):
        try:
            chunk = chunk[(chunk['category'].str.contains('actor|actress', case=False, na=False)) & 
                          (chunk['nconst'].isin(existing_actor_ids)) & 
                          (chunk['tconst'].isin(existing_movie_ids))]
            
            chunk = chunk.drop(['ordering', 'category', 'job', 'characters'], axis = 1)
            chunk = chunk.drop_duplicates()
            chunk = chunk.rename(columns={
                'tconst': 'movie',
                'nconst': 'actor',
            })

            #print(i, chunk.head())
            chunk.to_sql('played_in', con = engine, if_exists = 'append', index = False)

        except Exception as e:
            nb_errors = nb_errors + chunk.shape[0]
            print(f"Error : {e}, Chunk : {chunk.head()}, Nombre de lignes non-insérées : {nb_errors}")



def associate_movie_genre(engine, title_basics):
    """Link movie and its genres from title_basics DataFrame. 
    For a movie, if one of its genre is already referenced in genres table, we just add it to the movie as an attributes. 
    If it doesn't references, we add it in genres table, we collect its new id and we add it to the movie as an attributes.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.
        title_basics (pd.DataFrame): Cleaned DataFrame containing information about movies.

    Returns:
        asso (List): Return list of dictionnary which contains pairs movie-genre.
    """

    Session = sessionmaker(bind = engine)
    session = Session()
    
    # We want to add genres not already present on the table genres
    existing_genres = session.query(Genre.id, Genre.name).all()
    existing_genres = {name: genre_id for genre_id, name in existing_genres}
    asso = []

    for i, row in tqdm(title_basics.iterrows(), desc = 'Association movie-genre', total = title_basics.shape[0]):
        film = row['tconst']
        if pd.notna(row['genres']): 
            genres = row['genres'].split(",")
            for genre_name in genres:
                genre_name = genre_name.strip()
                existing_id = existing_genres.get(genre_name)
                # If the genre doesn't exist yet, we add it on the table and we collect its id
                if existing_id is None:
                    new_genre = Genre(name = genre_name)
                    session.add(new_genre)
                    session.flush()
                    existing_id = new_genre.id
                    existing_genres[genre_name] = new_genre.id
                
                asso.append({'movie': film, 'genre' : existing_id})

        # Add to the database every 5000 iterations
        if i%5000 == 0 : session.commit()
    
    session.commit()
    session.close()
    return asso


def load_movies(engine, test = False):
    """Call preprocess and association function, first to clean movies DataFrame, then to extract its genres for each movie.
    Finally, create movie table and movie_genre table, which associate movies and their genres.

    Args:
        engine (sqlalchemy.orm.engine): Engine to connect to database.
        test (bool, optional): if True, use the test table in test_small_db repository. Allow to test functions on small database.
          Defaults to False.
    """

    title_basics = preprocess_movies(engine, test)
    asso = associate_movie_genre(engine, title_basics)
    
    print("movie table creation...")
    title_basics = title_basics.drop(['genres'], axis = 1)
    title_basics.to_sql('movies', con = engine, if_exists='append', index=False)

    print("genre table creation...")
    asso = pd.DataFrame(asso)
    asso.to_sql('movie_genre', con = engine, if_exists = 'append', index = False)
    
