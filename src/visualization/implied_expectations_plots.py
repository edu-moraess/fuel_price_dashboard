# src/visualization/implied_expectations_plots.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_expectation_analysis(prices, ma_short, ma_long, expectation_index, upper_threshold, lower_threshold, country, product):
    """
    Plota os gráficos para a análise de expectativas implícitas.

    Args:
        prices (pd.Series): Série de preços.
        ma_short (pd.Series): Média móvel curta.
        ma_long (pd.Series): Média móvel longa.
        expectation_index (pd.Series): Índice de expectativa.
        upper_threshold (pd.Series): Limiar superior.
        lower_threshold (pd.Series): Limiar inferior.
        country (str): Nome do país.
        product (str): Nome do produto.

    Returns:
        plotly.graph_objects.Figure: Objeto da figura Plotly.
    """
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(f'Preço - {country}', f'Médias Móveis', 'Índice de Expectativa'),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
    )

    # Gráfico 1: Preço
    fig.add_trace(go.Scatter(x=prices.index, y=prices.values, mode='lines', name=f'Preço {product}', line=dict(color='blue')), row=1, col=1)

    # Gráfico 2: Médias Móveis
    fig.add_trace(go.Scatter(x=prices.index, y=ma_short.values, mode='lines', name=f'Média Curta', line=dict(color='orange')), row=2, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=ma_long.values, mode='lines', name=f'Média Longa', line=dict(color='red')), row=2, col=1)

    # Gráfico 3: Índice de Expectativa
    fig.add_trace(go.Scatter(x=prices.index, y=expectation_index.values, mode='lines', name='Índice de Expectativa', line=dict(color='purple')), row=3, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=upper_threshold.values, mode='lines', name='Limiar Superior', line=dict(color='lightcoral', dash='dash')), row=3, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=lower_threshold.values, mode='lines', name='Limiar Inferior', line=dict(color='lightgreen', dash='dash')), row=3, col=1)
    fig.add_hline(y=0, line_dash="solid", line_color="gray", row=3, col=1)

    fig.update_layout(height=800, title_text=f"Índice de Expectativas - {country} ({product})", showlegend=True)
    return fig 