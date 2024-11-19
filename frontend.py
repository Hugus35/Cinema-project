import streamlit as st
from app import get_data
import pandas as pd
import plotly.express as px
import numpy as np

# Page initialization
st.set_page_config(
    page_title="Film Database",
    page_icon="🎥",
    layout="wide",
    #initial_sidebar_state = "expanded"
)

# Plot the title
st.markdown(
    """
    <h1 style="text-align: center; color: white; background-color: #1f77b4; padding: 20px;">Cinema history</h1>
    <br><br><br>
    """, 
    unsafe_allow_html=True
)


# Gather data from API and plot the distribution of movie per year
data = get_data("http://127.0.0.1:8000/perYear")

data = pd.DataFrame(data)
data = data.rename(columns = {'year': 'Year', 'movie_number': 'Movie number'})
data = data.set_index('Year')

st.markdown(
    "<div style='text-align: center; font-size:24px;'> Amount of movie per year since 1894</div>",
    unsafe_allow_html=True
)
st.bar_chart(data, x_label = 'Year', y_label = "Movie number")



# Gather data from API and plot the pie chart of movie per genre
data = get_data("http://127.0.0.1:8000/perGenre")
data = pd.DataFrame(data)
data = data.rename(columns = {'genre': 'Genre', 'movie_number': 'Movie number'})

st.markdown(
    """
    <br><br>
    <div style='text-align: center; font-size:24px;'> Movie distribution per genre</div>
    """,
    unsafe_allow_html=True
)
fig = px.pie(data, names='Genre', values = 'Movie number')
st.plotly_chart(fig)


# Gather the movie TOP 10 from API
data_movie = get_data("http://127.0.0.1:8000/movieRating")
data_movie = pd.DataFrame(data_movie, index = range(1, 11))
data_movie['score'] = data_movie['score'].apply(np.round).astype('int')

data_movie['score'] = data_movie['score'].apply(lambda x: "{:,}".format(x))
data_movie['rating'] = data_movie['rating'].apply(lambda x: "{:.1f}".format(x))
data_movie['num_votes'] = data_movie['num_votes'].apply(lambda x: "{:,}".format(x))

data_movie = data_movie.rename(columns = {'title': 'Movie', 'num_votes': 'Number of votes', 'rating': 'Average Rating /10', 'score': 'Total score'})

# Set a style to the header of the dataframe, align values
data_movie = data_movie.style.set_table_styles([
    {'selector': 'thead th', 'props': [('background-color', '#1f77b4'), ('color', 'white'), ('font-size', '16px'), ('text-align', 'center')]},
     {'selector': 'td', 'props': [('text-align', 'right')]}
])


# Gather the actor TOP 10 from API
data_actors = get_data("http://127.0.0.1:8000/actorRanking")
data_actors = pd.DataFrame(data_actors, index = range(1, 11))
data_actors['score'] = data_actors['score'].apply(np.round).astype('int')
data_actors['num_votes'] = data_actors['num_votes'].apply(np.round).astype('int')

data_actors['score'] = data_actors['score'].apply(lambda x: "{:,}".format(x))
data_actors['average_rating'] = data_actors['average_rating'].apply(lambda x: "{:.1f}".format(x))
data_actors['num_votes'] = data_actors['num_votes'].apply(lambda x: "{:,}".format(x))


data_actors = data_actors.rename(columns = {'actor': 'Actor', 'score': 'Total score', 'average_rating': 'Average Rating /10', 
                                            'num_votes': 'Average Number of votes'})


# Set a style to the header of the dataframe, align values
data_actors = data_actors.style.set_table_styles([
    {'selector': 'thead th', 'props': [('background-color', '#1f77b4'), ('color', 'white'), ('font-size', '16px'), ('text-align', 'center')]},
     {'selector': 'td', 'props': [('text-align', 'right')]}
])

# Split the page into 2 columns to print tableau next to each other
col1, col2 = st.columns(2)

# Left side filling
with col1:
    st.markdown(
    """
    <br><br>
    <div style='text-align: center; font-size:24px;'> GOAT Movies </div>
    <br>
    """,
    unsafe_allow_html=True
    )

    # Convert into HTML before plotting to show the style of the Dataframe
    st.write(data_movie.to_html(), unsafe_allow_html=True)

    st.markdown(
        """
        <p style='font-size:12px; font-style:italic;'>Calculation details : 
        The score is the product of the average rating of a movie and its number of vote,
        representing the total number of points gathered by this movie.</p>
        """,
        unsafe_allow_html=True
        )

# Right side filling
with col2:
    
    st.markdown(
    """
    <br><br>
    <div style='text-align: center; font-size:24px;'> GOAT Actors </div>
    <br>
    """,
    unsafe_allow_html=True
    )

    # Convert into HTML before plotting to show the style of the Dataframe
    st.write(data_actors.to_html(), unsafe_allow_html=True)

    st.markdown(
        """
        <p style='font-size:12px; font-style:italic;'>Calculation details : 
        The total score is calculated by adding the scores of the 4 main movies of an actor.
        The average rating and average number of votes are the average for those 4 films.</p>
        """,
        unsafe_allow_html=True
        )


# Source website printing
st.markdown(
    """
    <br><br>
    <p style='text-align: center; font-size:12px; font-style:italic;'>
    Data from <a href="https://developer.imdb.com/non-commercial-datasets">IMDb Movies</a>. All rights reserved. </p>
    """,
    unsafe_allow_html=True
    )