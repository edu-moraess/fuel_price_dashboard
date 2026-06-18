import streamlit as st
from src.load_data import load_and_preprocess_data
from src.config import DATA_PATH


def init_session():
    """
    Inicializa dataset global do app de forma segura
    (evita ModuleNotFoundError e session_state quebrado)
    """

    if "df" not in st.session_state:
        df = load_and_preprocess_data(DATA_PATH)
        st.session_state.df = df

    return st.session_state.df 