# Financial Analytics ELT Pipeline

An end-to-end automated ELT (Extract, Load, Transform) data pipeline designed to ingest, process, and model daily stock market data. This project leverages **Apache Airflow**, **dbt (data build tool)**, **PostgreSQL**, and **yfinance** running inside **Docker containers**.

---

## Architecture & Tech Stack

* **Orchestration:** Apache Airflow (DAGs configured with sequential task dependencies and concurrency controls).
* **Ingestion:** Python (using `yfinance` to fetch live historical stock data) with incremental append logic.
* **Transformation & Modeling:** dbt-postgres (Staging, Marts, and incremental model builds).
* **Database:** PostgreSQL.
* **Environment:** Docker & Docker Compose.

## Pipeline Workflow

* **Extraction & Incremental Load (`PythonOperator`):**
  * Queries the PostgreSQL database to check the latest available date (`max(date)`) for each stock ticker (`AAPL`, `MSFT`, `TSLA`, `GOOGL`, `AMZN`).
  * Fetches only missing or new daily records from Yahoo Finance via `yfinance`.
  * Appends the new rows idempotently to the `raw_stock_prices` table to avoid duplicates.

* **Transformation (`BashOperator` running `dbt build`):**
  * Automatically triggered upon successful ingestion.
  * Runs dbt seeds, staging transformations, and analytical marts incrementally to keep data models up to date.
---

## 📂 Project Structure

```text

Airflow-dbt-ELT/
│
├── .github/
│   └── workflows/
│       └── data_platform_ci.yml   # <-- La pipeline di GitHub Actions
│
├── airflow-project/          # Airflow configuration and DAGs
│   ├── dags/
│   │   └── stock_market_elt_pipeline.py
│   └── tests/
│       └── test_dag_integrity.py  # <-- Unit test automatico per i DAG
│
├── financial-analytics/      # dbt project root
│   ├── models/
│   │   ├── staging/          # Staging models (cleaning raw data)
│   │   └── marts/            # Business-ready models and aggregations
│   ├── seeds/                # Static reference data (e.g., stocks.csv)
│   ├── dbt_project.yml       # dbt project configuration
│   └── profiles.yml          # Database connection profiles
│
└── docker-compose.yml        # Infrastructure setup (Airflow + Postgres)

