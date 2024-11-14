from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import pandas as pd

# ARIMA Model
def arima_forecast(data, kpi, periods):
    model = ARIMA(data[kpi], order=(5, 1, 0))  # Adjust ARIMA order based on performance
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=periods)
    return forecast

# Prophet Model
def prophet_forecast(data, kpi, periods):
    df = data[['date', kpi]].rename(columns={'date': 'ds', kpi: 'y'})
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat']].tail(periods)
