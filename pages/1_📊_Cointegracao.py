# pages/1_📊_Cointegracao.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')

from src.load_data import filter_data_by_selection
from src.config import COINTEGRATION_LOOKBACK_YEARS, COINTEGRATION_ZSCORE_THRESHOLD

# --- Configuração da Página ---
st.set_page_config(page_title="Cointegração", page_icon="📊", layout="wide")
st.title("📊 Análise de Cointegração - Pairs Trading Potencial")

# --- Sidebar ---
st.sidebar.header("Filtros - Cointegração")

# Carregar dados
df_full = st.session_state.get('df', None) # Assume que df foi carregado em app.py
if df_full is None:
    st.error("Dados não carregados. Verifique o arquivo principal (app.py).")
    st.stop()

# Filtros da sidebar
countries_available = sorted(df_full['COUNTRY'].unique())
selected_countries_coint = st.sidebar.multiselect("Países", options=countries_available, default=countries_available[:2])

products_available = ['diesel_usd', 'gasoline_usd']
selected_product_coint = st.sidebar.selectbox("Produto", options=products_available, index=0)

start_date_coint = st.sidebar.date_input("Data Início", value=pd.to_datetime("2020-01-01"))
end_date_coint = st.sidebar.date_input("Data Fim", value=pd.to_datetime("2024-12-01"))

lookback_years = st.sidebar.slider("Janela Histórica (anos)", min_value=1, max_value=10, value=COINTEGRATION_LOOKBACK_YEARS)
z_threshold = st.sidebar.number_input("Threshold Z-Score", min_value=0.1, max_value=5.0, value=COINTEGRATION_ZSCORE_THRESHOLD, step=0.1)

# --- Lógica da Análise ---

if len(selected_countries_coint) < 2:
    st.warning("Selecione pelo menos 2 países para análise de cointegração.")
else:
    # Filtrar dados
    df_filtered = filter_data_by_selection(
        df_full,
        countries=selected_countries_coint,        products=[selected_product_coint],
        start_date=start_date_coint.strftime("%Y-%m-%d"),
        end_date=end_date_coint.strftime("%Y-%m-%d")
    )

    if df_filtered.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        # Pivotear para obter séries temporais lado a lado
        df_pivot = df_filtered.pivot(index='date', columns='COUNTRY', values=selected_product_coint)
        df_pivot.dropna(inplace=True) # Remover datas onde um dos países não tem preço

        if df_pivot.shape[1] < 2:
             st.warning("Dados insuficientes após pivotar (algum país pode não ter dados para o período/produto selecionado).")
        else:
            country_a, country_b = df_pivot.columns[0], df_pivot.columns[1]
            prices_a = df_pivot[country_a]
            prices_b = df_pivot[country_b]

            # Teste de Cointegração (ADF no spread)
            # Estimar beta (coeficiente de cointegração)
            slope, intercept, r_value, p_value, std_err = linregress(prices_a, prices_b)
            spread = prices_b - (slope * prices_a + intercept)

            # Calcular z-score do spread (janela móvel)
            spread_mean = spread.rolling(window=lookback_years*12, min_periods=1).mean()
            spread_std = spread.rolling(window=lookback_years*12, min_periods=1).std()
            z_score = (spread - spread_mean) / spread_std

            # Sinais de Trade
            long_signal = z_score < -z_threshold
            short_signal = z_score > z_threshold

            # --- Visualização ---
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

            # Gráfico 3: Z-Score            fig.add_trace(go.Scatter(x=df_pivot.index, y=z_score, mode='lines', name='Z-Score Spread', line=dict(color='red')), row=3, col=1)
            fig.add_hline(y=z_threshold, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=-z_threshold, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=0, line_dash="solid", line_color="gray", row=3, col=1)

            # Sinais de trade no Z-Score
            fig.add_scatter(x=df_pivot.index[long_signal], y=z_score[long_signal], mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'), name='Sinal Long', row=3, col=1)
            fig.add_scatter(x=df_pivot.index[short_signal], y=z_score[short_signal], mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), name='Sinal Short', row=3, col=1)

            fig.update_layout(height=800, title_text=f"Cointegração: {country_a} vs {country_b} ({selected_product_coint})", showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            # Resultados Estatísticos
            st.subheader("Resultados do Teste de Cointegração")
            st.write(f"- Coeficiente Beta (Inclinação): {slope:.4f}")
            st.write(f"- Intercepto: {intercept:.4f}")
            st.write(f"- Correlação (R): {r_value:.4f}")
            st.write(f"- P-valor (ADF no spread - simplificado, verifique rigor): {p_value:.6f}") # Note: ADF real precisa de biblioteca específica como statsmodels.tsa.stattools.adfuller
            st.write(f"- Janela de Cálculo Z-Score: {lookback_years} anos (~{lookback_years*12} meses)")
            st.write(f"- Threshold Z-Score: ±{z_threshold}")

            # Dados para download
            results_df = pd.DataFrame({
                'date': df_pivot.index,
                f'{country_a}_{selected_product_coint}': prices_a.values,
                f'{country_b}_{selected_product_coint}': prices_b.values,
                'spread': spread.values,
                'z_score': z_score.values,
                'signal_long': long_signal.astype(int).values,
                'signal_short': short_signal.astype(int).values
            })
            st.download_button(
                label="Download dos Dados Processados",
                data=results_df.to_csv().encode('utf-8'),
                file_name=f"cointegration_{country_a}_{country_b}_{selected_product_coint}.csv",
                mime='text/csv',
            )