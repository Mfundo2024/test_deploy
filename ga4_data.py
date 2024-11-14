from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest
import pandas as pd
import streamlit as st


# Initialize GA4 Client
def initialize_ga4_client():
    credentials = service_account.Credentials.from_service_account_info(st.secrets["GA4_API_KEY"])
    client = BetaAnalyticsDataClient(credentials=credentials)
    return client


# Fetch data from GA4
def fetch_ga4_data(client, property_id, start_date, end_date):
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="userEngagementDuration"),
            Metric(name="bounceRate")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
    )

    response = client.run_report(request)
    data = []
    for row in response.rows:
        data.append({
            "date": row.dimension_values[0].value,
            "sessions": float(row.metric_values[0].value),
            "users": float(row.metric_values[1].value),
            "userEngagementDuration": float(row.metric_values[2].value),
            "bounce_rate": float(row.metric_values[3].value)
        })
    return pd.DataFrame(data)
