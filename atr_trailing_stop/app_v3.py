import streamlit as st
import pandas as pd
import yfinance as yf

# Set parameters
default_symbol = 'AAPL'
period = 21  # Commonly used period for ATR
multiplier = 3
start_date = "2024-01-01"
end_date = pd.Timestamp.today()

# Function to calculate ATR trailing stop
def calculate_atr_trailing_stop(ticker, period, multiplier, start_date, end_date):
    # Fetch historical data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Calculate True Range (TR)
    data['Previous Close'] = data['Close'].shift(1)
    data['High-Low'] = data['High'] - data['Low']
    data['High-PrevClose'] = abs(data['High'] - data['Previous Close'])
    data['Low-PrevClose'] = abs(data['Low'] - data['Previous Close'])

    # True Range is the maximum of the three values
    data['TR'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)

    # Calculate ATR using the smoothing method
    data['ATR'] = data['TR'].rolling(window=period).mean()

    # Calculate trailing stop
    data['TrailingStop'] = data['Close'] - (multiplier * data['ATR'])

    return data

# Streamlit app
def main():
    st.title("ATR Trailing Stop Calculator")

    # Get ticker input
    ticker = st.text_input("Enter a ticker symbol:", default_symbol)

    if st.button("Calculate"):
        if ticker:
            data = calculate_atr_trailing_stop(ticker, period, multiplier, start_date, end_date)
            
            # Filter data for a specific date range
            filtered_data = data.loc['2024-02-29':'2024-04-10']
            st.dataframe(filtered_data[['Close', 'ATR', 'TrailingStop']])
        else:
            st.warning("Please enter a ticker symbol.")

if __name__ == "__main__":
    main()