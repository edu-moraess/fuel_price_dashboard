# src/visualization/portfolio_simulation_plots.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_portfolio_simulation(returns_df, weights_max_sharpe, weights_min_var, perf_max_sharpe, perf_min_var):
    """
    Plota os gráficos para a simulação de portfólio (retornos, fronteira, composição).

    Args:
        returns_df (pd.DataFrame): DataFrame de retornos dos ativos.
        weights_max_sharpe (np.ndarray): Pesos do portfólio Max Sharpe.
        weights_min_var (np.ndarray): Pesos do portfólio Min Variância.
        perf_max_sharpe (tuple): (retorno, volatilidade) do portfólio Max Sharpe.
        perf_min_var (tuple): (retorno, volatilidade) do portfólio Min Variância.

    Returns:
        plotly.graph_objects.Figure: Objeto da figura Plotly.
    """
    # --- Visualização ---
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Retornos dos "Ativos"', 'Fronteira Eficiente (Sharpe)', 'Composição Portfólio Max Sharpe', 'Composição Portfólio Min Var'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}], [{"type": "domain"}, {"type": "domain"}]] # Pie charts nas últimas duas
    )

    # Gráfico 1: Retornos Acumulados dos Ativos
    returns_cumulative = (1 + returns_df).cumprod() - 1
    for col in returns_cumulative.columns:
        fig.add_trace(go.Scatter(x=returns_cumulative.index, y=returns_cumulative[col], mode='lines', name=col.replace('return_', '').replace('_', ' ').title()), row=1, col=1)

    # Gráfico 2: Fronteira Eficiente (Simplificada - NÃO é a verdadeira fronteira, apenas ilustrativo com alguns pontos)
    # Gerar pontos aleatórios para ilustrar
    num_assets = len(returns_df.columns)
    n_points = 100
    returns_frontier = []
    vols_frontier = []
    for _ in range(n_points):
         rand_weights = np.random.random(num_assets)
         rand_weights /= rand_weights.sum() # Normalizar
         ret, vol = calculate_portfolio_metrics(rand_weights, returns_df) # Usando a função do módulo analysis
         returns_frontier.append(ret)
         vols_frontier.append(vol)

    fig.add_trace(go.Scatter(x=vols_frontier, y=returns_frontier, mode='markers', name='Portfólios Aleatórios', marker=dict(opacity=0.3)), row=1, col=2)
    fig.add_trace(go.Scatter(x=[perf_min_var[1]], y=[perf_min_var[0]], mode='markers', name='Min Variância', marker=dict(size=10, symbol='star', color='red')), row=1, col=2)
    fig.add_trace(go.Scatter(x=[perf_max_sharpe[1]], y=[perf_max_sharpe[0]], mode='markers', name='Max Sharpe', marker=dict(size=10, symbol='diamond', color='green')), row=1, col=2)

    fig.update_xaxes(title_text="Volatilidade Anualizada", row=1, col=2)
    fig.update_yaxes(title_text="Retorno Anualizado", row=1, col=2)


    # Gráfico 3: Composição Max Sharpe
    fig.add_trace(go.Pie(labels=returns_df.columns.str.replace('return_', '').str.replace('_', ' ').str.title(), values=weights_max_sharpe, name="Max Sharpe"), row=2, col=1)

    # Gráfico 4: Composição Min Var
    fig.add_trace(go.Pie(labels=returns_df.columns.str.replace('return_', '').str.replace('_', ' ').str.title(), values=weights_min_var, name="Min Var"), row=2, col=2)

    fig.update_layout(height=800, title_text=f"Simulação de Portfólio", showlegend=True)
    return fig

# Se a função calculate_portfolio_metrics for usada fora deste módulo, talvez deva ser importada
# ou duplicada aqui. Por simplicidade, está sendo chamada diretamente acima.
# from src.analysis.portfolio_simulation import calculate_portfolio_metrics 