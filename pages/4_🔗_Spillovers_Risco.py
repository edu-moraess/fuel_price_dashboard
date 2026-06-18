# pages/4_🔗_Spillovers_Risco.py

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

from src.load_data import filter_data_by_selection
from src.config import RISK_SPILLOVER_VAR_LAGS

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
        df_full,        countries=selected_countries_risk,
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
             st.warning("Dados insuficientes após pivotar.")
        else:
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
                nodes = corr_matrix.columns.tolist()                edges = []
                weights = []
                for i in range(len(nodes)):
                    for j in range(i+1, len(nodes)):
                        weight = abs(corr_matrix.iloc[i, j]) # Usar valor absoluto da correlação como peso
                        if weight > 0.1: # Limiar para mostrar conexão
                            edges.append((nodes[i], nodes[j]))
                            weights.append(weight)

                # Verifica se há conexões para mostrar no grafo de rede
                if edges:
                    edge_source = [nodes.index(e[0]) for e in edges]
                    edge_target = [nodes.index(e[1]) for e in edges]
                    edge_width = [w * 10 for w in weights] # Escalonar peso para espessura da linha

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
                          color = "rgba(128, 128, 128, 0.4)" # Cor fixa para as conexões
                      )))

                    fig_net.update_layout(title_text="Rede de Conectividade (Correlação > 0.1)", font_size=10)
                    st.plotly_chart(fig_net, use_container_width=True)
                else:
                    st.info("Nenhuma correlação acima do limiar de 0.1 encontrada para o gráfico de rede.")

                # Gráfico 4: Contribuição de Spillover (FEVD) - Exemplo para o primeiro país
                if fevd is not None:
                    country_for_fevd = returns_scaled.columns[0]
                    fevd_df = pd.DataFrame(fevd.decomp_dict[country_for_fevd], index=range(1, fevd.periods+1), columns=returns_scaled.columns)
                    fevd_df.index.name = 'Horizon'
                    fig_fevd = go.Figure()
                    for col in fevd_df.columns:
                         fig_fevd.add_trace(go.Scatter(x=fevd_df.index, y=fevd_df[col], mode='lines', name=col, stackgroup='one'))
                    fig_fevd.update_layout(title=f'Contribuição de Spillover (FEVD) para {country_for_fevd}', xaxis_title='Horizon (Steps)', yaxis_title='Proportion of Variance Explained')
                    st.plotly_chart(fig_fevd, use_container_width=True)

                # --- Resultados ---
                st.subheader("Resultados do Modelo VAR")
                st.text(var_results.summary())

                # Dados para download                results_df = returns_log.copy()
                results_df.columns = [f"log_return_{col}" for col in results_df.columns]

                st.download_button(
                    label="Download dos Dados Processados (Retornos)",
                    data=results_df.to_csv().encode('utf-8'),
                    file_name=f"risk_spillovers_returns_{selected_product_risk}.csv",
                    mime='text/csv',
                )

            except Exception as e:
                st.error(f"Erro ao ajustar o modelo VAR ou calcular FEVD: {e}")
                st.write("Verifique se há dados suficientes e se o número de lags é apropriado.")