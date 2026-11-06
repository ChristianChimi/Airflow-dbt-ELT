{{ config(materialized='view') }}

with joined_data as (
    select * from {{ ref('fct_stock_daily') }}
)

select
    ticker,
    company_name,
    sector,
    date,
    close_price,
    volume,
    -- Variazione percentuale rispetto al giorno precedente con cast a numeric
    round(
        (((close_price - lag(close_price, 1) over (partition by ticker order by date)) 
        / nullif(lag(close_price, 1) over (partition by ticker order by date), 0)) * 100)::numeric, 
        2
    ) as daily_return_pct,
    
    -- Media mobile a 7 giorni del prezzo di chiusura con cast a numeric
    round(
        avg(close_price) over (
            partition by ticker 
            order by date 
            rows between 6 preceding and current row
        )::numeric, 
        2
    ) as ma_7_close
from joined_data