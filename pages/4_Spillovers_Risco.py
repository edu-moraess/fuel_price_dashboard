import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.vector_ar.var_model import VAR
import warnings

from src.load_data import filter_data_by_selection
from src.config import RISK_SPILLOVER_VAR_LAGS

warnings.filterwarnings("ignore")

# =========================
# 📊 PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Risk Spillover Engine",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 Risk Spillover Engine — Market Connectedness")

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
st.sidebar.header("Spillover Filters")

countries = sorted(df_full["COUNTRY"].unique())

selected_countries = st.sidebar.multiselect(
    "Countries",
    options=countries,
    default=countries[:3]
)

product = st.sidebar.selectbox(
    "Product",
    ["diesel_usd", "gasoline_usd"],
    index=0
)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-01"))

lags = st.sidebar.slider(
    "VAR Lags",
    1, 5,
    RISK_SPILLOVER_VAR_LAGS
)

# =========================
# 📊 DATA PREP
# =========================
if len(selected_countries) < 2:
    st.warning("Select at least 2 countries.")
    st.stop()

df_filtered = filter_data_by_selection(
    df_full,
    countries=selected_countries,
    products=[product],
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d")
)

if df_filtered.empty:
    st.warning("No data available.")
    st.stop()

df_pivot = df_filtered.pivot(
    index="date",
    columns="COUNTRY",
    values=product
).dropna()

# =========================
# 📈 RETURNS
# =========================
returns = np.log(df_pivot / df_pivot.shift(1)).dropna()
returns = returns.replace([np.inf, -np.inf], np.nan).dropna()

scaler = StandardScaler()
returns_scaled = pd.DataFrame(
    scaler.fit_transform(returns),
    index=returns.index,
    columns=returns.columns
)

# =========================
# 🧠 VAR MODEL
# =========================
try:
    model = VAR(returns_scaled)
    results = model.fit(lags)

    # =========================
    # 📊 RETURNS PLOT
    # =========================
    fig1 = go.Figure()

    for col in returns.columns:
        fig1.add_trace(
            go.Scatter(x=returns.index, y=returns[col], name=col)
        )

    fig1.update_layout(
        title="Log Returns",
        height=400
    )

    st.plotly_chart(fig1, use_container_width=True)

    # =========================
    # 🔥 CORRELATION HEATMAP
    # =========================
    corr = returns.corr()

    fig2 = px.imshow(
        corr,
        text_auto=True,
        title="Correlation Matrix (Risk Spillovers Proxy)"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # 🌐 SIMPLE NETWORK VIEW
    # =========================
    threshold = 0.2
    nodes = list(corr.columns)

    edges = []

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            w = abs(corr.iloc[i, j])
            if w > threshold:
                edges.append((i, j, w))

    if edges:
        fig3 = go.Figure()

        for i, j, w in edges:
            fig3.add_trace(
                go.Scatter(
                    x=[nodes[i], nodes[j]],
                    y=[w, w],
                    mode="lines+markers",
                    line=dict(width=w * 5),
                    name=f"{nodes[i]}-{nodes[j]}"
                )
            )

        fig3.update_layout(
            title="Risk Connectivity Network (Correlation Filtered)",
            height=400
        )

        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No strong spillover connections found.")

    # =========================
    # 📊 MODEL OUTPUT
    # =========================
    st.subheader("VAR Model Summary")
    st.text(results.summary())

    # =========================
    # 📥 EXPORT
    # =========================
    export_df = returns.copy()
    export_df.columns = [f"log_return_{c}" for c in export_df.columns]

    st.download_button(
        "Download Returns",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name=f"spillovers_{product}.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"VAR model error: {str(e)}")
    st.info("Try reducing number of countries or VAR lags.")