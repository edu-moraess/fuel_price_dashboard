# src/visualization/risk_spillovers_plots.py

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


def plot_spillover_overview(returns_log, cov_matrix, corr_matrix):
    """
    Plota visualizações gerais para análise de spillovers (retornos, cov, corr).

    Args:
        returns_log (pd.DataFrame): DataFrame de retornos logarítmicos.
        cov_matrix (pd.DataFrame): Matriz de covariância.
        corr_matrix (pd.DataFrame): Matriz de correlação.

    Returns:
        tuple: (fig_returns, fig_cov, fig_corr) Objetos das figuras Plotly.
    """
    # Gráfico 1: Séries de Retornos
    fig_returns = go.Figure()
    for col in returns_log.columns:
        fig_returns.add_trace(go.Scatter(x=returns_log.index, y=returns_log[col], mode='lines', name=col))
    fig_returns.update_layout(title='Retornos Logarítmicos', xaxis_title='Date', yaxis_title='Log Return')

    # Gráfico 2: Heatmap da Matriz de Covariância
    fig_cov = px.imshow(cov_matrix, text_auto=True, title="Matriz de Covariância (Risco Instantâneo)")

    # Gráfico 3: Heatmap da Matriz de Correlação
    fig_corr = px.imshow(corr_matrix, text_auto=True, title="Matriz de Correlação (Conectividade Linear)")

    return fig_returns, fig_cov, fig_corr

def plot_network_simple(corr_matrix, threshold=0.1):
    """
    Plota um grafo de rede simplificado (Sankey) com base na correlação.

    Args:
        corr_matrix (pd.DataFrame): Matriz de correlação.
        threshold (float): Limiar para mostrar conexão.

    Returns:
        plotly.graph_objects.Figure or None: Figura Sankey ou None se não houver conexões acima do limiar.
    """
    nodes = corr_matrix.columns.tolist()
    edges = []
    weights = []
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):            weight = abs(corr_matrix.iloc[i, j])
            if weight > threshold:
                edges.append((nodes[i], nodes[j]))
                weights.append(weight)

    if not edges:
        return None # Nenhuma conexão acima do limiar

    edge_source = [nodes.index(e[0]) for e in edges]
    edge_target = [nodes.index(e[1]) for e in edges]
    edge_width = [w * 10 for w in weights]

    fig_net = go.Figure(data=go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = nodes,
        ),
        link = dict(
          source = edge_source,
          target = edge_target,
          value = edge_width,
          color = "rgba(128, 128, 128, 0.4)"
      )))

    fig_net.update_layout(title_text=f"Rede de Conectividade (|Corr| > {threshold})", font_size=10)
    return fig_net

def plot_fevd(fevd_result, asset_name):
    """
    Plota a Decomposição da Variância do Erro de Previsão (FEVD) para um ativo.

    Args:
        fevd_result (FEVD object): Objeto resultante do cálculo FEVD.
        asset_name (str): Nome do ativo para título.

    Returns:
        plotly.graph_objects.Figure or None: Figura FEVD ou None se falhar.
    """
    if fevd_result is not None and hasattr(fevd_result, 'decomp_dict'):
        # Exemplo: pegar a decomposição para o primeiro ativo
        # Você pode querer selecionar o ativo com base na entrada
        decomp_data = fevd_result.decomp_dict.get(asset_name, None)
        if decomp_data is not None:
            decomp_df = pd.DataFrame(decomp_data, index=range(1, fevd_result.periods+1), columns=fevd_result.names)
            decomp_df.index.name = 'Horizon'

            fig_fevd = go.Figure()
            for col in decomp_df.columns:                 fig_fevd.add_trace(go.Scatter(x=decomp_df.index, y=decomp_df[col], mode='lines', name=col, stackgroup='one'))
            fig_fevd.update_layout(title=f'Contribuição de Spillover (FEVD) para {asset_name}', xaxis_title='Horizon (Steps)', yaxis_title='Proportion of Variance Explained')
            return fig_fevd
    return None