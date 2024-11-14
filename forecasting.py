import streamlit as st
from ga4_data import get_ga4_data
from fbprophet import Prophet
import pandas as pd

def forecast_data():
    # Load data for forecasting
    ga4_data_df = get_ga4_data()
    
    # Prepare data for Prophet
    df = ga4_data_df.rename(columns={"date": "ds", "totalUsers": "y"})
    df["ds"] = pd.to_datetime(df["ds"])  # Prophet requires datetime format

    # Initialize and fit the model
    model = Prophet()
    model.fit(df)

    # Make future predictions
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    st.subheader("Forecasted Users for Next 30 Days")
    st.write(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])

# Run forecasting if executed as main
if __name__ == "__main__":
    forecast_data()
