import streamlit as st
from app.imdb_client import fetch_top_movies
from app.similarity import calculate_similarity, interpret_score


@st.cache_data(ttl=3600)
def _buscar_filmes(n):
    return fetch_top_movies(n)


def _init_state():
    for key, default in [
        ("movies_uvu", []),
        ("n_uvu", 10),
        ("result_uvu", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


def _coletar_ranking(movies, prefixo):
    """Exibe os filmes em cards e coleta a posição atribuída pelo usuário a cada um."""
    n = len(movies)
    st.caption(f"Atribua uma posição de 1 (favorito) a {n} (menos favorito) para cada filme. Sem repetições.")

    posicoes = {}
    cols_per_row = 5

    for row_start in range(0, n, cols_per_row):
        row_movies = movies[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, movie in zip(cols, row_movies):
            idx = row_start + row_movies.index(movie)
            with col:
                if movie["image"]:
                    st.image(movie["image"], use_container_width=True)
                st.caption(f"**{movie['title']}**")
                st.caption(f"IMDb: {movie['rating']}")
                pos = st.number_input(
                    "Posicao",
                    min_value=1,
                    max_value=n,
                    value=idx + 1,
                    step=1,
                    key=f"{prefixo}_pos_{idx}",
                    label_visibility="collapsed",
                )
                posicoes[idx] = int(pos)

    return posicoes


def _posicoes_para_ranking(posicoes, n):
    """Converte {indice_filme: posicao} em lista ordenada de índices (pos 1 primeiro)."""
    return [idx for idx, _ in sorted(posicoes.items(), key=lambda x: x[1])]


def _validar(posicoes, n):
    valores = list(posicoes.values())
    if sorted(valores) != list(range(1, n + 1)):
        duplicados = [v for v in set(valores) if valores.count(v) > 1]
        ausentes = sorted(set(range(1, n + 1)) - set(valores))
        erros = []
        if duplicados:
            erros.append(f"Posicoes repetidas: {duplicados}")
        if ausentes:
            erros.append(f"Posicoes ausentes: {ausentes}")
        return erros
    return []


def render():
    _init_state()

    st.header("Usuario vs Usuario")
    st.markdown("Compare o ranking de dois usuarios para o mesmo conjunto de filmes do Top IMDb.")

    # Selecao de N e busca
    col_slider, col_btn = st.columns([3, 1])

    with col_slider:
        n = st.slider("Quantos filmes do Top IMDb?", min_value=5, max_value=50, value=st.session_state["n_uvu"], step=5)

    with col_btn:
        st.write("")
        st.write("")
        buscar = st.button("Buscar Filmes", use_container_width=True)

    if buscar:
        if n != st.session_state["n_uvu"]:
            st.session_state["result_uvu"] = None
        st.session_state["n_uvu"] = n
        with st.spinner("Buscando filmes no IMDb..."):
            st.session_state["movies_uvu"] = _buscar_filmes(n)

    movies = st.session_state["movies_uvu"]

    if not movies:
        st.info("Clique em **Buscar Filmes** para carregar o catalogo.")
        return

    # Rankings dos dois usuarios em abas
    st.divider()
    aba_a, aba_b = st.tabs(["Usuario A", "Usuario B"])

    with aba_a:
        posicoes_a = _coletar_ranking(movies, "a")

    with aba_b:
        posicoes_b = _coletar_ranking(movies, "b")

    # Botao comparar
    st.divider()
    if st.button("Comparar", type="primary"):
        erros_a = _validar(posicoes_a, n)
        erros_b = _validar(posicoes_b, n)

        if erros_a:
            st.error(f"Ranking do Usuario A invalido: {'; '.join(erros_a)}")
        if erros_b:
            st.error(f"Ranking do Usuario B invalido: {'; '.join(erros_b)}")

        if not erros_a and not erros_b:
            ranking_a = _posicoes_para_ranking(posicoes_a, n)
            ranking_b = _posicoes_para_ranking(posicoes_b, n)

            inversions = calculate_similarity(ranking_a, ranking_b)
            max_inversions = n * (n - 1) // 2
            similarity_pct, interpretation = interpret_score(inversions, max_inversions)

            st.session_state["result_uvu"] = {
                "inversions": inversions,
                "max_inversions": max_inversions,
                "similarity_pct": similarity_pct,
                "interpretation": interpretation,
                "ranking_a": ranking_a,
                "ranking_b": ranking_b,
            }

    # Resultado
    result = st.session_state["result_uvu"]
    if not result:
        return

    st.divider()
    st.subheader("Resultado")

    m1, m2, m3 = st.columns(3)
    m1.metric("Inversoes", f"{result['inversions']} / {result['max_inversions']}")
    m2.metric("Similaridade", f"{result['similarity_pct']:.1f}%")
    m3.metric("Maximo possivel", result["max_inversions"])

    st.success(result["interpretation"])

    # Tabelas comparativas
    st.subheader("Comparativo de Rankings")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Ranking - Usuario A**")
        tabela_a = [
            {"Posicao": pos + 1, "Filme": movies[idx]["title"]}
            for pos, idx in enumerate(result["ranking_a"])
        ]
        st.dataframe(tabela_a, use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("**Ranking - Usuario B**")
        tabela_b = [
            {"Posicao": pos + 1, "Filme": movies[idx]["title"]}
            for pos, idx in enumerate(result["ranking_b"])
        ]
        st.dataframe(tabela_b, use_container_width=True, hide_index=True)
