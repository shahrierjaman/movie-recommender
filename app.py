import streamlit as st
import pickle
import pandas as pd
import requests

# ---------------- LOAD DATA ----------------
movie_list = pickle.load(open('movies_dict_v3.pkl', 'rb'))
movies = pd.DataFrame(movie_list)
similarity = pickle.load(open('similarity_v3.pkl', 'rb'))

# ---------------- FETCH POSTER ----------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=f3eab8a78bf888910ee0826edd6dfe83&language=en-US"
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "https://via.placeholder.com/500x750?text=No+Poster"

# ---------------- RECOMMEND FUNCTION ----------------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movie_scores = []
    for i, sim in enumerate(distances):
        pop = movies.iloc[i]['popularity']
        hybrid_score = (0.7 * sim) + (0.3 * (pop / movies['popularity'].max()))
        movie_scores.append((i, hybrid_score))

    sorted_movies = sorted(movie_scores, key=lambda x: x[1], reverse=True)[1:6]

    results = []
    for i, score in sorted_movies:
        tmdb_id = movies.iloc[i]['movie_id']
        results.append({
            "title": movies.iloc[i].title,
            "poster": fetch_poster(tmdb_id),
            "match": round(score * 100, 2),
            "director": movies.iloc[i]['director'],
            "actors": movies.iloc[i]['top_actors']
        })
    return results

# ---------------- SESSION STATE INIT ----------------
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

# ---------------- UI DESIGN ----------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Dark mode & professional movie-style font CSS
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body, .stApp {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Cinzel', serif;
        }

        /* Header */
        .header {
            text-align: center;
            padding: 25px;
            background: linear-gradient(90deg, #4b6cb7, #182848);
            border-radius: 15px;
            box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
        }

        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }

        .header p {
            margin: 5px 0 0 0;
            font-size: 1.2rem;
        }

        /* Gradient button */
        .stButton>button {
            background: linear-gradient(90deg, #4b6cb7, #182848);
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px 20px;
            transition: transform 0.2s;
        }

        .stButton>button:hover {
            transform: scale(1.05);
        }

        /* Movie cards */
        .movie-card {
            background: #1f2937;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin-top: 15px;
            box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
            transition: transform 0.2s;
            width: 250px; /* match poster width */
        }

        .movie-card:hover {
            transform: scale(1.05);
        }

        .movie-card h4 {
            margin:5px 0;
            font-size: 1.1rem;
        }

        .movie-card p {
            margin:3px 0;
            font-size: 0.9rem;
        }

        /* Selectbox styling */
        div.stSelectbox > div > div > span {
            color: #fff;
            font-weight: bold;
        }

        div.stSelectbox > div > div {
            background-color: #1f2937;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <h1>🎬 Movie Recommendation System</h1>
        <p>Discover movies you'll love!</p>
    </div>
""", unsafe_allow_html=True)

# Movie selection
selected_movie = st.selectbox(
    "Select a movie you like:",
    movies['title'].values,
    index=0
)

# Recommend button
if st.button("Recommend Movies", icon="🎥", use_container_width=True):
    with st.spinner("Finding similar movies... ⏳"):
        st.session_state.recommendations = recommend(selected_movie)

# Display recommendations if exist
if st.session_state.recommendations:
    st.subheader(f"Movies similar to: **{selected_movie}**")
    cols = st.columns(5)

    for col, movie in zip(cols, st.session_state.recommendations):
        with col:
            st.image(movie["poster"], width=250)
            st.markdown(
                f"""
                <div class="movie-card">
                    <h4>{movie['title']}</h4>
                    <p>🎬 <b>Director:</b> {movie['director']}</p>
                    <p>⭐ <b>Actors:</b> {movie['actors']}</p>
                    <p>🎯 <b>Match:</b> {movie['match']}%</p>
                </div>
                """,
                unsafe_allow_html=True
            )
