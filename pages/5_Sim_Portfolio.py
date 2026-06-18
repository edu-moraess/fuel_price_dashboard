# pages/5_💼_Sim_Portfolio.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

from src.load_data import filter_data_by_selection
from src.config import PORTFOLIO_SIMULATION_DEFAULT_N_ASSETS, PORTFOLIO_SIMULATION_RETURN_COLUMN

# --- Configuração da Página ---
st.set_page_config(page_title="Simulação de Portfólio", page_icon="💼", layout="wide")
st.title("💼 Simulação de Portfólio com Ativos Derivados de Preços de Combustíveis")

# --- Sidebar ---
st.sidebar.header("Filtros - Simulação de Portfólio")

# Carregar dados
df_full = st.session_state.get('df', None)
if df_full is None:
    st.error("Dados não carregados. Verifique o arquivo principal (app.py).")
    st.stop()

# Filtros da sidebar
countries_available = sorted(df_full['COUNTRY'].unique())
selected_countries_port = st.sidebar.multiselect("Países (Até 5)", options=countries_available, default=countries_available[:PORTFOLIO_SIMULATION_DEFAULT_N_ASSETS])

products_available = ['diesel_usd', 'gasoline_usd']
selected_products_port = st.sidebar.multiselect("Produto por País (Mesmo número de países)", options=products_available, default=['diesel_usd']*len(selected_countries_port))

start_date_port = st.sidebar.date_input("Data Início", value=pd.to_datetime("2020-01-01"))
end_date_port = st.sidebar.date_input("Data Fim", value=pd.to_datetime("2024-12-01"))

# Garantir que número de países e produtos seja igual
if len(selected_countries_port) != len(selected_products_port):
     st.warning("Número de países e produtos selecionados deve ser igual.")
     st.stop()

# --- Lógica da Análise ---

if len(selected_countries_port) < 2:
    st.warning("Selecione pelo menos 2 países para simulação de portfólio.")
