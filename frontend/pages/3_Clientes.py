import streamlit as st
import pandas as pd
from api_client import get, post, put
from styles import get_css
from nav import render_nav

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
render_nav()
st.title("Clientes")

tab_lista, tab_agregar, tab_editar = st.tabs(["Lista", "Agregar", "Editar"])

# ── LISTA ─────────────────────────────────────────────────────────────────────
with tab_lista:
    busqueda = st.text_input("Buscar por nombre, apellido o DNI")
    try:
        clientes = get("/clientes/", busqueda=busqueda) if busqueda else get("/clientes/")
    except Exception as e:
        st.error(str(e))
        st.stop()

    if clientes:
        df = pd.DataFrame(clientes)
        st.dataframe(
            df[["id", "apellido", "nombre", "dni", "telefono", "email", "direccion"]],
            use_container_width=True,
        )
    else:
        st.info("No hay clientes.")

# ── AGREGAR ───────────────────────────────────────────────────────────────────
with tab_agregar:
    with st.form("nuevo_cliente"):
        c1, c2 = st.columns(2)
        nombre   = c1.text_input("Nombre *")
        apellido = c2.text_input("Apellido *")
        c3, c4 = st.columns(2)
        dni      = c3.text_input("DNI")
        telefono = c4.text_input("Teléfono")
        email    = st.text_input("Email")
        direccion = st.text_area("Dirección")

        if st.form_submit_button("Guardar", use_container_width=True):
            if not nombre or not apellido:
                st.error("Nombre y apellido son obligatorios")
            else:
                try:
                    post("/clientes/", {
                        "nombre": nombre, "apellido": apellido,
                        "dni": dni or None, "telefono": telefono or None,
                        "email": email or None, "direccion": direccion or None,
                    })
                    st.success("Cliente agregado")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

# ── EDITAR ────────────────────────────────────────────────────────────────────
with tab_editar:
    c_id, c_btn = st.columns([3, 1])
    edit_id = c_id.number_input("ID del cliente", min_value=1, step=1, key="edit_c_id")
    if c_btn.button("Cargar", key="cargar_c"):
        try:
            st.session_state["edit_cliente"] = get(f"/clientes/{edit_id}")
        except Exception:
            st.error("Cliente no encontrado")
            st.session_state.pop("edit_cliente", None)

    c = st.session_state.get("edit_cliente")
    if c:
        st.caption(f"Editando: {c['apellido']}, {c['nombre']} — ID {c['id']}")
        with st.form("edit_cliente"):
            c1, c2 = st.columns(2)
            nombre   = c1.text_input("Nombre *",   value=c["nombre"])
            apellido = c2.text_input("Apellido *",  value=c["apellido"])
            c3, c4 = st.columns(2)
            dni      = c3.text_input("DNI",         value=c["dni"]      or "")
            telefono = c4.text_input("Teléfono",    value=c["telefono"] or "")
            email    = st.text_input("Email",        value=c["email"]    or "")
            direccion = st.text_area("Dirección",   value=c["direccion"] or "")

            c_save, c_cancel = st.columns(2)
            guardado  = c_save.form_submit_button("Guardar cambios", use_container_width=True)
            cancelado = c_cancel.form_submit_button("Cancelar",       use_container_width=True)

        if guardado:
            if not nombre or not apellido:
                st.error("Nombre y apellido son obligatorios")
            else:
                try:
                    put(f"/clientes/{c['id']}", {
                        "nombre": nombre, "apellido": apellido,
                        "dni": dni or None, "telefono": telefono or None,
                        "email": email or None, "direccion": direccion or None,
                    })
                    st.success("Cliente actualizado")
                    st.session_state.pop("edit_cliente", None)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        if cancelado:
            st.session_state.pop("edit_cliente", None)
            st.rerun()
