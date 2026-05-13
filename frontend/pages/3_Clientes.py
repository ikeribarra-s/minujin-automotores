import streamlit as st
import pandas as pd
from api_client import get, post, put

if "token" not in st.session_state:
    st.switch_page("app.py")

st.title("Clientes")

busqueda = st.text_input("Buscar por nombre, apellido o DNI")
try:
    clientes = get("/clientes/", busqueda=busqueda) if busqueda else get("/clientes/")
except Exception as e:
    st.error(str(e))
    st.stop()

if clientes:
    df = pd.DataFrame(clientes)
    st.dataframe(df[["id", "apellido", "nombre", "dni", "telefono", "email"]], use_container_width=True)
else:
    st.info("No hay clientes.")

st.divider()
st.subheader("Agregar cliente")
with st.form("nuevo_cliente"):
    col1, col2 = st.columns(2)
    nombre = col1.text_input("Nombre *")
    apellido = col2.text_input("Apellido *")
    col3, col4 = st.columns(2)
    dni = col3.text_input("DNI")
    telefono = col4.text_input("Teléfono")
    email = st.text_input("Email")
    direccion = st.text_area("Dirección")
    if st.form_submit_button("Guardar"):
        if not nombre or not apellido:
            st.error("Nombre y apellido son obligatorios")
        else:
            try:
                post("/clientes/", {
                    "nombre": nombre, "apellido": apellido,
                    "dni": dni or None, "telefono": telefono or None,
                    "email": email or None, "direccion": direccion or None,
                })
                st.success("Cliente agregado")
                st.rerun()
            except Exception as e:
                st.error(str(e))
