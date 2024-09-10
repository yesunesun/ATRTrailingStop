import streamlit as st
import pandas as pd
import json
import yfinance as yf
from datetime import datetime, timedelta

# Helper functions to check if a date is a weekend and if the market was open
def is_weekend(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.weekday() >= 5

def is_market_open(date_str):
    start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    market_data = yf.download('SPY', start=start_date, end=end_date)
    return date_str in market_data.index.strftime('%Y-%m-%d')

def is_trading_day_for_symbol(symbol, date_str):
    if is_weekend(date_str):
        return False
    if not is_market_open(date_str):
        return False
    start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return not stock_data.empty and date_str in stock_data.index.strftime('%Y-%m-%d')

# Streamlit app
st.title("Symbol Validation with Progress Feedback")

# File uploader
uploaded_file = st.file_uploader("Upload a text file", type="txt")

# Get a reference date for validation (today or any specific date you want)
date_str = datetime.today().strftime('%Y-%m-%d')

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    
    # Extract JSON-like part from the content
    start_index = content.find('[')
    json_data = content[start_index:].strip()

    try:
        symbols_data = json.loads(json_data)
        df = pd.DataFrame(symbols_data)
        df['id'] = df['id'].astype(str)

        # Progress indicator
        progress = st.progress(0)
        status_message = st.empty()
        
        company_names = []
        statuses = []

        # Iterate over the symbols for validation with progress
        for i, symbol in enumerate(df['symbol']):
            with st.spinner(f"Validating {symbol}..."):
                # Use the is_trading_day_for_symbol function for validation
                traded = is_trading_day_for_symbol(symbol, date_str)
                company_name = f"Company {symbol}" if traded else "N/A"
                status = "Valid" if traded else "Invalid"
                company_names.append(company_name)
                statuses.append(status)

            # Update progress
            progress.progress((i + 1) / len(df))

        df['Company Name'] = company_names
        df['Status'] = statuses

        # Display the resulting table
        st.dataframe(df[['id', 'symbol', 'Company Name', 'Status']])

    except json.JSONDecodeError as e:
        st.error(f"Error parsing the JSON data: {e}")
else:
    st.write("Please upload a valid text file with the symbols data.")
