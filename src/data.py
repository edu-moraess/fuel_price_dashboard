import pandas as pd
import streamlit as st
from src.config import DATA_PATH, DATE_COL, COUNTRY_COL, PRODUCTS, DATE_FORMAT


@st.cache_data(show_spinner=False)
def load() -> pd.DataFrame:
    try:
        df = pd.read_csv(DATA_PATH, parse_dates=[DATE_COL])
    except FileNotFoundError:
        return pd.DataFrame()

    required = [DATE_COL, COUNTRY_COL] + PRODUCTS
    if not all(c in df.columns for c in required):
        return pd.DataFrame()

    for col in PRODUCTS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df.dropna(subset=[DATE_COL], inplace=True)
    df.sort_values([DATE_COL, COUNTRY_COL], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def filter_df(
    df: pd.DataFrame,
    countries: list,
    product: str,
    start: str,
    end: str,
) -> pd.DataFrame:
    mask = (
        df[COUNTRY_COL].isin(countries)
        & (df[DATE_COL] >= pd.to_datetime(start))
        & (df[DATE_COL] <= pd.to_datetime(end))
        & df[product].notna()
    )
    return df.loc[mask, [DATE_COL, COUNTRY_COL, product]].copy()
