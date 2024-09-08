import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

def calculate_atr(high, low, close, period=21):
    tr = np.maximum(high - low, np.abs(high - close.shift(1)), np.abs(low - close.shift(1)))
    atr = tr.rolling(window=period).mean()
    return atr

def calculate_trailing_stop(data, atr_period=21, atr_multiplier=3, update_interval=5):
    atr = calculate_atr(data['High'], data['Low'], data['Close'], period=atr_period)
    trailing_stop = pd.Series(index=data.index, dtype=float)
    is_uptrend = True
    
    # Handle the case when there's not enough data
    if len(data) <= atr_period:
        return trailing_stop
    
    current_stop = data['Close'].iloc[atr_period] - atr_multiplier * atr.iloc[atr_period]
    last_update = atr_period

    for i in range(atr_period, len(data)):
        if i - last_update >= update_interval:
            if is_uptrend:
                new_stop = data['Close'].iloc[i] - atr_multiplier * atr.iloc[i]
                if new_stop > current_stop:
                    current_stop = new_stop
                    last_update = i
                elif data['Close'].iloc[i] < current_stop:
                    is_uptrend = False
                    current_stop = data['Close'].iloc[i] + atr_multiplier * atr.iloc[i]
                    last_update = i
            else:
                new_stop = data['Close'].iloc[i] + atr_multiplier * atr.iloc[i]
                if new_stop < current_stop:
                    current_stop = new_stop
                    last_update = i
                elif data['Close'].iloc[i] > current_stop:
                    is_uptrend = True
                    current_stop = data['Close'].iloc[i] - atr_multiplier * atr.iloc[i]
                    last_update = i

        trailing_stop.iloc[i] = current_stop

    return trailing_stop

def plot_atr_trailing_stop(data, symbol, atr_period, atr_multiplier):
    # Calculate ATR and Trailing Stop
    data['ATR'] = calculate_atr(data['High'], data['Low'], data['Close'], period=atr_period)
    data['TrailingStop'] = calculate_trailing_stop(data, atr_period, atr_multiplier)

    # Remove NaN values for plotting
    data_clean = data.dropna(subset=['TrailingStop'])

    # Create the plot
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.plot(data_clean.index, data_clean['Close'], label='Close Price', color='blue')
    ax.plot(data_clean.index, data_clean['TrailingStop'], label='Trailing Stop', color='red', drawstyle='steps-post')
    
    ax.set_title(f'{symbol} - Close Price and ATR Trailing Stop ({atr_period}, {atr_multiplier}x)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True)
    
    # Ensure both lines are visible by setting y-axis limits
    y_min = min(data_clean['Close'].min(), data_clean['TrailingStop'].min())
    y_max = max(data_clean['Close'].max(), data_clean['TrailingStop'].max())
    ax.set_ylim(y_min - 0.5, y_max + 0.5)  # Add some padding

    return fig

# Streamlit app
import streamlit as st

# Set the page title
st.set_page_config(page_title="ATR Trailing Stop Calculator", page_icon="📊")

# Your app content
st.title("ATR Trailing Stop Calculator")
st.write("Welcome to the ATR Trailing Stop calculator app.")

# User inputs
symbol = st.text_input('Enter stock symbol (e.g., AAPL):', 'AAPL')

# Date range selection
today = datetime.now().date()
start_of_year = datetime(today.year, 1, 1).date()
start_date = st.date_input("Start date", value=start_of_year, max_value=today)
end_date = st.date_input("End date", value=today, max_value=today, min_value=start_date)

atr_period = st.number_input('ATR Period:', min_value=1, max_value=50, value=21)
atr_multiplier = st.number_input('ATR Multiplier:', min_value=0.1, max_value=10.0, value=3.0, step=0.1)

if st.button('Generate Chart'):
    # Download data
    data = yf.download(symbol, start=start_date, end=end_date)

    if data.empty:
        st.error(f"No data found for {symbol}. Please check the stock symbol and date range, then try again.")
    else:
        # Create and display the chart
        fig = plot_atr_trailing_stop(data, symbol, atr_period, atr_multiplier)
        st.pyplot(fig)

        # Display the data table
        st.subheader('Data Table')
        display_columns = ['Open', 'High', 'Low', 'Close', 'ATR', 'TrailingStop']
        st.dataframe(data[display_columns])

# Add some information about the app
st.sidebar.header('About')
st.sidebar.info('This app generates an ATR Trailing Stop chart for a given stock symbol. '
                'You can select the date range, ATR period, and ATR multiplier. '
                'The chart shows the close price and the calculated trailing stop.')

st.sidebar.header('ATR Trailing Stop Calculation')

import streamlit as st

st.sidebar.markdown('''
**How the ATR Trailing Stop is Calculated:**

1. **Calculate the True Range (TR):**

   - The **True Range (TR)** measures market volatility. It is the greatest of the following:
     - Current High minus Current Low
     - Absolute value of the Current High minus the Previous Close
     - Absolute value of the Current Low minus the Previous Close

   - Formula for **True Range (TR)**:
''')

# True Range formula with abs()
st.sidebar.latex(r'''
TR = \max(\text{High} - \text{Low}, \text{abs}(\text{High} - \text{Previous Close}), \text{abs}(\text{Low} - \text{Previous Close}))
''')

st.sidebar.markdown('''
2. **Calculate the Average True Range (ATR):**

   - Once we have the TR, we calculate the **Average True Range (ATR)** as the sum of the True Range (TR) over a number of days divided by the number of days (n):
''')

# ATR formula
st.sidebar.latex(r'''
ATR = \frac{\text{Sum of TR over } n \text{ days}}{n}
''')

st.sidebar.markdown('''
   where **n** is the number of days in the chosen period (typically 14 days).

3. **Calculate the Trailing Stop:**

   - When the price is in an **uptrend**, the trailing stop is calculated as:
''')

# Uptrend Trailing Stop formula
st.sidebar.latex(r'''
TrailingStop = \text{Current Price} - (ATR \times \text{Multiplier})
''')

st.sidebar.markdown('''
   - When the price is in a **downtrend**, the trailing stop is calculated as:
''')

# Downtrend Trailing Stop formula
st.sidebar.latex(r'''
TrailingStop = \text{Current Price} + (ATR \times \text{Multiplier})
''')

st.sidebar.markdown('''
   The **Multiplier** is a factor that adjusts the distance of the stop from the current price, often set between 2 and 3.

4. **Updating the Trailing Stop:**

   - In an **uptrend**, raise the trailing stop when the new stop value is higher than the previous one.
   - In a **downtrend**, lower the trailing stop when the new stop value is lower than the previous one.
   - The trend changes (from up to down or vice versa) when the price crosses the Trailing Stop.

**Key Takeaway:**  
The Trailing Stop adjusts based on market volatility (measured by ATR) and price movement. It acts as a dynamic stop-loss, protecting gains while allowing for market fluctuations.
''')
