import streamlit as st
import plotly.graph_objects as go
from utils import get_robust_data, create_future_exog
from model import RobustForecastModel


st.set_page_config(page_title="AI Quant Pro", layout="wide")

if st.sidebar.button("Reset system Cache "):
    st.cache_resource.clear()
    st.success("Cache cleaned!")
st.title(" AI Financial Terminal")

ticker = st.sidebar.text_input("Ticker symbol", "NVDA").upper()
period = st.sidebar.selectbox("Historical data range", ["2y", "3y", "5y"], index=1)
horizon = st.sidebar.slider("Prediction Horizon (Days)", 7, 60, 30)


@st.cache_resource
def load_engine(h):
    return RobustForecastModel(horizon=h)


if st.sidebar.button("Start analysis"):
    data = get_robust_data(ticker, period=period)

    if data is not None:
        engine = load_engine(horizon)
        tab1, tab2 = st.tabs(["Future forecast", "Backtesting (Last 30days)"])

        with tab1:
            with st.spinner("Generating prediction..."):
                futr_df = create_future_exog(data, horizon)
                forecast = engine.train_and_predict(data, futr_df)
                col_p10 = [c for c in forecast.columns if "0.1" in c or "lo" in c][0]
                col_p50 = [
                    c
                    for c in forecast.columns
                    if "0.5" in c or "NHITS" == c or "median" in c
                ][0]
                col_p90 = [c for c in forecast.columns if "0.9" in c or "hi" in c][0]
                fig = go.Figure()

                hist_plot = data.tail(504)
                fig.add_trace(
                    go.Scatter(
                        x=hist_plot["ds"],
                        y=hist_plot["y"],
                        name="History",
                        line=dict(color="#636efa"),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=forecast["ds"].tolist() + forecast["ds"].tolist()[::-1],
                        y=forecast[col_p90].tolist() + forecast[col_p10].tolist()[::-1],
                        fill="toself",
                        fillcolor="rgba(0, 255, 255, 0.1)",
                        line=dict(color="rgba(0,0,0,0)"),
                        name="Range 80%",
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=forecast["ds"],
                        y=forecast[col_p50],
                        name="Prediction",
                        line=dict(color="cyan", width=3),
                    )
                )
                fig.update_layout(template="plotly_dark", height=600)
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            with st.spinner("Running backtest..."):
                try:
                    bt_forecast, real_data = engine.run_backtest(data)
                    col_bt = [
                        c for c in bt_forecast.columns if "0.5" in c or "NHITS" == c
                    ][0]
                    fig_bt = go.Figure()
                    fig_bt.add_trace(
                        go.Scatter(
                            x=real_data["ds"],
                            y=real_data["y"],
                            name="Real price",
                            line=dict(color="white"),
                        )
                    )
                    fig_bt.add_trace(
                        go.Scatter(
                            x=bt_forecast["ds"],
                            y=bt_forecast[col_bt],
                            name="AI Backtest",
                            line=dict(color="orange", dash="dash"),
                        )
                    )
                    fig_bt.update_layout(
                        template="plotly_dark",
                        title="Comparation: reality vs prediction (Last month)",
                    )
                    st.plotly_chart(fig_bt, use_container_width=True)
                    errore = abs(
                        real_data["y"].values - bt_forecast[col_bt].values
                    ).mean()
                    st.metric("Mean error3", f"${errore:.2f}")

                except Exception as e:
                    st.error(f"Error during backtesting: {e}")
    else:
        st.error("Ticker not found or o error during download.")
