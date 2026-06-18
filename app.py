import streamlit as st
import pandas as pd
from src.load_data import load_and_preprocess_data
from src.config import DATA_PATH

# --- Configuração da Página ---
st.set_page_config(
    page_title="Fuel Price Insights",
    page_icon="⛽",
    layout="wide", # Layout mais amplo
    initial_sidebar_state="expanded", # Sidebar expandida por padrão
)

# --- Título do Dashboard ---
st.title("⛽ Fuel Price Insights Dashboard")
st.markdown("### Análise Quantitativa Avançada de Preços de Combustíveis (IEA)")

# --- Carregamento de Dados Inicial ---
@st.cache_data # Cache para otimizar o carregamento
def get_data():
    df = load_and_preprocess_data(DATA_PATH)
    return df

df = get_data()

# --- Sidebar Global ---
st.sidebar.header("Configurações Globais")

# Aqui você pode adicionar filtros globais se necessário,
# embora cada página terá sua própria sidebar específica.
# Exemplo:
# selected_global_countries = st.sidebar.multiselect("Países (Global)", options=df['COUNTRY'].unique())

# --- Mensagem Inicial na Home ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

if st.session_state.page == "Home":
    st.info("Bem-vindo ao Dashboard de Insights de Preços de Combustíveis!")
    st.write("Selecione uma análise no menu lateral esquerdo.")
    # Você pode exibir uma visão geral aqui se quiser, ou deixar como página de boas-vindas.
    # Porém, para 5 abas dedicadas, é comum não ter conteúdo extenso aqui.

# A navegação é feita automaticamente pelo Streamlit com base nos arquivos em 'pages/'
# Mantenha este arquivo leve, apenas para configurações globais e carregamento inicial.