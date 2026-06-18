# pages/3_🔮_Expectativas_Impl.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.load_data import filter_data_by_selection
from src.config import IMPLIED_EXPECT_SHORT_WINDOW, IMPLIED_EXPECT_LONG_WINDOW
from src.bootstrap import init_session

st.set_page_config(page_title="Expectativas Implícitas", page_icon="🔮", layout="wide")
st.title("🔮 Expectativas Implícitas")

df_full = init_session()

st.sidebar.header("Filtros")

country = st.sidebar.selectbox("País", sorted(df_full['COUNTRY'].unique()))
product = st.sidebar.selectbox("Produto", ['diesel_usd', 'gasoline_usd'])

start = st.sidebar.date_input("Início")
end = st.sidebar.date_input("Fim")

short_w = st.sidebar.slider("Curta", 1, 24, IMPLIED_EXPECT_SHORT_WINDOW)
long_w = st.sidebar.slider("Longa", 6, 60, IMPLIED_EXPECT_LONG_WINDOW)

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

ma_short = prices.rolling(short_w).mean()
ma_long = prices.rolling(long_w).mean()

spread = ma_short - ma_long
index = spread / (spread.rolling(long_w).std() + 1e-8)

fig = make_subplots(rows=2, cols=1)

fig.add_trace(go.Scatter(x=prices.index, y=prices, name="Preço"), row=1, col=1)
fig.add_trace(go.Scatter(x=prices.index, y=index, name="Índice"), row=2, col=1)

st.plotly_chart(fig, use_container_width=True)