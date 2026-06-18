import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
import warnings

from src.load_data import filter_data_by_selection
from src.config import REGIME_SWITCHING_DEFAULT_REGIMES, REGIME_SWITCHING_PREDICTION_STEPS

warnings.filterwarnings("ignore")

# =========================
# 📊 PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Regime Switching Engine",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Regime Switching Engine — Market State Detection")

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
st.sidebar.header("Regime Filters")

countries_available = sorted(df_full["COUNTRY"].unique())

selected_country = st.sidebar.selectbox(
    "Country",
    options=countries_available,
    index=0
)

products_available = ["diesel_usd", "gasoline_usd"]

selected_product = st.sidebar.selectbox(
    "Product",
    options=products_available,
    index=0
)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-01"))

num_regimes = st.sidebar.slider(
    "Number of Regimes",
    2, 4,
    REGIME_SWITCHING_DEFAULT_REGIMES
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
returns = prices.pct_change().dropna()

# Alinhamento seguro
returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
prices = prices.loc[returns.index]

# =========================
# 🧠 MODEL
# =========================
try:
    model = MarkovRegression(
        returns,
        k_regimes=num_regimes,
        trend="c",
        switching_variance=True
    )

    res = model.fit(disp=False)

    probs = res.smoothed_marginal_probabilities

    # garantir DataFrame
    if isinstance(probs, np.ndarray):
        probs = pd.DataFrame(
            probs,
            index=returns.index,
            columns=[f"Regime {i+1}" for i in range(num_regimes)]
        )

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
            "Returns",
            "Regime Probabilities"
        )
    )

    # Price
    fig.add_trace(
        go.Scatter(x=prices.index, y=prices.values, name="Price"),
        row=1, col=1
    )

    # Returns
    fig.add_trace(
        go.Scatter(x=returns.index, y=returns.values, name="Returns"),
        row=2, col=1
    )

    # Regimes
    for i in range(num_regimes):
        fig.add_trace(
            go.Scatter(
                x=probs.index,
                y=probs.iloc[:, i],
                name=f"Regime {i+1}"
            ),
            row=3, col=1
        )

    fig.update_layout(
        height=850,
        title=f"Regime Switching Model — {selected_country} ({selected_product})",
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 📊 MODEL OUTPUT
    # =========================
    st.subheader("Model Summary")
    st.text(res.summary())

    # =========================
    # 📥 EXPORT
    # =========================
    results_df = pd.DataFrame({
        "date": returns.index,
        "price": prices.values,
        "return": returns.values
    })

    for i in range(num_regimes):
        results_df[f"regime_{i+1}_prob"] = probs.iloc[:, i].values

    st.download_button(
        "Download Results",
        data=results_df.to_csv(index=False).encode("utf-8"),
        file_name=f"regime_switching_{selected_country}_{selected_product}.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Model error: {str(e)}")
    st.info("Try reducing number of regimes or checking data quality.")