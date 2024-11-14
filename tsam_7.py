import streamlit as st
import openai
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient

# Load secrets from Streamlit secrets
ga4_property_id = st.secrets["GA4_PROPERTY_ID"]
openai.api_key = st.secrets["INSIGHTS_API_KEY"]
credentials_info = st.secrets["google_service_account"]
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Initialize GA4 client
client = BetaAnalyticsDataClient(credentials=credentials)

# Sample data for demonstration
kpi_data = {
    "Date": pd.date_range(start="2024-01-01", periods=30, freq="D"),
    "Users": [5000 + i*10 for i in range(30)],
    "Sessions": [7000 + i*15 for i in range(30)],
    "Bounce Rate": [60 - i*0.5 for i in range(30)]
}
kpi_df = pd.DataFrame(kpi_data)

def main():
    st.title("KPI Dashboard with Visuals")
    
    # 1. KPI Gauges
    st.subheader("Monthly KPI Progress")
    gauge_fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=kpi_df["Users"].sum(),
        title={"text": "Total Users"},
        gauge={"axis": {"range": [0, 70000]}, "bar": {"color": "blue"}}
    ))
    gauge_fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=kpi_df["Sessions"].sum(),
        title={"text": "Total Sessions"},
        gauge={"axis": {"range": [0, 100000]}, "bar": {"color": "green"}}
    ))
    gauge_fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=kpi_df["Bounce Rate"].mean(),
        title={"text": "Average Bounce Rate"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "red"}}
    ))
    st.plotly_chart(gauge_fig1)
    st.plotly_chart(gauge_fig2)
    st.plotly_chart(gauge_fig3)

    # 2. Timeline Chart for KPI Trends
    st.subheader("KPI Timeline for Current Month")
    line_fig = px.line(kpi_df, x="Date", y=["Users", "Sessions", "Bounce Rate"],
                       labels={"value": "Metrics", "Date": "Date"},
                       title="Daily KPIs Over Time")
    st.plotly_chart(line_fig)

    # 3. Table of KPI Data
    st.subheader("KPI Data Table")
    st.write(kpi_df)

    # 4. OpenAI-Powered Insights
    st.subheader("AI-Generated Insights")
    prompt = "Generate insights based on user engagement data for the past month."
    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=50)
    st.write("Generated Insight:", response.choices[0].text.strip())

if __name__ == "__main__":
    main()
