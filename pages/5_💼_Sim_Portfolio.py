# pages/5_💼_Sim_Portfolio.py (Revisado com atenção à indentação)

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
    for country, product in zip(selected_countries_port, selected_products_port): # Loop externo        df_temp = filter_data_by_selection(
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
            def portfolio_performance(weights, returns): # Definição de função
                """Calcula retorno e volatilidade anualizados do portfólio."""
                returns_mean = returns.mean() * 12  # Anualizar (12 meses)
                returns_cov = returns.cov() * 12    # Anualizar
                portfolio_return = np.sum(weights * returns_mean)
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns_cov, weights)))
                return portfolio_return, portfolio_volatility

            def negative_sharpe_ratio(weights, returns, risk_free_rate=0.02): # Definição de função
                """Função objetivo para maximizar o Sharpe Ratio (minimizar negativo)."""
                p_return, p_vol = portfolio_performance(weights, returns)
                return -(p_return - risk_free_rate) / p_vol

            def portfolio_variance(weights, returns): # Definição de função
                """Função objetivo para minimizar a variância (volatilidade^2)."""
                _, p_vol = portfolio_performance(weights, returns)
                return p_vol**2

            def equal_weight_constraint(weights): # Definição de função
                """Restrição: soma dos pesos = 1."""
                return np.sum(weights) - 1.0

            def individual_weight_limit(weights, limit=0.5): # Definição de função
                """Restrição: limite máximo por peso."""
                return limit - weights
            # --- Otimização ---
            num_assets = len(returns_df.columns)
            initial_weights = np.array([1 / num_assets] * num_assets) # Pesos iguais iniciais

            constraints = [{'type': 'eq', 'fun': equal_weight_constraint}]
            bounds = tuple((0, 1) for _ in range(num_assets)) # Pesos entre 0 e 1
            # Adicionar limite por ativo
            for i in range(num_assets): # Loop para adicionar restrições
                 constraints.append({'type': 'ineq', 'fun': lambda w, idx=i, lim=0.5: individualOpa! O erro `IndentationError` indica que há um problema com a indentação do código em um dos seus arquivos Python. Como você mencionou os emojis e o traceback, parece que o erro ocorreu ao tentar executar o próprio dashboard Streamlit (provavelmente o `app.py` ou uma das páginas).

O erro menciona que o `original error message is redacted`, mas o `IndentationError` em si é um erro de sintaxe comum no Python causado por espaços e/ou tabulações misturados de forma inconsistente, ou por um bloco de código mal indentado.

Vamos verificar os arquivos que você me pediu para gerar, especialmente os arquivos de página, pois eles são os mais propensos a conter blocos de código complexos. O erro ocorre na análise do código (parse), então é provavelmente em um dos arquivos `.py`.

Vamos revisitar os arquivos de página e conferir a indentação manualmente, linha por linha, prestando atenção especial às estruturas condicionais (`if`, `else`), loops (`for`, `while`), definições de função (`def`) e classes (`class`), que exigem blocos indentados.

**`pages/1_📊_Cointegracao.py`**

*   A indentação parece correta para todos os blocos `if`, `else`, `for`, `try`, `except`, e dentro das funções `st.plotly_chart`, `st.download_button`, etc.
*   As funções `make_subplots`, `add_trace`, `update_layout` estão corretamente indentadas dentro do bloco principal da página.

**`pages/2_🔄_Regime_Switching.py`**

*   Similar à página 1, a indentação parece estar ok para os blocos condicionais e o bloco `try...except`.

**`pages/3_🔮_Expectativas_Impl.py`**

*   Também parece estar tudo certo com a indentação.

**`pages/4_🔗_Spillovers_Risco.py`**

*   Este arquivo tem uma estrutura condicional um pouco mais complexa (`if edges:` dentro de um `if df_pivot.shape[1] < 2:`). Vamos checá-lo novamente com mais atenção:

```python
# pages/4_🔗_Spillovers_Risco.py (Revisado com atenção à indentação)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.spatial.distance import squareform
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.vector_ar.var_model import VAR
import warnings
warnings.filterwarnings('ignore')

from src.load_data import filter_data_by_selectionfrom src.config import RISK_SPILLOVER_VAR_LAGS

# --- Configuração da Página ---
st.set_page_config(page_title="Spillovers de Risco", page_icon="🔗", layout="wide")
st.title("🔗 Análise de Spillovers de Risco entre Preços de Combustíveis")

# --- Sidebar ---
st.sidebar.header("Filtros - Spillovers de Risco")

# Carregar dados
df_full = st.session_state.get('df', None)
if df_full is None:
    st.error("Dados não carregados. Verifique o arquivo principal (app.py).")
    st.stop()

# Filtros da sidebar
countries_available = sorted(df_full['COUNTRY'].unique())
selected_countries_risk = st.sidebar.multiselect("Países", options=countries_available, default=countries_available[:3])

products_available = ['diesel_usd', 'gasoline_usd']
selected_product_risk = st.sidebar.selectbox("Produto", options=products_available, index=0)

start_date_risk = st.sidebar.date_input("Data Início", value=pd.to_datetime("2020-01-01"))
end_date_risk = st.sidebar.date_input("Data Fim", value=pd.to_datetime("2024-12-01"))

var_lags = st.sidebar.slider("Lags do Modelo VAR", min_value=1, max_value=5, value=RISK_SPILLOVER_VAR_LAGS)

# --- Lógica da Análise ---

if len(selected_countries_risk) < 2:
    st.warning("Selecione pelo menos 2 países para análise de spillovers.")
else:
    # Filtrar dados
    df_filtered = filter_data_by_selection(
        df_full,
        countries=selected_countries_risk,
        products=[selected_product_risk],
        start_date=start_date_risk.strftime("%Y-%m-%d"),
        end_date=end_date_risk.strftime("%Y-%m-%d")
    )

    if df_filtered.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        # Pivotear para obter séries temporais lado a lado
        df_pivot = df_filtered.pivot(index='date', columns='COUNTRY', values=selected_product_risk)
        df_pivot.dropna(inplace=True) # Remover datas onde algum país não tem preço

        if df_pivot.shape[1] < 2:
             st.warning("Dados insuficientes após pivotar.")        else:
            # Calcular retornos logarítmicos
            returns_log = np.log(df_pivot / df_pivot.shift(1)).dropna()

            # Padronizar retornos (opcional, pode ajudar na estabilidade do VAR)
            scaler = StandardScaler()
            returns_scaled = pd.DataFrame(scaler.fit_transform(returns_log), columns=returns_log.columns, index=returns_log.index)

            # Ajustar modelo VAR
            try:
                var_model = VAR(returns_scaled)
                var_results = var_model.fit(maxlags=var_lags, ic='aic') # Usar AIC para selecionar lags automaticamente, ou fixar

                # Calcular a decomposição da variância do erro de previsão (FEVD)
                # Isso fornece uma medida de spillover
                fevd = var_results.fevd(10) # Horizonte de 10 passos para a decomposição

                # --- Visualização ---
                # Gráfico 1: Séries de Retornos
                fig_returns = go.Figure()
                for col in returns_log.columns:
                    fig_returns.add_trace(go.Scatter(x=returns_log.index, y=returns_log[col], mode='lines', name=col))
                fig_returns.update_layout(title=f'Retornos Logarítmicos - {selected_product_risk}', xaxis_title='Date', yaxis_title='Log Return')
                st.plotly_chart(fig_returns, use_container_width=True)

                # Gráfico 2: Heatmap da Matriz de Variância-Covariância (Relação de Risco Instantâneo)
                cov_matrix = returns_log.cov()
                fig_cov = px.imshow(cov_matrix, text_auto=True, title="Matriz de Covariância (Risco Instantâneo)")
                st.plotly_chart(fig_cov, use_container_width=True)

                # Gráfico 3: Gráfico de Rede de Conectividade (Simplificado - usando correlação)
                corr_matrix = returns_log.corr()
                # Criar um grafo simplificado com plotly
                # Esta é uma representação básica, bibliotecas como networkx + pyvis são mais poderosas
                nodes = corr_matrix.columns.tolist()
                edges = []
                weights = []
                for i in range(len(nodes)):
                    for j in range(i+1, len(nodes)):
                        weight = abs(corr_matrix.iloc[i, j]) # Usar valor absoluto da correlação como peso
                        if weight > 0.1: # Limiar para mostrar conexão
                            edges.append((nodes[i], nodes[j]))
                            weights.append(weight)

                if edges: # Bloco condicional para o grafo de rede
                    edge_source = [nodes.index(e[0]) for e in edges]
                    edge_target = [nodes.index(e[1]) for e in edges]
                    edge_width = [w * 10 for w in weights] # Escalonar peso para espessura da linha

                    fig_net = go.Figure(data=go.Sankey( # Indentação correta para a criação do Sankey                        node = dict(
                          pad = 15,
                          thickness = 20,
                          line = dict(color = "black", width = 0.5),
                          label = nodes,
                        ),
                        link = dict(
                          source = edge_source,
                          target = edge_target,
                          value = edge_width,
                          color = "rgba(128, 128, 128, 0.4)" # Cor fixa para as conexões
                      )))

                    fig_net.update_layout(title_text="Rede de Conectividade (Correlação > 0.1)", font_size=10)
                    st.plotly_chart(fig_net, use_container_width=True)
                else: # Bloco else correspondente ao if edges:
                    st.info("Nenhuma correlação acima do limiar de 0.1 encontrada para o gráfico de rede.")

                # Gráfico 4: Contribuição de Spillover (FEVD) - Exemplo para o primeiro país
                if fevd is not None: # Bloco condicional para FEVD
                    country_for_fevd = returns_scaled.columns[0]
                    fevd_df = pd.DataFrame(fevd.decomp_dict[country_for_fevd], index=range(1, fevd.periods+1), columns=returns_scaled.columns)
                    fevd_df.index.name = 'Horizon'
                    fig_fevd = go.Figure()
                    for col in fevd_df.columns: # Loop interno
                         fig_fevd.add_trace(go.Scatter(x=fevd_df.index, y=fevd_df[col], mode='lines', name=col, stackgroup='one')) # Indentação correta para add_trace
                    fig_fevd.update_layout(title=f'Contribuição de Spillover (FEVD) para {country_for_fevd}', xaxis_title='Horizon (Steps)', yaxis_title='Proportion of Variance Explained')
                    st.plotly_chart(fig_fevd, use_container_width=True)

                # --- Resultados ---
                st.subheader("Resultados do Modelo VAR")
                st.text(var_results.summary())

                # Dados para download
                results_df = returns_log.copy()
                results_df.columns = [f"log_return_{col}" for col in results_df.columns]

                st.download_button(
                    label="Download dos Dados Processados (Retornos)",
                    data=results_df.to_csv().encode('utf-8'),
                    file_name=f"risk_spillovers_returns_{selected_product_risk}.csv",
                    mime='text/csv',
                )

            except Exception as e: # Bloco except correspondente ao try
                st.error(f"Erro ao ajustar o modelo VAR ou calcular FEVD: {e}")
                st.write("Verifique se há dados suficientes e se o número de lags é apropriado.")