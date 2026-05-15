import json
import streamlit as st
import pandas as pd
from api_client import get, post, patch, upload_file
from styles import get_css
from nav import render_nav

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
render_nav("Cheques")
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

@st.dialog("Editar cheque", width="large")
def dialogo_editar_cheque(ch: dict):
    with st.form("form_edit_cheque"):
        c1, c2 = st.columns(2)
        numero = c1.text_input("Número",  value=ch.get("numero") or "")
        banco  = c2.text_input("Banco",   value=ch.get("banco")  or "")

        c3, c4 = st.columns(2)
        titular = c3.text_input("Titular",  value=ch.get("titular") or "")
        entrega = c4.text_input("Entrega",  value=ch.get("entrega") or "")

        c5, c6 = st.columns(2)
        monto       = c5.number_input("Monto $", min_value=0.01,
                                       value=float(ch.get("monto") or 0), format="%.2f")
        estado      = c6.selectbox("Estado", ESTADOS,
                                    index=ESTADOS.index(ch.get("estado", "pendiente")))

        import datetime as _dt
        def _d(v):
            try: return _dt.date.fromisoformat(v) if v else None
            except: return None

        c7, c8 = st.columns(2)
        fecha_emision = c7.date_input("Fecha emisión",  value=_d(ch.get("fecha_emision")))
        fecha_cobro   = c8.date_input("Fecha cobro",    value=_d(ch.get("fecha_cobro")))

        c9, c10 = st.columns(2)
        es_cpd            = c9.checkbox("CPD (pago diferido)", value=ch.get("es_cpd", False))
        discrepancia_monto = c10.checkbox("Discrepancia monto", value=ch.get("discrepancia_monto", False))

        monto_letras = st.text_input("Monto en letras", value=ch.get("monto_letras") or "")
        observaciones = st.text_area("Observaciones",   value=ch.get("observaciones") or "")

        c_save, c_cancel = st.columns(2)
        guardado  = c_save.form_submit_button("Guardar cambios", use_container_width=True)
        cancelado = c_cancel.form_submit_button("Cancelar",      use_container_width=True)

    if guardado:
        try:
            patch(f"/cheques/{ch['id']}", {
                "numero":             numero or None,
                "banco":              banco or None,
                "titular":            titular or None,
                "entrega":            entrega or None,
                "monto":              monto,
                "estado":             estado,
                "fecha_emision":      str(fecha_emision) if fecha_emision else None,
                "fecha_cobro":        str(fecha_cobro)   if fecha_cobro   else None,
                "es_cpd":             es_cpd,
                "discrepancia_monto": discrepancia_monto,
                "monto_letras":       monto_letras or None,
                "observaciones":      observaciones or None,
            })
            st.session_state["cheque_msg"] = "Cheque actualizado"
            st.rerun()
        except Exception as e:
            st.error(str(e))
    if cancelado:
        st.rerun()


if "ch_edit" in st.session_state:
    dialogo_editar_cheque(st.session_state["ch_edit"])

if "cheque_msg" in st.session_state:
    st.success(st.session_state.pop("cheque_msg"))

tab_cartera, tab_escanear, tab_registrar = st.tabs(
    ["Cartera", "Escanear", "Registrar manual"]
)

# ── CARTERA ───────────────────────────────────────────────────────────────────
with tab_cartera:
    estado_filtro = st.selectbox("Estado", ["todos"] + ESTADOS)
    try:
        params  = {} if estado_filtro == "todos" else {"estado": estado_filtro}
        cheques = get("/cheques/", **params)
    except Exception as e:
        st.error(str(e))
        st.stop()

    if not cheques:
        st.info("No hay cheques.")
    else:
        ESTADO_COLOR = {
            "pendiente":  "#F59E0B",
            "depositado": "#3B82F6",
            "cobrado":    "#22C55E",
            "rechazado":  "#EF4444",
        }
        for ch in cheques:
            color = ESTADO_COLOR.get(ch["estado"], "#6B7280")
            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                entrega_txt = f" · Entrega: {ch['entrega']}" if ch.get("entrega") else ""
                st.markdown(
                    f"**{ch['banco']}** N° {ch['numero']}"
                    f"<br><span style='color:#888;font-size:0.8rem'>"
                    f"{ch.get('titular') or '—'}{entrega_txt}</span>",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"**${float(ch['monto']):,.0f}**"
                    f"<br><span style='color:#888;font-size:0.8rem'>{ch['fecha_cobro']}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<span style='color:{color};font-size:0.72rem;font-weight:700;"
                    f"text-transform:uppercase;letter-spacing:0.05em'>{ch['estado']}</span>",
                    unsafe_allow_html=True,
                )
            with c3:
                if st.button("Editar", key=f"edit_ch_{ch['id']}", use_container_width=True):
                    st.session_state["ch_edit"] = ch
                    st.rerun()
            st.divider()

