"""
All page render functions. Each receives the full dataframe.
Pure functions: no session_state writes, no navigation calls.
"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.stats import linregress
from scipy.optimize import minimize
import streamlit as st

from src.theme import C, apply, section, page_header
from src.data import filter_df
from src.config import (
    COINT_LOOKBACK_YEARS, COINT_ZSCORE_THRESH,
    REGIME_N_DEFAULT, IE_SHORT_WINDOW, IE_LONG_WINDOW,
    VAR_LAGS_DEFAULT, PORT_N_ASSETS_DEFAULT, PORT_N_SIM,
    COUNTRY_COL, DATE_COL,
)

PALETTE = [C["amber"], C["blue"], C["green"], C["red"],
           "#7B5EA7", "#1F7A8C", "#A0522D", "#4E8098"]


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _sidebar_filters_single(df, key, default_country=None, default_product=0,
                             default_start="2018-01-01", default_end="2024-12-01"):
    countries = sorted(df[COUNTRY_COL].unique())
    default_c = default_country or countries[0]
    country = st.sidebar.selectbox("Country", countries,
                                   index=countries.index(default_c) if default_c in countries else 0,
                                   key=f"{key}_country")
    product = st.sidebar.selectbox("Product", ["diesel_usd", "gasoline_usd"],
                                   index=default_product, key=f"{key}_product")
    start = st.sidebar.date_input("Start Date", pd.to_datetime(default_start), key=f"{key}_start")
    end   = st.sidebar.date_input("End Date",   pd.to_datetime(default_end),   key=f"{key}_end")
    return country, product, str(start), str(end)


def _sidebar_filters_multi(df, key, n_default=3,
                            default_start="2018-01-01", default_end="2024-12-01"):
    countries = sorted(df[COUNTRY_COL].unique())
    selected = st.sidebar.multiselect("Countries", countries,
                                      default=countries[:n_default], key=f"{key}_countries")
    product = st.sidebar.selectbox("Product", ["diesel_usd", "gasoline_usd"],
                                   key=f"{key}_product")
    start = st.sidebar.date_input("Start Date", pd.to_datetime(default_start), key=f"{key}_start")
    end   = st.sidebar.date_input("End Date",   pd.to_datetime(default_end),   key=f"{key}_end")
    return selected, product, str(start), str(end)


def _metric_row(items: list):
    cols = st.columns(len(items))
    for col, (label, val) in zip(cols, items):
        col.metric(label, val)


# ─────────────────────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────────────────────
def page_home(df: pd.DataFrame):
    # Hero banner
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {C['surface']} 0%, {C['elevated']} 100%);
        border: 1px solid {C['border']}; border-left: 4px solid {C['amber']};
        border-radius: 2px; padding: 28px 32px 24px 32px;
        margin-bottom: 28px; position: relative; overflow: hidden;">
        <div style="position:absolute;top:0;right:0;width:100px;height:100%;
            background: repeating-linear-gradient(-45deg, transparent, transparent 7px,
            {C['amber_lo']} 7px, {C['amber_lo']} 8px); opacity:0.5;"></div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.58rem;
                    letter-spacing:0.20em; color:{C['amber']}; text-transform:uppercase;
                    margin-bottom:8px;">⛽ Fuel Price Quant Research Platform</div>
        <div style="font-family:'IBM Plex Sans Condensed',sans-serif; font-weight:700;
                    font-size:1.9rem; color:{C['text']}; text-transform:uppercase;
                    letter-spacing:0.03em; line-height:1.1;">
            Global Energy<br><span style="color:{C['amber']};">Market Intelligence</span>
        </div>
        <div style="font-size:0.72rem; color:{C['text_sub']}; margin-top:10px;
                    font-family:'IBM Plex Mono',monospace; letter-spacing:0.04em;">
            Cointegration · Regime Detection · Risk Spillovers · Portfolio Optimization
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.error("Dataset not loaded.")
        return

    _metric_row([
        ("Records",    f"{len(df):,}"),
        ("Countries",  df[COUNTRY_COL].nunique()),
        ("Start Date", str(df[DATE_COL].min())[:10]),
        ("End Date",   str(df[DATE_COL].max())[:10]),
    ])

    st.divider()
    section("Market Coverage")
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.78rem; '
        f'color:{C["amber"]}; background:{C["elevated"]}; '
        f'border:1px solid {C["border"]}; padding:10px 16px; border-radius:2px; '
        f'letter-spacing:0.10em;">DIESEL &nbsp;|&nbsp; GASOLINE</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    section("Country Panel")
    all_countries = sorted(df[COUNTRY_COL].unique())
    st.markdown(
        f'<div style="font-size:0.72rem; color:{C["text_sub"]}; line-height:2.0; '
        f'font-family:\'IBM Plex Mono\',monospace; letter-spacing:0.04em;">'
        + " &nbsp;·&nbsp; ".join(all_countries) + "</div>",
        unsafe_allow_html=True,
    )

    st.divider()
    st.info(
        "RESEARCH PROTOTYPE — All outputs are exploratory and for analytical purposes only. "
        "Not investment advice. Source: IEA."
    )


# ─────────────────────────────────────────────────────────────
# PAGE: COINTEGRATION
# ─────────────────────────────────────────────────────────────
def page_cointegration(df: pd.DataFrame):
    page_header("Cointegration Analysis",
                "Pairs Trading · Spread Dynamics · Z-Score Signals")

    section("Parameters")
    countries_avail = sorted(df[COUNTRY_COL].unique())
    col_a, col_b = st.sidebar.columns(2)
    country_a = st.sidebar.selectbox("Country A", countries_avail, index=0, key="co_a")
    country_b = st.sidebar.selectbox("Country B", countries_avail, index=1, key="co_b")
    product   = st.sidebar.selectbox("Product", ["diesel_usd", "gasoline_usd"], key="co_prod")
    start     = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"), key="co_start")
    end       = st.sidebar.date_input("End Date",   pd.to_datetime("2024-12-01"), key="co_end")
    lookback  = st.sidebar.slider("Lookback Window (years)", 1, 10, COINT_LOOKBACK_YEARS, key="co_lb")
    z_thresh  = st.sidebar.number_input("Z-Score Threshold", 0.1, 5.0,
                                         COINT_ZSCORE_THRESH, 0.1, key="co_zt")

    if country_a == country_b:
        st.warning("Select two different countries.")
        return

    dfa = filter_df(df, [country_a], product, str(start), str(end))
    dfb = filter_df(df, [country_b], product, str(start), str(end))

    if dfa.empty or dfb.empty:
        st.warning("No data found for the selected filters.")
        return

    merged = pd.merge(
        dfa.set_index(DATE_COL)[product].rename(country_a),
        dfb.set_index(DATE_COL)[product].rename(country_b),
        left_index=True, right_index=True,
    ).dropna()

    if len(merged) < 24:
        st.warning("Insufficient overlapping observations (need ≥ 24).")
        return

    pa, pb = merged[country_a], merged[country_b]
    slope, intercept, r_value, p_value, _ = linregress(pa, pb)
    spread = pb - (slope * pa + intercept)

    window = lookback * 12
    s_mean = spread.rolling(window, min_periods=6).mean()
    s_std  = spread.rolling(window, min_periods=6).std()
    z      = (spread - s_mean) / s_std.replace(0, np.nan)

    long_sig  = z < -z_thresh
    short_sig = z > z_thresh

    _metric_row([
        ("Beta (β)",         f"{slope:.4f}"),
        ("Intercept",        f"{intercept:.4f}"),
        ("Correlation (r)",  f"{r_value:.4f}"),
        ("Current Z-Score",  f"{z.iloc[-1]:.2f}" if not np.isnan(z.iloc[-1]) else "—"),
    ])

    st.divider()

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        subplot_titles=(
            f"Price — {country_a} vs {country_b}",
            "Cointegrated Spread",
            "Spread Z-Score",
        ),
    )
    fig.add_trace(go.Scatter(x=merged.index, y=pa, name=country_a,
                             line=dict(color=C["amber"], width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=merged.index, y=pb, name=country_b,
                             line=dict(color=C["blue"], width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=merged.index, y=spread, name="Spread",
                             line=dict(color=C["text_sub"], width=1.2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=merged.index, y=z, name="Z-Score",
                             line=dict(color=C["amber"], width=1.2)), row=3, col=1)
    for lvl, col in [(z_thresh, C["red"]), (-z_thresh, C["green"])]:
        fig.add_hline(y=lvl, line_dash="dash", line_color=col, line_width=1, row=3, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color=C["border"], line_width=1, row=3, col=1)
    if long_sig.any():
        fig.add_scatter(x=merged.index[long_sig], y=z[long_sig], mode="markers",
                        name="Long", marker=dict(symbol="triangle-up", size=8, color=C["green"]),
                        row=3, col=1)
    if short_sig.any():
        fig.add_scatter(x=merged.index[short_sig], y=z[short_sig], mode="markers",
                        name="Short", marker=dict(symbol="triangle-down", size=8, color=C["red"]),
                        row=3, col=1)
    fig.update_layout(height=740)
    apply(fig)
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# PAGE: REGIME SWITCHING
# ─────────────────────────────────────────────────────────────
def page_regime(df: pd.DataFrame):
    page_header("Regime Switching Models",
                "Markov Switching · Smoothed Probabilities · Regime Classification")

    try:
        from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
    except ImportError:
        st.error("statsmodels not available.")
        return

    section("Parameters")
    country, product, start, end = _sidebar_filters_single(df, "reg")
    n_reg = st.sidebar.slider("Number of Regimes", 2, 4, REGIME_N_DEFAULT, key="reg_n")

    data = filter_df(df, [country], product, start, end)
    if data.empty:
        st.warning("No data found for the selected filters.")
        return

    prices  = data.set_index(DATE_COL)[product]
    returns = prices.pct_change().dropna()

    if len(returns) < 30:
        st.warning("Insufficient observations (need ≥ 30).")
        return

    with st.spinner("Fitting Markov Switching model…"):
        try:
            model = MarkovRegression(returns, k_regimes=n_reg,
                                     trend="c", switching_variance=True)
            res   = model.fit(disp=False)
            probs = res.smoothed_marginal_probabilities
        except Exception as e:
            st.error(f"Model error: {e}")
            return

    dominant = int(probs.iloc[-1].idxmax()) + 1
    _metric_row([
        ("Country",           country),
        ("Observations",      len(returns)),
        ("Regimes",           n_reg),
        ("Current Regime",    f"Regime {dominant}"),
    ])

    st.divider()

    reg_pal = [C["amber"], C["blue"], C["green"], C["red"]]
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        subplot_titles=(f"Price — {country} ({product})",
                        "Return (%)", "Smoothed Regime Probabilities"),
    )
    fig.add_trace(go.Scatter(x=prices.index, y=prices, name="Price (USD)",
                             line=dict(color=C["amber"], width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=returns.index, y=returns * 100, name="Return %",
                             line=dict(color=C["text_sub"], width=1.0),
                             fill="tozeroy",
                             fillcolor="rgba(200,126,10,0.07)"), row=2, col=1)
    for i in range(n_reg):
        hex_c = reg_pal[i % len(reg_pal)]
        r, g, b = int(hex_c[1:3],16), int(hex_c[3:5],16), int(hex_c[5:7],16)
        fig.add_trace(go.Scatter(
            x=probs.index, y=probs.iloc[:, i],
            name=f"Regime {i+1}",
            stackgroup="reg",
            line=dict(color=hex_c, width=0.8),
            fillcolor=f"rgba({r},{g},{b},0.22)",
        ), row=3, col=1)
    fig.update_layout(height=740)
    apply(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    section("Model Summary")
    st.code(str(res.summary()), language=None)


# ─────────────────────────────────────────────────────────────
# PAGE: IMPLIED EXPECTATIONS
# ─────────────────────────────────────────────────────────────
def page_implied(df: pd.DataFrame):
    page_header("Implied Expectations",
                "Moving Average Signals · Expectation Index · Momentum")

    section("Parameters")
    country, product, start, end = _sidebar_filters_single(df, "ie",
                                                            default_start="2015-01-01")
    short_w = st.sidebar.slider("Short Window (months)", 1, 24, IE_SHORT_WINDOW, key="ie_sw")
    long_w  = st.sidebar.slider("Long Window (months)",  6, 60, IE_LONG_WINDOW,  key="ie_lw")

    data = filter_df(df, [country], product, start, end)
    if data.empty:
        st.warning("No data found for the selected filters.")
        return

    prices   = data.set_index(DATE_COL)[product]
    ma_s     = prices.rolling(short_w, min_periods=1).mean()
    ma_l     = prices.rolling(long_w,  min_periods=1).mean()
    spread   = ma_s - ma_l
    std_roll = spread.rolling(long_w, min_periods=3).std().replace(0, np.nan)
    index    = spread / (std_roll + 1e-8)

    _metric_row([
        ("Current Price (USD)",        f"{prices.iloc[-1]:.3f}"),
        (f"MA {short_w}m (USD)",       f"{ma_s.iloc[-1]:.3f}"),
        (f"MA {long_w}m (USD)",        f"{ma_l.iloc[-1]:.3f}"),
        ("Expectation Index",          f"{index.iloc[-1]:.3f}" if not np.isnan(index.iloc[-1]) else "—"),
    ])

    st.divider()

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        subplot_titles=(
            f"Price — {country} ({product})",
            f"Moving Averages ({short_w}m / {long_w}m)",
            "Expectation Index (Normalized Spread)",
        ),
    )
    fig.add_trace(go.Scatter(x=prices.index, y=prices, name="Price",
                             line=dict(color=C["text"], width=1.4)), row=1, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=ma_s, name=f"MA {short_w}m",
                             line=dict(color=C["amber"], width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=ma_l, name=f"MA {long_w}m",
                             line=dict(color=C["blue"], width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=index, name="Expectation Index",
                             line=dict(color=C["amber"], width=1.2),
                             fill="tozeroy",
                             fillcolor="rgba(200,126,10,0.07)"), row=3, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color=C["border"], row=3, col=1)
    fig.update_layout(height=740)
    apply(fig)
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# PAGE: SPILLOVERS & RISK
# ─────────────────────────────────────────────────────────────
def page_spillovers(df: pd.DataFrame):
    page_header("Spillovers & Risk Propagation",
                "VAR Model · Covariance · Correlation Network")

    try:
        from statsmodels.tsa.vector_ar.var_model import VAR
    except ImportError:
        st.error("statsmodels not available.")
        return

    section("Parameters")
    countries, product, start, end = _sidebar_filters_multi(df, "sp", n_default=4)
    lags = st.sidebar.slider("VAR Lags", 1, 5, VAR_LAGS_DEFAULT, key="sp_lags")

    if len(countries) < 2:
        st.warning("Select at least 2 countries.")
        return

    frames = []
    for c in countries:
        d = filter_df(df, [c], product, start, end)
        if not d.empty:
            frames.append(d.set_index(DATE_COL)[product].rename(c))

    if len(frames) < 2:
        st.warning("Insufficient data after filtering.")
        return

    pivot   = pd.concat(frames, axis=1).dropna()
    returns = np.log(pivot).diff().dropna()

    if len(returns) < lags + 5:
        st.warning("Insufficient observations for the selected lag order.")
        return

    corr = returns.corr()
    cov  = returns.cov()

    _metric_row([
        ("Countries",    pivot.shape[1]),
        ("Observations", len(returns)),
        ("VAR Lags",     lags),
        ("Avg |Corr|",   f"{corr.abs().where(~np.eye(len(corr), dtype=bool)).stack().mean():.3f}"),
    ])

    st.divider()
    section("Log-Return Series")
    fig_r = go.Figure()
    for i, col in enumerate(returns.columns):
        fig_r.add_trace(go.Scatter(x=returns.index, y=returns[col], name=col,
                                   line=dict(color=PALETTE[i % len(PALETTE)], width=1.1)))
    fig_r.update_layout(height=300, xaxis_title="Date", yaxis_title="Log Return")
    apply(fig_r)
    st.plotly_chart(fig_r, use_container_width=True)

    section("Correlation Matrix")
    fig_c = px.imshow(
        corr.round(3), text_auto=True,
        color_continuous_scale=[[0, C["bg"]], [0.5, C["amber_lo"]], [1, C["amber"]]],
        zmin=-1, zmax=1,
    )
    fig_c.update_layout(height=420)
    apply(fig_c)
    st.plotly_chart(fig_c, use_container_width=True)

    st.divider()
    section("VAR Model Summary")
    try:
        res = VAR(returns).fit(lags)
        st.code(str(res.summary()), language=None)
    except Exception as e:
        st.error(f"VAR error: {e}")


# ─────────────────────────────────────────────────────────────
# PAGE: PORTFOLIO SIMULATION
# ─────────────────────────────────────────────────────────────
def page_portfolio(df: pd.DataFrame):
    page_header("Portfolio Simulation",
                "Mean-Variance · Max Sharpe · Min Variance · Efficient Frontier")

    section("Parameters")
    countries, product, start, end = _sidebar_filters_multi(
        df, "pf", n_default=PORT_N_ASSETS_DEFAULT)

    if not countries:
        st.warning("Select at least 2 countries.")
        return

    frames = []
    for c in countries:
        d = filter_df(df, [c], product, start, end)
        if not d.empty:
            s = np.log(d.set_index(DATE_COL)[product]
                       .replace(0, np.nan).dropna())
            s = s.diff().dropna().rename(c)
            frames.append(s)

    if len(frames) < 2:
        st.warning("Need at least 2 countries with valid data.")
        return

    returns = pd.concat(frames, axis=1).dropna()

    if len(returns) < 12:
        st.warning("Insufficient observations (need ≥ 12 months).")
        return

    n   = len(returns.columns)
    mu  = returns.mean().values * 12
    cov = returns.cov().values * 12
    w0  = np.ones(n) / n
    bnd = [(0, 1)] * n
    con = {"type": "eq", "fun": lambda w: w.sum() - 1}

    def port_perf(w):
        r = mu.dot(w)
        v = np.sqrt(w @ cov @ w)
        return r, v

    res_sh = minimize(lambda w: -(mu.dot(w) / np.sqrt(w @ cov @ w + 1e-12)),
                      w0, bounds=bnd, constraints=con)
    res_mv = minimize(lambda w: np.sqrt(w @ cov @ w),
                      w0, bounds=bnd, constraints=con)

    w_sh = res_sh.x if res_sh.success else w0
    w_mv = res_mv.x if res_mv.success else w0
    r_sh, v_sh = port_perf(w_sh)
    r_mv, v_mv = port_perf(w_mv)

    _metric_row([
        ("Max Sharpe — Ret",  f"{r_sh*100:.2f}%"),
        ("Max Sharpe — Vol",  f"{v_sh*100:.2f}%"),
        ("Min Var — Ret",     f"{r_mv*100:.2f}%"),
        ("Min Var — Vol",     f"{v_mv*100:.2f}%"),
    ])

    st.divider()

    # Monte Carlo frontier
    np.random.seed(42)
    mc_r, mc_v, mc_sh = [], [], []
    for _ in range(PORT_N_SIM):
        w = np.random.dirichlet(np.ones(n))
        r, v = port_perf(w)
        mc_r.append(r); mc_v.append(v)
        mc_sh.append(r / v if v > 0 else 0)

    section("Efficient Frontier & Weights")
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Efficient Frontier (Monte Carlo)", "Portfolio Weights"),
        specs=[[{"type": "scatter"}, {"type": "bar"}]],
    )
    fig.add_trace(go.Scatter(
        x=mc_v, y=mc_r, mode="markers", name="Random Portfolios",
        marker=dict(size=4, color=mc_sh,
                    colorscale=[[0, C["elevated"]], [1, C["amber"]]],
                    opacity=0.55, showscale=False),
    ), row=1, col=1)
    for (r, v, label, sym, col) in [
        (r_sh, v_sh, "Max Sharpe", "diamond", C["amber"]),
        (r_mv, v_mv, "Min Variance", "star", C["blue"]),
    ]:
        fig.add_trace(go.Scatter(
            x=[v], y=[r], mode="markers+text", name=label,
            marker=dict(size=13, symbol=sym, color=col,
                        line=dict(color=C["text"], width=1.5)),
            text=[label], textposition="top right",
            textfont=dict(color=col, size=9),
        ), row=1, col=1)

    fig.add_trace(go.Bar(x=list(returns.columns), y=w_sh * 100,
                         name="Max Sharpe", marker_color=C["amber"],
                         opacity=0.85), row=1, col=2)
    fig.add_trace(go.Bar(x=list(returns.columns), y=w_mv * 100,
                         name="Min Var", marker_color=C["blue"],
                         opacity=0.75), row=1, col=2)

    fig.update_xaxes(title_text="Annualized Vol", row=1, col=1)
    fig.update_yaxes(title_text="Annualized Return", row=1, col=1)
    fig.update_yaxes(title_text="Weight (%)", row=1, col=2)
    fig.update_layout(height=460, barmode="group")
    apply(fig)
    st.plotly_chart(fig, use_container_width=True)

    section("Cumulative Returns — Individual Assets")
    cum = (1 + returns).cumprod() - 1
    fig2 = go.Figure()
    for i, col in enumerate(cum.columns):
        fig2.add_trace(go.Scatter(x=cum.index, y=cum[col] * 100, name=col,
                                  line=dict(color=PALETTE[i % len(PALETTE)], width=1.4)))
    fig2.update_layout(height=340, xaxis_title="Date", yaxis_title="Cumulative Return (%)")
    apply(fig2)
    st.plotly_chart(fig2, use_container_width=True)

    if not res_sh.success:
        st.warning("Max Sharpe did not converge — showing equal-weight fallback.")
    if not res_mv.success:
        st.warning("Min Variance did not converge — showing equal-weight fallback.")
