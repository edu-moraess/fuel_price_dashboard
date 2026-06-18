import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import linregress
import warnings

from src.load_data import filter_data_by_selection
from src.config import COINTEGRATION_LOOKBACK_YEARS, COINTEGRATION_ZSCORE_THRESHOLD

warnings.filterwarnings("ignore")

# =========================
# 📊 PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Cointegration Engine",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Cointegration Engine — Pairs Trading Signals")

# =========================
# 📦 DATA
# =========================
df_full = st.session_state.get("df", None)

if df_full is None:
    st.error("Dataset não carregado. Verifique o app.py.")
    st.stop()

# =========================
# 🎛️ SIDEBAR
# =========================
st.sidebar.header("Cointegration Filters")

countries_available = sorted(df_full["COUNTRY"].unique())

selected_countries = st.sidebar.multiselect(
    "Countries",
    options=countries_available,
    default=countries_available[:2]
)

products_available = ["diesel_usd", "gasoline_usd"]

selected_product = st.sidebar.selectbox(
    "Product",
    options=products_available,
    index=0
)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-01"))

lookback_years = st.sidebar.slider(
    "Rolling Window (years)",
    1, 10,
    COINTEGRATION_LOOKBACK_YEARS
)

z_threshold = st.sidebar.number_input(
    "Z-Score Threshold",
    min_value=0.1,
    max_value=5.0,
    value=COINTEGRATION_ZSCORE_THRESHOLD,
    step=0.1
)

# =========================
# 🧠 VALIDATION
# =========================
if len(selected_countries) < 2:
    st.warning("Select at least 2 countries.")
    st.stop()

# =========================
# 📊 DATA PREP
# =========================
df_filtered = filter_data_by_selection(
    df_full,
    countries=selected_countries,
    products=[selected_product],
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d")
)

if df_filtered.empty:
    st.warning("No data for selected filters.")
    st.stop()

df_pivot = df_filtered.pivot(
    index="date",
    columns="COUNTRY",
    values=selected_product
).dropna()

if df_pivot.shape[1] < 2:
    st.warning("Insufficient data after pivot.")
    st.stop()

# =========================
# 📈 CORE MODEL
# =========================
country_a, country_b = df_pivot.columns[:2]

prices_a = df_pivot[country_a]
prices_b = df_pivot[country_b]

slope, intercept, r_value, p_value, std_err = linregress(prices_a, prices_b)

spread = prices_b - (slope * prices_a + intercept)

window = lookback_years * 12

spread_mean = spread.rolling(window=window, min_periods=1).mean()
spread_std = spread.rolling(window=window, min_periods=1).std()

z_score = (spread - spread_mean) / spread_std

long_signal = z_score < -z_threshold
short_signal = z_score > z_threshold

# =========================
# 📊 PLOT
# =========================
fig = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.08,
    subplot_titles=(
        f"Prices: {country_a} vs {country_b}",
        "Spread",
        "Z-Score (Mean Reversion Signals)"
    )
)

# Prices
fig.add_trace(
    go.Scatter(x=df_pivot.index, y=prices_a, name=country_a),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(x=df_pivot.index, y=prices_b, name=country_b),
    row=1, col=1
)

# Spread
fig.add_trace(
    go.Scatter(x=df_pivot.index, y=spread, name="Spread", line=dict(color="orange")),
    row=2, col=1
)

# Z-score
fig.add_trace(
    go.Scatter(x=df_pivot.index, y=z_score, name="Z-Score", line=dict(color="red")),
    row=3, col=1
)

# Signals
fig.add_trace(
    go.Scatter(
        x=df_pivot.index[long_signal],
        y=z_score[long_signal],
        mode="markers",
        name="Long",
        marker=dict(symbol="triangle-up", size=10, color="green")
    ),
    row=3, col=1
)

fig.add_trace(
    go.Scatter(
        x=df_pivot.index[short_signal],
        y=z_score[short_signal],
        mode="markers",
        name="Short",
        marker=dict(symbol="triangle-down", size=10, color="red")
    ),
    row=3, col=1
)

# Threshold lines (safe version)
fig.add_shape(
    type="line",
    x0=df_pivot.index[0],
    x1=df_pivot.index[-1],
    y0=z_threshold,
    y1=z_threshold,
    line=dict(color="red", dash="dash"),
    row=3, col=1
)

fig.add_shape(
    type="line",
    x0=df_pivot.index[0],
    x1=df_pivot.index[-1],
    y0=-z_threshold,
    y1=-z_threshold,
    line=dict(color="red", dash="dash"),
    row=3, col=1
)

fig.add_shape(
    type="line",
    x0=df_pivot.index[0],
    x1=df_pivot.index[-1],
    y0=0,
    y1=0,
    line=dict(color="gray")
)

fig.update_layout(
    height=850,
    title=f"Cointegration Signal: {country_a} vs {country_b}",
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 📊 STATS
# =========================
st.subheader("Model Diagnostics")

col1, col2, col3 = st.columns(3)

col1.metric("Beta", f"{slope:.4f}")
col2.metric("Correlation", f"{r_value:.4f}")
col3.metric("P-value", f"{p_value:.6f}")

st.write(f"Intercept: {intercept:.4f}")
st.write(f"Rolling window: {lookback_years} years ({window} months)")
st.write(f"Z threshold: ±{z_threshold}")

# =========================
# 📥 EXPORT
# =========================
results_df = pd.DataFrame({
    "date": df_pivot.index,
    f"{country_a}_{selected_product}": prices_a.values,
    f"{country_b}_{selected_product}": prices_b.values,
    "spread": spread.values,
    "z_score": z_score.values,
    "long_signal": long_signal.astype(int).values,
    "short_signal": short_signal.astype(int).values
})

st.download_button(
    "Download Data",
    data=results_df.to_csv(index=False).encode("utf-8"),
    file_name=f"cointegration_{country_a}_{country_b}.csv",
    mime="text/csv"
)