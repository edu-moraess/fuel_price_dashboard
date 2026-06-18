# src/visualization/regime_switching_plots.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_regime_switching_analysis(prices, returns, smoothed_probs, num_regimes):
    """
    Plota os gráficos para a análise de mudança de regime.

    Args:
        prices (pd.Series): Série de preços.
        returns (pd.Series): Série de retornos.
        smoothed_probs (pd.DataFrame): Probabilidades suavizadas de regime.
        num_regimes (int): Número de regimes.

    Returns:
        plotly.graph_objects.Figure: Objeto da figura Plotly.
    """
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(f'Preço', 'Retorno Percentual', 'Probabilidades Suavizadas por Regime'),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
    )

    # Gráfico 1: Preço
    fig.add_trace(go.Scatter(x=prices.index, y=prices.values, mode='lines', name='Preço', line=dict(color='blue')), row=1, col=1)

    # Gráfico 2: Retorno
    fig.add_trace(go.Scatter(x=returns.index, y=returns.values, mode='lines', name='Retorno %', line=dict(color='orange')), row=2, col=1)

    # Gráfico 3: Probabilidades
    for i in range(num_regimes):
        fig.add_trace(go.Scatter(x=smoothed_probs.index, y=smoothed_probs.iloc[:, i], mode='lines', name=f'Regime {i+1}', stackgroup='one'), row=3, col=1)

    fig.update_layout(height=800, title_text=f"Mudança de Regime - {num_regimes} Regimes", showlegend=True)
    return fig