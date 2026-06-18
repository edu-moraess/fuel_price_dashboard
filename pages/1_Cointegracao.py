# pages/1_Cointegracao.py

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
from src.theme import inject_theme, apply_plotly_theme, section_header, COLORS

st.set_page_config(page_title="Cointegration Analysis", page_icon="📊", layout="wide")
inject_theme()

st.markdown('<h1>Cointegration Analysis</h1>', unsafe_allow_html=True)
st.markdown(
    f'<p style="color:{COLORS["text_secondary"]};font-size:0.78rem;letter-spacing:0.06em;'
    f'margin-bottom:20px;">Pairs Trading · Spread Dynamics · Z-Score Signals</p>',
    unsafe_allow_html=True,
)

df_full = init_session()

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.markdown(
    f'<p style="font-size:0.68rem;letter-spacing:0.14em;color:{COLORS["text_muted"]};'
    f'text-transform:uppercase;margin-bottom:8px;">Research Parameters</p>',
    unsafe_allow_html=True,
)

countries_available = sorted(df_full['COUNTRY'].unique())
selected_countries_coint = st.sidebar.multiselect(
    "Countries",
    options=countries_available,
    default=countries_available[:2]
)

products_available = ['diesel_usd', 'gasoline_usd']
selected_product_coint = st.sidebar.selectbox("Product", options=products_available, index=0)

start_date_coint = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date_coint   = st.sidebar.date_input("End Date",   value=pd.to_datetime("2024-12-01"))

lookback_years = st.sidebar.slider("Lookback Window (years)", 1, 10, COINTEGRATION_LOOKBACK_YEARS)
z_threshold    = st.sidebar.number_input("Z-Score Threshold", 0.1, 5.0, COINTEGRATION_ZSCORE_THRESHOLD, 0.1)

# ── Analysis ─────────────────────────────────────────────────
if len(selected_countries_coint) < 2:
    st.warning("Select at least 2 countries for cointegration analysis.")
else:
    df_filtered = filter_data_by_selection(
        df_full,
        countries=selected_countries_coint,
        products=[selected_product_coint],
        start_date=start_date_coint.strftime("%Y-%m-%d"),
        end_date=end_date_coint.strftime("%Y-%m-%d"),
    )

    if df_filtered.empty:
        st.warning("No data found for the selected filters.")
    else:
        df_pivot = df_filtered.pivot(index='date', columns='COUNTRY', values=selected_product_coint)
        df_pivot.dropna(inplace=True)

        if df_pivot.shape[1] < 2:
            st.warning("Insufficient data after pivot.")
        else:
            country_a, country_b = df_pivot.columns[0], df_pivot.columns[1]
            prices_a = df_pivot[country_a]
            prices_b = df_pivot[country_b]

            try:
                slope, intercept, r_value, p_value, std_err = linregress(prices_a, prices_b)
                spread = prices_b - (slope * prices_a + intercept)
            except Exception as e:
                st.error(f"Regression error: {e}")
                st.stop()

            spread_mean = spread.rolling(window=lookback_years * 12, min_periods=1).mean()
            spread_std  = spread.rolling(window=lookback_years * 12, min_periods=1).std()
            z_score     = (spread - spread_mean) / spread_std

            long_signal  = z_score < -z_threshold
            short_signal = z_score > z_threshold

            # ── Metrics row ───────────────────────────────────
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Beta (β)", f"{slope:.4f}")
            c2.metric("Intercept", f"{intercept:.4f}")
            c3.metric("Correlation (r)", f"{r_value:.4f}")
            c4.metric("Current Z-Score", f"{z_score.iloc[-1]:.2f}")

            st.divider()

            # ── Chart ─────────────────────────────────────────
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.07,
                subplot_titles=(
                    f"Price Series — {country_a} vs {country_b}",
                    "Cointegrated Spread",
                    "Spread Z-Score"
                ),
            )

            fig.add_trace(go.Scatter(
                x=df_pivot.index, y=prices_a, name=country_a,
                line=dict(color=COLORS["amber"], width=1.5)
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df_pivot.index, y=prices_b, name=country_b,
                line=dict(color="#2E6DA4", width=1.5)
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df_pivot.index, y=spread, name="Spread",
                line=dict(color=COLORS["text_secondary"], width=1.2)
            ), row=2, col=1)

            fig.add_trace(go.Scatter(
                x=df_pivot.index, y=z_score, name="Z-Score",
                line=dict(color=COLORS["amber"], width=1.2)
            ), row=3, col=1)

            for level, color in [(z_threshold, COLORS["red_signal"]), (-z_threshold, COLORS["green_signal"])]:
                fig.add_hline(y=level, line_dash="dash", line_color=color, line_width=1, row=3, col=1)
            fig.add_hline(y=0, line_dash="dot", line_color=COLORS["border"], line_width=1, row=3, col=1)

            if long_signal.any():
                fig.add_scatter(
                    x=df_pivot.index[long_signal], y=z_score[long_signal],
                    mode='markers', name='Long Signal',
                    marker=dict(symbol='triangle-up', size=8, color=COLORS["green_signal"]),
                    row=3, col=1
                )
            if short_signal.any():
                fig.add_scatter(
                    x=df_pivot.index[short_signal], y=z_score[short_signal],
                    mode='markers', name='Short Signal',
                    marker=dict(symbol='triangle-down', size=8, color=COLORS["red_signal"]),
                    row=3, col=1
                )

            fig.update_layout(height=760)
            apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
