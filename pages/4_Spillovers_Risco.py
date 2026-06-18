# pages/4_🔗_Spillovers_Risco.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.vector_ar.var_model import VAR

from src.load_data import filter_data_by_selection
from src.config import RISK_SPILLOVER_VAR_LAGS
from src.bootstrap import init_session

st.set_page_config(page_title="Spillovers", page_icon="🔗", layout="wide")
st.title("🔗 Spillovers de Risco")

df_full = init_session()

st.sidebar.header("Filtros")

countries = st.sidebar.multiselect(
    "Países",
    sorted(df_full['COUNTRY'].unique()),
    default=sorted(df_full['COUNTRY'].unique())[:3]
)

product = st.sidebar.selectbox("Produto", ['diesel_usd', 'gasoline_usd'])

start = st.sidebar.date_input("Início")
end = st.sidebar.date_input("Fim")

lags = st.sidebar.slider("Lags VAR", 1, 5, RISK_SPILLOVER_VAR_LAGS)

df_filtered = filter_data_by_selection(
    df_full,
    countries=countries,
    products=[product],
    start_date=start.strftime("%Y-%m-%d"),
    end_date=end.strftime("%Y-%m-%d")
)

if df_filtered.empty:
    st.warning("Sem dados")
    st.stop()

pivot = df_filtered.pivot(index='date', columns='COUNTRY', values=product).dropna()

returns = np.log(pivot).diff().dropna()

model = VAR(returns)
res = model.fit(lags)

st.text(res.summary())