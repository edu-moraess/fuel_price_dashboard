# pages/2_🔄_Regime_Switching.py

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
from src.bootstrap import init_session

st.set_page_config(page_title="Regime Switching", page_icon="🔄", layout="wide")
st.title("🔄 Mudança de Regime")

df_full = init_session()

st.sidebar.header("Filtros")

countries = sorted(df_full['COUNTRY'].unique())
country = st.sidebar.selectbox("País", countries)

product = st.sidebar.selectbox("Produto", ['diesel_usd', 'gasoline_usd'])

start = st.sidebar.date_input("Início", pd.to_datetime("2020-01-01"))
end = st.sidebar.date_input("Fim", pd.to_datetime("2024-12-01"))

num_regimes = st.sidebar.slider("Regimes", 2, 4, REGIME_SWITCHING_DEFAULT_REGIMES)

df_filtered = filter_data_by_selection(
    df_full,
    countries=[country],
    products=[product],
    start_date=start.strftime("%Y-%m-%d"),
    end_date=end.strftime("%Y-%m-%d")
)

if df_filtered.empty:
    st.warning("Sem dados")
    st.stop()

prices = df_filtered.set_index('date')[product]
returns = prices.pct_change().dropna()

model = MarkovRegression(returns, k_regimes=num_regimes, trend='c', switching_variance=True)
res = model.fit(disp=False)

probs = res.smoothed_marginal_probabilities

fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

fig.add_trace(go.Scatter(x=prices.index, y=prices, name="Preço"), row=1, col=1)

for i in range(num_regimes):
    fig.add_trace(go.Scatter(x=probs.index, y=probs.iloc[:, i], name=f"Regime {i+1}"), row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

st.text(res.summary())