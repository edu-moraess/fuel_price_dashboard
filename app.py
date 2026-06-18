import streamlit as st

st.set_page_config(
    page_title="Fuel Price Intelligence",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.theme import inject, sidebar_logo, nav_label, status_dot
from src.nav import init, render_nav, current
from src.data import load
from src import pages as P

# ── Boot ─────────────────────────────────────────────────────
inject()
init()
df = load()

# ── Sidebar ──────────────────────────────────────────────────
sidebar_logo()
render_nav()
st.sidebar.divider()
nav_label("System Status")
status_dot(not df.empty)

# ── Page router ──────────────────────────────────────────────
page = current()

if page == "home":
    P.page_home(df)
elif page == "coint":
    P.page_cointegration(df)
elif page == "regime":
    P.page_regime(df)
elif page == "implied":
    P.page_implied(df)
elif page == "spillovers":
    P.page_spillovers(df)
elif page == "portfolio":
    P.page_portfolio(df)
