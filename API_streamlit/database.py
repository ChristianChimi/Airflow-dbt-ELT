import pandas as pd
from sqlalchemy import create_engine

# Stringa di connessione al tuo database PostgreSQL (puoi usare variabili d'ambiente)
DB_CONNECTION_STRING = "postgresql://username:password@localhost:5432/nome_database"


def load_data_from_dbt_view(ticker_symbol: str, period_years: int = 3) -> pd.DataFrame:
    engine = create_engine(DB_CONNECTION_STRING)

    # Interroghiamo direttamente la vista prodotta da dbt
    query = f"""
        SELECT
            ticker as unique_id,
            date as ds,
            close_price as y,
            volume,
            ma_7_close as vol_ma,
            daily_return_pct
        FROM tua_vista_dbt_name
        WHERE ticker = '{ticker_symbol}'
          -- Filtriamo per lo storico desiderato (es. ultimi 3 anni)
          AND date >= CURRENT_DATE - INTERVAL '{period_years} years'
        ORDER BY date ASC;
    """

    df = pd.read_sql(query, con=engine)

    # Assicuriamoci che il formato della data sia corretto e senza fusi orari
    df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)

    return df
