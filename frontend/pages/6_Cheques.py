import streamlit as st
import pandas as pd
from api_client import get, post, patch
from styles import get_css

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
st.title("Cartera de Cheques")

ESTADOS = ["pendiente", "cobrado", "depositado", "rechazado"]

try:
    cobros   = get("/cobros/")
    clientes = get("/clientes/")
except Exception as e:
    st.error(str(e))
    st.stop()

cliente_map = {c["id"]: f"{c['apellido']}, {c['nombre']}" for c in clientes}
cobro_opts  = {
    f"Cobro #{c['id']} — {cliente_map.get(c['cliente_id'], '?')} — ${c['monto']}": c["id"]
    for c in cobros
}

tab_cartera, tab_registrar, tab_estado = st.tabs(["Cartera", "Registrar", "Actualizar estado"])

# ── CARTERA ───────────────────────────────────────────────────────────────────
with tab_cartera:
    estado_filtro = st.selectbox("Estado", ["todos"] + ESTADOS)
    try:
        params  = {} if estado_filtro == "todos" else {"estado": estado_filtro}
        cheques = get("/cheques/", **params)
    except Exception as e:
        st.error(str(e))
        st.stop()

    if cheques:
        df = pd.DataFrame(cheques)
        st.dataframe(
            df[["id", "numero", "banco", "titular", "monto", "fecha_cobro", "estado"]],
            use_container_width=True,
        )
    else:
        st.info("No hay cheques.")

# ── REGISTRAR ─────────────────────────────────────────────────────────────────
with tab_registrar:
    with st.form("nuevo_cheque"):
        cobro_sel = st.selectbox("Cobro *",
            list(cobro_opts.keys()) if cobro_opts else ["Sin cobros"])
        c1, c2 = st.columns(2)
        numero  = c1.text_input("Número *")
        banco   = c2.text_input("Banco *")
        titular = st.text_input("Titular")
        c3, c4 = st.columns(2)
        monto       = c3.number_input("Monto *", min_value=0.01, format="%.2f")
        fecha_cobro = c4.date_input("Fecha de cobro *")
        fecha_emision = st.date_input("Fecha de emisión (opcional)", value=None)

        if st.form_submit_button("Registrar cheque", use_container_width=True):
            if not cobro_opts:
                st.error("No hay cobros disponibles")
            elif not numero or not banco:
                st.error("Número y banco son obligatorios")
            else:
                try:
                    post("/cheques/", {
                        "cobro_id":    cobro_opts[cobro_sel],
                        "numero":      numero,
                        "banco":       banco,
                        "titular":     titular or None,
                        "monto":       monto,
                        "fecha_cobro": str(fecha_cobro),
                        "fecha_emision": str(fecha_emision) if fecha_emision else None,
                    })
                    st.success("Cheque registrado")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

# ── ACTUALIZAR ESTADO ─────────────────────────────────────────────────────────
with tab_estado:
    c_id, c_btn = st.columns([3, 1])
    cheque_id = c_id.number_input("ID del cheque", min_value=1, step=1, key="edit_ch_id")
    if c_btn.button("Cargar", key="cargar_ch"):
        try:
            st.session_state["edit_cheque"] = get(f"/cheques/{cheque_id}")
        except Exception:
            st.error("Cheque no encontrado")
            st.session_state.pop("edit_cheque", None)

    ch = st.session_state.get("edit_cheque")
    if ch:
        st.caption(f"Cheque #{ch['id']} — {ch['banco']} N° {ch['numero']} — ${ch['monto']} — vence {ch['fecha_cobro']}")
        st.caption(f"Estado actual: **{ch['estado']}**")

        with st.form("edit_cheque"):
            nuevo_estado  = st.selectbox("Nuevo estado", ESTADOS,
                                          index=ESTADOS.index(ch["estado"]))
            observaciones = st.text_area("Observaciones", value=ch.get("observaciones") or "")

            c_save, c_cancel = st.columns(2)
            guardado  = c_save.form_submit_button("Guardar", use_container_width=True)
            cancelado = c_cancel.form_submit_button("Cancelar", use_container_width=True)

        if guardado:
            try:
                patch(f"/cheques/{ch['id']}", {
                    "estado": nuevo_estado,
                    "observaciones": observaciones or None,
                })
                st.success("Cheque actualizado")
                st.session_state.pop("edit_cheque", None)
                st.rerun()
            except Exception as e:
                st.error(str(e))

        if cancelado:
            st.session_state.pop("edit_cheque", None)
            st.rerun()
