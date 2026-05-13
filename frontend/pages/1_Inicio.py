import streamlit as st
from api_client import get

if "token" not in st.session_state:
    st.switch_page("app.py")

st.title("Dashboard")

try:
    stock = get("/vehiculos/", estado="disponible")
    cheques = get("/cheques/", estado="pendiente")
    cobros = get("/cobros/")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Stock disponible", len(stock))
col2.metric("Cheques pendientes", len(cheques))
col3.metric("Cobros registrados", len(cobros))
