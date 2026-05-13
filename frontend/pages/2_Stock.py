import streamlit as st
import pandas as pd
from api_client import get, post, put, delete

if "token" not in st.session_state:
    st.switch_page("app.py")

st.title("Stock de Vehículos")

estado_filtro = st.selectbox("Filtrar por estado", ["todos", "disponible", "reservado", "vendido"])
try:
    params = {} if estado_filtro == "todos" else {"estado": estado_filtro}
    vehiculos = get("/vehiculos/", **params)
except Exception as e:
    st.error(str(e))
    st.stop()

if vehiculos:
    df = pd.DataFrame(vehiculos)
    st.dataframe(df[["id", "marca", "modelo", "anio", "patente", "precio_venta", "estado", "kilometraje"]], use_container_width=True)
else:
    st.info("No hay vehículos.")

st.divider()
st.subheader("Agregar vehículo")
with st.form("nuevo_vehiculo"):
    col1, col2, col3 = st.columns(3)
    marca = col1.text_input("Marca *")
    modelo = col2.text_input("Modelo *")
    anio = col3.number_input("Año *", min_value=1950, max_value=2100, value=2020)
    col4, col5, col6 = st.columns(3)
    version = col4.text_input("Versión")
    color = col5.text_input("Color")
    km = col6.number_input("Kilometraje", min_value=0, value=0)
    col7, col8, col9 = st.columns(3)
    tipo = col7.selectbox("Tipo", ["usado", "cero_km"])
    procedencia = col8.selectbox("Procedencia", ["compra", "permuta", "consignacion"])
    patente = col9.text_input("Patente")
    col10, col11 = st.columns(2)
    precio_compra = col10.number_input("Precio compra", min_value=0.0, format="%.2f")
    precio_venta = col11.number_input("Precio venta", min_value=0.0, format="%.2f")
    observaciones = st.text_area("Observaciones")
    if st.form_submit_button("Guardar"):
        if not marca or not modelo:
            st.error("Marca y modelo son obligatorios")
        else:
            try:
                post("/vehiculos/", {
                    "marca": marca, "modelo": modelo, "anio": anio,
                    "version": version or None, "color": color or None,
                    "kilometraje": km, "tipo": tipo, "procedencia": procedencia,
                    "patente": patente or None,
                    "precio_compra": precio_compra or None,
                    "precio_venta": precio_venta or None,
                    "observaciones": observaciones or None,
                })
                st.success("Vehículo agregado")
                st.rerun()
            except Exception as e:
                st.error(str(e))
