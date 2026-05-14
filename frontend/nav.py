import streamlit as st

_PAGES = [
    ("pages/1_Inicio.py",   "Inicio",   "📊"),
    ("pages/2_Stock.py",    "Stock",    "🚗"),
    ("pages/3_Clientes.py", "Clientes", "👥"),
    ("pages/4_Ventas.py",   "Ventas",   "📋"),
    ("pages/5_Cobros.py",   "Cobros",   "💰"),
    ("pages/6_Cheques.py",  "Cheques",  "🏦"),
]

_CSS = """
<style>
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

/* Nav link base */
div[data-testid="stPageLink"] a {
    display: flex !important;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 6px 2px 8px !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent;
    border-radius: 0 !important;
    color: #6B7280 !important;
    font-size: 0.7rem !important;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    text-decoration: none !important;
    white-space: nowrap;
    transition: color 0.15s, border-color 0.15s;
}
div[data-testid="stPageLink"] a:hover {
    color: #D1D5DB !important;
    border-bottom-color: #444 !important;
    background: transparent !important;
}
div[data-testid="stPageLink"] a[aria-current="page"] {
    color: #FF6B2B !important;
    border-bottom-color: #FF6B2B !important;
}

/* Remove column gaps so links sit flush */
div[data-testid="stPageLink"] {
    padding: 0 !important;
}
</style>
"""

_DIVIDER = "<hr style='margin: 0 0 1.2rem; border: none; border-top: 1px solid #1f1f1f;'>"


def render_nav():
    st.markdown(_CSS, unsafe_allow_html=True)
    cols = st.columns(len(_PAGES))
    for col, (path, label, icon) in zip(cols, _PAGES):
        with col:
            st.page_link(path, label=label, icon=icon, use_container_width=True)
    st.markdown(_DIVIDER, unsafe_allow_html=True)
