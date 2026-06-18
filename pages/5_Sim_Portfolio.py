import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize
import warnings

from src.load_data import filter_data_by_selection
from src.config import PORTFOLIO_SIMULATION_DEFAULT_N_ASSETS

warnings.filterwarnings("ignore")

# =========================
# 📊 CONFIG
# =========================
st.set_page_config(
    page_title="Portfolio Simulation Engine",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Portfolio Simulation Engine — Energy Assets")

# =========================
# 📦 DATA
# =========================
df_full = st.session_state.get("df", None)

if df_full is None:
    st.error("Dataset not loaded. Check app.py.")
    st.stop()

# =========================
# 🎛️ SIDEBAR
# =========================
st.sidebar.header("Portfolio Inputs")

countries = sorted(df_full["COUNTRY"].unique())

selected_countries = st.sidebar.multiselect(
    "Countries (Assets)",
    options=countries,
    default=countries[:PORTFOLIO_SIMULATION_DEFAULT_N_ASSETS]
)

products = ["diesel_usd", "gasoline_usd"]

selected_products = st.sidebar.multiselect(
    "Product per Country",
    options=products,
    default=["diesel_usd"] * len(selected_countries)
)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-01"))

if len(selected_countries) != len(selected_products):
    st.warning("Number of countries must match number of products.")
    st.stop()

# =========================
# 📊 DATA PREP
# =========================
returns_list = []

for country, product in zip(selected_countries, selected_products):

    df_temp = filter_data_by_selection(
        df_full,
        countries=[country],
        products=[product],
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )

    if df_temp.empty:
        continue

    df_temp = df_temp.sort_values("date")

    asset_name = f"{country}_{product}"

    df_temp[asset_name] = np.log(df_temp[product] / df_temp[product].shift(1))

    returns_list.append(df_temp.set_index("date")[asset_name])

if not returns_list:
    st.warning("No valid assets found.")
    st.stop()

returns_df = pd.concat(returns_list, axis=1).dropna()

if returns_df.shape[1] < 2:
    st.warning("Need at least 2 assets.")
    st.stop()

# =========================
# 📈 FUNCTIONS
# =========================
def portfolio_perf(weights, returns):
    mean = returns.mean() * 12
    cov = returns.cov() * 12

    ret = np.dot(weights, mean)
    vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))

    return ret, vol


def sharpe_neg(weights, returns):
    r, v = portfolio_perf(weights, returns)
    if v == 0:
        return 999
    return -(r - 0.02) / v


def variance(weights, returns):
    _, v = portfolio_perf(weights, returns)
    return v ** 2


# =========================
# 🧠 OPTIMIZATION
# =========================
n = len(returns_df.columns)
init = np.ones(n) / n

bounds = [(0, 1) for _ in range(n)]
constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

max_sharpe = minimize(
    sharpe_neg,
    init,
    args=(returns_df,),
    method="SLSQP",
    bounds=bounds,
    constraints=constraints
)

min_var = minimize(
    variance,
    init,
    args=(returns_df,),
    method="SLSQP",
    bounds=bounds,
    constraints=constraints
)

w_sharpe = max_sharpe.x
w_var = min_var.x

r_sharpe, v_sharpe = portfolio_perf(w_sharpe, returns_df)
r_var, v_var = portfolio_perf(w_var, returns_df)

# =========================
# 📊 VISUALS
# =========================
fig = make_subplots(
    rows=2,
    cols=2,
    specs=[[{"type": "xy"}, {"type": "xy"}],
           [{"type": "domain"}, {"type": "domain"}]],
    subplot_titles=(
        "Asset Cumulative Returns",
        "Efficient Frontier (Simulated)",
        "Max Sharpe Allocation",
        "Min Variance Allocation"
    )
)

cum = (1 + returns_df).cumprod()

for c in cum.columns:
    fig.add_trace(
        go.Scatter(x=cum.index, y=cum[c], name=c),
        row=1, col=1
    )

# simulated frontier
frontier_r, frontier_v = [], []

for _ in range(200):
    w = np.random.random(n)
    w /= w.sum()
    r, v = portfolio_perf(w, returns_df)
    frontier_r.append(r)
    frontier_v.append(v)

fig.add_trace(
    go.Scatter(x=frontier_v, y=frontier_r, mode="markers", name="Random Portfolios"),
    row=1, col=2
)

fig.add_trace(go.Pie(labels=returns_df.columns, values=w_sharpe), row=2, col=1)
fig.add_trace(go.Pie(labels=returns_df.columns, values=w_var), row=2, col=2)

fig.update_layout(height=800, title="Portfolio Simulation Engine")

st.plotly_chart(fig, use_container_width=True)

# =========================
# 📊 RESULTS
# =========================
st.subheader("Optimization Results")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Max Sharpe")
    st.metric("Return", f"{r_sharpe:.2%}")
    st.metric("Volatility", f"{v_sharpe:.2%}")

    for c, w in zip(returns_df.columns, w_sharpe):
        st.write(f"{c}: {w:.2%}")

with col2:
    st.markdown("### Min Variance")
    st.metric("Return", f"{r_var:.2%}")
    st.metric("Volatility", f"{v_var:.2%}")

    for c, w in zip(returns_df.columns, w_var):
        st.write(f"{c}: {w:.2%}")

# =========================
# 📥 EXPORT
# =========================
export = returns_df.copy()
export["portfolio_sharpe"] = returns_df @ w_sharpe
export["portfolio_minvar"] = returns_df @ w_var

st.download_button(
    "Download Portfolio Data",
    export.to_csv().encode("utf-8"),
    file_name="portfolio_simulation.csv",
    mime="text/csv"
)