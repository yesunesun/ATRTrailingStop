import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Function to calculate True Range
def calculate_true_range(high, low, previous_close):
    tr = max(high - low, abs(high - previous_close), abs(low - previous_close))
    return tr

# Function to calculate ATR using the exponential moving average (smoothing method shown in the formula)
def calculate_atr(highs, lows, closes, period):
    atr_values = []
    previous_atr = 0

    if len(highs) < period:
        return [float('NaN')] * len(highs)

    for i in range(len(highs)):
        if i == 0:
            true_ranges = [calculate_true_range(highs.iloc[j], lows.iloc[j], closes.iloc[j-1] if j > 0 else closes.iloc[0]) for j in range(min(period, len(highs)))]
            previous_atr = sum(true_ranges) / period
            atr_values.append(previous_atr)
        else:
            current_tr = calculate_true_range(highs.iloc[i], lows.iloc[i], closes.iloc[i-1])
            current_atr = (previous_atr * (period - 1) + current_tr) / period
            atr_values.append(current_atr)
            previous_atr = current_atr

    return pd.Series(atr_values, index=highs.index)

# Function to calculate the trailing stop loss for both long and short positions
def calculate_trailing_stop(df, multiplier, atr_period):
    atr = df['ATR']
    ts = atr * multiplier

    atr_ts = pd.Series(np.nan, index=df.index)

    for i in range(1, len(df)):
        if df['Close'].iloc[i] > atr_ts.iloc[i-1] if not np.isnan(atr_ts.iloc[i-1]) else 0:
            if df['Close'].iloc[i-1] > atr_ts.iloc[i-1] if not np.isnan(atr_ts.iloc[i-1]) else 0:
                atr_ts.iloc[i] = max(atr_ts.iloc[i-1] if not np.isnan(atr_ts.iloc[i-1]) else df['Close'].iloc[i] - ts.iloc[i], df['Close'].iloc[i] - ts.iloc[i])
            else:
                atr_ts.iloc[i] = df['Close'].iloc[i] - ts.iloc[i]
        elif df['Close'].iloc[i] < atr_ts.iloc[i-1] if not np.isnan(atr_ts.iloc[i-1]) else 0:
            if df['Close'].iloc[i-1] < atr_ts.iloc[i-1] if not np.isnan(atr_ts.iloc[i-1]) else 0:
                atr_ts.iloc[i] = min(atr_ts.iloc[i-1] if not np.isnan(atr_ts.iloc[i-1]) else df['Close'].iloc[i] + ts.iloc[i], df['Close'].iloc[i] + ts.iloc[i])
            else:
                atr_ts.iloc[i] = df['Close'].iloc[i] + ts.iloc[i]
        else:
            atr_ts.iloc[i] = atr_ts.iloc[i-1] if not np.isnan(atr_ts.iloc[i-1]) else df['Close'].iloc[i] - ts.iloc[i]

    return atr_ts

# Streamlit app
def app():
    st.set_page_config(page_title="ATR Trailing Stop", layout="wide")

    # Sidebar Inputs
    st.sidebar.title("Input Parameters")
    symbol = st.sidebar.text_input("Ticker Symbol", "AAPL")
    start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))
    end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))
    atr_period = st.sidebar.number_input("ATR Period", min_value=1, max_value=100, value=21)
    multiplier = st.sidebar.number_input("Multiplier", min_value=1.0, max_value=10.0, value=3.0, step=0.1)

    # Sidebar for formulas in LaTeX
    st.sidebar.title("Formulas")

    # True Range Formula
    st.sidebar.latex(r"""
        TR = \max(High - Low, |High - PreviousClose|, |Low - PreviousClose|)
        """)
    st.sidebar.write("True Range (TR) measures volatility by taking the largest of the current high minus low, the absolute value of the high minus the previous close, and the absolute value of the low minus the previous close.")

    # ATR Formula
    st.sidebar.latex(r"""
        ATR_{t} = \frac{(ATR_{t-1} \cdot (n-1) + TR)}{n}
        """)
    st.sidebar.write("The Average True Range (ATR) is a moving average of True Range, calculated with a smoothing factor, providing insight into price volatility.")

    # Trailing Stop Formula (Long and Short)
    st.sidebar.latex(r"""
        TrailingStop_{Long} = Close - (Multiplier \cdot ATR)
        """)
    st.sidebar.write("The trailing stop for long positions subtracts a multiple of the ATR from the closing price.")

    st.sidebar.latex(r"""
        TrailingStop_{Short} = Close + (Multiplier \cdot ATR)
        """)
    st.sidebar.write("The trailing stop for short positions adds a multiple of the ATR to the closing price.")

    # Trend Identification Formula
    st.sidebar.latex(r"""
        Trend = 
        \begin{cases}
        \text{Long} & \text{if Close} > \text{ATR Trailing Stop} \\
        \text{Short} & \text{if Close} < \text{ATR Trailing Stop} \\
        \end{cases}
        """)
    st.sidebar.write("The trend is identified based on the position of the closing price relative to the ATR trailing stop. If the price is above the trailing stop, it is a long trend, otherwise, it is a short trend.")

    # Download data and calculate ATR and trailing stop loss
    df = yf.download(symbol, start=start_date, end=end_date)

    if not df.empty:
        df = df.round(2).drop(columns='Volume')
        df['ATR'] = calculate_atr(df['High'], df['Low'], df['Close'], atr_period)
        df['ATR_Trailing_Stop'] = calculate_trailing_stop(df, multiplier, atr_period)

        # Display Title and Header
        st.header(f"ATR Trailing Stop for {symbol}")

        # Plot chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df.index, df['Close'], label='Close Price', color='blue')
        ax.plot(df.index, df['ATR_Trailing_Stop'], label='ATR Trailing Stop', color='red', linestyle='--')
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        ax.set_title(f"{symbol} - ATR Trailing Stop Chart")
        st.pyplot(fig)

        # Show Data Table
        st.write(df[['High', 'Low', 'Close', 'ATR', 'ATR_Trailing_Stop']])

    else:
        st.write("No data available for the selected inputs.")

if __name__ == "__main__":
    app()
