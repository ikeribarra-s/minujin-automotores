import streamlit as st
import pandas as pd
from api_client import get, post
from styles import get_css

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
st.title("Cobros")

try:
    ventas   = get("/ventas/")
    clientes = get("/clientes/")
except Exception as e:
    st.error(str(e))
    st.stop()

cliente_map = {c["id"]: f"{c['apellido']}, {c['nombre']}" for c in clientes}
venta_opts  = {
    f"Venta #{v['id']} — {cliente_map.get(v['cliente_id'], '?')} — ${v['precio_final']}": v
    for v in ventas
}

tab_lista, tab_registrar = st.tabs(["Lista", "Registrar"])

# ── LISTA ─────────────────────────────────────────────────────────────────────
with tab_lista:
    filtro = st.selectbox("Filtrar por venta", ["Todos"] + list(venta_opts.keys()))
    try:
        if filtro == "Todos":
            cobros = get("/cobros/")
        else:
            cobros = get("/cobros/", venta_id=venta_opts[filtro]["id"])
    except Exception as e:
        st.error(str(e))
        st.stop()

    if cobros:
        df = pd.DataFrame(cobros)
        df["cliente"] = df["cliente_id"].map(cliente_map)
        st.dataframe(
            df[["id", "fecha", "venta_id", "cliente", "monto", "concepto", "forma_pago"]],
            use_container_width=True,
        )
    else:
        st.info("No hay cobros.")

# ── REGISTRAR ─────────────────────────────────────────────────────────────────
with tab_registrar:
    cliente_opts = {f"{c['apellido']}, {c['nombre']}": c["id"] for c in clientes}

    with st.form("nuevo_cobro"):
        venta_sel   = st.selectbox("Venta *",
            list(venta_opts.keys()) if venta_opts else ["Sin ventas"])
        cliente_sel = st.selectbox("Cliente *",
            list(cliente_opts.keys()) if cliente_opts else ["Sin clientes"])
        monto       = st.number_input("Monto *", min_value=0.01, format="%.2f")
        concepto    = st.selectbox("Concepto",    ["saldo", "sena", "cuota", "otro"])
        forma_pago  = st.selectbox("Forma de pago", ["efectivo", "transferencia", "cheque", "tarjeta"])
        observaciones = st.text_area("Observaciones")

        if st.form_submit_button("Registrar cobro", use_container_width=True):
            if not venta_opts or not cliente_opts:
                st.error("Se necesita al menos una venta y un cliente")
            else:
                try:
                    post("/cobros/", {
                        "venta_id":   venta_opts[venta_sel]["id"],
                        "cliente_id": cliente_opts[cliente_sel],
                        "monto":      monto,
                        "concepto":   concepto,
                        "forma_pago": forma_pago,
                        "observaciones": observaciones or None,
                    })
                    st.success("Cobro registrado")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
