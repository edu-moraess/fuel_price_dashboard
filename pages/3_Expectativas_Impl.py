import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.load_data import filter_data_by_selection
from src.config import IMPLIED_EXPECT_SHORT_WINDOW, IMPLIED_EXPECT_LONG_WINDOW

# =========================
# 📊 PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Expectation Index Engine",
    page_icon="🔮",
    layout="wide"
)

st.title("🔮 Expectation Index Engine — Market Sentiment Proxy")

# =========================
# 📦 DATA
# =========================
df_full = st.session_state.get("df", None)

if df_full is None:
    st.error("Dataset não carregado. Verifique app.py.")
    st.stop()

# =========================
# 🎛️ SIDEBAR
# =========================
st.sidebar.header("Expectation Filters")

countries = sorted(df_full["COUNTRY"].unique())

selected_country = st.sidebar.selectbox(
    "Country",
    options=countries,
    index=0
)

products = ["diesel_usd", "gasoline_usd"]

selected_product = st.sidebar.selectbox(
    "Product",
    options=products,
    index=0
)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-01"))

short_window = st.sidebar.slider(
    "Short Window (months)",
    1, 24,
    IMPLIED_EXPECT_SHORT_WINDOW
)

long_window = st.sidebar.slider(
    "Long Window (months)",
    6, 60,
    IMPLIED_EXPECT_LONG_WINDOW
)

# =========================
# 📊 DATA PREP
# =========================
df_filtered = filter_data_by_selection(
    df_full,
    countries=[selected_country],
    products=[selected_product],
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d")
)

if df_filtered.empty:
    st.warning("No data for selected filters.")
    st.stop()

prices = df_filtered.set_index("date")[selected_product].dropna()

# =========================
# 📈 FEATURES
# =========================
ma_short = prices.rolling(short_window, min_periods=1).mean()
ma_long = prices.rolling(long_window, min_periods=1).mean()

spread_ma = ma_short - ma_long

spread_vol = spread_ma.rolling(long_window, min_periods=1).std()

expectation_index = spread_ma / (spread_vol + 1e-8)

# robust trimming (evita lixo inicial)
expectation_index = expectation_index.replace([np.inf, -np.inf], np.nan).fillna(0)

perc_high = expectation_index.rolling(long_window * 2, min_periods=5).quantile(0.8)
perc_low = expectation_index.rolling(long_window * 2, min_periods=5).quantile(0.2)

# =========================
# 📊 PLOT
# =========================
fig = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.08,
    subplot_titles=(
        f"Price - {selected_country}",
        f"Moving Averages ({short_window} vs {long_window})",
        "Expectation Index"
    )
)

# Price
fig.add_trace(
    go.Scatter(x=prices.index, y=prices, name="Price"),
    row=1, col=1
)

# MAs
fig.add_trace(
    go.Scatter(x=prices.index, y=ma_short, name="Short MA"),
    row=2, col=1
)

fig.add_trace(
    go.Scatter(x=prices.index, y=ma_long, name="Long MA"),
    row=2, col=1
)

# Index
fig.add_trace(
    go.Scatter(x=prices.index, y=expectation_index, name="Expectation Index"),
    row=3, col=1
)

fig.add_trace(
    go.Scatter(x=prices.index, y=perc_high, name="80% Threshold", line=dict(dash="dash")),
    row=3, col=1
)

fig.add_trace(
    go.Scatter(x=prices.index, y=perc_low, name="20% Threshold", line=dict(dash="dash")),
    row=3, col=1
)

fig.add_hline(y=0, line_color="gray", row=3, col=1)

fig.update_layout(
    height=850,
    title=f"Expectation Index — {selected_country} ({selected_product})",
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 📊 METRICS
# =========================
st.subheader("Latest Signals")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Price", f"{prices.iloc[-1]:.4f}")
col2.metric("Short MA", f"{ma_short.iloc[-1]:.4f}")
col3.metric("Long MA", f"{ma_long.iloc[-1]:.4f}")
col4.metric("Index", f"{expectation_index.iloc[-1]:.4f}")

# =========================
# 📥 EXPORT
# =========================
results_df = pd.DataFrame({
    "date": prices.index,
    "price": prices.values,
    "ma_short": ma_short.values,
    "ma_long": ma_long.values,
    "spread_ma": spread_ma.values,
    "expectation_index": expectation_index.values,
    "perc_high": perc_high.values,
    "perc_low": perc_low.values
})

st.download_button(
    "Download Data",
    data=results_df.to_csv(index=False).encode("utf-8"),
    file_name=f"expectation_index_{selected_country}_{selected_product}.csv",
    mime="text/csv"
)