# ── ESCANEAR ──────────────────────────────────────────────────────────────────
with tab_escanear:
    st.subheader("Escanear cheque o pagaré")
    st.caption("Subí una foto del documento. La IA extraerá los datos automáticamente.")

    uploaded = st.file_uploader(
        "Imagen del cheque / pagaré",
        type=["jpg", "jpeg", "png", "webp"],
        key="scanner_upload",
    )

    if uploaded:
        st.image(uploaded, caption="Vista previa", use_container_width=True)

        if st.button("Escanear documento", type="primary"):
            with st.spinner("Extrayendo datos… esto puede tardar unos segundos"):
                try:
                    result = upload_file(
                        "/cheques/scan",
                        uploaded.getvalue(),
                        uploaded.name,
                        uploaded.type or "image/jpeg",
                    )
                    st.session_state["scan_result"] = result
                    if result.get("warning"):
                        st.warning(result["warning"])
                    if result.get("discrepancia_monto"):
                        st.warning("Discrepancia detectada: el monto en números no coincide con el escrito en letras.")
                except Exception as e:
                    st.error(f"Error al escanear: {e}")
                    st.session_state.pop("scan_result", None)

    scan = st.session_state.get("scan_result")
    if scan:
        st.success("Datos extraídos. Revisá y completá los campos faltantes.")

        with st.expander("Ver OCR completo", expanded=False):
            st.text(scan.get("raw_ocr_text", ""))

        with st.form("confirmar_scan"):
            st.markdown("**Datos del documento**")
            c1, c2 = st.columns(2)
            tipo_val = scan.get("tipo") or "cheque"
            tipo = c1.selectbox("Tipo", ["cheque", "pagare"], index=0 if tipo_val == "cheque" else 1)
            numero = c2.text_input("Número", value=scan.get("numero") or "")

            c3, c4 = st.columns(2)
            banco = c3.text_input("Banco", value=scan.get("banco") or "")
            titular = c4.text_input("Titular / Pagador", value=scan.get("pagador_nombre") or "")

            c5, c6 = st.columns(2)
            monto_val = scan.get("monto_numerico") or 0.0
            monto = c5.number_input("Monto $", min_value=0.01, value=float(monto_val), format="%.2f")
            pagador_cuit = c6.text_input("CUIT pagador", value=scan.get("pagador_cuit") or "")

            monto_letras = st.text_input("Monto en letras", value=scan.get("monto_letras") or "")
            beneficiario = st.text_input("Beneficiario", value=scan.get("beneficiario") or "")

            c7, c8 = st.columns(2)
            sucursal = c7.text_input("Sucursal", value=scan.get("sucursal") or "")
            localidad = c8.text_input("Localidad", value=scan.get("localidad") or "")

            import datetime as dt
            def _parse(val):
                if not val:
                    return None
                try:
                    return dt.date.fromisoformat(val)
                except Exception:
                    return None

            c9, c10 = st.columns(2)
            fecha_emision_default = _parse(scan.get("fecha_emision"))
            fecha_cobro_default   = _parse(scan.get("fecha_vencimiento"))
            fecha_emision = c9.date_input("Fecha emisión", value=fecha_emision_default)
            fecha_cobro   = c10.date_input("Fecha vencimiento / cobro", value=fecha_cobro_default or dt.date.today())

            es_cpd = st.checkbox("Cheque de pago diferido (CPD)", value=scan.get("es_cpd", False))

            entrega = st.text_input("Entrega (quién entregó el cheque)", value="")

            st.markdown("**Asociar al cobro**")
            if not cobro_opts:
                st.warning("No hay cobros disponibles. Creá un cobro primero.")
                cobro_sel = None
            else:
                cobro_sel = st.selectbox("Cobro *", list(cobro_opts.keys()))

            observaciones = st.text_area("Observaciones")

            submitted = st.form_submit_button("Guardar cheque", type="primary", use_container_width=True)

        if submitted:
            if not cobro_opts or cobro_sel is None:
                st.error("Seleccioná un cobro")
            elif not numero or not banco:
                st.error("Número y banco son obligatorios")
            else:
                try:
                    post("/cheques/", {
                        "cobro_id":          cobro_opts[cobro_sel],
                        "numero":            numero,
                        "banco":             banco,
                        "titular":           titular or None,
                        "monto":             monto,
                        "fecha_cobro":       str(fecha_cobro),
                        "fecha_emision":     str(fecha_emision) if fecha_emision else None,
                        "observaciones":     observaciones or None,
                        "monto_letras":      monto_letras or None,
                        "pagador_cuit":      pagador_cuit or None,
                        "beneficiario":      beneficiario or None,
                        "sucursal":          sucursal or None,
                        "localidad":         localidad or None,
                        "es_cpd":            es_cpd,
                        "discrepancia_monto": scan.get("discrepancia_monto", False),
                        "raw_ocr_text":      scan.get("raw_ocr_text"),
                        "raw_json":          json.dumps(scan.get("raw_json")) if scan.get("raw_json") else None,
                        "entrega":           entrega or None,
                    })
                    st.success("Cheque guardado correctamente.")
                    st.session_state.pop("scan_result", None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# ── REGISTRAR MANUAL ──────────────────────────────────────────────────────────
with tab_registrar:
    with st.form("nuevo_cheque"):
        cobro_sel = st.selectbox("Cobro *",
            list(cobro_opts.keys()) if cobro_opts else ["Sin cobros"])
        c1, c2 = st.columns(2)
        numero  = c1.text_input("Número *")
        banco   = c2.text_input("Banco *")
        titular = st.text_input("Titular")
        entrega_manual = st.text_input("Entrega (quién entregó el cheque)")
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
                        "entrega":     entrega_manual or None,
                        "monto":       monto,
                        "fecha_cobro": str(fecha_cobro),
                        "fecha_emision": str(fecha_emision) if fecha_emision else None,
                    })
                    st.success("Cheque registrado")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

