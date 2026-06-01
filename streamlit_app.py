import streamlit as st
from ui import mode_user_vs_imdb, mode_user_vs_user

st.set_page_config(
    page_title="RankMatch 🎬",
    page_icon="🎬",
    layout="wide",
)

st.sidebar.title("🎬 RankMatch")
st.sidebar.markdown("Descubra o quanto seu gosto cinematográfico combina com o de outra pessoa ou com o ranking oficial do IMDb.")
st.sidebar.divider()

modo = st.sidebar.radio(
    "Modo de comparação",
    ["Usuário vs IMDb", "Usuário vs Usuário"],
)

st.sidebar.divider()
st.sidebar.caption("Algoritmo: Contagem de Inversões (Dividir e Conquistar)")

if modo == "Usuário vs IMDb":
    mode_user_vs_imdb.render()
else:
    mode_user_vs_user.render()
