import streamlit as st

COLS_PER_ROW = 5


def render_movie_grid(movies, widget_fn):
    """
    Exibe os filmes em grade de 5 colunas.
    Para cada filme, renderiza imagem, titulo e nota IMDb,
    depois chama widget_fn(movie, idx) para o widget especifico do modo.
    """
    for row_start in range(0, len(movies), COLS_PER_ROW):
        row_movies = movies[row_start:row_start + COLS_PER_ROW]
        cols = st.columns(COLS_PER_ROW)

        for col, movie in zip(cols, row_movies):
            idx = row_start + row_movies.index(movie)
            with col:
                if movie["image"]:
                    st.image(movie["image"], use_container_width=True)
                st.caption(f"**{movie['title']}**")
                st.caption(f"⭐ IMDb: {movie['rating']}")
                widget_fn(movie, idx)
