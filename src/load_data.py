# src/load_data.py

import pandas as pd
import numpy as np
from datetime import datetime
from src.config import DATE_COLUMN, COUNTRY_COLUMN, PRODUCT_COLUMNS, DEFAULT_DATE_FORMAT

def load_and_preprocess_data(filepath):
    """
    Carrega e faz o pré-processamento inicial dos dados de preços de combustíveis.

    Args:
        filepath (str): Caminho para o arquivo CSV.

    Returns:
        pd.DataFrame: DataFrame com colunas 'date', 'COUNTRY', 'diesel_usd', 'gasoline_usd'.
                      Índice pode ser opcionalmente definido como MultiIndex (date, COUNTRY).
    """
    try:
        df = pd.read_csv(filepath, parse_dates=[DATE_COLUMN])
        print(f"Dados carregados com sucesso de {filepath}. Shape: {df.shape}")
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {filepath}")
        return pd.DataFrame() # Retorna DataFrame vazio em caso de erro
    except Exception as e:
        print(f"Erro inesperado ao carregar dados: {e}")
        return pd.DataFrame()

    # Garantir que as colunas esperadas existam
    required_columns = [DATE_COLUMN, COUNTRY_COLUMN] + PRODUCT_COLUMNS
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        print(f"Erro: Colunas ausentes no CSV: {missing_cols}")
        return pd.DataFrame()

    # Ordenar por data e país para garantir consistência
    df.sort_values(by=[DATE_COLUMN, COUNTRY_COLUMN], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Converter preços para numérico, forçando erros a NaN
    for col in PRODUCT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remover linhas com datas ou preços inválidos (NaN)
    df.dropna(subset=[DATE_COLUMN] + PRODUCT_COLUMNS, inplace=True)

    # Converter coluna de data para datetime se ainda não estiver
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], format=DEFAULT_DATE_FORMAT, errors='coerce')
    df.dropna(subset=[DATE_COLUMN], inplace=True) # Remove datas inválidas convertidas para NaT

    print(f"Dados limpos. Shape final: {df.shape}")
    return df

def filter_data_by_selection(df, countries=None, products=None, start_date=None, end_date=None):
    """
    Filtra o DataFrame com base nas seleções do usuário.

    Args:
        df (pd.DataFrame): DataFrame original.
        countries (list, optional): Lista de países a filtrar.
        products (list, optional): Lista de produtos ('diesel_usd', 'gasoline_usd') a filtrar.
        start_date (str or datetime, optional): Data inicial.
        end_date (str or datetime, optional): Data final.

    Returns:
        pd.DataFrame: DataFrame filtrado.
    """
    filtered_df = df.copy()

    if countries:
        filtered_df = filtered_df[filtered_df[COUNTRY_COLUMN].isin(countries)]

    if products:
        # Manter apenas as colunas de data, país e os produtos selecionados
        cols_to_keep = [DATE_COLUMN, COUNTRY_COLUMN] + [p for p in PRODUCT_COLUMNS if p in products]
        filtered_df = filtered_df[cols_to_keep]

    if start_date:
        if isinstance(start_date, str):
             start_date = datetime.strptime(start_date, DEFAULT_DATE_FORMAT)
        filtered_df = filtered_df[filtered_df[DATE_COLUMN] >= start_date]

    if end_date:
        if isinstance(end_date, str):
             end_date = datetime.strptime(end_date, DEFAULT_DATE_FORMAT)
        filtered_df = filtered_df[filtered_df[DATE_COLUMN] <= end_date]

    return filtered_df

# Exemplo de uso (opcional, pode ser removido ou comentado):
# if __name__ == "__main__":
#     from config import DATA_PATH
#     df = load_and_preprocess_data(DATA_PATH)
#     print(df.head())
#     print(df.info())