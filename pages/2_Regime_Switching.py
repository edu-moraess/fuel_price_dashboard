# pages/2_Regime_Switching.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
import warnings
warnings.filterwarnings('ignore')

from src.load_data import filter_data_by_selection
from src.config import REGIME_SWITCHING_DEFAULT_REGIMES, REGIME_SWITCHING_PREDICTION_STEPS
from src.session import init_session
from src.theme import inject_theme, apply_plotly_theme, COLORS

st.set_page_config(page_title="Regime Switching", page_icon="🔄", layout="wide")
inject_theme()

st.markdown('<h1>Regime Switching Models</h1>', unsafe_allow_html=True)
st.markdown(
    f'<p style="color:{COLORS["text_secondary"]};font-size:0.78rem;letter-spacing:0.06em;'
    f'margin-bottom:20px;">Markov Switching · Smoothed Probabilities · Regime Classification</p>',
    unsafe_allow_html=True,
)

df_full = init_session()

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.markdown(
    f'<p style="font-size:0.68rem;letter-spacing:0.14em;color:{COLORS["text_muted"]};'
    f'text-transform:uppercase;margin-bottom:8px;">Research Parameters</p>',
    unsafe_allow_html=True,
)

countries = sorted(df_full['COUNTRY'].unique())
country     = st.sidebar.selectbox("Country", countries)
product     = st.sidebar.selectbox("Product", ['diesel_usd', 'gasoline_usd'])
start       = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end         = st.sidebar.date_input("End Date",   pd.to_datetime("2024-12-01"))
num_regimes = st.sidebar.slider("Number of Regimes", 2, 4, REGIME_SWITCHING_DEFAULT_REGIMES)

df_filtered = filter_data_by_selection(
    df_full, countries=[country], products=[product],
    start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d"),
)

if df_filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

prices  = df_filtered.set_index('date')[product]
returns = prices.pct_change().dropna()

try:
    model = MarkovRegression(returns, k_regimes=num_regimes, trend='c', switching_variance=True)
    res   = model.fit(disp=False)
    probs = res.smoothed_marginal_probabilities
except Exception as e:
    st.error(f"Model fitting error: {e}")
    st.stop()

# ── Metrics ──────────────────────────────────────────────────
dominant_regime = int(probs.iloc[-1].idxmax()) + 1
c1, c2, c3 = st.columns(3)
c1.metric("Current Dominant Regime", f"Regime {dominant_regime}")
c2.metric("Regimes Fitted", num_regimes)
c3.metric("Observations", len(returns))

st.divider()

# ── Chart ────────────────────────────────────────────────────
regime_palette = [COLORS["amber"], "#2E6DA4", COLORS["green_signal"], COLORS["red_signal"]]

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.07,
    subplot_titles=(f"Price — {country} ({product})", "Return (%)", "Smoothed Regime Probabilities"),
)

fig.add_trace(go.Scatter(
    x=prices.index, y=prices, name="Price (USD)",
    line=dict(color=COLORS["amber"], width=1.5)
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=returns.index, y=returns * 100, name="Return %",
    line=dict(color=COLORS["text_secondary"], width=1.0),
    fill='tozeroy', fillcolor=f'rgba(200,126,10,0.08)'
), row=2, col=1)

for i in range(num_regimes):
    fig.add_trace(go.Scatter(
        x=probs.index, y=probs.iloc[:, i],
        name=f"Regime {i+1}",
        stackgroup='regimes',
        line=dict(color=regime_palette[i % len(regime_palette)], width=0.8),
        fillcolor=f'rgba({int(regime_palette[i % len(regime_palette)][1:3], 16)},'
                  f'{int(regime_palette[i % len(regime_palette)][3:5], 16)},'
                  f'{int(regime_palette[i % len(regime_palette)][5:7], 16)},0.25)',
    ), row=3, col=1)

fig.update_layout(height=760)
apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown(f'<h2>Model Summary</h2>', unsafe_allow_html=True)
st.code(str(res.summary()), language=None)
