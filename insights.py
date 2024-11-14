from openai import OpenAI
import pandas as pd

client = INSIGHTS_API_KEY

# Define KPI targets, thresholds, and challenges
KPI_BENCHMARKS = {
    "Users": {"threshold": 50000, "target": 70000, "challenge": 90000},
    "Sessions": {"threshold": 80000, "target": 100000, "challenge": 120000},
    "Average Engagement Time": {"threshold": "3:00", "target": "4:00", "challenge": "5:00"},
    "Bounce Rate": {"threshold": 60, "target": 50, "challenge": 35},  # In percentages
}


# Function to get the last month's date range
def get_last_month_range():
    # Get today's date
    today = pd.Timestamp.today()

    # Calculate the first and last day of the previous month
    first_day_last_month = today.replace(day=1) - pd.DateOffset(months=1)
    last_day_last_month = today.replace(day=1) - pd.DateOffset(days=1)

    return first_day_last_month, last_day_last_month

# Function to call OpenAI for insights using chat-based models
def generate_openai_insights(historical_data, forecast_data, kpi, target_last_month, target_this_month):
      # Replace with your OpenAI API Key
    # Get the last month's date range
    first_day_last_month, last_day_last_month = get_last_month_range()

    # Filter historical data for the last month only
    historical_last_month_data = historical_data[
        (historical_data['date'] >= first_day_last_month) &
        (historical_data['date'] <= last_day_last_month)
    ]

    # Check if the KPI exists in historical data
    if kpi not in historical_last_month_data.columns:
        raise KeyError(f"KPI '{kpi}' not found in historical data columns: {historical_data.columns}")

    # Sum the historical data for the last month
    historical_last_month_total = historical_last_month_data[kpi].sum()

    # Use 'yhat' for forecast data since the original KPI name isn't retained
    forecast_subset = forecast_data[['ds', 'yhat']].to_dict()  # Use 'yhat' as forecasted values

    # Retrieve the thresholds, targets, and challenges for the current KPI
    kpi_benchmarks = KPI_BENCHMARKS.get(kpi, {})
    threshold = kpi_benchmarks.get('threshold', 'N/A')
    target = kpi_benchmarks.get('target', 'N/A')
    challenge = kpi_benchmarks.get('challenge', 'N/A')

    # Prepare messages for the chat completion API
    messages = [
        {"role": "system", "content": "You are a world-class data scientist."},
        {"role": "user", "content": f"""
        Analyze the following KPI data (historical and forecast) and generate insights for a business to take action.
        
        KPI: {kpi}
        Target Last Month: {target_last_month}
        Target This Month: {target_this_month}
        Threshold: {threshold}
        Target: {target}
        Challenge: {challenge}
        
        Historical Total for Last Month: {historical_last_month_total}
        
        Forecast Data (Predicted - yhat): {forecast_subset}
        
        Please provide:
        1. Did we meet all the KPIs last month?
        2. Are we on track to meet all the KPIs this month?
        3. Provide detailed insights, including wins, challenges, and what should be done based on the data.
        """}
    ]

    # Use OpenAI's ChatCompletion API for GPT-4
    response = client.chat.completions.create(model="gpt-4",  # GPT-4 model for chat completions
    messages=messages,
    max_tokens=500,  # Max tokens for the response
    temperature=0.7)

    # Return the assistant's message
    return response.choices[0].message.content
