# pages/5_💼_Sim_Portfolio.py

import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import minimize

from src.load_data import filter_data_by_selection
from src.config import PORTFOLIO_SIMULATION_DEFAULT_N_ASSETS
from src.session import init_session

st.set_page_config(page_title="Portfolio", page_icon="💼", layout="wide")
st.title("💼 Simulação de Portfólio")

df_full = init_session()

st.sidebar.header("Seleção")

countries = st.sidebar.multiselect(
    "Países",
    sorted(df_full['COUNTRY'].unique()),
    default=sorted(df_full['COUNTRY'].unique())[:PORTFOLIO_SIMULATION_DEFAULT_N_ASSETS]
)

product = st.sidebar.selectbox("Produto", ['diesel_usd', 'gasoline_usd'])

start = st.sidebar.date_input("Início")
end = st.sidebar.date_input("Fim")

dfs = []

for c in countries:
    df_temp = filter_data_by_selection(
        df_full,
        countries=[c],
        products=[product],
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d")
    )

    if not df_temp.empty:
        df_temp = df_temp.set_index('date')[[product]]
        df_temp = np.log(df_temp / df_temp.shift(1))
        df_temp.columns = [c]
        dfs.append(df_temp)

if not dfs:
    st.warning("Sem dados")
    st.stop()

returns = pd.concat(dfs, axis=1).dropna()

if returns.empty:
    st.error("Dados insuficientes para otimização de portfólio após alinhar as datas.")
    st.stop()

def perf(w):
    ret = returns.mean().dot(w) * 12
    vol = np.sqrt(w.T @ (returns.cov().values) @ w) * np.sqrt(12)
    return ret, vol

def sharpe(w):
    r, v = perf(w)
    if v == 0: return 0
    return -(r / v)

n = len(returns.columns)
w0 = np.ones(n) / n

try:
    res = minimize(sharpe, w0, bounds=[(0,1)]*n, constraints={'type':'eq','fun':lambda w: w.sum()-1})
    if res.success:
        st.write("Pesos ótimos:", pd.Series(res.x, index=returns.columns))
    else:
        st.error("A otimização não convergiu.")
except Exception as e:
    st.error(f"Erro na otimização: {e}")