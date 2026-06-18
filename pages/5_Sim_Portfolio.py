# pages/5_Sim_Portfolio.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize

from src.load_data import filter_data_by_selection
from src.config import PORTFOLIO_SIMULATION_DEFAULT_N_ASSETS
from src.session import init_session
from src.theme import inject_theme, apply_plotly_theme, COLORS

st.set_page_config(page_title="Portfolio Simulation", page_icon="💼", layout="wide")
inject_theme()

st.markdown('<h1>Portfolio Simulation</h1>', unsafe_allow_html=True)
st.markdown(
    f'<p style="color:{COLORS["text_secondary"]};font-size:0.78rem;letter-spacing:0.06em;'
    f'margin-bottom:20px;">Mean-Variance Optimization · Max Sharpe · Min Variance · Efficient Frontier</p>',
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
    default=sorted(df_full['COUNTRY'].unique())[:PORTFOLIO_SIMULATION_DEFAULT_N_ASSETS],
)
product = st.sidebar.selectbox("Product", ['diesel_usd', 'gasoline_usd'])
start   = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
end     = st.sidebar.date_input("End Date",   pd.to_datetime("2024-12-01"))

# ── Build returns matrix ──────────────────────────────────────
dfs = []
for c in countries:
    df_temp = filter_data_by_selection(
        df_full, countries=[c], products=[product],
        start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d"),
    )
    if not df_temp.empty:
        s = df_temp.set_index('date')[[product]]
        s = np.log(s / s.shift(1))
        s.columns = [c]
        dfs.append(s)

if not dfs:
    st.warning("No data available for the selected filters.")
    st.stop()

returns = pd.concat(dfs, axis=1).dropna()

if returns.empty:
    st.error("Insufficient data after aligning dates.")
    st.stop()

# ── Optimization ─────────────────────────────────────────────
def perf(w):
    ret = returns.mean().dot(w) * 12
    vol = np.sqrt(w.T @ returns.cov().values @ w) * np.sqrt(12)
    return ret, vol

def neg_sharpe(w):
    r, v = perf(w)
    return -(r / v) if v != 0 else 0

def min_vol(w):
    return perf(w)[1]

n    = len(returns.columns)
w0   = np.ones(n) / n
bnds = [(0, 1)] * n
cons = {'type': 'eq', 'fun': lambda w: w.sum() - 1}

res_sharpe = minimize(neg_sharpe, w0, bounds=bnds, constraints=cons)
res_minvar = minimize(min_vol,    w0, bounds=bnds, constraints=cons)

sharpe_ok = res_sharpe.success
minvar_ok = res_minvar.success

w_sharpe = res_sharpe.x if sharpe_ok else w0
w_minvar = res_minvar.x if minvar_ok else w0

ret_s, vol_s = perf(w_sharpe)
ret_m, vol_m = perf(w_minvar)

# ── Metrics ──────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Max Sharpe — Return (ann.)", f"{ret_s*100:.2f}%")
c2.metric("Max Sharpe — Vol (ann.)",    f"{vol_s*100:.2f}%")
c3.metric("Min Var — Return (ann.)",    f"{ret_m*100:.2f}%")
c4.metric("Min Var — Vol (ann.)",       f"{vol_m*100:.2f}%")

st.divider()

# ── Efficient frontier (Monte Carlo) ─────────────────────────
np.random.seed(42)
n_sim = 600
sims_ret, sims_vol = [], []
for _ in range(n_sim):
    rw = np.random.dirichlet(np.ones(n))
    r, v = perf(rw)
    sims_ret.append(r)
    sims_vol.append(v)

# ── Charts ───────────────────────────────────────────────────
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=("Efficient Frontier (Monte Carlo)", "Portfolio Weights Comparison"),
    specs=[[{"type": "scatter"}, {"type": "bar"}]],
)

# Frontier scatter
sharpe_vals = [r / v if v > 0 else 0 for r, v in zip(sims_ret, sims_vol)]
fig.add_trace(go.Scatter(
    x=sims_vol, y=sims_ret, mode='markers',
    name="Random Portfolios",
    marker=dict(size=4, color=sharpe_vals,
                colorscale=[[0, COLORS["bg_elevated"]], [1, COLORS["amber"]]],
                opacity=0.6, showscale=False),
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=[vol_s], y=[ret_s], mode='markers+text',
    name="Max Sharpe",
    marker=dict(size=12, symbol='diamond', color=COLORS["amber"],
                line=dict(color=COLORS["amber_bright"], width=2)),
    text=["Max Sharpe"], textposition="top right",
    textfont=dict(color=COLORS["amber"], size=10),
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=[vol_m], y=[ret_m], mode='markers+text',
    name="Min Variance",
    marker=dict(size=12, symbol='star', color="#2E6DA4",
                line=dict(color="#5AADDC", width=2)),
    text=["Min Var"], textposition="top right",
    textfont=dict(color="#5AADDC", size=10),
), row=1, col=1)

# Weight bars
fig.add_trace(go.Bar(
    x=returns.columns, y=w_sharpe * 100,
    name="Max Sharpe Weights",
    marker_color=COLORS["amber"], opacity=0.85,
), row=1, col=2)
fig.add_trace(go.Bar(
    x=returns.columns, y=w_minvar * 100,
    name="Min Var Weights",
    marker_color="#2E6DA4", opacity=0.75,
), row=1, col=2)

fig.update_xaxes(title_text="Annualized Volatility", row=1, col=1)
fig.update_yaxes(title_text="Annualized Return",     row=1, col=1)
fig.update_yaxes(title_text="Weight (%)",            row=1, col=2)
fig.update_layout(height=480, barmode='group')
apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True)

# ── Cumulative returns chart ──────────────────────────────────
st.divider()
st.markdown('<h2>Cumulative Returns — Individual Assets</h2>', unsafe_allow_html=True)

cum_ret = (1 + returns).cumprod() - 1
palette = [COLORS["amber"], "#2E6DA4", COLORS["green_signal"], COLORS["red_signal"],
           "#7B5EA7", "#1F7A8C", "#A0522D"]

fig2 = go.Figure()
for i, col in enumerate(cum_ret.columns):
    fig2.add_trace(go.Scatter(
        x=cum_ret.index, y=cum_ret[col] * 100,
        name=col, line=dict(color=palette[i % len(palette)], width=1.5)
    ))
fig2.update_layout(height=360, xaxis_title="Date", yaxis_title="Cumulative Return (%)")
apply_plotly_theme(fig2)
st.plotly_chart(fig2, use_container_width=True)

if not sharpe_ok:
    st.warning("Max Sharpe optimization did not converge. Displaying equal-weight fallback.")
if not minvar_ok:
    st.warning("Min Variance optimization did not converge. Displaying equal-weight fallback.")
