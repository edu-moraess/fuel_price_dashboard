# pages/2_🔄_Regime_Switching.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

from src.load_data import filter_data_by_selection
from src.config import REGIME_SWITCHING_DEFAULT_REGIMES, REGIME_SWITCHING_PREDICTION_STEPS

# --- Configuração da Página ---
st.set_page_config(page_title="Regime Switching", page_icon="🔄", layout="wide")
st.title("🔄 Análise de Mudança de Regime - Estados de Mercado")

# --- Sidebar ---
st.sidebar.header("Filtros - Regime Switching")

# Carregar dados
df_full = st.session_state.get('df', None)
if df_full is None:
    st.error("Dados não carregados. Verifique o arquivo principal (app.py).")
    st.stop()

# Filtros da sidebar
countries_available = sorted(df_full['COUNTRY'].unique())
selected_country_regime = st.sidebar.selectbox("País", options=countries_available, index=0)

products_available = ['diesel_usd', 'gasoline_usd']
selected_product_regime = st.sidebar.selectbox("Produto", options=products_available, index=0)

start_date_regime = st.sidebar.date_input("Data Início", value=pd.to_datetime("2020-01-01"))
end_date_regime = st.sidebar.date_input("Data Fim", value=pd.to_datetime("2024-12-01"))

num_regimes = st.sidebar.slider("Número de Regimes", min_value=2, max_value=4, value=REGIME_SWITCHING_DEFAULT_REGIMES)
prediction_steps = st.sidebar.slider("Passos para Previsão", min_value=1, max_value=24, value=REGIME_SWITCHING_PREDICTION_STEPS)

# --- Lógica da Análise ---

# Filtrar dados
df_filtered = filter_data_by_selection(
    df_full,
    countries=[selected_country_regime],
    products=[selected_product_regime],
    start_date=start_date_regime.strftime("%Y-%m-%d"),
    end_date=end_date_regime.strftime("%Y-%m-%d"))

if df_filtered.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
else:
    prices = df_filtered.set_index('date')[selected_product_regime]
    returns = prices.pct_change().dropna() # Calcular retornos

    # Ajustar modelo Markov Switching
    try:
        mod = MarkovRegression(returns, k_regimes=num_regimes, trend='c', switching_variance=True)
        res = mod.fit(disp=False) # disp=False para silenciar prints do solver

        # Obter probabilidades suavizadas
        smoothed_probs = res.smoothed_marginal_probabilities

        # --- Visualização ---
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=(f'Preço - {selected_country_regime}', 'Retorno Percentual', 'Probabilidades Suavizadas por Regime'),
            specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
        )

        # Gráfico 1: Preço
        fig.add_trace(go.Scatter(x=prices.index, y=prices.values, mode='lines', name=f'Preço {selected_product_regime}', line=dict(color='blue')), row=1, col=1)

        # Gráfico 2: Retorno
        fig.add_trace(go.Scatter(x=returns.index, y=returns.values, mode='lines', name='Retorno %', line=dict(color='orange')), row=2, col=1)

        # Gráfico 3: Probabilidades
        for i in range(num_regimes):
            fig.add_trace(go.Scatter(x=smoothed_probs.index, y=smoothed_probs.iloc[:, i], mode='lines', name=f'Regime {i+1}', stackgroup='one'), row=3, col=1) # Usar stackgroup para área empilhada

        fig.update_layout(height=800, title_text=f"Mudança de Regime - {selected_country_regime} ({selected_product_regime}) - {num_regimes} Regimes", showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        # --- Resultados Estatísticos ---
        st.subheader("Resultados do Modelo Markov Switching")
        st.text(res.summary()) # Mostrar sumário do modelo

        # --- Interpretação Básica (Exemplo) ---
        st.subheader("Interpretação dos Regimes (Exemplo - Verifique o Sumário)")
        regime_info = []
        for i in range(num_regimes):
            mean_ret = res.params[f'mean[{i}]'] if f'mean[{i}]' in res.params.index else 'N/A'
            variance = res.params[f'sigma2[{i}]'] if f'sigma2[{i}]' in res.params.index else 'N/A'
            regime_info.append({
                "Regime": i+1,                "Média Retorno": mean_ret,
                "Variância": variance
            })
        st.table(pd.DataFrame(regime_info))

        # Dados para download
        results_df = pd.DataFrame({
            'date': returns.index,
            'price': prices.loc[returns.index].values, # Alinhar com retornos
            'return': returns.values,
        })
        for i in range(num_regimes):
            results_df[f'prob_regime_{i+1}'] = smoothed_probs.iloc[:, i].values

        st.download_button(
            label="Download dos Dados Processados",
            data=results_df.to_csv().encode('utf-8'),
            file_name=f"regime_switching_{selected_country_regime}_{selected_product_regime}.csv",
            mime='text/csv',
        )

    except Exception as e:
        st.error(f"Erro ao ajustar o modelo Markov Switching: {e}")
        st.write("Verifique se há dados suficientes e se o número de regimes é apropriado.")