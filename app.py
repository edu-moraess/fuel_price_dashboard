import streamlit as st
import pandas as pd
from src.load_data import load_and_preprocess_data
from src.config import DATA_PATH
from src.theme import inject_theme, apply_plotly_theme, status_badge, COLORS

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="Fuel Price Quant Research Platform",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

# ── Data layer ───────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_and_preprocess_data(DATA_PATH)

df = get_data()

if "df" not in st.session_state:
    st.session_state["df"] = df

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.markdown(
    f"""
    <div style="padding: 18px 0 10px 0; border-bottom: 1px solid {COLORS['border']}; margin-bottom: 18px;">
        <div style="font-family:'IBM Plex Sans Condensed',sans-serif; font-size:0.65rem;
                    letter-spacing:0.18em; color:{COLORS['text_muted']}; text-transform:uppercase;
                    margin-bottom:4px;">Quant Research Platform</div>
        <div style="font-family:'IBM Plex Sans Condensed',sans-serif; font-weight:700;
                    font-size:1.15rem; color:{COLORS['text_primary']}; letter-spacing:0.04em;
                    text-transform:uppercase; line-height:1.2;">Fuel Price<br>
            <span style="color:{COLORS['amber']};">Intelligence</span>
        </div>
        <div style="font-size:0.65rem; color:{COLORS['text_muted']}; margin-top:6px;
                    letter-spacing:0.06em;">IEA · GLOBAL · MACRO</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    f'<p style="font-size:0.68rem; letter-spacing:0.12em; color:{COLORS["text_muted"]}; text-transform:uppercase; margin-bottom:6px;">Modules</p>',
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f"""
    <div style="font-size:0.80rem; color:{COLORS['text_secondary']}; line-height:2.0;
                border-left: 2px solid {COLORS['border']}; padding-left: 10px;">
        <span style="color:{COLORS['amber']};">→</span> Cointegration Analysis<br>
        <span style="color:{COLORS['amber']};">→</span> Regime Switching Models<br>
        <span style="color:{COLORS['amber']};">→</span> Implied Expectations<br>
        <span style="color:{COLORS['amber']};">→</span> Spillovers &amp; Risk<br>
        <span style="color:{COLORS['amber']};">→</span> Portfolio Simulation
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.divider()

st.sidebar.markdown(
    f'<p style="font-size:0.68rem; letter-spacing:0.12em; color:{COLORS["text_muted"]}; text-transform:uppercase; margin-bottom:6px;">System Status</p>',
    unsafe_allow_html=True,
)
status_badge(not df.empty)

# ── Hero header ──────────────────────────────────────────────
st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['bg_surface']} 0%, {COLORS['bg_elevated']} 100%);
        border: 1px solid {COLORS['border']};
        border-left: 4px solid {COLORS['amber']};
        border-radius: 2px;
        padding: 28px 32px 22px 32px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute; top: 0; right: 0;
            width: 120px; height: 100%;
            background: repeating-linear-gradient(
                -45deg,
                transparent,
                transparent 8px,
                {COLORS['amber_dim']} 8px,
                {COLORS['amber_dim']} 9px
            );
            opacity: 0.35;
        "></div>
        <div style="font-family:'IBM Plex Sans Condensed',sans-serif; font-size:0.62rem;
                    letter-spacing:0.20em; color:{COLORS['amber']}; text-transform:uppercase;
                    margin-bottom: 8px;">⛽ Fuel Price Quant Research Platform</div>
        <div style="font-family:'IBM Plex Sans Condensed',sans-serif; font-weight:700;
                    font-size:2.0rem; color:{COLORS['text_primary']}; line-height:1.1;
                    letter-spacing:0.03em; text-transform:uppercase;">
            Global Energy<br>
            <span style="color:{COLORS['amber']};">Market Intelligence</span>
        </div>
        <div style="font-size:0.78rem; color:{COLORS['text_secondary']}; margin-top:10px;
                    font-family:'IBM Plex Mono',monospace; letter-spacing:0.04em;">
            Cointegration · Regime Detection · Risk Spillovers · Portfolio Optimization
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Key metrics ──────────────────────────────────────────────
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Records", f"{len(df):,}")
    col2.metric("Countries", df["COUNTRY"].nunique())
    col3.metric("Start Date", str(df["date"].min())[:10])
    col4.metric("End Date",   str(df["date"].max())[:10])

    st.divider()

    # ── Coverage snapshot ─────────────────────────────────────
    st.markdown(
        f'<h2>Market Coverage</h2>',
        unsafe_allow_html=True,
    )

    products = [
        col.replace("_usd", "").upper()
        for col in ["diesel_usd", "gasoline_usd"]
        if col in df.columns
    ]
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.80rem; '
        f'color:{COLORS["amber"]}; background:{COLORS["bg_elevated"]}; '
        f'border:1px solid {COLORS["border"]}; padding:10px 16px; border-radius:2px; '
        f'letter-spacing:0.10em;">'
        + " &nbsp;|&nbsp; ".join(products) +
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Disclaimer ────────────────────────────────────────────
    st.info(
        "RESEARCH PROTOTYPE — All outputs are exploratory and for analytical purposes only. "
        "Not investment advice. IEA data source."
    )