else:
    # Filtrar dados para todos os pares país-produto selecionados
    dfs_list = []
    for country, product in zip(selected_countries_port, selected_products_port):        df_temp = filter_data_by_selection(
            df_full,
            countries=[country],
            products=[product],
            start_date=start_date_port.strftime("%Y-%m-%d"),
            end_date=end_date_port.strftime("%Y-%m-%d")
        )
        if not df_temp.empty:
            # Renomear coluna de preço para identificar o 'ativo'
            df_temp.rename(columns={product: f'return_{country}_{product}'}, inplace=True)
            # Calcular retornos logarítmicos
            df_temp[f'return_{country}_{product}'] = np.log(df_temp[f'return_{country}_{product}'] / df_temp[f'return_{country}_{product}'].shift(1))
            dfs_list.append(df_temp[['date', f'return_{country}_{product}']].set_index('date'))

    if not dfs_list:
         st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        # Concatenar retornos de todos os 'ativos'
        returns_df = pd.concat(dfs_list, axis=1).dropna()

        if returns_df.empty or returns_df.shape[1] < 2:
             st.warning("Dados insuficientes para calcular retornos ou criar portfólio.")
        else:

            # --- Funções de Otimização ---
            def portfolio_performance(weights, returns):
                """Calcula retorno e volatilidade anualizados do portfólio."""
                returns_mean = returns.mean() * 12  # Anualizar (12 meses)
                returns_cov = returns.cov() * 12    # Anualizar
                portfolio_return = np.sum(weights * returns_mean)
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns_cov, weights)))
                return portfolio_return, portfolio_volatility

            def negative_sharpe_ratio(weights, returns, risk_free_rate=0.02): # Assumindo taxa livre de risco anual de 2%
                """Função objetivo para maximizar o Sharpe Ratio (minimizar negativo)."""
                p_return, p_vol = portfolio_performance(weights, returns)
                return -(p_return - risk_free_rate) / p_vol

            def portfolio_variance(weights, returns):
                """Função objetivo para minimizar a variância (volatilidade^2)."""
                _, p_vol = portfolio_performance(weights, returns)
                return p_vol**2

            def equal_weight_constraint(weights):
                """Restrição: soma dos pesos = 1."""
                return np.sum(weights) - 1.0

            def individual_weight_limit(weights, limit=0.5): # Limite máximo de 50% por ativo
                """Restrição: limite máximo por peso."""
                return limit - weights
            # --- Otimização ---
            num_assets = len(returns_df.columns)
            initial_weights = np.array([1 / num_assets] * num_assets) # Pesos iguais iniciais

            constraints = [{'type': 'eq', 'fun': equal_weight_constraint}]
            bounds = tuple((0, 1) for _ in range(num_assets)) # Pesos entre 0 e 1
            # Adicionar limite por ativo
            for i in range(num_assets):
                 constraints.append({'type': 'ineq', 'fun': lambda w, idx=i, lim=0.5: individual_weight_limit(w, lim)[idx]})

            # Otimizar para Sharpe Ratio Máximo
            result_max_sharpe = minimize(negative_sharpe_ratio, initial_weights, args=(returns_df,), method='SLSQP', bounds=bounds, constraints=constraints)
            weights_max_sharpe = result_max_sharpe.x
            perf_max_sharpe = portfolio_performance(weights_max_sharpe, returns_df)

            # Otimizar para Variância Mínima
            result_min_var = minimize(portfolio_variance, initial_weights, args=(returns_df,), method='SLSQP', bounds=bounds, constraints=constraints)
            weights_min_var = result_min_var.x
            perf_min_var = portfolio_performance(weights_min_var, returns_df)

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
            n_points = 100
            returns_frontier = []
            vols_frontier = []
            for _ in range(n_points):
                 rand_weights = np.random.random(num_assets)
                 rand_weights /= rand_weights.sum() # Normalizar
                 ret, vol = portfolio_performance(rand_weights, returns_df)
                 returns_frontier.append(ret)
                 vols_frontier.append(vol)

            fig.add_trace(go.Scatter(x=vols_frontier, y=returns_frontier, mode='markers', name='Portfólios Aleatórios', marker=dict(opacity=0.3)), row=1, col=2)
            fig.add_trace(go.Scatter(x=[perf_min_var[1]], y=[perf_min_var[0]], mode='markers', name='Min Variância', marker=dict(size=10, symbol='star', color='red')), row=1, col=2)
            fig.add_trace(go.Scatter(x=[perf_max_sharpe[1]], y=[perf_max_sharpe[0]], mode='markers', name='Max Sharpe', marker=dict(size=10, symbol='diamond', color='green')), row=1, col=2)

            fig.update_xaxes(title_text="Volatilidade Anualizada", row=1, col=2)            fig.update_yaxes(title_text="Retorno Anualizado", row=1, col=2)


            # Gráfico 3: Composição Max Sharpe
            fig.add_trace(go.Pie(labels=returns_df.columns.str.replace('return_', '').str.replace('_', ' ').str.title(), values=weights_max_sharpe, name="Max Sharpe"), row=2, col=1)

            # Gráfico 4: Composição Min Var
            fig.add_trace(go.Pie(labels=returns_df.columns.str.replace('return_', '').str.replace('_', ' ').str.title(), values=weights_min_var, name="Min Var"), row=2, col=2)

            fig.update_layout(height=800, title_text=f"Simulação de Portfólio - {len(selected_countries_port)} Ativos Derivados de Preços", showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            # --- Resultados ---
            st.subheader("Resultados da Otimização")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Portfólio Max Sharpe")
                st.metric(label="Retorno Anualizado", value=f"{perf_max_sharpe[0]:.2%}")
                st.metric(label="Volatilidade Anualizada", value=f"{perf_max_sharpe[1]:.2%}")
                st.metric(label="Sharpe Ratio", value=f"{(perf_max_sharpe[0] - 0.02) / perf_max_sharpe[1]:.2f}")
                st.write("**Composição dos Pesos:**")
                for asset, weight in zip(returns_df.columns, weights_max_sharpe):
                     st.write(f"- {asset.replace('return_', '').replace('_', ' ').title()}: {weight:.2%}")

            with col2:
                st.markdown("#### Portfólio Min Variância")
                st.metric(label="Retorno Anualizado", value=f"{perf_min_var[0]:.2%}")
                st.metric(label="Volatilidade Anualizada", value=f"{perf_min_var[1]:.2%}")
                st.metric(label="Sharpe Ratio", value=f"{(perf_min_var[0] - 0.02) / perf_min_var[1]:.2f}")
                st.write("**Composição dos Pesos:**")
                for asset, weight in zip(returns_df.columns, weights_min_var):
                     st.write(f"- {asset.replace('return_', '').replace('_', ' ').title()}: {weight:.2%}")

            # Dados para download
            results_df = returns_df.copy()
            results_df['portfolio_return_max_sharpe'] = (returns_df * weights_max_sharpe).sum(axis=1)
            results_df['portfolio_return_min_var'] = (returns_df * weights_min_var).sum(axis=1)

            st.download_button(
                label="Download dos Dados Processados (Retornos e Portfólios)",
                data=results_df.to_csv().encode('utf-8'),
                file_name=f"portfolio_simulation_returns.csv",
                mime='text/csv',
            )
