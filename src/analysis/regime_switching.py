# src/analysis/regime_switching.py

import pandas as pd
import numpy as np
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
import warnings
warnings.filterwarnings('ignore') # Opcional: para silenciar warnings do solver do Markov Regression


def fit_markov_switching_model(returns, num_regimes=2, trend='c'):
    """
    Ajusta um modelo de Markov Switching para uma série de retornos.

    Args:
        returns (pd.Series): Série temporal de retornos.
        num_regimes (int): Número de regimes a estimar.
        trend (str): Tipo de tendência ('c' para constante, 'nc' para nenhuma).

    Returns:
        tuple: (model_result, smoothed_probs)
               model_result: Objeto resultante do modelo ajustado.
               smoothed_probs: DataFrame com as probabilidades suavizadas de regime.
    """
    try:
        mod = MarkovRegression(returns, k_regimes=num_regimes, trend=trend, switching_variance=True)
        res = mod.fit(disp=False) # disp=False para silenciar prints do solver
        smoothed_probs = res.smoothed_marginal_probabilities
        return res, smoothed_probs
    except Exception as e:
        print(f"Erro ao ajustar modelo Markov Switching: {e}")
        return None, None

def predict_regime_probability(model_result, steps=1):
    """
    Prever a probabilidade de regimes para os próximos 'steps'.

    NOTA: statsmodels MarkovRegression não fornece uma função direta para previsão
          de probabilidades futuras de regime. Esta função é uma simplificação
          que assume que a probabilidade mais recente é a melhor estimativa.
          Uma abordagem mais robusta envolve simulações ou extrapolação do filtro de Kalman.
    """
    if model_result is None:
        return None
    # Retorna as probabilidades suavizadas do último ponto observado como estimativa
    # para o próximo período (limitação do modelo/statsmodels para previsão direta).
    latest_smoothed_probs = model_result.smoothed_marginal_probabilities.iloc[-1:]
    # Repete para o número de steps desejados
    future_probs = pd.concat([latest_smoothed_probs]*steps, ignore_index=True)
    return future_probs