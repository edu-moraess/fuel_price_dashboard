# src/analysis/implied_expectations.py

import pandas as pd
import numpy as np


def calculate_ma_expectation_index(prices, short_window=3, long_window=12):
    """
    Calcula um índice de expectativa implícita baseado em médias móveis.

    Args:
        prices (pd.Series): Série temporal de preços.
        short_window (int): Janela para a média móvel curta.
        long_window (int): Janela para a média móvel longa.

    Returns:
        tuple: (ma_short, ma_long, spread_ma, expectation_index)
    """
    ma_short = prices.rolling(window=short_window, min_periods=1).mean()
    ma_long = prices.rolling(window=long_window, min_periods=1).mean()
    spread_ma = ma_short - ma_long

    # Índice baseado no Z-score do spread em relação à sua própria volatilidade
    # (ou em relação à volatilidade da média longa, ou outro denominador)
    # Usando a volatilidade do próprio spread para normalização
    spread_vol = spread_ma.rolling(window=long_window).std()
    # Adiciona um pequeno valor para evitar divisão por zero
    expectation_index = spread_ma / (spread_vol + 1e-8)

    return ma_short, ma_long, spread_ma, expectation_index

def calculate_percentile_thresholds(expectation_index, window=24, high_percentile=80, low_percentile=20):
    """
    Calcula limiares percentis para o índice de expectativa.

    Args:
        expectation_index (pd.Series): Série do índice de expectativa.
        window (int): Janela para calcular os percentis.
        high_percentile (float): Percentil superior (ex: 80 para 80%).
        low_percentile (float): Percentil inferior (ex: 20 para 20%).

    Returns:
        tuple: (upper_threshold, lower_threshold) Series.
    """
    upper_threshold = expectation_index.rolling(window=window).quantile(high_percentile / 100.0)
    lower_threshold = expectation_index.rolling(window=window).quantile(low_percentile / 100.0)
    return upper_threshold, lower_threshold