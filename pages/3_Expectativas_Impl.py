# pages/3_Expectativas_Impl.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.load_data import filter_data_by_selection
from src.config import IMPLIED_EXPECT_SHORT_WINDOW, IMPLIED_EXPECT_LONG_WINDOW
from src.session import init_session
from src.theme import inject_theme, apply_plotly_theme, COLORS

st.set_page_config(page_title="Implied Expectations", page_icon="🔮", layout="wide")
inject_theme()

st.markdown('<h1>Implied Expectations</h1>', unsafe_allow_html=True)
st.markdown(
    f'<p style="color:{COLORS["text_secondary"]};font-size:0.78rem;letter-spacing:0.06em;'
    f'margin-bottom:20px;">Moving Average Signals · Expectation Index · Momentum Detection</p>',
    unsafe_allow_html=True,
)

df_full = init_session()

st.sidebar.markdown(
    f'<p style="font-size:0.68rem;letter-spacing:0.14em;color:{COLORS["text_muted"]};'
    f'text-transform:uppercase;margin-bottom:8px;">Research Parameters</p>',
    unsafe_allow_html=True,
)

country = st.sidebar.selectbox("Country", sorted(df_full['COUNTRY'].unique()))
product = st.sidebar.selectbox("Product", ['diesel_usd', 'gasoline_usd'])
start   = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
end     = st.sidebar.date_input("End Date",   pd.to_datetime("2024-12-01"))
short_w = st.sidebar.slider("Short Window (months)", 1, 24, IMPLIED_EXPECT_SHORT_WINDOW)
long_w  = st.sidebar.slider("Long Window (months)",  6, 60, IMPLIED_EXPECT_LONG_WINDOW)

df_filtered = filter_data_by_selection(
    df_full, countries=[country], products=[product],
    start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d"),
)

if df_filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

prices   = df_filtered.set_index('date')[product]
ma_short = prices.rolling(short_w).mean()
ma_long  = prices.rolling(long_w).mean()
spread   = ma_short - ma_long
index    = spread / (spread.rolling(long_w).std() + 1e-8)

c1, c2, c3 = st.columns(3)
c1.metric("Current Price (USD)", f"{prices.iloc[-1]:.3f}")
c2.metric("Expectation Index", f"{index.iloc[-1]:.3f}")
c3.metric(f"MA Spread ({short_w}m - {long_w}m)", f"{spread.iloc[-1]:.3f}")

st.divider()

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.07,
    subplot_titles=(
        f"Price — {country} ({product})",
        f"Moving Averages ({short_w}m / {long_w}m)",
        "Expectation Index (Normalized Spread)",
    ),
)

fig.add_trace(go.Scatter(
    x=prices.index, y=prices, name="Price (USD)",
    line=dict(color=COLORS["text_primary"], width=1.5)
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=prices.index, y=ma_short, name=f"MA {short_w}m",
    line=dict(color=COLORS["amber"], width=1.5)
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=prices.index, y=ma_long, name=f"MA {long_w}m",
    line=dict(color="#2E6DA4", width=1.5)
), row=2, col=1)

fig.add_trace(go.Scatter(
    x=prices.index, y=index, name="Expectation Index",
    line=dict(color=COLORS["amber"], width=1.3),
    fill='tozeroy', fillcolor='rgba(200,126,10,0.08)',
), row=3, col=1)
fig.add_hline(y=0, line_dash="dot", line_color=COLORS["border"], line_width=1, row=3, col=1)

fig.update_layout(height=760)
apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True)
