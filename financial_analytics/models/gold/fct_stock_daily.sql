{{ config(materialized='table') }}

with prices as (
    select * from {{ ref('stg_stock_prices') }}
),

stocks as (
    select * from {{ ref('stg_stocks') }}
)

select
    p.ticker,
    s.company_name,
    s.sector,
    p.date,
    p.open_price,
    p.high_price,
    p.low_price,
    p.close_price,
    p.volume
from prices p
inner join stocks s on p.ticker = s.ticker