I trained three different neural networks using PyTorch and Neural Forecaster:
Robust Financial Forecasting (NHITS):
- Developed an advanced forecasting pipeline using the NHITS architecture to predict market trends with a 30-day horizon.
- Integrated multi-quantile loss functions (10%, 50%, 90%) to provide probabilistic uncertainty intervals and risk assessment.
- Exogenous Feature Engineering: Optimized model accuracy by incorporating dynamic exogenous variables, including VIX, S&P 500, and volume metrics.
- Engineered a resilient "triple-pass" data pipeline to handle financial outliers and ensure 100% data integrity through robust scaling and automated imputation.
- Api available here https://financial-analytics-lwhmddpjchajmpnxgfv2gm.streamlit.app/
