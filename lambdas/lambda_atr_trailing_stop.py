import json
import pandas as pd
import yfinance as yf
from numpy import nan, uintc, zeros_like
from numba import njit

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

def load_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    return stock_data

def lambda_handler(event, context):
    ticker = event.get('ticker', 'AAPL')
    multiplier = event.get('multiplier', 3.0)
    length = event.get('length', 21)
    start_date = event.get('start_date', '2024-01-01')
    end_date = event.get('end_date', '2024-09-01')

    # Load stock data
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

    # Convert to JSON
    return {
        'statusCode': 200,
        'body': data[['Adj Close', 'ATR_Trailing_Stop', 'Long_Stop', 'Short_Stop']].dropna().to_json()
    }
