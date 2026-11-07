{{ config(materialized='view') }}

with stock_features as (
    -- Dati delle azioni processati da fct_stock_daily
    select * from {{ ref('fct_stock_daily') }}
),

raw_data as (
    -- Peschiamo S&P 500 e VIX direttamente dalla tabella Bronze su PostgreSQL
    select
        date,
        ticker,
        close as close_price
    from public_bronze.raw_stock_prices
    where ticker in ('^GSPC', '^VIX')
),

sp500 as (
    select date, close_price as sp500_close
    from raw_data
    where ticker = '^GSPC'
),

vix as (
    select date, close_price as vix_close
    from raw_data
    where ticker = '^VIX'
)

select
    s.ticker,
    s.date,
    s.close_price,
    s.volume,

    -- Inseriamo S&P500 e VIX allineati per data
    coalesce(sp.sp500_close, 0) as sp500_close,
    coalesce(v.vix_close, 0) as vix_close,

    -- Variazione percentuale rispetto al giorno precedente
    round(
        (((s.close_price - lag(s.close_price, 1) over (partition by s.ticker order by s.date))
        / nullif(lag(s.close_price, 1) over (partition by s.ticker order by s.date), 0)) * 100)::numeric,
        2
    ) as daily_return_pct,

    -- Media mobile a 7 giorni del prezzo
    round(
        avg(s.close_price) over (
            partition by s.ticker
            order by s.date
            rows between 6 preceding and current row
        )::numeric,
        2
    ) as ma_7_close
from stock_features s
left join sp500 sp on s.date = sp.date
left join vix v on s.date = v.date
