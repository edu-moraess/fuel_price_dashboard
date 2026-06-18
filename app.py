import streamlit as st
import pandas as pd
from src.load_data import load_and_preprocess_data
from src.config import DATA_PATH

# =========================
# 🔧 CONFIGURAÇÃO GLOBAL
# =========================
st.set_page_config(
    page_title="ETIL Macro Intelligence Terminal",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# 🧠 HEADER (IDENTIDADE DO SISTEMA)
# =========================
st.markdown(
    """
    # ⛽ ETIL Macro Intelligence Terminal
    ### Fuel Prices • Regimes • Cointegration • Risk Signals • Macro Quant Research
    """
)

st.divider()

# =========================
# 📦 DATA LAYER
# =========================
@st.cache_data
def get_data():
    df = load_and_preprocess_data(DATA_PATH)
    return df

df = get_data()

if "df" not in st.session_state:
    st.session_state["df"] = df

# =========================
# 📊 SIDEBAR (RESEARCH DESK STYLE)
# =========================
st.sidebar.markdown("## 🧭 Research Desk")
st.sidebar.caption("ETIL System Controls")

st.sidebar.divider()

st.sidebar.markdown("### Modules")

st.sidebar.markdown(
"""
- 📊 Cointegration Analysis  
- 🔄 Regime Switching Models  
- 🔮 Expectations & Signals  
- 🔗 Spillovers & Risk Propagation  
- 💼 Portfolio Simulation  
"""
)

st.sidebar.divider()

st.sidebar.markdown("### System Status")

if not df.empty:
    st.sidebar.success("Data Loaded")
else:
    st.sidebar.error("Data Missing")

# =========================
# 🏠 HOME DASHBOARD
# =========================
if "page" not in st.session_state:
    st.session_state.page = "Home"

if st.session_state.page == "Home":

    st.markdown("## 📊 Market Intelligence Overview")

    st.write(
        "System initialized. Select a module in the sidebar to run quantitative analysis."
    )

    if not df.empty:

        # =========================
        # 📈 KEY METRICS
        # =========================
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Records", f"{len(df):,}")
        col2.metric("Countries", df["COUNTRY"].nunique())
        col3.metric("Start Date", str(df["date"].min())[:10])
        col4.metric("End Date", str(df["date"].max())[:10])

        st.divider()

        # =========================
        # 📦 COVERAGE SNAPSHOT
        # =========================
        st.markdown("### 📌 Market Coverage")

        products = [
            col.replace("_usd", "").title()
            for col in ["diesel_usd", "gasoline_usd"]
            if col in df.columns
        ]

        st.code(" | ".join(products))

        st.divider()

        # =========================
        # 🧠 SYSTEM MESSAGE
        # =========================
        st.info(
            "ETIL is a research-grade prototype for macro-energy quantitative analysis. "
            "All outputs are exploratory and not investment advice."
        )