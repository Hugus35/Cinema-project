# Cinema history
## The project
This project aims to plot some statistics and graphical presentations about cinema.
Data are gathered from the website IMDb, here is the link of the different files : [imdbws](https://datasets.imdbws.com). 
Only name.basics, title.basics and title.ratings and title.principals have been used so far.

## Project process
- First, the raw data are cleaned and loaded into pandas DataFrame.
- The SQL data model is set up using sqlalchemy (refer to models.py).
- The database is created and loaded. Since we tackle a large amount of data, algorithms to fill the database have been designed to make the filling as quick as possible, but it's still quite long. To test the functions, a small database has been created (ie test_small_db repository).
- A local API is created using fastapi. API allows to collect data from the database in a useful form, making easy to plot some scheme and statistics on the next step. To ensure data are in the right form, a data model is created in data_validation.py.
- Finally, data are collected from the API and plot with the Python library streamlit.

## How to launch the project ?
- First of all, open a terminal and locate you in the project repository.
- It is better to create an environment for this project, to avoid version conflits (Some packages are used by Conda, it is better not to be on the base environment).
- Make sure you have a Python version over 3.11 on this environment.
- Install every mandatory library with the command:  
    $ pip install -r requirements.txt
- If it is the first time you use the project, you need to recreate database from scratch. So you need to use :  
    $ python setup_database.py  
    The next time you launch the project, it is not compulsory to recreate the database since it is saved on your project repository.
- Then, launch the API with :  
    $ uvicorn app:app --reload
- Finally, plot the different statistics with :  
    $ streamlit run frontend.py
    (Not working on Safari browser, prefer Firefox)

## What next ?
- A great improvement should be an automatic update during the API launching, since data files are daily updated on the website.
- Plotting more statistics and patterns about cinema is also in process.