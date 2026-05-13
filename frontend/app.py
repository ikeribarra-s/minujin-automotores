import base64
import streamlit as st
from pathlib import Path
from api_client import login
from styles import get_css

st.set_page_config(
    page_title="Minujin Automotores",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(get_css(), unsafe_allow_html=True)

if "token" not in st.session_state:
    # Hide sidebar only on the login screen
    st.markdown("""
    <style>
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] { display: none !important; }
    .block-container { padding-top: 1rem !important; }

    .mn-card {
        background: #141414;
        border: 1px solid #222;
        border-radius: 16px;
        padding: 52px 44px 44px;
        margin: 40px auto 0;
    }
    .mn-rule {
        width: 48px; height: 3px;
        background: #FF6B2B; border-radius: 2px;
        margin: 22px auto 10px;
    }
    .mn-eyebrow {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 0.68rem; font-weight: 700;
        letter-spacing: 0.22em; text-transform: uppercase;
        color: #787878; text-align: center; margin-bottom: 32px;
    }
    </style>
    """, unsafe_allow_html=True)

    logo_path = Path(__file__).parent.parent / "gui" / "minujin-logo.png"
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()

    st.markdown(f"""
    <div class="mn-card">
        <img src="data:image/png;base64,{logo_b64}"
             style="width:100%; filter:invert(1); display:block;"
             alt="Minujin Automotores" />
        <div class="mn-rule"></div>
        <p class="mn-eyebrow">Sistema de Gestión Interna</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login", clear_on_submit=False):
        username = st.text_input("Nombre de usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar", use_container_width=True)

    if submitted:
        if login(username, password):
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# ── Authenticated home ──────────────────────────────────────────────────────
st.title("Inicio")
st.write("Seleccioná una sección en el menú lateral.")
