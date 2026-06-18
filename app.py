# app.py (Revisado com atenção à indentação)

import streamlit as st
import pandas as pd
from src.load_data import load_and_preprocess_data
from src.config import DATA_PATH

# --- Configuração da Página ---
st.set_page_config(
    page_title="Fuel Price Insights",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Título do Dashboard ---
st.title("⛽ Fuel Price Insights Dashboard")
st.markdown("### Análise Quantitativa Avançada de Preços de Combustíveis (IEA)")

# --- Carregamento de Dados Inicial ---
@st.cache_data # Decorator
def get_data(): # Definição de função
    df = load_and_preprocess_data(DATA_PATH)
    return df

df = get_data()

# Armazenar o dataframe carregado no session_state para compartilhar com as páginas
if 'df' not in st.session_state:
    st.session_state['df'] = df

# --- Sidebar Global ---
st.sidebar.header("Configurações Globais")

# Exemplo de filtro global (poderia ser usado em todas as páginas)
# available_countries = st.session_state.df['COUNTRY'].unique() if not st.session_state.df.empty else []
# global_countries_filter = st.sidebar.multiselect("Países (Global)", options=available_countries, default=available_countries)

# --- Mensagem Inicial na Home ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

if st.session_state.page == "Home": # Bloco condicional
    st.info("Bem-vindo ao Dashboard de Insights de Preços de Combustíveis!")
    st.write("Selecione uma análise no menu lateral esquerdo.")
    # Mostrar informações básicas sobre os dados carregados
    if not df.empty: # Bloco condicional aninhado
        st.write("**Informações sobre os dados carregados:**")
        st.write(f"- Total de registros: {len(df)}")
        st.write(f"- Período: {df['date'].min()} a {df['date'].max()}")
        st.write(f"- Países disponíveis: {df['COUNTRY'].nunique()}")
        st.write(f"- Produtos disponíveis: {', '.join([col.replace('_usd', '').title() for col in ['diesel_usd', 'gasoline_usd'] if col in df.columns])}")

# A navegação é feita automaticamente pelo Streamlit com base nos arquivos em 'pages/'