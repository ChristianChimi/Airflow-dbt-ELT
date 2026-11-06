from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from sqlalchemy import create_engine
import pandas as pd
import yfinance as yf
from requests import Session

def fetch_and_load_data():
    session = Session()
    session.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

    db_url = 'postgresql+psycopg2://airflow:airflow@postgres:5432/airflow'
    engine = create_engine(db_url)
    
    tickers = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN']
    all_data = []
    
    for ticker in tickers:
        try:
            existing_df = pd.read_sql(f"SELECT DISTINCT date FROM raw_stock_prices WHERE ticker = '{ticker}'", con=engine)
            existing_dates = set(pd.to_datetime(existing_df['date']).dt.date)
            max_date = max(existing_dates) if existing_dates else None
        except Exception:
            existing_dates = set()
            max_date = None
            
        stock = yf.Ticker(ticker, session=session)
        
        if max_date:
            print(f"[{ticker}] Latest date in DB: {max_date}. Downloading from {max_date}...")
            df = stock.history(start=str(max_date))
        else:
            print(f"[{ticker}] No previous data found. Downloading 1 month of historical data...")
            df = stock.history(period='1mo')
            
        if df.empty:
            continue
            
        df = df.reset_index()
        df['ticker'] = ticker
        df = df[['Date', 'ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df.columns = ['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        df = df[~df['date'].isin(existing_dates)]
        
        if not df.empty:
            all_data.append(df)
            print(f"[{ticker}] Found {len(df)} new rows to append.")
        else:
            print(f"[{ticker}] No new rows found (already up to date).")
        
    if not all_data:
        print('No new data to load for any ticker.')
        return

    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_sql('raw_stock_prices', con=engine, if_exists='append', index=False, chunksize=1000)
    print(f'Loading completed: added {len(final_df)} new rows.')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'stock_market_elt_pipeline',
    default_args=default_args,
    description='Incremental ELT pipeline for stock data with dbt build',
    schedule='@daily',  
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    ingest_task = PythonOperator(
        task_id='fetch_and_load_stock_data',
        python_callable=fetch_and_load_data,
    )

    dbt_build_task = BashOperator(
    task_id='dbt_build_transformations',
    bash_command='cd /opt/airflow/financial_analytics && pip install dbt-postgres && dbt build --profiles-dir .',
)

    # Sequential dependencies definition
    ingest_task >> dbt_build_task