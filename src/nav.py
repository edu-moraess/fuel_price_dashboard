"""
Single-file navigation state manager.
Pages are rendered inside app.py — no pages/ folder needed.
This eliminates the duplicate sidebar nav issue entirely.
"""
import streamlit as st

PAGES = [
    ("home",        "Overview"),
    ("coint",       "Cointegration"),
    ("regime",      "Regime Switching"),
    ("implied",     "Implied Expectations"),
    ("spillovers",  "Spillovers & Risk"),
    ("portfolio",   "Portfolio Simulation"),
]


def init():
    if "page" not in st.session_state:
        st.session_state.page = "home"


def current() -> str:
    return st.session_state.get("page", "home")


def go(page_id: str):
    st.session_state.page = page_id
    st.rerun()


def render_nav():
    """Renders nav buttons in sidebar. Call after logo."""
    from src.theme import C
    cur = current()
    for pid, label in PAGES:
        active = pid == cur
        css_class = "nav-btn-active nav-btn" if active else "nav-btn"
        with st.sidebar:
            with st.container():
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                if st.button(label, key=f"nav_{pid}", use_container_width=True):
                    go(pid)
                st.markdown("</div>", unsafe_allow_html=True)
