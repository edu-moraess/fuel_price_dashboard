# src/analysis/portfolio_simulation.py

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


def calculate_portfolio_metrics(weights, returns):
    """
    Calcula retorno e volatilidade anualizados do portfólio.

    Args:
        weights (np.ndarray): Array de pesos dos ativos.
        returns (pd.DataFrame): DataFrame de retornos dos ativos.

    Returns:
        tuple: (retorno_anualizado, volatilidade_anualizada).
    """
    returns_mean = returns.mean() * 12  # Anualizar (12 meses)
    returns_cov = returns.cov() * 12    # Anualizar
    portfolio_return = np.sum(weights * returns_mean)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns_cov, weights)))
    return portfolio_return, portfolio_volatility


def objective_sharpe(weights, returns, risk_free_rate=0.02):
    """
    Função objetivo para maximizar o Sharpe Ratio.

    Args:
        weights (np.ndarray): Array de pesos.
        returns (pd.DataFrame): DataFrame de retornos.
        risk_free_rate (float): Taxa livre de risco anual.

    Returns:
        float: Negativo do Sharpe Ratio (para minimização).
    """
    p_return, p_vol = calculate_portfolio_metrics(weights, returns)
    sharpe = (p_return - risk_free_rate) / p_vol
    return -sharpe


def objective_variance(weights, returns):
    """
    Função objetivo para minimizar a variância do portfólio.

    Args:
        weights (np.ndarray): Array de pesos.        returns (pd.DataFrame): DataFrame de retornos.

    Returns:
        float: Variância do portfólio.
    """
    _, p_vol = calculate_portfolio_metrics(weights, returns)
    return p_vol**2 # Retorna a variância (vol^2)


def optimize_portfolio(returns, objective_func, initial_weights, constraints, bounds):
    """
    Otimiza o portfólio usando scipy.minimize.

    Args:
        returns (pd.DataFrame): DataFrame de retornos.
        objective_func (callable): Função objetivo a ser minimizada.
        initial_weights (np.ndarray): Pesos iniciais.
        constraints (list): Lista de dicionários de restrições.
        bounds (tuple): Tupla de limites para os pesos.

    Returns:
        OptimizeResult: Resultado da otimização.
    """
    result = minimize(
        objective_func,
        initial_weights,
        args=(returns,),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    return result


def create_optimization_constraints_and_bounds(n_assets, weight_limits=(0, 1), total_weight=1.0):
    """
    Cria restrições e limites padrão para otimização de portfólio.

    Args:
        n_assets (int): Número de ativos.
        weight_limits (tuple): Limites (min, max) para pesos individuais.
        total_weight (float): Valor total dos pesos (geralmente 1.0).

    Returns:
        tuple: (constraints_list, bounds_tuple).
    """
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - total_weight}
    ]
    bounds = tuple(weight_limits for _ in range(n_assets))
    return constraints, bounds 