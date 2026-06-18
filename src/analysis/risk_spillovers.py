# src/analysis/risk_spillovers.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.vector_ar.var_model import VAR
from scipy.spatial.distance import squareform
import warnings
warnings.filterwarnings('ignore')


def prepare_returns_data(df_pivot, standardize=True):
    """
    Prepara dados de retornos logarítmicos para análise VAR.

    Args:
        df_pivot (pd.DataFrame): DataFrame com preços.
        standardize (bool): Se True, padroniza os retornos.

    Returns:
        pd.DataFrame: DataFrame de retornos logarítmicos (e opcionalmente padronizados).
    """
    returns_log = np.log(df_pivot / df_pivot.shift(1)).dropna()

    if standardize:
        scaler = StandardScaler()
        returns_scaled = pd.DataFrame(
            scaler.fit_transform(returns_log),
            columns=returns_log.columns,
            index=returns_log.index
        )
        return returns_scaled
    return returns_log


def fit_var_model(returns_df, lags=2, ic=None):
    """
    Ajusta um modelo VAR.

    Args:
        returns_df (pd.DataFrame): DataFrame de retornos.
        lags (int): Número de lags (ignorado se ic for especificado).
        ic (str): Critério de informação ('aic', 'bic', 'hqic', 'fpe') para auto-seleção de lags.

    Returns:
        VARResultsWrapper: Objeto resultante do modelo VAR ajustado.
    """
    try:
        var_model = VAR(returns_df)
        if ic:
            # Seleciona automaticamente o número de lags com base no critério de informação
            selected_lags = var_model.select_order(maxlags=lags*2, trend='c') # Exemplo: olha até 2*lags
            # Acessa o lag sugerido pelo critério (ex: selected_lags.aic)
            # Vamos pegar o primeiro critério retornado ou usar o padrão se ic falhar
            best_lag = getattr(selected_lags, ic, lags)
            var_results = var_model.fit(maxlags=best_lag, ic=None) # ic=None porque já selecionamos
        else:
            var_results = var_model.fit(maxlags=lags, ic=None)
        return var_results
    except Exception as e:
        print(f"Erro ao ajustar modelo VAR: {e}")
        return None


def calculate_fevd(var_results, horizon=10):
    """
    Calcula a Decomposição da Variância do Erro de Previsão (FEVD).

    Args:
        var_results: Objeto resultante do modelo VAR ajustado.
        horizon (int): Horizonte para a decomposição.

    Returns:
        FEVD: Objeto FEVD ou None se falhar.
    """
    if var_results is not None:
        try:
            fevd = var_results.fevd(horizon)
            return fevd
        except Exception as e:
            print(f"Erro ao calcular FEVD: {e}")
            return None
    return None


def calculate_correlation_matrix(returns_df):
    """
    Calcula a matriz de correlação.

    Args:
        returns_df (pd.DataFrame): DataFrame de retornos.

    Returns:
        pd.DataFrame: Matriz de correlação.
    """
    return returns_df.corr()