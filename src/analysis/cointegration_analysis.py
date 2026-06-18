# src/analysis/cointegration_analysis.py

import pandas as pd
import numpy as np
from scipy.stats import linregress
from statsmodels.tsa.stattools import adfuller


def calculate_cointegration_spread(df_pivot, col_a, col_b):
    """
    Calcula o spread de cointegração entre duas séries temporais.

    Args:
        df_pivot (pd.DataFrame): DataFrame com colunas de preços para dois países/produtos.
        col_a (str): Nome da coluna do primeiro ativo.
        col_b (str): Nome da coluna do segundo ativo.

    Returns:
        tuple: (beta, intercept, spread, p_value_adf)
               beta: Coeficiente angular da regressão linear.
               intercept: Intercepto da regressão linear.
               spread: Série temporal do spread (col_b - beta * col_a - intercept).
               p_value_adf: P-valor do teste ADF no spread (indicativo de cointegração).
    """
    prices_a = df_pivot[col_a]
    prices_b = df_pivot[col_b]

    # Estimar beta (coeficiente de cointegração) via regressão linear
    slope, intercept, r_value, p_value_reg, std_err = linregress(prices_a, prices_b)

    # Calcular o spread cointegrado
    spread = prices_b - (slope * prices_a + intercept)

    # Testar estacionariedade do spread (cointegração) com ADF
    # A hipótese nula do ADF é que há uma raiz unitária (não é estacionário)
    adf_result = adfuller(spread)
    p_value_adf = adf_result[1]

    return slope, intercept, spread, p_value_adf

def calculate_zscore(spread, lookback_period=60):
    """
    Calcula o z-score móvel de um spread.

    Args:
        spread (pd.Series): Série temporal do spread.
        lookback_period (int): Número de períodos para calcular média e std móveis.

    Returns:
        pd.Series: Série temporal do z-score móvel do spread.
    """
    spread_mean = spread.rolling(window=lookback_period, min_periods=1).mean()
    spread_std = spread.rolling(window=lookback_period, min_periods=1).std(ddof=0) # ddof=0 para pop std
    z_score = (spread - spread_mean) / spread_std
    return z_score

def generate_trade_signals(z_scores, threshold=2.0):
    """
    Gera sinais de trade com base no z-score do spread.

    Args:
        z_scores (pd.Series): Série temporal do z-score do spread.
        threshold (float): Limiar para gerar sinais.

    Returns:
        tuple: (long_signal, short_signal) Series booleanas.
    """
    long_signal = z_scores < -threshold
    short_signal = z_scores > threshold
    return long_signal, short_signal