import streamlit as st
import pandas as pd
from api_client import get, post, put
from styles import get_css

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
st.title("Ventas")

FORMAS_PAGO = ["contado", "financiado", "permuta", "mixto"]

try:
    ventas   = get("/ventas/")
    clientes = get("/clientes/")
except Exception as e:
    st.error(str(e))
    st.stop()

cliente_map = {c["id"]: f"{c['apellido']}, {c['nombre']}" for c in clientes}

tab_lista, tab_registrar, tab_editar = st.tabs(["Lista", "Registrar", "Editar"])

# ── LISTA ─────────────────────────────────────────────────────────────────────
with tab_lista:
    if ventas:
        df = pd.DataFrame(ventas)
        df["cliente"] = df["cliente_id"].map(cliente_map)
        st.dataframe(
            df[["id", "fecha_venta", "cliente", "vehiculo_id",
                "precio_final", "forma_pago", "observaciones"]],
            use_container_width=True,
        )
    else:
        st.info("No hay ventas registradas.")

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
        precio_final = st.number_input("Precio final *", min_value=0.01, format="%.2f")
        forma_pago   = st.selectbox("Forma de pago", FORMAS_PAGO)
        observaciones = st.text_area("Observaciones")

        if st.form_submit_button("Registrar venta", use_container_width=True):
            if not vehiculo_opts or not cliente_opts:
                st.error("Se necesita al menos un vehículo disponible y un cliente")
            else:
                try:
                    post("/ventas/", {
                        "vehiculo_id": vehiculo_opts[vehiculo_sel],
                        "cliente_id":  cliente_opts[cliente_sel],
                        "precio_final": precio_final,
                        "forma_pago":   forma_pago,
                        "observaciones": observaciones or None,
                    })
                    st.success("Venta registrada")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

# ── EDITAR ────────────────────────────────────────────────────────────────────
with tab_editar:
    st.caption("Solo se pueden modificar precio, forma de pago y observaciones.")

    c_id, c_btn = st.columns([3, 1])
    edit_id = c_id.number_input("ID de la venta", min_value=1, step=1, key="edit_vta_id")
    if c_btn.button("Cargar", key="cargar_vta"):
        try:
            st.session_state["edit_venta"] = get(f"/ventas/{edit_id}")
        except Exception:
            st.error("Venta no encontrada")
            st.session_state.pop("edit_venta", None)

    vta = st.session_state.get("edit_venta")
    if vta:
        cliente_label = cliente_map.get(vta["cliente_id"], f"ID {vta['cliente_id']}")
        st.caption(f"Editando venta #{vta['id']} — Cliente: {cliente_label} — Vehículo ID: {vta['vehiculo_id']}")

        with st.form("edit_venta"):
            precio_final  = st.number_input("Precio final", min_value=0.01,
                                            value=float(vta["precio_final"]), format="%.2f")
            forma_pago    = st.selectbox("Forma de pago", FORMAS_PAGO,
                                         index=FORMAS_PAGO.index(vta["forma_pago"]))
            observaciones = st.text_area("Observaciones", value=vta["observaciones"] or "")

            c_save, c_cancel = st.columns(2)
            guardado  = c_save.form_submit_button("Guardar cambios", use_container_width=True)
            cancelado = c_cancel.form_submit_button("Cancelar",       use_container_width=True)

        if guardado:
            try:
                put(f"/ventas/{vta['id']}", {
                    "precio_final":  precio_final,
                    "forma_pago":    forma_pago,
                    "observaciones": observaciones or None,
                })
                st.success("Venta actualizada")
                st.session_state.pop("edit_venta", None)
                st.rerun()
            except Exception as e:
                st.error(str(e))

        if cancelado:
            st.session_state.pop("edit_venta", None)
            st.rerun()
