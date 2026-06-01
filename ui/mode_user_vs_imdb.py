import streamlit as st
from app.imdb_client import fetch_top_movies
from app.similarity import ratings_to_permutation, interpret_score
from algorithm.sort_and_count import sort_and_count


@st.cache_data(ttl=3600)
def _buscar_filmes(n):
    return fetch_top_movies(n)


def _init_state():
    for key, default in [
        ("movies_uvi", []),
        ("n_uvi", 10),
        ("result_uvi", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


def render():
    _init_state()

    st.header("Usuário vs IMDb")
    st.markdown("Avalie os filmes do Top IMDb e veja o quanto seu gosto coincide com o ranking oficial.")

    # ── Seleção de N e busca ──────────────────────────────────────────────────
    col_slider, col_btn = st.columns([3, 1])

    with col_slider:
        n = st.slider("Quantos filmes do Top IMDb?", min_value=5, max_value=50, value=st.session_state["n_uvi"], step=5)

    with col_btn:
        st.write("")
        st.write("")
        buscar = st.button("🎬 Buscar Filmes", use_container_width=True)

    if buscar:
        if n != st.session_state["n_uvi"]:
            st.session_state["result_uvi"] = None
        st.session_state["n_uvi"] = n
        with st.spinner("Buscando filmes no IMDb..."):
            st.session_state["movies_uvi"] = _buscar_filmes(n)

    movies = st.session_state["movies_uvi"]

    if not movies:
        st.info("Clique em **Buscar Filmes** para carregar o catálogo.")
        return

    # ── Cards + sliders de nota ───────────────────────────────────────────────
    st.divider()
    st.subheader("Atribua sua nota de 0 a 10 para cada filme")

    ratings = []
    cols_per_row = 5

    for row_start in range(0, len(movies), cols_per_row):
        row_movies = movies[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, movie in zip(cols, row_movies):
            with col:
                if movie["image"]:
                    st.image(movie["image"], use_container_width=True)
                st.caption(f"**{movie['title']}**")
                st.caption(f"⭐ IMDb: {movie['rating']}")
                nota = st.number_input(
                    "Sua nota",
                    min_value=0.0,
                    max_value=10.0,
                    value=5.0,
                    step=0.5,
                    key=f"uvi_nota_{row_start + row_movies.index(movie)}",
                    label_visibility="collapsed",
                )
                ratings.append(nota)

    # ── Botão comparar ────────────────────────────────────────────────────────
    st.divider()
    if st.button("Comparar com IMDb", type="primary", use_container_width=False):
        permutation = ratings_to_permutation(ratings)
        _, inversions = sort_and_count(permutation)
        max_inversions = n * (n - 1) // 2
        similarity_pct, interpretation = interpret_score(inversions, max_inversions)

        st.session_state["result_uvi"] = {
            "inversions": inversions,
            "max_inversions": max_inversions,
            "similarity_pct": similarity_pct,
            "interpretation": interpretation,
            "ratings": ratings,
            "permutation": permutation,
        }

    # ── Resultado ────────────────────────────────────────────────────────────
    result = st.session_state["result_uvi"]
    if not result:
        return

    st.divider()
    st.subheader("Resultado")

    m1, m2, m3 = st.columns(3)
    m1.metric("Inversões", f"{result['inversions']} / {result['max_inversions']}")
    m2.metric("Similaridade", f"{result['similarity_pct']:.1f}%")
    m3.metric("Máximo possível", result["max_inversions"])

    st.success(result["interpretation"])

    # Duas tabelas lado a lado: ranking IMDb e ranking do usuário
    st.subheader("Comparativo de Rankings")

    user_order = result["permutation"]  # índices dos filmes na ordem do usuário (melhor → pior)
    ratings_list = result["ratings"]

    col_imdb, col_user = st.columns(2)

    with col_imdb:
        st.markdown("**Ranking IMDb**")
        imdb_table = [
            {
                "Posição": i + 1,
                "Filme": movies[i]["title"],
                "Nota IMDb": movies[i]["rating"],
            }
            for i in range(len(movies))
        ]
        st.dataframe(imdb_table, use_container_width=True, hide_index=True)

    with col_user:
        st.markdown("**Seu Ranking**")
        user_table = [
            {
                "Posição": rank + 1,
                "Filme": movies[idx]["title"],
                "Sua Nota": ratings_list[idx],
            }
            for rank, idx in enumerate(user_order)
        ]
        st.dataframe(user_table, use_container_width=True, hide_index=True)
