import streamlit as st
from api_client import get, post, put, delete, upload_file
from styles import get_css
from nav import render_nav

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
render_nav("Stock")
st.markdown("""
<style>
/* Compact card action buttons */
[data-testid="stHorizontalBlock"] .stButton > button {
    padding: 5px 8px !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Stock de Vehículos")

TIPOS        = ["usado", "cero_km"]
PROCEDENCIA  = ["compra", "permuta", "consignacion"]
ESTADOS      = ["disponible", "reservado", "vendido"]
ESTADO_COLOR = {
    "disponible": ("#22C55E", "rgba(34,197,94,0.12)"),
    "reservado":  ("#F59E0B", "rgba(245,158,11,0.12)"),
    "vendido":    ("#6B7280", "rgba(107,114,128,0.12)"),
}


def fmt_precio(p) -> str:
    if p is None:
        return "Consultar"
    return "$ " + f"{float(p):,.0f}".replace(",", ".")


def fmt_km(k) -> str:
    return f"{int(k or 0):,} km".replace(",", ".")


def render_card(v: dict):
    color, badge_bg = ESTADO_COLOR.get(v["estado"], ("#888", "#1C1C1C"))
    foto = v.get("foto_url") or ""
    version_label = f" <span style='color:#555;font-size:0.85rem;font-weight:400'>{v['version']}</span>" if v.get("version") else ""
    patente_label = f"&nbsp;·&nbsp;{v['patente']}" if v.get("patente") else ""

    img_css = f"background:url({foto}) center/cover no-repeat" if foto else "background:#181818"
    icon    = "" if foto else '<span style="font-size:2.8rem;color:#2A2A2A;">◈</span>'

    st.markdown(f"""
    <div style="background:#141414;border:1px solid #222;border-radius:10px;overflow:hidden;margin-bottom:2px;">
        <div style="height:148px;{img_css};display:flex;align-items:center;justify-content:center;">{icon}</div>
        <div style="padding:13px 14px 11px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:2px;">
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:800;text-transform:uppercase;letter-spacing:0.03em;line-height:1.2;">
                    {v['marca']} {v['modelo']}{version_label}
                </div>
                <span style="color:#444;font-size:0.68rem;font-weight:600;padding-top:3px;">#{v['id']}</span>
            </div>
            <div style="color:#555;font-size:0.76rem;margin-bottom:10px;">
                {v['anio']}{patente_label}&nbsp;·&nbsp;{fmt_km(v.get('kilometraje'))}
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.45rem;font-weight:800;color:#F0F0F0;">
                    {fmt_precio(v.get('precio_venta'))}
                </span>
                <span style="background:{badge_bg};color:{color};font-size:0.58rem;font-weight:700;
                             padding:3px 10px;border-radius:20px;text-transform:uppercase;
                             letter-spacing:0.1em;border:1px solid {color}40;">
                    {v['estado']}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    if c1.button("Editar", key=f"edit_{v['id']}", use_container_width=True):
        st.session_state["veh_edit"] = v
        st.rerun()
    if c2.button("Eliminar", key=f"del_{v['id']}", use_container_width=True):
        st.session_state["veh_delete"] = v
        st.rerun()


# ── CONFIRM DELETE DIALOG ─────────────────────────────────────────────────────
@st.dialog("Confirmar eliminación")
def dialogo_eliminar(v: dict):
    st.markdown(f"¿Eliminar **{v['marca']} {v['modelo']} {v['anio']}** (ID {v['id']})?")
    st.caption("Solo podés eliminar vehículos con estado **disponible**. Esta acción no se puede deshacer.")
    c1, c2 = st.columns(2)
    if c1.button("Sí, eliminar", use_container_width=True):
        try:
            delete(f"/vehiculos/{v['id']}")
            st.session_state.pop("veh_delete", None)
            st.session_state["stock_msg"] = ("success", f"Vehículo #{v['id']} eliminado")
            st.rerun()
        except Exception as e:
            st.error(str(e))
    if c2.button("Cancelar", use_container_width=True):
        st.session_state.pop("veh_delete", None)
        st.rerun()


if "veh_delete" in st.session_state:
    dialogo_eliminar(st.session_state["veh_delete"])

if "stock_msg" in st.session_state:
    lvl, msg = st.session_state.pop("stock_msg")
    (st.success if lvl == "success" else st.error)(msg)

# ─────────────────────────────────────────────────────────────────────────────
tab_lista, tab_agregar, tab_foto = st.tabs(["Lista", "Agregar", "Foto"])

# ── LISTA ─────────────────────────────────────────────────────────────────────
with tab_lista:
    try:
        todos = get("/vehiculos/")
    except Exception as e:
        st.error(str(e))
        st.stop()

    # Summary strip
    disp = sum(1 for v in todos if v["estado"] == "disponible")
    res  = sum(1 for v in todos if v["estado"] == "reservado")
    vend = sum(1 for v in todos if v["estado"] == "vendido")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total",       len(todos))
    c2.metric("Disponibles", disp)
    c3.metric("Reservados",  res)
    c4.metric("Vendidos",    vend)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    estado_filtro = st.selectbox("Filtrar", ["todos"] + ESTADOS, label_visibility="collapsed")
    vehiculos = [v for v in todos if estado_filtro == "todos" or v["estado"] == estado_filtro]

    if not vehiculos:
        st.info("No hay vehículos para el filtro seleccionado.")
    else:
        N = 3
        for i in range(0, len(vehiculos), N):
            cols = st.columns(N)
            for col, v in zip(cols, vehiculos[i:i+N]):
                with col:
                    render_card(v)

    # Inline edit form (shown when a card's Editar is clicked)
    veh = st.session_state.get("veh_edit")
    if veh:
        st.divider()
        hdr, close_btn = st.columns([5, 1])
        hdr.subheader(f"Editando — {veh['marca']} {veh['modelo']} {veh['anio']}")
        if close_btn.button("✕ Cerrar", key="close_edit"):
            st.session_state.pop("veh_edit", None)
            st.rerun()

        with st.form("form_edit_veh"):
            c1, c2, c3 = st.columns(3)
            marca   = c1.text_input("Marca *",   value=veh["marca"])
            modelo  = c2.text_input("Modelo *",  value=veh["modelo"])
            anio    = c3.number_input("Año *", min_value=1950, max_value=2100, value=veh["anio"])

            c4, c5, c6 = st.columns(3)
            version     = c4.text_input("Versión",     value=veh["version"] or "")
            color       = c5.text_input("Color",        value=veh["color"]   or "")
            km          = c6.number_input("Kilometraje", min_value=0, value=veh["kilometraje"] or 0)

            c7, c8, c9 = st.columns(3)
            tipo        = c7.selectbox("Tipo",        TIPOS,       index=TIPOS.index(veh["tipo"]))
            procedencia = c8.selectbox("Procedencia", PROCEDENCIA, index=PROCEDENCIA.index(veh["procedencia"]))
            patente     = c9.text_input("Patente", value=veh["patente"] or "", help="AB 123 CD  ó  ABC 123")

            c10, c11, c12 = st.columns(3)
            precio_compra = c10.number_input("Precio compra", min_value=0.0,
                                              value=float(veh["precio_compra"] or 0), format="%.2f")
            precio_venta  = c11.number_input("Precio venta",  min_value=0.0,
                                              value=float(veh["precio_venta"]  or 0), format="%.2f")
            estado        = c12.selectbox("Estado", ESTADOS, index=ESTADOS.index(veh["estado"]))

            observaciones = st.text_area("Observaciones", value=veh["observaciones"] or "")
            guardado = st.form_submit_button("Guardar cambios", use_container_width=True)

        if guardado:
            try:
                put(f"/vehiculos/{veh['id']}", {
                    "marca": marca, "modelo": modelo, "anio": anio,
                    "version": version or None, "color": color or None,
                    "kilometraje": km, "tipo": tipo, "procedencia": procedencia,
                    "patente": patente or None,
                    "precio_compra": precio_compra or None,
                    "precio_venta":  precio_venta  or None,
                    "estado": estado,
                    "observaciones": observaciones or None,
                })
                st.session_state.pop("veh_edit", None)
                st.session_state["stock_msg"] = ("success", "Vehículo actualizado")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# ── AGREGAR ───────────────────────────────────────────────────────────────────
with tab_agregar:
    with st.form("form_nuevo_veh"):
        c1, c2, c3 = st.columns(3)
        marca   = c1.text_input("Marca *")
        modelo  = c2.text_input("Modelo *")
        anio    = c3.number_input("Año *", min_value=1950, max_value=2100, value=2020)

        c4, c5, c6 = st.columns(3)
        version     = c4.text_input("Versión")
        color       = c5.text_input("Color")
        km          = c6.number_input("Kilometraje", min_value=0, value=0)

        c7, c8, c9 = st.columns(3)
        tipo        = c7.selectbox("Tipo",        TIPOS)
        procedencia = c8.selectbox("Procedencia", PROCEDENCIA)
        patente     = c9.text_input("Patente", help="AB 123 CD  ó  ABC 123")

        c10, c11 = st.columns(2)
        precio_compra = c10.number_input("Precio compra", min_value=0.0, format="%.2f")
        precio_venta  = c11.number_input("Precio venta",  min_value=0.0, format="%.2f")

        observaciones = st.text_area("Observaciones")
        foto_nueva    = st.file_uploader("Foto (opcional)", type=["jpg", "jpeg", "png", "webp"])
        guardado_nuevo = st.form_submit_button("Guardar vehículo", use_container_width=True)

    if guardado_nuevo:
        if not marca or not modelo:
            st.error("Marca y modelo son obligatorios")
        else:
            try:
                creado = post("/vehiculos/", {
                    "marca": marca, "modelo": modelo, "anio": anio,
                    "version": version or None, "color": color or None,
                    "kilometraje": km, "tipo": tipo, "procedencia": procedencia,
                    "patente": patente or None,
                    "precio_compra": precio_compra or None,
                    "precio_venta":  precio_venta  or None,
                    "observaciones": observaciones or None,
                })
                if foto_nueva:
                    upload_file(f"/vehiculos/{creado['id']}/foto",
                                foto_nueva.getvalue(), foto_nueva.name, foto_nueva.type)
                st.session_state["stock_msg"] = ("success", f"Vehículo #{creado['id']} agregado")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# ── FOTO ──────────────────────────────────────────────────────────────────────
with tab_foto:
    c_id, c_btn = st.columns([3, 1])
    foto_id = c_id.number_input("ID del vehículo", min_value=1, step=1, key="foto_id")
    if c_btn.button("Cargar", key="btn_cargar_foto"):
        try:
            st.session_state["foto_veh"] = get(f"/vehiculos/{foto_id}")
        except Exception:
            st.error("Vehículo no encontrado")
            st.session_state.pop("foto_veh", None)

    fv = st.session_state.get("foto_veh")
    if fv:
        st.caption(f"{fv['marca']} {fv['modelo']} {fv['anio']} — ID {fv['id']}")
        if fv.get("foto_url"):
            st.image(fv["foto_url"], width=380)
        else:
            st.info("Sin foto cargada")

        upload = st.file_uploader("Subir / reemplazar foto", type=["jpg", "jpeg", "png", "webp"])
        if upload and st.button("Subir foto"):
            try:
                upload_file(f"/vehiculos/{fv['id']}/foto",
                            upload.getvalue(), upload.name, upload.type)
                st.session_state.pop("foto_veh", None)
                st.session_state["stock_msg"] = ("success", "Foto actualizada")
                st.rerun()
            except Exception as e:
                st.error(str(e))
