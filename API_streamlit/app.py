import plotly.graph_objects as go
import streamlit as st
from model import RobustForecastModel
from utils import create_future_exog, get_robust_data

st.title("Financial Analytics & MLOps Forecasting")

ticker = st.selectbox(
    "Select Ticker", ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "^GSPC", "^VIX"]
)
horizon = st.slider("Forecast Horizon (Days)", 10, 60, 30)

if st.button("Start analysis"):
    data = get_robust_data(ticker)
    if data is not None and not data.empty:
        engine = RobustForecastModel(horizon=horizon)
        tab1, tab2 = st.tabs(["Future forecast", "Backtesting (Last 30days)"])

        with tab1, st.spinner("Generating prediction..."):
            futr_df = create_future_exog(data, horizon)
            forecast = engine.train_and_predict(data, futr_df)
            col_p10 = next(c for c in forecast.columns if "0.1" in c or "lo" in c)
            col_p50 = next(
                c
                for c in forecast.columns
                if "0.5" in c or "NHITS" == c or "median" in c
            )
            col_p90 = next(c for c in forecast.columns if "0.9" in c or "hi" in c)
            fig = go.Figure()

            hist_plot = data.tail(504)
            fig.add_trace(
                go.Scatter(
                    x=hist_plot["ds"],
                    y=hist_plot["y"],
                    name="History",
                    line={"color": "#636efa"},
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=forecast["ds"].tolist() + forecast["ds"].tolist()[::-1],
                    y=forecast[col_p90].tolist() + forecast[col_p10].tolist()[::-1],
                    fill="toself",
                    fillcolor="rgba(0, 255, 255, 0.1)",
                    line={"color": "rgba(0,0,0,0)"},
                    name="Range 80%",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=forecast["ds"],
                    y=forecast[col_p50],
                    name="Prediction",
                    line={"color": "cyan", "width": 3},
                )
            )
            fig.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig, use_container_width=True)

        with tab2, st.spinner("Running backtest..."):
            try:
                bt_forecast, real_data = engine.run_backtest(data)
                col_bt = next(
                    c for c in bt_forecast.columns if "0.5" in c or "NHITS" == c
                )
                fig_bt = go.Figure()
                fig_bt.add_trace(
                    go.Scatter(
                        x=real_data["ds"],
                        y=real_data["y"],
                        name="Real price",
                        line={"color": "white"},
                    )
                )
                fig_bt.add_trace(
                    go.Scatter(
                        x=bt_forecast["ds"],
                        y=bt_forecast[col_bt],
                        name="AI Backtest",
                        line={"color": "orange", "dash": "dash"},
                    )
                )
                fig_bt.update_layout(
                    template="plotly_dark",
                    title="Comparation: reality vs prediction (Last month)",
                )
                st.plotly_chart(fig_bt, use_container_width=True)
                errore = abs(real_data["y"].values - bt_forecast[col_bt].values).mean()
                st.metric("Mean error3", f"${errore:.2f}")

            except Exception as e:  # noqa: BLE001
                st.error(f"Error during backtesting: {e}")
    else:
        st.error("No data found for this ticker.")
