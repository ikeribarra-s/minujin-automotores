import streamlit as st
import pandas as pd
from api_client import get, post
from styles import get_css

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)

st.title("Ventas")

try:
    ventas = get("/ventas/")
    vehiculos = get("/vehiculos/", estado="disponible")
    clientes = get("/clientes/")
except Exception as e:
    st.error(str(e))
    st.stop()

if ventas:
    df = pd.DataFrame(ventas)
    st.dataframe(df[["id", "fecha_venta", "vehiculo_id", "cliente_id", "precio_final", "forma_pago"]], use_container_width=True)
else:
    st.info("No hay ventas registradas.")

st.divider()
st.subheader("Registrar venta")

vehiculo_opts = {f"{v['marca']} {v['modelo']} {v['anio']} — {v['patente'] or 'sin patente'}": v["id"] for v in vehiculos}
cliente_opts = {f"{c['apellido']}, {c['nombre']} — DNI {c['dni'] or '-'}": c["id"] for c in clientes}

with st.form("nueva_venta"):
    vehiculo_sel = st.selectbox("Vehículo *", list(vehiculo_opts.keys()) if vehiculo_opts else ["Sin stock disponible"])
    cliente_sel = st.selectbox("Cliente *", list(cliente_opts.keys()) if cliente_opts else ["Sin clientes"])
    precio_final = st.number_input("Precio final *", min_value=0.01, format="%.2f")
    forma_pago = st.selectbox("Forma de pago", ["contado", "financiado", "permuta", "mixto"])
    observaciones = st.text_area("Observaciones")
    if st.form_submit_button("Registrar"):
        if not vehiculo_opts or not cliente_opts:
            st.error("Se necesita al menos un vehículo disponible y un cliente")
        else:
            try:
                post("/ventas/", {
                    "vehiculo_id": vehiculo_opts[vehiculo_sel],
                    "cliente_id": cliente_opts[cliente_sel],
                    "precio_final": precio_final,
                    "forma_pago": forma_pago,
                    "observaciones": observaciones or None,
                })
                st.success("Venta registrada")
                st.rerun()
            except Exception as e:
                st.error(str(e))
