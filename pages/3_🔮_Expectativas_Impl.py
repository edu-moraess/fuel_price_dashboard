# pages/3_🔮_Expectativas_Impl.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

from src.load_data import filter_data_by_selection
from src.config import IMPLIED_EXPECT_SHORT_WINDOW, IMPLIED_EXPECT_LONG_WINDOW

# --- Configuração da Página ---
st.set_page_config(page_title="Expectativas Implícitas", page_icon="🔮", layout="wide")
st.title("🔮 Índice de Expectativas Implícitas de Preços")

# --- Sidebar ---
st.sidebar.header("Filtros - Expectativas Implícitas")

# Carregar dados
df_full = st.session_state.get('df', None)
if df_full is None:
    st.error("Dados não carregados. Verifique o arquivo principal (app.py).")
    st.stop()

# Filtros da sidebar
countries_available = sorted(df_full['COUNTRY'].unique())
selected_country_exp = st.sidebar.selectbox("País", options=countries_available, index=0)

products_available = ['diesel_usd', 'gasoline_usd']
selected_product_exp = st.sidebar.selectbox("Produto", options=products_available, index=0)

start_date_exp = st.sidebar.date_input("Data Início", value=pd.to_datetime("2020-01-01"))
end_date_exp = st.sidebar.date_input("Data Fim", value=pd.to_datetime("2024-12-01"))

short_window = st.sidebar.slider("Janela Curta (meses)", min_value=1, max_value=24, value=IMPLIED_EXPECT_SHORT_WINDOW)
long_window = st.sidebar.slider("Janela Longa (meses)", min_value=6, max_value=60, value=IMPLIED_EXPECT_LONG_WINDOW)

# --- Lógica da Análise ---

# Filtrar dados
df_filtered = filter_data_by_selection(
    df_full,
    countries=[selected_country_exp],
    products=[selected_product_exp],
    start_date=start_date_exp.strftime("%Y-%m-%d"),
    end_date=end_date_exp.strftime("%Y-%m-%d")
)

if df_filtered.empty:    st.warning("Nenhum dado encontrado com os filtros selecionados.")
else:
    prices = df_filtered.set_index('date')[selected_product_exp]

    # Calcular médias móveis
    ma_short = prices.rolling(window=short_window, min_periods=1).mean()
    ma_long = prices.rolling(window=long_window, min_periods=1).mean()

    # Índice de Expectativa: função do spread (ma_short - ma_long) e sua variação
    spread_ma = ma_short - ma_long
    # Normalizar o spread usando percentis para criar um índice entre -1 e 1 (exemplo)
    # Outra opção: (spread_ma - spread_ma.rolling(long_window*2).min()) / (spread_ma.rolling(long_window*2).max() - spread_ma.rolling(long_window*2).min()) * 2 - 1
    # Aqui, vamos usar Z-score da diferença normalizada pela volatilidade do spread
    spread_vol = spread_ma.rolling(window=long_window).std()
    normalized_spread = (spread_ma - ma_long.mean()) / ma_long.std() # Exemplo alternativo
    # Índice baseado no Z-score do spread em relação à sua própria volatilidade
    expectation_index = spread_ma / (spread_vol + 1e-8) # Adiciona pequeno valor para evitar divisão por zero

    # Calcular percentis para zonas de overbought/oversold
    perc_high = expectation_index.rolling(window=long_window*2).quantile(0.8)
    perc_low = expectation_index.rolling(window=long_window*2).quantile(0.2)


    # --- Visualização ---
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(f'Preço - {selected_country_exp}', f'Médias Móveis ({short_window}m vs {long_window}m)', 'Índice de Expectativa'),
        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
    )

    # Gráfico 1: Preço
    fig.add_trace(go.Scatter(x=prices.index, y=prices.values, mode='lines', name=f'Preço {selected_product_exp}', line=dict(color='blue')), row=1, col=1)

    # Gráfico 2: Médias Móveis
    fig.add_trace(go.Scatter(x=prices.index, y=ma_short.values, mode='lines', name=f'Média Curta ({short_window}m)', line=dict(color='orange')), row=2, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=ma_long.values, mode='lines', name=f'Média Longa ({long_window}m)', line=dict(color='red')), row=2, col=1)

    # Gráfico 3: Índice de Expectativa
    fig.add_trace(go.Scatter(x=prices.index, y=expectation_index.values, mode='lines', name='Índice de Expectativa', line=dict(color='purple')), row=3, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=perc_high.values, mode='lines', name='Limiar Superior (80%)', line=dict(color='lightcoral', dash='dash')), row=3, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=perc_low.values, mode='lines', name='Limiar Inferior (20%)', line=dict(color='lightgreen', dash='dash')), row=3, col=1)
    fig.add_hline(y=0, line_dash="solid", line_color="gray", row=3, col=1)


    fig.update_layout(height=800, title_text=f"Índice de Expectativas - {selected_country_exp} ({selected_product_exp})", showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # --- Resultados ---    st.subheader("Resultados")
    latest_index_value = expectation_index.iloc[-1]
    latest_price = prices.iloc[-1]
    latest_ma_short = ma_short.iloc[-1]
    latest_ma_long = ma_long.iloc[-1]

    st.metric(label="Preço Atual", value=f"{latest_price:.4f}")
    st.metric(label="Média Curta", value=f"{latest_ma_short:.4f}")
    st.metric(label="Média Longa", value=f"{latest_ma_long:.4f}")
    st.metric(label="Índice de Expectativa Atual", value=f"{latest_index_value:.4f}")


    # Dados para download
    results_df = pd.DataFrame({
        'date': prices.index,
        f'{selected_product_exp}': prices.values,
        f'ma_{short_window}m': ma_short.values,
        f'ma_{long_window}m': ma_long.values,
        'spread_ma': spread_ma.values,
        'expectation_index': expectation_index.values,
        'threshold_high': perc_high.values,
        'threshold_low': perc_low.values
    })

    st.download_button(
        label="Download dos Dados Processados",
        data=results_df.to_csv().encode('utf-8'),
        file_name=f"expectation_index_{selected_country_exp}_{selected_product_exp}.csv",
        mime='text/csv',
    )