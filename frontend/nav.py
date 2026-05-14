import streamlit as st

_PAGES = [
    ("/Inicio",   "Inicio"),
    ("/Stock",    "Stock"),
    ("/Clientes", "Clientes"),
    ("/Ventas",   "Ventas"),
    ("/Cobros",   "Cobros"),
    ("/Cheques",  "Cheques"),
]

_CSS = """
<style>
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

[data-testid="stForm"] small,
.stTextInput small,
.stNumberInput small,
.stTextArea small,
.stDateInput small,
.stSelectbox small { display: none !important; }

.mn-nav {
    display: flex;
    flex-direction: row;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
    border-bottom: 1px solid #1f1f1f;
    margin-bottom: 1.2rem;
}
.mn-nav::-webkit-scrollbar { display: none; }
.mn-nav a {
    flex: 0 0 auto;
    display: block;
    padding: 10px 14px;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    color: #6B7280 !important;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    text-decoration: none !important;
    white-space: nowrap;
    transition: color 0.15s, border-color 0.15s;
}
.mn-nav a:hover   { color: #D1D5DB !important; border-bottom-color: #555; }
.mn-nav a.mn-act  { color: #FF6B2B !important; border-bottom-color: #FF6B2B; }
</style>
"""


def render_nav(active: str = ""):
    links = ""
    for url, label in _PAGES:
        cls = ' class="mn-act"' if label == active else ""
        links += f'<a href="{url}"{cls}>{label}</a>\n'
    st.markdown(f'{_CSS}<nav class="mn-nav">{links}</nav>', unsafe_allow_html=True)