# Financial Analytics ELT Pipeline

An end-to-end automated ELT (Extract, Load, Transform) data pipeline designed to ingest, process, and model daily stock market data. This project leverages **Apache Airflow**, **dbt (data build tool)**, **PostgreSQL**, and **yfinance** running inside **Docker containers**.

---

## Architecture & Tech Stack

- **Orchestration:** Apache Airflow (DAGs configured with sequential task dependencies and concurrency controls).
- **Ingestion:** Python (using `yfinance` to fetch live historical stock data) with incremental append logic.
- **Transformation & Modeling:** dbt-postgres (Staging, Silver, and Gold incremental model builds).
- **Code Quality & Git Hygiene:** `pre-commit` hooks running **Ruff** (linting and formatting) and file hygiene checks locally before every commit.
- **CI/CD Automation:** GitHub Actions (Unified sequential workflow featuring automated linting, unit testing, dbt parsing, and automated Docker image builds published to **GitHub Container Registry (GHCR)**).
- **Database:** PostgreSQL.
- **Environment:** Docker & Docker Compose.

## Pipeline Workflow

- **Extraction & Incremental Load (`PythonOperator`):**
  * Queries the PostgreSQL database to check the latest available date (`max(date)`) for each stock ticker (`AAPL`, `MSFT`, `TSLA`, `GOOGL`, `AMZN`).
  * Fetches only missing or new daily records from Yahoo Finance via `yfinance`.
  * Appends the new rows idempotently to the `raw_stock_prices` table to avoid duplicates.

- **Transformation (`BashOperator` running `dbt build`):**
  * Automatically triggered upon successful ingestion.
  * Runs dbt seeds, transformations, and analytical marts incrementally to keep data models up to date.

## Local Quality Controls & Pre-commit Hooks

To maintain high code standards and catch formatting issues before code is even committed, the repository is integrated with **`pre-commit`**:
- **Ruff & Ruff-format:** Instant Python linting, style enforcement, and automatic code formatting.
- **Whitespace & YAML Checks:** Automatic removal of trailing whitespaces, correct end-of-file formatting, and YAML syntax validation.
- **Large File Protection:** Prevents accidental commits of heavy datasets or files exceeding 500 KB.

## CI/CD Quality Controls (GitHub Actions)

To ensure high code quality and prevent runtime failures, the repository features an automated sequential CI/CD pipeline running on every push and pull request:
- **CI Job (Validation):** 
  - **Ruff:** Code style, formatting, and linter checks.
  - **Pytest:** Automated DAG integrity tests using Airflow's `DagBag` (isolating custom DAGs with `include_examples=False`) after running `airflow db migrate`.
  - **dbt Parse:** Compilation and dependency checks across all dbt models and schemas.
- **CD Job (Deployment):** Triggered only on the `main` branch upon successful completion of the CI job, handling container build via Docker Buildx (with `./airflow-project` context) and secure push to GHCR.

## 📂 Project Structure

```text
Airflow-dbt-ELT/
│
├── .github/
│   └── workflows/
│       └── CI_CD_main.yml          # Unified CI/CD pipeline (Lint, Test, Parse, Build & Push)
│
├── airflow-project/                # Airflow configuration and DAGs
│   ├── dags/
│   │   └── stock_market_elt_pipeline.py
│   ├── tests/
│   │   └── test_dag_integrity.py   # Automatic DAG integrity unit tests
│   ├── Dockerfile                  # Custom Airflow container image definition
│   └── requirements.txt            # Python dependencies (Airflow providers, yfinance)
│
├── financial_analytics/            # dbt project root
│   ├── models/
│   │   ├── silver/                 # Silver models (cleaned and standardized data)
│   │   └── gold/                   # Gold models (business-ready aggregations and marts)
│   ├── seeds/                      # Static reference data (e.g., stocks.csv)
│   ├── dbt_project.yml             # dbt project configuration
│   └── profiles.yml                # Database connection profiles
│
├── docker-compose.yml              # Infrastructure setup (Airflow + Postgres)
└── .pre-commit-config.yaml         # Local git hooks configuration (Ruff & hygiene)
