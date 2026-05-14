import streamlit as st

_PAGES = [
    ("pages/1_Inicio.py",   "Inicio"),
    ("pages/2_Stock.py",    "Stock"),
    ("pages/3_Clientes.py", "Clientes"),
    ("pages/4_Ventas.py",   "Ventas"),
    ("pages/5_Cobros.py",   "Cobros"),
    ("pages/6_Cheques.py",  "Cheques"),
]

_CSS = """
<style>
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

/* Prevent iOS auto-zoom on input focus (triggered when font-size < 16px) */
input, textarea, select,
input[type="text"], input[type="number"],
input[type="email"], input[type="password"],
input[type="search"], input[type="date"] {
    font-size: 16px !important;
}

/* Hide "Press Enter to submit" hint */
[data-testid="stForm"] small,
.stTextInput small,
.stNumberInput small,
.stTextArea small,
.stDateInput small,
.stSelectbox small { display: none !important; }

/* Nav: horizontal only, no vertical scroll */
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPageLink"]) {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    touch-action: pan-x !important;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
    border-bottom: 1px solid #1f1f1f;
    margin-bottom: 1rem;
    gap: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPageLink"])::-webkit-scrollbar {
    display: none;
}
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPageLink"]) > div[data-testid="stColumn"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: fit-content !important;
    padding: 0 !important;
}

/* Nav link styling */
div[data-testid="stPageLink"] {
    padding: 0 !important;
}
div[data-testid="stPageLink"] a {
    display: block !important;
    padding: 10px 14px !important;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    background: transparent !important;
    border-radius: 0 !important;
    color: #6B7280 !important;
    font-size: 0.72rem !important;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    text-decoration: none !important;
    white-space: nowrap;
    transition: color 0.15s, border-color 0.15s;
}
div[data-testid="stPageLink"] a:hover {
    color: #D1D5DB !important;
    border-bottom-color: #555 !important;
    background: transparent !important;
}
div[data-testid="stPageLink"] a[aria-current="page"] {
    color: #FF6B2B !important;
    border-bottom-color: #FF6B2B !important;
}
</style>
"""


def render_nav(active: str = ""):
    # Force a clean rerun when the page changes so stale widget state doesn't bleed through
    if st.session_state.get("_current_page") != active:
        st.session_state["_current_page"] = active
        st.rerun()

    st.markdown(_CSS, unsafe_allow_html=True)
    cols = st.columns(len(_PAGES))
    for col, (path, label) in zip(cols, _PAGES):
        with col:
            st.page_link(path, label=label, use_container_width=True)