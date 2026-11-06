{{ config(materialized='view') }}

select
    ticker,
    company_name,
    sector
from {{ ref('stocks') }}