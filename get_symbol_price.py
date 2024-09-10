import yfinance as yf
from datetime import datetime, timedelta

def is_weekend(date_str):
    """
    Check if a given date is a weekend.
    
    :param date_str: Date in the format 'YYYY-MM-DD'
    :return: True if the date is a weekend, False otherwise
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.weekday() >= 5  # Saturday is 5 and Sunday is 6

def is_market_open(date_str):
    """
    Check if the market was open on a given date by using a continuously traded symbol like 'SPY'.
    
    :param date_str: Date in the format 'YYYY-MM-DD'
    :return: True if the market was open, False otherwise
    """
    # Define a broader date range (including a buffer day before and after the target date)
    start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

    # Use 'SPY' (S&P 500 ETF) to check if the market was open
    market_data = yf.download('SPY', start=start_date, end=end_date)

    # Check if the specific date exists in the data (indicating that the market was open)
    return date_str in market_data.index.strftime('%Y-%m-%d')

def is_trading_day_for_symbol(symbol, date_str):
    """
    Check if the given date was a trading day for the specific symbol, ensuring the symbol existed.
    
    :param symbol: Stock symbol (e.g. 'AAPL')
    :param date_str: Date in the format 'YYYY-MM-DD'
    :return: True if the market was open and the symbol was traded on that day, False otherwise
    """
    # Check if the date falls on a weekend
    if is_weekend(date_str):
        print(f"{date_str} is a weekend. Markets are closed.")
        return False

    # Check if the market was open using 'SPY' as the reference symbol
    if not is_market_open(date_str):
        print(f"{date_str} is a holiday or non-trading day. No market data available.")
        return False

    # Check if the symbol existed and was traded on that day
    start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Download data for the specific symbol
    stock_data = yf.download(symbol, start=start_date, end=end_date)

    # Check if the symbol was traded on the specific date
    if stock_data.empty or date_str not in stock_data.index.strftime('%Y-%m-%d'):
        print(f"{symbol} was not traded on {date_str}. The symbol might not have existed then.")
        return False

    print(f"{symbol} was traded on {date_str}.")
    return True

# Example usage
symbol = 'meta'
date = '2003-09-03'  # Date format: 'YYYY-MM-DD'

is_trading_day_for_symbol(symbol, date)
