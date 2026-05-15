import streamlit as st
from api_client import get, post, patch
from styles import get_css
from nav import render_nav

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
render_nav("Cobros")
st.title("Cobros")

CONCEPTOS   = ["saldo", "sena", "cuota", "otro"]
FORMAS_PAGO = ["efectivo", "transferencia", "cheque", "tarjeta"]

try:
    ventas   = get("/ventas/")
    clientes = get("/clientes/")
except Exception as e:
    st.error(str(e))
    st.stop()

cliente_map = {c["id"]: f"{c['apellido']}, {c['nombre']}" for c in clientes}
venta_opts  = {
    f"Venta #{v['id']} — {cliente_map.get(v['cliente_id'], '?')} — ${float(v['precio_final']):,.0f}": v
    for v in ventas
}

CONCEPTO_COLOR = {
    "saldo":  "#22C55E",
    "sena":   "#3B82F6",
    "cuota":  "#F59E0B",
    "otro":   "#6B7280",
}
FORMA_ICON = {
    "efectivo":      "💵",
    "transferencia": "🏦",
    "cheque":        "📄",
    "tarjeta":       "💳",
}


@st.dialog("Editar cobro", width="large")
def dialogo_editar_cobro(cobro: dict):
    with st.form("form_edit_cobro"):
        c1, c2 = st.columns(2)
        monto      = c1.number_input("Monto $", min_value=0.01,
                                      value=float(cobro["monto"]), format="%.2f")
        concepto   = c2.selectbox("Concepto", CONCEPTOS,
                                   index=CONCEPTOS.index(cobro.get("concepto", "saldo")))
        forma_pago = st.selectbox("Forma de pago", FORMAS_PAGO,
                                   index=FORMAS_PAGO.index(cobro.get("forma_pago", "efectivo")))
        observaciones = st.text_area("Observaciones", value=cobro.get("observaciones") or "")

        c_save, c_cancel = st.columns(2)
        guardado  = c_save.form_submit_button("Guardar cambios", use_container_width=True)
        cancelado = c_cancel.form_submit_button("Cancelar",      use_container_width=True)

    if guardado:
        try:
            patch(f"/cobros/{cobro['id']}", {
                "monto":         monto,
                "concepto":      concepto,
                "forma_pago":    forma_pago,
                "observaciones": observaciones or None,
            })
            st.session_state["cobro_msg"] = "Cobro actualizado"
            st.rerun()
        except Exception as e:
            st.error(str(e))
    if cancelado:
        st.rerun()


if "cobro_edit" in st.session_state:
    dialogo_editar_cobro(st.session_state["cobro_edit"])

if "cobro_msg" in st.session_state:
    st.success(st.session_state.pop("cobro_msg"))

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

    if not cobros:
        st.info("No hay cobros.")
    else:
        for cobro in cobros:
            color = CONCEPTO_COLOR.get(cobro.get("concepto", "otro"), "#6B7280")
            icon  = FORMA_ICON.get(cobro.get("forma_pago", ""), "")
            cliente_nombre = cliente_map.get(cobro.get("cliente_id"), "—")

            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                obs = cobro.get("observaciones")
                obs_txt = f"<br><span style='color:#888;font-size:0.8rem'>{obs}</span>" if obs else ""
                st.markdown(
                    f"**{cliente_nombre}** · Venta #{cobro.get('venta_id', '—')}"
                    f"<br><span style='color:#888;font-size:0.8rem'>{cobro['fecha']}</span>"
                    f"{obs_txt}",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"**${float(cobro['monto']):,.0f}**"
                    f"<br><span style='color:#888;font-size:0.8rem'>{icon} {cobro.get('forma_pago', '')}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<span style='color:{color};font-size:0.72rem;font-weight:700;"
                    f"text-transform:uppercase;letter-spacing:0.05em'>{cobro.get('concepto', '')}</span>",
                    unsafe_allow_html=True,
                )
            with c3:
                if st.button("Editar", key=f"edit_cobro_{cobro['id']}", use_container_width=True):
                    st.session_state["cobro_edit"] = cobro
                    st.rerun()
            st.divider()

# ── REGISTRAR ─────────────────────────────────────────────────────────────────
with tab_registrar:
    cliente_opts = {f"{c['apellido']}, {c['nombre']}": c["id"] for c in clientes}

    with st.form("nuevo_cobro"):
        venta_sel   = st.selectbox("Venta *",
            list(venta_opts.keys()) if venta_opts else ["Sin ventas"])
        cliente_sel = st.selectbox("Cliente *",
            list(cliente_opts.keys()) if cliente_opts else ["Sin clientes"])
        monto       = st.number_input("Monto *", min_value=0.01, format="%.2f")
        concepto    = st.selectbox("Concepto",     CONCEPTOS)
        forma_pago  = st.selectbox("Forma de pago", FORMAS_PAGO)
        observaciones = st.text_area("Observaciones")

        if st.form_submit_button("Registrar cobro", use_container_width=True):
            if not venta_opts or not cliente_opts:
                st.error("Se necesita al menos una venta y un cliente")
            else:
                try:
                    post("/cobros/", {
                        "venta_id":      venta_opts[venta_sel]["id"],
                        "cliente_id":    cliente_opts[cliente_sel],
                        "monto":         monto,
                        "concepto":      concepto,
                        "forma_pago":    forma_pago,
                        "observaciones": observaciones or None,
                    })
                    st.success("Cobro registrado")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
