import yfinance as yf
import pandas as pd
import streamlit as st
import altair as alt
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

# Function to plot the chart using Altair with hover tooltips
def plot_basket_performance(basket_performance, prices):
    # Create a DataFrame with performance and date for charting
    performance_df = basket_performance.reset_index()
    performance_df['Date'] = pd.to_datetime(performance_df['Date']).dt.date  # Converting to just the date
    
    # Melt the DataFrame to have stock symbols as rows instead of columns for better tooltip interaction
    melted_prices = prices.reset_index()
    melted_prices['Date'] = pd.to_datetime(melted_prices['Date']).dt.date  # Ensure the date is in the same format
    melted_prices = melted_prices.melt(id_vars=['Date'], var_name='Symbol', value_name='Price')

    # Combine performance and prices into a single charting data
    chart_data = pd.merge(melted_prices, performance_df, on='Date', how='inner')

    # Create Altair chart
    line_chart = alt.Chart(chart_data).mark_line().encode(
        x='Date:T',
        y='Basket Performance:Q',
        color='Symbol:N',
        tooltip=['Date:T', 'Symbol:N', 'Price:Q', 'Basket Performance:Q']  # Tooltip to show metrics
    ).interactive()  # Add interaction for hovering
    
    return line_chart

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

        # Displaying the investment, current market value, and overall performance as cards
        st.markdown("""
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 22%;">
                <h6 style="font-size: 18px; font-weight: bold;">Investment</h6>
                <p style="font-size: 16px;">${:,.2f}</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 22%;">
                <h6 style="font-size: 18px; font-weight: bold;">Market Value</h6>
                <p style="font-size: 16px;">${:,.2f}</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 22%;">
                <h6 style="font-size: 18px; font-weight: bold;">Basket Performance</h6>
                <p style="font-size: 16px;">{:.2f}%</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; width: 22%;">
                <h6 style="font-size: 18px; font-weight: bold;">Daily Performance (Last Day)</h6>
                <p style="font-size: 16px;">{:.2f}%</p>
            </div>
        </div>
        """.format(initial_investment, market_value, overall_performance, last_day_performance.mean()), unsafe_allow_html=True)

        # Use Altair for performance chart with hover metrics
        performance_chart = plot_basket_performance(basket_performance, prices)
        st.altair_chart(performance_chart, use_container_width=True)

        # Combine prices and overall performance in a single dataframe
        # First, ensure that all column names in prices and basket_performance are strings
        prices.columns = prices.columns.map(str)
        basket_performance.name = 'Basket Performance (%)'  # Ensure the name is a string

        # Concatenate the two DataFrames
        performance_table = pd.concat([prices, basket_performance], axis=1)

        # Convert all column names to strings to avoid mixed-type warnings
        performance_table.columns = performance_table.columns.map(str)

        # Show the full data table (date format without time)
        performance_table.index = performance_table.index.date
        st.write(f"Daily prices and overall performance of the {basket_name}:")
        st.dataframe(performance_table)

        # Sidebar Calculations for Market Value, Basket Performance, and Daily Performance (formulas instead of values)
        st.sidebar.subheader("Calculations (Formulas)")
        st.sidebar.write("""
        **Market Value Formula:**
        Market Value = (Latest Stock Price / Initial Stock Price) * Initial Investment
        """)
        st.sidebar.write("""
        **Basket Performance Formula:**
        Basket Performance = ((Market Value - Initial Investment) / Initial Investment) * 100
        """)
        st.sidebar.write("""
        **Daily Performance Formula:**
        Daily Performance = Percentage change in stock prices for each day
        """)

    except Exception as e:
        st.write(f"Error fetching data: {e}")
