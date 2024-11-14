import streamlit as st
import openai
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from ga4_data import get_ga4_data  # Import GA4 data function from ga4_data.py
from insights import generate_insights  # Import insights function from insights.py

# Load OpenAI API Key from Streamlit secrets
openai.api_key = st.secrets["INSIGHTS_API_KEY"]

def main():
    st.title("KPI Dashboard with Visuals")

    # Retrieve GA4 data
    ga4_data_df = get_ga4_data()
    st.write("GA4 Data:", ga4_data_df)

    # 1. KPI Gauges
    st.subheader("Monthly KPI Progress")
    gauge_fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ga4_data_df["totalUsers"].astype(int).sum(),
        title={"text": "Total Users"},
        gauge={"axis": {"range": [0, 70000]}, "bar": {"color": "blue"}}
    ))
    gauge_fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ga4_data_df["sessions"].astype(int).sum(),
        title={"text": "Total Sessions"},
        gauge={"axis": {"range": [0, 100000]}, "bar": {"color": "green"}}
    ))
    gauge_fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ga4_data_df["bounceRate"].astype(float).mean(),
        title={"text": "Average Bounce Rate"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "red"}}
    ))
    st.plotly_chart(gauge_fig1)
    st.plotly_chart(gauge_fig2)
    st.plotly_chart(gauge_fig3)

    # 2. Timeline Chart for KPI Trends
    st.subheader("KPI Timeline for Current Month")
    line_fig = px.line(ga4_data_df, x="date", y=["totalUsers", "sessions", "bounceRate"],
                       labels={"value": "Metrics", "date": "Date"},
                       title="Daily KPIs Over Time")
    st.plotly_chart(line_fig)

    # 3. Table of KPI Data
    st.subheader("KPI Data Table")
    st.write(ga4_data_df)

    # 4. OpenAI-Powered Insights
    st.subheader("AI-Generated Insights")
    prompt = "Generate insights based on user engagement data for the past month."
    insight = generate_insights(prompt)
    st.write("Generated Insight:", insight)

if __name__ == "__main__":
    main()
