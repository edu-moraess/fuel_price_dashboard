# src/config.py

import os

# --- Caminhos ---
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fuel_prices_clean_iea.csv")

# --- Constantes ---
DATE_COLUMN = 'date'
COUNTRY_COLUMN = 'COUNTRY'
PRODUCT_COLUMNS = ['diesel_usd', 'gasoline_usd'] # Ordem importante
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

# --- Valores Padrão ---
DEFAULT_START_DATE = '2015-01-01'
DEFAULT_END_DATE = '2025-12-01' # Ou a data máxima disponível no dataset

# --- Análise ---
# --- Cointegração ---
COINTEGRATION_THRESHOLD = 0.05 # Nível de significância para o teste ADF no spread
COINTEGRATION_LOOKBACK_YEARS = 5 # Janela padrão para cointegração
COINTEGRATION_ZSCORE_THRESHOLD = 2.0 # Threshold para sinais de trade

# --- Mudança de Regime ---
REGIME_SWITCHING_DEFAULT_REGIMES = 2
REGIME_SWITCHING_PREDICTION_STEPS = 12

# --- Expectativas Implícitas ---
IMPLIED_EXPECT_SHORT_WINDOW = 3
IMPLIED_EXPECT_LONG_WINDOW = 12

# --- Spillovers de Risco ---
RISK_SPILLOVER_VAR_LAGS = 2 # Lags para o modelo VAR
RISK_SPILLOVER_GARCH_LAGS = 1 # Lags para o modelo GARCH univariado (opcional)

# --- Simulação de Portfólio ---
PORTFOLIO_SIMULATION_DEFAULT_N_ASSETS = 5
PORTFOLIO_SIMULATION_RETURN_COLUMN = 'return' # Nome da coluna de retorno calculado
PORTFOLIO_SIMULATION_WEIGHTS_COLUMN = 'weight' # Nome da coluna de pesos