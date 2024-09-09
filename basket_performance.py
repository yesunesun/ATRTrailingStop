import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Helper function to get date range based on period selection
def get_date_range(period, creation_date, performance_type):
    end_date = datetime.now().date()
    
    if performance_type == 'Since Inception':
        start_date = creation_date  # Always use basket creation date for Since Inception
    else:  # For Historical Performance, use the selected time period
        if period == '1W':
            start_date = end_date - timedelta(weeks=1)
        elif period == '1M':
            start_date = end_date - timedelta(weeks=4)
        elif period == '3M':
            start_date = end_date - timedelta(weeks=12)
        elif period == '6M':
            start_date = end_date - timedelta(weeks=24)
        elif period == '1Y':
            start_date = end_date - timedelta(weeks=52)
        elif period == 'YTD':
            start_date = datetime(end_date.year, 1, 1).date()
        else:
            start_date = pd.to_datetime('2023-01-01').date()  # Default start date
            
    return start_date, end_date

# Function to fetch stock data
def get_stock_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)
    return data['Adj Close']

# Function to calculate overall daily performance of the basket
def calculate_basket_performance(prices):
    daily_returns = prices.pct_change().dropna() * 100  # Daily return in percentage
    overall_performance = daily_returns.mean(axis=1)  # Average performance across all symbols
    return daily_returns, overall_performance

# Function to calculate the current market value and overall performance
def calculate_market_value_and_performance(prices, initial_investment):
    latest_prices = prices.iloc[-1]  # Latest closing prices of the stocks
    market_value = (latest_prices / prices.iloc[0]).mean() * initial_investment  # Assuming equal investment in all stocks
    overall_performance = ((market_value - initial_investment) / initial_investment) * 100
    return market_value, overall_performance

# Streamlit app layout
st.title('Basket Performance')

# Sidebar for user input
st.sidebar.header('User Inputs')

# Basket name input
basket_name = st.sidebar.text_input('Basket Name', value='Magnificent Seven')

# Stock symbols input
default_symbols = 'AAPL, AMZN, GOOG, META, MSFT, NVDA, TSLA'
symbols = st.sidebar.text_input('Enter Stock Symbols (comma separated)', default_symbols)

# Initial investment input
initial_investment = st.sidebar.number_input('Initial Investment (default 100,000)', value=100000)

# Period selection for data
st.sidebar.subheader('Select a Time Period')
period = st.sidebar.selectbox('', ['1W', '1M', '3M', '6M', '1Y', 'YTD'], index=5, key='time_period')

# Basket creation date input
basket_creation_date = st.sidebar.date_input('Basket Creation Date', value=pd.to_datetime('2024-01-01'))

# Performance type selection
performance_type = st.sidebar.radio('Performance Type', ['Historical Performance (Last 5 Years)', 'Since Inception'], index=1)

# Generate Chart Button
if st.sidebar.button('Generate Chart') or 'first_load' not in st.session_state:
    # Mark that the first load has occurred
    st.session_state.first_load = True

    # Get date range based on period selection and performance type
    start_date, end_date = get_date_range(period, basket_creation_date, performance_type)

    # Fetching and calculating performance based on inputs
    tickers = [symbol.strip() for symbol in symbols.split(',')]

    try:
        # Fetch stock data
        prices = get_stock_data(tickers, start_date, end_date)

        # Check for missing data and forward fill it
        prices.ffill(inplace=True)  # Forward filling any missing data

        # Calculate daily returns and overall performance
        daily_returns, basket_performance = calculate_basket_performance(prices)

        # Calculate market value and overall basket performance
        market_value, overall_performance = calculate_market_value_and_performance(prices, initial_investment)

        # Get the last day's daily performance
        last_day_performance = daily_returns.iloc[-1]

        # Displaying the time period as a line of text
        st.write(f"**Time Period: {start_date} to {end_date}**")

        # Displaying the investment, current market value, basket performance, and daily performance as cards
        st.markdown("""
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 22%;">
                <h4>Investment</h4>
                <p>${:,.2f}</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 22%;">
                <h4>Market Value</h4>
                <p>${:,.2f}</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 22%;">
                <h4>Basket Performance</h4>
                <p>{:.2f}%</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 22%;">
                <h4>Daily Performance (Last Day)</h4>
                <p>{:.2f}%</p>
            </div>
        </div>
        """.format(initial_investment, market_value, overall_performance, last_day_performance.mean()), unsafe_allow_html=True)

        # Show performance as line chart
        st.line_chart(basket_performance)

        # Combine prices and overall performance in a single dataframe
        performance_table = pd.concat([prices, basket_performance], axis=1)
        performance_table.columns = list(prices.columns) + ['Basket Performance (%)']

        # Show the full data table (date format without time)
        performance_table.index = performance_table.index.date
        st.write(f"Daily prices and overall performance of the {basket_name}:")
        st.dataframe(performance_table)

    except Exception as e:
        st.write(f"Error fetching data: {e}")
