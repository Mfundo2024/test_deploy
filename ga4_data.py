import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

# Load Google service account credentials and GA4 Property ID from secrets
credentials_info = st.secrets["google_service_account"]
credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = BetaAnalyticsDataClient(credentials=credentials)
ga4_property_id = st.secrets["GA4_PROPERTY_ID"]

def get_ga4_data():
    # Define the request to GA4 API
    request = RunReportRequest(
        property=f"properties/{ga4_property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="bounceRate")
        ],
        date_ranges=[DateRange(start_date="2024-01-01", end_date="2024-01-30")]
    )

    # Run the request
    response = client.run_report(request)

    # Parse and display results
    rows = []
    for row in response.rows:
        data = {
            "date": row.dimension_values[0].value,
            "activeUsers": row.metric_values[0].value,
            "sessions": row.metric_values[1].value,
            "bounceRate": row.metric_values[2].value
        }
        rows.append(data)
    
    # Convert to DataFrame for easier analysis and display
    df = pd.DataFrame(rows)
    return df

# Run data retrieval if executed as main
if __name__ == "__main__":
    df = get_ga4_data()
    st.write("GA4 Data:", df)
