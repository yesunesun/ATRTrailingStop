
import streamlit as st
import pandas as pd
from numpy import isnan, nan, uintc, zeros_like
from numba import njit
import yfinance as yf
from datetime import datetime

# ATR Trailing Stop Loss Algorithm
@njit(cache=True)
def nb_atrts(x, ma, atr_, length, ma_length):
    m = x.size
    k = max(length, ma_length)

    result = x.copy()
    up = zeros_like(x, dtype=uintc)
    dn = zeros_like(x, dtype=uintc)

    expn = x > ma
    up[expn], dn[~expn] = 1, 1
    up[:k], dn[:k] = 0, 0
    result[:k] = nan

    for i in range(k, m):
        pr = result[i - 1]
        if up[i]:
            result[i] = x[i] - atr_[i]
            if result[i] < pr:
                result[i] = pr
        if dn[i]:
            result[i] = x[i] + atr_[i]
            if result[i] > pr:
                result[i] = pr

    long, short = result * up, result * dn
    long[long == 0], short[short == 0] = nan, nan

    return result, long, short

# Load Stock Data
def load_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    return stock_data

# Set the page title
st.set_page_config(page_title="ATR Trailing Stop Calculator", page_icon="📊")

# Streamlit UI
st.title("ATR Trailing Stop Loss")

# Sidebar with corrected formulas
st.sidebar.title("Formulas Used in Calculations")

st.sidebar.markdown("### 1. True Range (TR):")
st.sidebar.latex(r"TR = \max(High - Low, |High - Previous\ Close|, |Low - Previous\ Close|)")

st.sidebar.markdown("### 2. Average True Range (ATR):")
st.sidebar.latex(r"ATR = \frac{\sum TR}{n}")

st.sidebar.markdown("### 3. Moving Average (MA):")
st.sidebar.latex(r"MA = \frac{\sum Adj\ Close}{n}")

st.sidebar.markdown("### 4. ATR Trailing Stop for Uptrend (Long Stop):")
st.sidebar.latex(r"Long\ Stop = Current\ Price - (ATR \times Multiplier)")

st.sidebar.markdown("### 5. ATR Trailing Stop for Downtrend (Short Stop):")
st.sidebar.latex(r"Short\ Stop = Current\ Price + (ATR \times Multiplier)")


# Input from user
ticker = st.text_input("Enter the stock ticker", value='AAPL')
multiplier = st.slider("Select ATR Multiplier", 1.0, 5.0, 3.0)
length = st.slider("Select ATR Length", 5, 50, 21)

# Date range input
start_date = st.date_input("Select start date", value=datetime(2024, 1, 1))
end_date = st.date_input("Select end date", value=datetime.today())

if ticker:
    data = load_data(ticker, start_date, end_date)
    
    # Calculate ATR
    data['High-Low'] = data['High'] - data['Low']
    data['High-PrevClose'] = abs(data['High'] - data['Adj Close'].shift(1))
    data['Low-PrevClose'] = abs(data['Low'] - data['Adj Close'].shift(1))
    data['TR'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=length).mean()

    # Calculate Moving Average (MA)
    data['MA'] = data['Adj Close'].rolling(window=length).mean()

    # ATR Trailing Stop Calculation
    result, long_stop, short_stop = nb_atrts(data['Adj Close'].values, data['MA'].values, data['ATR'].values, length, length)

    data['ATR_Trailing_Stop'] = result
    data['Long_Stop'] = long_stop
    data['Short_Stop'] = short_stop

    # Display the chart title before the chart
    st.subheader(f"{ticker} ATR Trailing Stop Loss Chart")

    # Display the chart
    st.line_chart(data[['Adj Close', 'ATR_Trailing_Stop']])

    
    # Display the full data table (same data as in chart)
    st.subheader(f"{ticker} Stock Data with ATR Trailing Stop Loss")
    st.write(data[['Adj Close', 'ATR_Trailing_Stop', 'Long_Stop', 'Short_Stop']])
