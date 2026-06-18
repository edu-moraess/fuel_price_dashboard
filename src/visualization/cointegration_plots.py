# src/visualization/cointegration_plots.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_cointegration_analysis(df_pivot, country_a, country_b, spread, z_score, long_signal, short_signal, z_threshold):
    """
    Plota os gráficos para a análise de cointegração.

    Args:
        df_pivot (pd.DataFrame): DataFrame com os preços originais.
        country_a (str): Nome do primeiro país/produto.
        country_b (str): Nome do segundo país/produto.
        spread (pd.Series): Série do spread cointegrado.
        z_score (pd.Series): Série do z-score do spread.
        long_signal (pd.Series): Série booleana de sinais long.
        short_signal (pd.Series): Série booleana de sinais short.
        z_threshold (float): Limiar do z-score para sinais.

    Returns:
        plotly.graph_objects.Figure: Objeto da figura Plotly.
    """
    prices_a = df_pivot[country_a]
    prices_b = df_pivot[country_b]

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(f'Preços: {country_a} vs {country_b}', 'Spread Cointegrado', 'Z-Score do Spread'),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
    )

    # Gráfico 1: Preços
    fig.add_trace(go.Scatter(x=df_pivot.index, y=prices_a, mode='lines', name=country_a, legendgroup=country_a), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_pivot.index, y=prices_b, mode='lines', name=country_b, legendgroup=country_b), row=1, col=1)

    # Gráfico 2: Spread
    fig.add_trace(go.Scatter(x=df_pivot.index, y=spread, mode='lines', name=f'Spread ({country_b} - beta*{country_a})', line=dict(color='orange')), row=2, col=1)

    # Gráfico 3: Z-Score
    fig.add_trace(go.Scatter(x=df_pivot.index, y=z_score, mode='lines', name='Z-Score Spread', line=dict(color='red')), row=3, col=1)
    fig.add_hline(y=z_threshold, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=-z_threshold, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=0, line_dash="solid", line_color="gray", row=3, col=1)

    # Sinais de trade no Z-Score
    if long_signal.any():
        fig.add_scatter(x=df_pivot.index[long_signal], y=z_score[long_signal], mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'), name='Sinal Long', row=3, col=1)
    if short_signal.any():
        fig.add_scatter(x=df_pivot.index[short_signal], y=z_score[short_signal], mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), name='Sinal Short', row=3, col=1)

    fig.update_layout(height=800, title_text=f"Cointegração: {country_a} vs {country_b}", showlegend=True)
    return fig 