import pandas as pd
import torch
from neuralforecast import NeuralForecast
from neuralforecast.losses.pytorch import QuantileLoss
from neuralforecast.models import NHITS


class RobustForecastModel:
    def __init__(self, horizon=30):
        self.horizon = horizon
        self.futr_exog = ["sp500", "vix", "volume", "vol_ma"]
        quantiles_tensor = torch.tensor([0.1, 0.5, 0.9])

        trainer_kw = {"enable_progress_bar": False}

        self.model = NHITS(
            h=self.horizon,
            input_size=60,
            futr_exog_list=self.futr_exog,
            scaler_type="robust",
            max_steps=50,
            accelerator="cpu",
            loss=QuantileLoss(q=quantiles_tensor),
            trainer_kwargs=trainer_kw,
        )
        self.nf = NeuralForecast(models=[self.model], freq="B")

    def train_and_predict(self, df, _unused):
        df_clean = df.copy().ffill().bfill().fillna(0)
        self.nf.fit(df=df_clean)
        correct_futr = self._prepare_and_clean_future(df_clean, df_clean)

        forecasts = self.nf.predict(futr_df=correct_futr)
        return forecasts.reset_index()

    def _prepare_and_clean_future(self, train_df, reference_df):
        futr_df = self.nf.make_future_dataframe(df=train_df)

        cols_to_merge = ["ds"] + [
            c for c in self.futr_exog if c in reference_df.columns
        ]
        futr_df = pd.merge(
            futr_df[["unique_id", "ds"]],
            reference_df[cols_to_merge],
            on="ds",
            how="left",
        )
        futr_df = futr_df.ffill().bfill()

        for col in self.futr_exog:
            if futr_df[col].isnull().any():
                last_known = train_df[col].iloc[-1]
                futr_df[col] = futr_df[col].fillna(last_known)
            futr_df[col] = futr_df[col].fillna(0)
        return futr_df

    def run_backtest(self, df):
        df_clean = df.copy().ffill().bfill().fillna(0)

        train_df = df_clean.iloc[: -self.horizon].copy()
        test_df = df_clean.iloc[-self.horizon :].copy()

        self.nf.fit(df=train_df)
        correct_futr_bt = self._prepare_and_clean_future(train_df, df_clean)

        backtest_forecast = self.nf.predict(futr_df=correct_futr_bt)
        backtest_forecast = backtest_forecast.tail(self.horizon)

        return backtest_forecast.reset_index(), test_df
