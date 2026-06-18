# Fuel Price Quant Research Platform

A modular quantitative research platform for global fuel price analysis using IEA data. Built with Streamlit, it covers statistical modeling, regime detection, risk propagation, and portfolio optimization across a cross-sectional panel of countries.

---

## Project Structure

```
app.py                          # Entry point and home dashboard
data/
  fuel_prices_clean_iea.csv     # IEA fuel price dataset (diesel & gasoline, USD)
pages/
  1_Cointegracao.py             # Cointegration analysis & pairs trading signals
  2_Regime_Switching.py         # Markov regime switching models
  3_Expectativas_Impl.py        # Implied expectations via moving average signals
  4_Spillovers_Risco.py         # VAR-based risk spillovers & correlation network
  5_Sim_Portfolio.py            # Mean-variance portfolio optimization
src/
  theme.py                      # Global visual theme (CSS + Plotly)
  config.py                     # Constants, paths, and model parameters
  session.py                    # Session state manager
  load_data.py                  # Data ingestion and preprocessing
  analysis/
    cointegration_analysis.py
    implied_expectations.py
    portfolio_simulation.py
    regime_switching.py
    risk_spillovers.py
  visualization/
    cointegration_plots.py
    implied_expectations_plots.py
    portfolio_simulation_plots.py
    regime_switching_plots.py
    risk_spillovers_plots.py
```

---

## Dataset

- **Source:** IEA (International Energy Agency)
- **File:** `data/fuel_prices_clean_iea.csv`
- **Columns:** `date`, `COUNTRY`, `diesel_usd`, `gasoline_usd`
- **Frequency:** Monthly
- **Coverage:** Multi-country cross-section

---

## Modules

### Cointegration Analysis
Tests for long-run price relationships between country pairs using OLS regression on the spread. Computes rolling Z-score and generates long/short signals when the spread deviates beyond a configurable threshold.

### Regime Switching
Fits a Markov Switching regression (statsmodels) with configurable number of regimes (2–4) and switching variance. Displays smoothed regime probabilities alongside price and return series.

### Implied Expectations
Constructs a normalized expectation index from the spread between short and long moving averages. Captures momentum and mean-reversion signals without parametric assumptions.

### Spillovers & Risk Propagation
Estimates a Vector Autoregression (VAR) model across selected countries. Displays log-return series, correlation heatmap, and full VAR summary to assess cross-country price transmission.

### Portfolio Simulation
Runs mean-variance optimization (scipy) to find the Max Sharpe and Min Variance portfolios. Plots the efficient frontier via Monte Carlo simulation alongside individual cumulative returns.

---

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
streamlit run app.py
```

---

## Design

Visual theme is defined entirely in `src/theme.py`. Call `inject_theme()` at the top of any page and `apply_plotly_theme(fig)` on any Plotly figure to apply the consistent petro-industrial dark palette. No other file needs to be modified to change the global appearance.

---

## Disclaimer

Research prototype. All outputs are exploratory and for analytical purposes only. Not investment advice.
