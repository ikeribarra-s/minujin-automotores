def get_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

/* ─────────────────────────────────────────────
   TOKENS
───────────────────────────────────────────── */
:root {
    --bg:            #0A0A0A;
    --bg-card:       #141414;
    --bg-elevated:   #1C1C1C;
    --accent:        #FF6B2B;
    --accent-soft:   rgba(255, 107, 43, 0.13);
    --accent-glow:   rgba(255, 107, 43, 0.35);
    --text:          #F0F0F0;
    --text-muted:    #787878;
    --border:        #222222;
    --border-mid:    #2E2E2E;
    --success:       #22C55E;
    --danger:        #EF4444;
    --r:             6px;
    --r-lg:          12px;
}

/* ─────────────────────────────────────────────
   BASE
───────────────────────────────────────────── */
.stApp {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ─────────────────────────────────────────────
   SIDEBAR
───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0D0D0D !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebarNav"] {
    padding-top: 8px !important;
}

[data-testid="stSidebarNav"] a {
    border-radius: var(--r) !important;
    padding: 10px 14px !important;
    margin: 1px 8px !important;
    color: var(--text-muted) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    transition: all 0.15s ease !important;
    display: block !important;
}

[data-testid="stSidebarNav"] a:hover {
    background: var(--accent-soft) !important;
    color: var(--accent) !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: var(--accent-soft) !important;
    color: var(--accent) !important;
    border-left: 3px solid var(--accent) !important;
}

/* ─────────────────────────────────────────────
   TYPOGRAPHY
───────────────────────────────────────────── */
h1 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.2rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: var(--text) !important;
    padding-bottom: 4px !important;
    border-bottom: 2px solid var(--accent) !important;
    margin-bottom: 24px !important;
}

h2 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--text) !important;
}

h3 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

/* ─────────────────────────────────────────────
   METRIC CARDS
───────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-mid) !important;
    border-top: 3px solid var(--accent) !important;
    border-radius: var(--r-lg) !important;
    padding: 20px 24px 18px !important;
}

[data-testid="metric-container"] label {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 3rem !important;
    font-weight: 800 !important;
    color: var(--text) !important;
    line-height: 1 !important;
}

[data-testid="stMetricDelta"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
}

/* ─────────────────────────────────────────────
   BUTTONS
───────────────────────────────────────────── */
.stButton > button,
.stFormSubmitButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    border-radius: var(--r) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 10px 22px !important;
    transition: background 0.15s ease, box-shadow 0.15s ease, transform 0.1s ease !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #FF8C5A !important;
    box-shadow: 0 4px 18px var(--accent-glow) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active,
.stFormSubmitButton > button:active {
    transform: translateY(0) !important;
}

/* ─────────────────────────────────────────────
   FORM INPUTS
───────────────────────────────────────────── */
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label,
.stNumberInput > label,
.stFileUploader > label,
.stDateInput > label {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: var(--r) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}

.stSelectbox > div > div,
[data-baseweb="select"] > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: var(--r) !important;
}

/* ─────────────────────────────────────────────
   FORM WRAPPER
───────────────────────────────────────────── */
[data-testid="stForm"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    padding: 24px 28px !important;
}

/* ─────────────────────────────────────────────
   DATAFRAME / TABLE
───────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-mid) !important;
    border-radius: var(--r-lg) !important;
    overflow: hidden !important;
}

[data-testid="stDataFrame"] th {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    background: var(--bg-elevated) !important;
    color: var(--text-muted) !important;
}

/* ─────────────────────────────────────────────
   FILE UPLOADER
───────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--bg-elevated) !important;
    border: 1px dashed var(--border-mid) !important;
    border-radius: var(--r-lg) !important;
    transition: border-color 0.15s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ─────────────────────────────────────────────
   ALERTS
───────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--r) !important;
}

.stSuccess > div {
    background: rgba(34, 197, 94, 0.08) !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
    border-radius: var(--r) !important;
    color: #4ade80 !important;
}

.stError > div {
    background: rgba(239, 68, 68, 0.08) !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important;
    border-radius: var(--r) !important;
}

.stInfo > div {
    background: var(--accent-soft) !important;
    border: 1px solid rgba(255, 107, 43, 0.3) !important;
    border-radius: var(--r) !important;
    color: var(--accent) !important;
}

/* ─────────────────────────────────────────────
   DIVIDER
───────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 28px 0 !important;
}

/* ─────────────────────────────────────────────
   TABS
───────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 4px !important;
}

[data-baseweb="tab"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border-radius: var(--r) var(--r) 0 0 !important;
    transition: color 0.15s ease !important;
}

[aria-selected="true"][data-baseweb="tab"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ─────────────────────────────────────────────
   SCROLLBAR
───────────────────────────────────────────── */
::-webkit-scrollbar            { width: 5px; height: 5px; }
::-webkit-scrollbar-track      { background: var(--bg); }
::-webkit-scrollbar-thumb      { background: var(--border-mid); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ─────────────────────────────────────────────
   STREAMLIT CHROME
───────────────────────────────────────────── */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"]                  { display: none !important; }
</style>
"""
