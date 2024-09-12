import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# Function to calculate ATR
def average_true_range(df, n):
    high = df['High']
    low = df['Low']
    close = df['Close']

    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))

    true_range = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    atr = true_range.rolling(window=n).mean()
    return atr

# Yahoo Finance ATR Trailing Stop Loss Algorithm
def yahoo_atr_trailing_stop(df, atr_length, atr_multiplier):
    close = df['Close']
    atr = average_true_range(df, atr_length)
    
    atr_stop = pd.Series(index=df.index)
    trend = pd.Series(index=df.index)
    
    for i in range(len(close)):
        if i == 0:
            atr_stop.iloc[i] = close.iloc[i]
            trend.iloc[i] = 1
        else:
            prev_trend = trend.iloc[i-1]
            prev_atr_stop = atr_stop.iloc[i-1]
            curr_close = close.iloc[i]
            curr_atr = atr.iloc[i]
            
            if prev_trend == 1:
                if curr_close > prev_atr_stop:
                    atr_stop.iloc[i] = round(max(prev_atr_stop, curr_close - (atr_multiplier * curr_atr)), 2)
                    trend.iloc[i] = 1
                else:
                    atr_stop.iloc[i] = round(curr_close + (atr_multiplier * curr_atr), 2)
                    trend.iloc[i] = -1
            else:  # prev_trend == -1
                if curr_close < prev_atr_stop:
                    atr_stop.iloc[i] = round(min(prev_atr_stop, curr_close + (atr_multiplier * curr_atr)), 2)
                    trend.iloc[i] = -1
                else:
                    atr_stop.iloc[i] = round(curr_close - (atr_multiplier * curr_atr), 2)
                    trend.iloc[i] = 1
    
    return atr_stop

# Load Stock Data
def load_data(ticker, start_date, end_date):
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
        if stock_data.empty:
            st.warning(f"No data found for ticker {ticker}")
        return stock_data
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        return pd.DataFrame()

# Set the page title
st.set_page_config(page_title="Yahoo ATR Trailing Stop Calculator", page_icon="📊")

# Streamlit UI
st.title("Yahoo ATR Trailing Stop Loss")

# Input from user
period = 21
multi = 3.0
ticker = st.text_input("Enter the stock ticker", value='AAPL')
multiplier = st.slider("Select ATR Multiplier", 1.0, 5.0, multi)
length = st.slider("Select ATR Period", 5, 50, period)

# Date range input
start_date = st.date_input("Select start date", value=datetime(2024, 1, 1))
end_date = st.date_input("Select end date", value=datetime.today())

# Validate the input and calculate the ATR Trailing Stop
if ticker:
    data = load_data(ticker, start_date, end_date)
    
    if not data.empty:
        # Calculate Yahoo ATR Trailing Stop
        data['Yahoo_ATR_Trailing_Stop'] = yahoo_atr_trailing_stop(data, length, multiplier)

        # Display the chart
        st.subheader(f"{ticker} Yahoo ATR Trailing Stop Loss Chart")
        st.line_chart(data[['Close', 'Yahoo_ATR_Trailing_Stop']])

        # Specify the date range (e.g., March 1st, 2024 to April 30th, 2024)
        start_date = '2024-02-29'
        end_date = '2024-04-10'

        # Filter the data between the start and end dates
        filtered_data = data.loc[start_date:end_date]
        st.subheader(f"{ticker} Stock Data with Yahoo ATR Trailing Stop Loss")
        st.write(filtered_data[['Open', 'High', 'Low', 'Close', 'Yahoo_ATR_Trailing_Stop']])
