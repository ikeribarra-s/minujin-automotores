import streamlit as st
import pandas as pd
from api_client import get, post, put
from styles import get_css
from nav import render_nav

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
render_nav("Ventas")
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

    if not ventas:
        st.info("No hay ventas registradas.")
    else:
        venta_opts = {
            f"#{v['id']} · {cliente_map.get(v['cliente_id'], '?')} · ${float(v['precio_final']):,.0f} · {v['fecha_venta']}": v
            for v in ventas
        }
        sel_label = st.selectbox("Seleccionar venta", list(venta_opts.keys()))
        vta = venta_opts[sel_label]

        st.caption(f"Vehículo #{vta['vehiculo_id']} · {vta['forma_pago']}")

        with st.form("edit_venta"):
            precio_final  = st.number_input("Precio final", min_value=0.01,
                                            value=float(vta["precio_final"]), format="%.2f")
            forma_pago    = st.selectbox("Forma de pago", FORMAS_PAGO,
                                         index=FORMAS_PAGO.index(vta["forma_pago"]))
            observaciones = st.text_area("Observaciones", value=vta.get("observaciones") or "")

            guardado = st.form_submit_button("Guardar cambios", use_container_width=True)

        if guardado:
            try:
                put(f"/ventas/{vta['id']}", {
                    "precio_final":  precio_final,
                    "forma_pago":    forma_pago,
                    "observaciones": observaciones or None,
                })
                st.success("Venta actualizada")
                st.rerun()
            except Exception as e:
                st.error(str(e))
