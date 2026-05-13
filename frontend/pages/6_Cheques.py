import streamlit as st
import pandas as pd
from api_client import get, post, patch
from styles import get_css

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)

st.title("Cartera de Cheques")

estado_filtro = st.selectbox("Estado", ["pendiente", "cobrado", "depositado", "rechazado", "todos"])

try:
    params = {} if estado_filtro == "todos" else {"estado": estado_filtro}
    cheques = get("/cheques/", **params)
    cobros = get("/cobros/")
except Exception as e:
    st.error(str(e))
    st.stop()

if cheques:
    df = pd.DataFrame(cheques)
    st.dataframe(df[["id", "numero", "banco", "titular", "monto", "fecha_cobro", "estado"]], use_container_width=True)
else:
    st.info("No hay cheques.")

st.divider()
st.subheader("Actualizar estado de cheque")
with st.form("actualizar_cheque"):
    cheque_id = st.number_input("ID del cheque", min_value=1, step=1)
    nuevo_estado = st.selectbox("Nuevo estado", ["cobrado", "depositado", "rechazado", "pendiente"])
    if st.form_submit_button("Actualizar"):
        try:
            patch(f"/cheques/{cheque_id}", {"estado": nuevo_estado})
            st.success("Estado actualizado")
            st.rerun()
        except Exception as e:
            st.error(str(e))

st.divider()
st.subheader("Registrar cheque")
cobro_opts = {f"Cobro #{c['id']} — venta {c['venta_id']} — ${c['monto']}": c["id"] for c in cobros}

with st.form("nuevo_cheque"):
    cobro_sel = st.selectbox("Cobro *", list(cobro_opts.keys()) if cobro_opts else ["Sin cobros"])
    col1, col2 = st.columns(2)
    numero = col1.text_input("Número *")
    banco = col2.text_input("Banco *")
    titular = st.text_input("Titular")
    col3, col4 = st.columns(2)
    monto = col3.number_input("Monto *", min_value=0.01, format="%.2f")
    fecha_cobro = col4.date_input("Fecha de cobro *")
    fecha_emision = st.date_input("Fecha de emisión (opcional)", value=None)
    if st.form_submit_button("Registrar"):
        if not cobro_opts:
            st.error("No hay cobros disponibles")
        elif not numero or not banco:
            st.error("Número y banco son obligatorios")
        else:
            try:
                post("/cheques/", {
                    "cobro_id": cobro_opts[cobro_sel],
                    "numero": numero,
                    "banco": banco,
                    "titular": titular or None,
                    "monto": monto,
                    "fecha_cobro": str(fecha_cobro),
                    "fecha_emision": str(fecha_emision) if fecha_emision else None,
                })
                st.success("Cheque registrado")
                st.rerun()
            except Exception as e:
                st.error(str(e))
