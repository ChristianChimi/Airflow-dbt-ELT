import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# Connessione al database PostgreSQL sul container Airflow
DB_CONNECTION_STRING = "postgresql://airflow:airflow@localhost:5433/airflow"


def get_robust_data(ticker, period="3y"):
    """
    Legge i dati storici, i volumi, le feature di dbt e gli indici macro
    direttamente dalla vista Gold (mrt_stock_performance) su PostgreSQL.
    """
    try:
        engine = create_engine(DB_CONNECTION_STRING)

        # Interroghiamo la vista mrt_stock_performance prodotta da dbt
        query = f"""
            SELECT
                ticker as unique_id,
                date as ds,
                close_price as y,
                volume,
                sp500_close as sp500,
                vix_close as vix,
                ma_7_close as vol_ma
            FROM public_gold.mrt_stock_performance
            WHERE ticker = '{ticker.upper()}'
            ORDER BY date ASC;
        """

        df = pd.read_sql(query, con=engine)

        if df.empty:
            return None

        # Formattazione e pulizia date/valori
        df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)
        df = df.ffill().bfill().fillna(0)

        return df[["unique_id", "ds", "y", "volume", "sp500", "vix", "vol_ma"]]

    except Exception as e:  # noqa: BLE001
        st.error(f"Errore di connessione o query al DB: {e}")
        return None


def create_future_exog(df, horizon):
    """
    Genera le esogene future per l'orizzonte temporale basandosi
    sull'ultimo stato disponibile nel Feature Store.
    """
    last_row = df.iloc[-1]
    future_dates = pd.date_range(
        start=df["ds"].iloc[-1] + pd.Timedelta(days=1), periods=horizon, freq="B"
    )
    return pd.DataFrame(
        {
            "ds": future_dates,
            "unique_id": df["unique_id"].iloc[0],
            "sp500": last_row["sp500"],
            "vix": last_row["vix"],
            "volume": last_row["volume"],
            "vol_ma": last_row["vol_ma"],
        }
    )
