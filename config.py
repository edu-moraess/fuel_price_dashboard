import os

BASE_DIR   = os.path.dirname(os.path.dirname(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "data", "fuel_prices_clean_iea.csv")

DATE_COL     = "date"
COUNTRY_COL  = "COUNTRY"
PRODUCTS     = ["diesel_usd", "gasoline_usd"]
DATE_FORMAT  = "%Y-%m-%d"

# Cointegration
COINT_LOOKBACK_YEARS  = 5
COINT_ZSCORE_THRESH   = 2.0

# Regime switching
REGIME_N_DEFAULT      = 2

# Implied expectations
IE_SHORT_WINDOW       = 3
IE_LONG_WINDOW        = 12

# VAR spillovers
VAR_LAGS_DEFAULT      = 2

# Portfolio
PORT_N_ASSETS_DEFAULT = 5
PORT_N_SIM            = 800
