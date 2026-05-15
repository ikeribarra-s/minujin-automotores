import streamlit as st
from api_client import get, post, put
from styles import get_css
from nav import render_nav

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
render_nav("Ventas")
st.title("Ventas")

FORMAS_PAGO = ["contado", "financiado", "permuta", "mixto"]

FORMA_COLOR = {
    "contado":    "#22C55E",
    "financiado": "#3B82F6",
    "permuta":    "#F59E0B",
    "mixto":      "#EC4899",
}

try:
    ventas   = get("/ventas/")
    clientes = get("/clientes/")
except Exception as e:
    st.error(str(e))
    st.stop()

cliente_map = {c["id"]: f"{c['apellido']}, {c['nombre']}" for c in clientes}


@st.dialog("Editar venta", width="large")
def dialogo_editar_venta(vta: dict):
    st.caption(f"Vehículo #{vta['vehiculo_id']} · {vta['fecha_venta']}")
    with st.form("form_edit_venta"):
        precio_final  = st.number_input("Precio final", min_value=0.01,
                                        value=float(vta["precio_final"]), format="%.2f")
        forma_pago    = st.selectbox("Forma de pago", FORMAS_PAGO,
                                     index=FORMAS_PAGO.index(vta["forma_pago"]))
        observaciones = st.text_area("Observaciones", value=vta.get("observaciones") or "")

        c_save, c_cancel = st.columns(2)
        guardado  = c_save.form_submit_button("Guardar cambios", use_container_width=True)
        cancelado = c_cancel.form_submit_button("Cancelar",      use_container_width=True)

    if guardado:
        try:
            put(f"/ventas/{vta['id']}", {
                "precio_final":  precio_final,
                "forma_pago":    forma_pago,
                "observaciones": observaciones or None,
            })
            st.session_state["venta_msg"] = "Venta actualizada"
            st.rerun()
        except Exception as e:
            st.error(str(e))
    if cancelado:
        st.rerun()


if "venta_edit" in st.session_state:
    dialogo_editar_venta(st.session_state["venta_edit"])

if "venta_msg" in st.session_state:
    st.success(st.session_state.pop("venta_msg"))

tab_lista, tab_registrar = st.tabs(["Lista", "Registrar"])

# ── LISTA ─────────────────────────────────────────────────────────────────────
with tab_lista:
    if not ventas:
        st.info("No hay ventas registradas.")
    else:
        for vta in sorted(ventas, key=lambda v: v["fecha_venta"], reverse=True):
            color  = FORMA_COLOR.get(vta["forma_pago"], "#6B7280")
            cliente = cliente_map.get(vta["cliente_id"], "—")

            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                obs = vta.get("observaciones")
                obs_txt = f"<br><span style='color:#888;font-size:0.8rem'>{obs}</span>" if obs else ""
                st.markdown(
                    f"**{cliente}** · Vehículo #{vta['vehiculo_id']}"
                    f"<br><span style='color:#888;font-size:0.8rem'>{vta['fecha_venta']}</span>"
                    f"{obs_txt}",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"**${float(vta['precio_final']):,.0f}**",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<span style='color:{color};font-size:0.72rem;font-weight:700;"
                    f"text-transform:uppercase;letter-spacing:0.05em'>{vta['forma_pago']}</span>",
                    unsafe_allow_html=True,
                )
            with c3:
                if st.button("Editar", key=f"edit_vta_{vta['id']}", use_container_width=True):
                    st.session_state["venta_edit"] = vta
                    st.rerun()
            st.divider()

# ── REGISTRAR ─────────────────────────────────────────────────────────────────
with tab_registrar:
    try:
        vehiculos_disp = get("/vehiculos/", estado="disponible")
    except Exception as e:
        st.error(str(e))
        st.stop()

    vehiculo_opts = {
        f"{v['marca']} {v['modelo']} {v['anio']} — {v['patente'] or 'sin patente'}": v["id"]
        for v in vehiculos_disp
    }
    cliente_opts = {
        f"{c['apellido']}, {c['nombre']} — DNI {c['dni'] or '-'}": c["id"]
        for c in clientes
    }

    with st.form("nueva_venta"):
        vehiculo_sel = st.selectbox("Vehículo *",
            list(vehiculo_opts.keys()) if vehiculo_opts else ["Sin stock disponible"])
        cliente_sel = st.selectbox("Cliente *",
            list(cliente_opts.keys()) if cliente_opts else ["Sin clientes"])
        precio_final  = st.number_input("Precio final *", min_value=0.01, format="%.2f")
        forma_pago    = st.selectbox("Forma de pago", FORMAS_PAGO)
        observaciones = st.text_area("Observaciones")

        if st.form_submit_button("Registrar venta", use_container_width=True):
            if not vehiculo_opts or not cliente_opts:
                st.error("Se necesita al menos un vehículo disponible y un cliente")
            else:
                try:
                    post("/ventas/", {
                        "vehiculo_id":   vehiculo_opts[vehiculo_sel],
                        "cliente_id":    cliente_opts[cliente_sel],
                        "precio_final":  precio_final,
                        "forma_pago":    forma_pago,
                        "observaciones": observaciones or None,
                    })
                    st.success("Venta registrada")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
