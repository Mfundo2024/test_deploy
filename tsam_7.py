import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from ga4_data import fetch_ga4_data, initialize_ga4_client
from forecasting import prophet_forecast
from insights import generate_openai_insights

# Define KPI benchmarks
KPI_BENCHMARKS = {
    "users": {"threshold": 50000, "target": 70000, "challenge": 90000},
    "sessions": {"threshold": 80000, "target": 100000, "challenge": 120000},
    "Average Engagement Time": {"threshold": 180, "target": 240, "challenge": 300},  # In seconds
    "Bounce Rate": {"threshold": 60, "target": 50, "challenge": 35},  # In percentages
}

# Streamlit app
def main():
    st.title('KPI Forecast Tracker')

    # GA4 setup
    property_id = st.secrets["GA4_PROPERTY_ID"]
    client = initialize_ga4_client()

    # Date inputs
    start_date = st.date_input("Select start date for historical data", value=pd.to_datetime('2022-01-01'))
    end_date = st.date_input("Select end date for historical data", value=pd.to_datetime('2024-09-30'))

    # Load historical data from GA4
    st.write("Fetching data from GA4...")
    ga4_data = fetch_ga4_data(client, property_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    ga4_data['date'] = pd.to_datetime(ga4_data['date'])

    # Check for necessary columns and calculate if missing
    if 'Average Engagement Time' not in ga4_data.columns:
        ga4_data['Average Engagement Time'] = ga4_data['userEngagementDuration'] / ga4_data['sessions']
    if 'Bounce Rate' not in ga4_data.columns:
        ga4_data['Bounce Rate'] = ga4_data['bounce_rate'] * 100

    # Sort actual data by date to ensure it's in ascending order
    ga4_data = ga4_data.sort_values(by='date')

    # User input for KPIs
    kpi_choice = st.selectbox('Select KPI to forecast:', ['users', 'sessions', 'Average Engagement Time', 'Bounce Rate'])

    # Retrieve the thresholds, targets, and challenges for the selected KPI
    kpi_benchmarks = KPI_BENCHMARKS.get(kpi_choice, {})
    threshold = kpi_benchmarks.get('threshold', 'N/A')
    target = kpi_benchmarks.get('target', 'N/A')
    challenge = kpi_benchmarks.get('challenge', 'N/A')

    # Display KPI benchmarks
    if kpi_choice in ["Average Engagement Time"]:
        st.write(f"**Threshold:** {threshold} seconds")
        st.write(f"**Target:** {target} seconds")
        st.write(f"**Challenge:** {challenge} seconds")
    elif kpi_choice == "Bounce Rate":
        st.write(f"**Threshold:** {threshold}%")
        st.write(f"**Target:** {target}%")
        st.write(f"**Challenge:** {challenge}%")
    else:
        st.write(f"**Threshold:** {threshold}")
        st.write(f"**Target:** {target}")
        st.write(f"**Challenge:** {challenge}")

    # Numeric inputs for the target values
    target_last_month = st.number_input(f'Enter target for last month\'s {kpi_choice}:', min_value=0, value=target if isinstance(target, int) else 0)
    target_this_month = st.number_input(f'Enter target for this month\'s {kpi_choice}:', min_value=0, value=target if isinstance(target, int) else 0)

    # Time period to forecast (for the current month)
    forecast_period = pd.Period(pd.Timestamp.today(), freq='M').days_in_month

    # Start the forecast from the beginning of the current month
    first_day_of_month = pd.Timestamp.today().replace(day=1)

    # Filter actual data to only include the current month
    actual_data_this_month = ga4_data[ga4_data['date'] >= first_day_of_month]

    # Perform the forecast using Prophet from the first day of the month
    forecast = prophet_forecast(ga4_data, kpi_choice, forecast_period)

    # Calculate cumulative forecast
    forecast_total = np.sum(forecast['yhat'])

    # Create two columns for the gauge and timeline
    col1, col2 = st.columns(2)

    with col1:
        # Gauge Chart (Last Month)
        st.write("## Did we meet all the KPIs last month?")
        gauge_fig_last_month = go.Figure(go.Indicator(
            mode="gauge+number",
            value=forecast_total,
            title={'text': f"{kpi_choice} Progress Last Month"},
            gauge={
                'axis': {'range': [None, 150000]},
                'steps': [
                    {'range': [0, threshold], 'color': "lightgray"},
                    {'range': [threshold, target], 'color': "lightgray"},
                    {'range': [target, challenge], 'color': "lightgray"},
                    {'range': [challenge, 150000], 'color': "lightgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 5},
                    'thickness': 0.75,
                    'value': target_last_month
                }
            }
        ))
        st.plotly_chart(gauge_fig_last_month)

    with col2:
        # Timeline Chart (Current Month)
        st.write("## KPI Timeline for the Current Month")
        
        current_month_start = pd.Timestamp.today().replace(day=1)
        current_month_days = pd.Period(current_month_start, freq='M').days_in_month
        daily_target = target_this_month / current_month_days
        today = pd.Timestamp.today()
        yesterday = today - pd.Timedelta(days=1)

        # Filter actual data up to yesterday
        actual_data_filtered = actual_data_this_month[actual_data_this_month['date'] <= yesterday]

        # Convert dates to ensure matching format (dates only)
        actual_data_filtered['date'] = pd.to_datetime(actual_data_filtered['date']).dt.date

        # Create a date range for the full month
        date_range = pd.date_range(start=current_month_start, periods=current_month_days).date
        forecast_full_month = forecast['yhat'].iloc[:current_month_days].reset_index(drop=True)

        # Combine actual, forecast, and target data
        timeline_data = pd.DataFrame({
            'date': date_range,
            'actual': pd.Series([np.nan] * current_month_days),
            'forecast': forecast_full_month,
            'target': [daily_target] * current_month_days
        })

        # Ensure timeline_data dates are in date format
        timeline_data['date'] = pd.to_datetime(timeline_data['date']).dt.date

        # Overwrite the actual values where available by matching dates
        for idx, row in actual_data_filtered.iterrows():
            timeline_data.loc[timeline_data['date'] == row['date'], 'actual'] = row[kpi_choice]

        # Plot timeline using Plotly Express
        timeline_fig = px.line(timeline_data, x='date', y=['actual', 'forecast', 'target'], labels={
            'value': kpi_choice,
            'date': 'Date'
        })
        st.plotly_chart(timeline_fig)

    # Insights for last month
    insights_last_month = generate_openai_insights(ga4_data, forecast, kpi_choice, target_last_month, target_this_month)
    st.write(insights_last_month)

if __name__ == "__main__":
    main()
