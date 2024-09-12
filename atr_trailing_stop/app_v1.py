import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Function to calculate ATR Trailing Stop
def yahoo_atr_trailing_stop(df, atr_length=14, atr_multiplier=3.0):
    high = df['High']
    low = df['Low']
    close = df['Close']

    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Calculate ATR using EMA
    atr = tr.ewm(span=atr_length, adjust=False).mean()

    # Initialize variables
    atr_stop = pd.Series(index=df.index)
    trend = pd.Series(index=df.index)
    
    # Set initial values
    atr_stop.iloc[0] = close.iloc[0]
    trend.iloc[0] = 1 if close.iloc[0] > close.iloc[0] - (atr_multiplier * atr.iloc[0]) else -1

    for i in range(1, len(df)):
        prev_trend = trend.iloc[i-1]
        prev_atr_stop = atr_stop.iloc[i-1]
        curr_close = close.iloc[i]
        curr_atr = atr.iloc[i]
        
        if prev_trend == 1:
            if curr_close > prev_atr_stop:
                atr_stop.iloc[i] = max(prev_atr_stop, curr_close - (atr_multiplier * curr_atr))
                trend.iloc[i] = 1
            else:
                atr_stop.iloc[i] = curr_close + (atr_multiplier * curr_atr)
                trend.iloc[i] = -1
        else:  # prev_trend == -1
            if curr_close < prev_atr_stop:
                atr_stop.iloc[i] = min(prev_atr_stop, curr_close + (atr_multiplier * curr_atr))
                trend.iloc[i] = -1
            else:
                atr_stop.iloc[i] = curr_close - (atr_multiplier * curr_atr)
                trend.iloc[i] = 1

    # Shift the results forward by one day to align with Yahoo Finance
    atr_stop = atr_stop.shift(-1)

    # Round to 2 decimal places to match Yahoo Finance
    return atr_stop.round(2)

# Function to load stock data
def load_data(ticker, start_date, end_date):
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
        if stock_data.empty:
            st.warning(f"No data found for ticker {ticker}")
            return None
        return stock_data
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        return None

# Streamlit app
st.set_page_config(page_title="Yahoo ATR Trailing Stop Calculator", page_icon="📈")

st.title("Yahoo ATR Trailing Stop Calculator")

# User inputs
col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Enter stock ticker", value="AAPL")
    atr_length = st.number_input("ATR Length", min_value=1, value=14)
with col2:
    end_date = st.date_input("End Date", value=datetime.now())
    start_date = st.date_input("Start Date", value=end_date - timedelta(days=365))
    atr_multiplier = st.number_input("ATR Multiplier", min_value=0.1, value=3.0, step=0.1)

if st.button("Calculate ATR Trailing Stop"):
    data = load_data(ticker, start_date, end_date)
    
    if data is not None and not data.empty:
        data['Yahoo_ATR_Trailing_Stop'] = yahoo_atr_trailing_stop(data, atr_length, atr_multiplier)
        
        # Ensure the index is a DatetimeIndex
        data.index = pd.to_datetime(data.index)
        
        # Display the data
        st.subheader(f"{ticker} Yahoo ATR Trailing Stop Loss Data")
        display_data = data[['Close', 'Yahoo_ATR_Trailing_Stop']].copy()
        display_data.index = display_data.index.date  # Convert to date for display
        st.dataframe(display_data.style.format({'Close': '{:.2f}', 'Yahoo_ATR_Trailing_Stop': '{:.2f}'}))
        
        # Plot the data
        st.subheader(f"{ticker} Price and ATR Trailing Stop")
        st.line_chart(display_data)
    else:
        st.warning("Unable to process the data. Please check your inputs and try again.")

st.markdown("---")
st.markdown("Created with ❤️ using Streamlit and yfinance")