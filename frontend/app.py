import streamlit as st
from api_client import login

st.set_page_config(page_title="Automotora", layout="wide")

if "token" not in st.session_state:
    st.title("Automotora — Ingreso")
    with st.form("login"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")
    if submitted:
        if login(username, password):
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    st.stop()

st.title("Automotora")
st.write("Seleccioná una sección en el menú lateral.")
