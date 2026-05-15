import streamlit as st
from api_client import get, post, put
from styles import get_css
from nav import render_nav

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
render_nav("Clientes")
st.title("Clientes")


@st.dialog("Editar cliente", width="large")
def dialogo_editar_cliente(c: dict):
    with st.form("form_edit_cliente"):
        c1, c2 = st.columns(2)
        nombre   = c1.text_input("Nombre *",   value=c["nombre"])
        apellido = c2.text_input("Apellido *",  value=c["apellido"])
        c3, c4 = st.columns(2)
        dni      = c3.text_input("DNI",         value=c.get("dni")      or "")
        telefono = c4.text_input("Teléfono",    value=c.get("telefono") or "")
        email    = st.text_input("Email",        value=c.get("email")    or "")
        direccion = st.text_area("Dirección",   value=c.get("direccion") or "")

        c_save, c_cancel = st.columns(2)
        guardado  = c_save.form_submit_button("Guardar cambios", use_container_width=True)
        cancelado = c_cancel.form_submit_button("Cancelar",      use_container_width=True)

    if guardado:
        if not nombre or not apellido:
            st.error("Nombre y apellido son obligatorios")
        else:
            try:
                put(f"/clientes/{c['id']}", {
                    "nombre":    nombre,
                    "apellido":  apellido,
                    "dni":       dni or None,
                    "telefono":  telefono or None,
                    "email":     email or None,
                    "direccion": direccion or None,
                })
                st.session_state["cliente_msg"] = "Cliente actualizado"
                st.rerun()
            except Exception as e:
                st.error(str(e))
    if cancelado:
        st.rerun()


if "cliente_edit" in st.session_state:
    dialogo_editar_cliente(st.session_state["cliente_edit"])

if "cliente_msg" in st.session_state:
    st.success(st.session_state.pop("cliente_msg"))

tab_lista, tab_agregar = st.tabs(["Lista", "Agregar"])

# ── LISTA ─────────────────────────────────────────────────────────────────────
with tab_lista:
    busqueda = st.text_input("Buscar por nombre, apellido o DNI")
    try:
        clientes = get("/clientes/", busqueda=busqueda) if busqueda else get("/clientes/")
    except Exception as e:
        st.error(str(e))
        st.stop()

    if not clientes:
        st.info("No hay clientes.")
    else:
        for cliente in clientes:
            c1, c2, c3 = st.columns([4, 3, 1])
            with c1:
                dni_txt = f" · DNI {cliente['dni']}" if cliente.get("dni") else ""
                st.markdown(
                    f"**{cliente['apellido']}, {cliente['nombre']}**{dni_txt}"
                    f"<br><span style='color:#888;font-size:0.8rem'>"
                    f"{cliente.get('email') or '—'}</span>",
                    unsafe_allow_html=True,
                )
            with c2:
                tel = cliente.get("telefono") or "—"
                dir_ = cliente.get("direccion") or "—"
                st.markdown(
                    f"<span style='font-size:0.85rem'>📞 {tel}</span>"
                    f"<br><span style='color:#888;font-size:0.8rem'>📍 {dir_}</span>",
                    unsafe_allow_html=True,
                )
            with c3:
                if st.button("Editar", key=f"edit_cli_{cliente['id']}", use_container_width=True):
                    st.session_state["cliente_edit"] = cliente
                    st.rerun()
            st.divider()

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
                        "nombre":    nombre,
                        "apellido":  apellido,
                        "dni":       dni or None,
                        "telefono":  telefono or None,
                        "email":     email or None,
                        "direccion": direccion or None,
                    })
                    st.success("Cliente agregado")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
