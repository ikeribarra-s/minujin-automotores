import streamlit as st
from pathlib import Path
from api_client import login

st.set_page_config(page_title="Minujin Automotores", layout="centered")

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 3rem;}
</style>
""", unsafe_allow_html=True)

if "token" not in st.session_state:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        logo = Path(__file__).parent.parent / "gui" / "minujin-logo.png"
        st.image(str(logo), use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login"):
            username = st.text_input("Nombre de usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar", use_container_width=True)
        if submitted:
            if login(username, password):
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.stop()

st.title("Minujin Automotores")
st.write("Seleccioná una sección en el menú lateral.")
