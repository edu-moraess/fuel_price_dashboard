# pages/1_📊_Cointegracao.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')

from src.load_data import filter_data_by_selection
from src.config import COINTEGRATION_LOOKBACK_YEARS, COINTEGRATION_ZSCORE_THRESHOLD
from src.session import init_session

# --- Configuração da Página ---
st.set_page_config(page_title="Cointegração", page_icon="📊", layout="wide")
st.title("📊 Análise de Cointegração - Pairs Trading Potencial")

# --- Data (FIX) ---
df_full = init_session()

# --- Sidebar ---
st.sidebar.header("Filtros - Cointegração")

countries_available = sorted(df_full['COUNTRY'].unique())
selected_countries_coint = st.sidebar.multiselect(
    "Países",
    options=countries_available,
    default=countries_available[:2]
)

products_available = ['diesel_usd', 'gasoline_usd']
selected_product_coint = st.sidebar.selectbox("Produto", options=products_available, index=0)

start_date_coint = st.sidebar.date_input("Data Início", value=pd.to_datetime("2020-01-01"))
end_date_coint = st.sidebar.date_input("Data Fim", value=pd.to_datetime("2024-12-01"))

lookback_years = st.sidebar.slider(
    "Janela Histórica (anos)",
    min_value=1,
    max_value=10,
    value=COINTEGRATION_LOOKBACK_YEARS
)

z_threshold = st.sidebar.number_input(
    "Threshold Z-Score",
    min_value=0.1,
    max_value=5.0,
    value=COINTEGRATION_ZSCORE_THRESHOLD,
    step=0.1
)

# --- Lógica ---
if len(selected_countries_coint) < 2:
    st.warning("Selecione pelo menos 2 países para análise de cointegração.")
else:

    df_filtered = filter_data_by_selection(
        df_full,
        countries=selected_countries_coint,
        products=[selected_product_coint],
        start_date=start_date_coint.strftime("%Y-%m-%d"),
        end_date=end_date_coint.strftime("%Y-%m-%d")
    )

    if df_filtered.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:

        df_pivot = df_filtered.pivot(index='date', columns='COUNTRY', values=selected_product_coint)
        df_pivot.dropna(inplace=True)

        if df_pivot.shape[1] < 2:
            st.warning("Dados insuficientes após pivot.")
        else:

            country_a, country_b = df_pivot.columns[0], df_pivot.columns[1]
            prices_a = df_pivot[country_a]
            prices_b = df_pivot[country_b]

            try:
                slope, intercept, r_value, p_value, std_err = linregress(prices_a, prices_b)
                spread = prices_b - (slope * prices_a + intercept)
            except Exception as e:
                st.error(f"Erro na regressão linear: {e}")
                st.stop()

            spread_mean = spread.rolling(window=lookback_years * 12, min_periods=1).mean()
            spread_std = spread.rolling(window=lookback_years * 12, min_periods=1).std()
            z_score = (spread - spread_mean) / spread_std

            long_signal = z_score < -z_threshold
            short_signal = z_score > z_threshold

            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                subplot_titles=(f'Preços: {country_a} vs {country_b}', 'Spread', 'Z-Score')
            )

            fig.add_trace(go.Scatter(x=df_pivot.index, y=prices_a, name=country_a), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_pivot.index, y=prices_b, name=country_b), row=1, col=1)

            fig.add_trace(go.Scatter(x=df_pivot.index, y=spread, name='Spread'), row=2, col=1)

            fig.add_trace(go.Scatter(x=df_pivot.index, y=z_score, name='Z-Score'), row=3, col=1)

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Resultados")
            st.write(f"Beta: {slope:.4f}")
            st.write(f"Intercepto: {intercept:.4f}")
            st.write(f"Correlação: {r_value:.4f}")