# pages/4_Spillovers_Risco.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from statsmodels.tsa.vector_ar.var_model import VAR

from src.load_data import filter_data_by_selection
from src.config import RISK_SPILLOVER_VAR_LAGS
from src.session import init_session
from src.theme import inject_theme, apply_plotly_theme, COLORS

st.set_page_config(page_title="Risk Spillovers", page_icon="🔗", layout="wide")
inject_theme()

st.markdown('<h1>Spillovers & Risk Propagation</h1>', unsafe_allow_html=True)
st.markdown(
    f'<p style="color:{COLORS["text_secondary"]};font-size:0.78rem;letter-spacing:0.06em;'
    f'margin-bottom:20px;">VAR Model · Covariance Structure · Correlation Network</p>',
    unsafe_allow_html=True,
)

df_full = init_session()

st.sidebar.markdown(
    f'<p style="font-size:0.68rem;letter-spacing:0.14em;color:{COLORS["text_muted"]};'
    f'text-transform:uppercase;margin-bottom:8px;">Research Parameters</p>',
    unsafe_allow_html=True,
)

countries = st.sidebar.multiselect(
    "Countries",
    sorted(df_full['COUNTRY'].unique()),
    default=sorted(df_full['COUNTRY'].unique())[:3],
)
product = st.sidebar.selectbox("Product", ['diesel_usd', 'gasoline_usd'])
start   = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
end     = st.sidebar.date_input("End Date",   pd.to_datetime("2024-12-01"))
lags    = st.sidebar.slider("VAR Lags", 1, 5, RISK_SPILLOVER_VAR_LAGS)

df_filtered = filter_data_by_selection(
    df_full, countries=countries, products=[product],
    start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d"),
)

if df_filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

pivot = df_filtered.pivot(index='date', columns='COUNTRY', values=product).dropna()

if pivot.shape[1] < 2:
    st.error("Select at least 2 countries for spillover analysis.")
    st.stop()

returns = np.log(pivot).diff().dropna()

if returns.empty:
    st.error("Insufficient data after log-differencing.")
    st.stop()

# ── Metrics ──────────────────────────────────────────────────
corr_matrix = returns.corr()
cov_matrix  = returns.cov()

c1, c2, c3 = st.columns(3)
c1.metric("Countries", pivot.shape[1])
c2.metric("Observations", len(returns))
c3.metric("VAR Lags", lags)

st.divider()

# ── Log-return series ─────────────────────────────────────────
st.markdown('<h2>Log-Return Series</h2>', unsafe_allow_html=True)
fig_ret = go.Figure()
palette = [COLORS["amber"], "#2E6DA4", COLORS["green_signal"], COLORS["red_signal"],
           "#7B5EA7", "#1F7A8C"]
for i, col in enumerate(returns.columns):
    fig_ret.add_trace(go.Scatter(
        x=returns.index, y=returns[col], name=col,
        line=dict(color=palette[i % len(palette)], width=1.2)
    ))
fig_ret.update_layout(height=320, xaxis_title="Date", yaxis_title="Log Return")
apply_plotly_theme(fig_ret)
st.plotly_chart(fig_ret, use_container_width=True)

# ── Correlation heatmap ───────────────────────────────────────
st.markdown('<h2>Correlation Matrix</h2>', unsafe_allow_html=True)
fig_corr = px.imshow(
    corr_matrix.round(3), text_auto=True,
    color_continuous_scale=[[0, COLORS["bg_base"]], [0.5, COLORS["amber_dim"]], [1, COLORS["amber"]]],
    zmin=-1, zmax=1,
)
fig_corr.update_layout(height=420)
apply_plotly_theme(fig_corr)
st.plotly_chart(fig_corr, use_container_width=True)

# ── VAR model ────────────────────────────────────────────────
st.divider()
st.markdown('<h2>VAR Model Summary</h2>', unsafe_allow_html=True)
try:
    model = VAR(returns)
    res   = model.fit(lags)
    st.code(str(res.summary()), language=None)
except Exception as e:
    st.error(f"VAR fitting error: {e}")
