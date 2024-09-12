import yfinance as yf
from datetime import datetime, timedelta

def is_weekend(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.weekday() >= 5

def is_market_open(date_str):
    start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    market_data = yf.download('SPY', start=start_date, end=end_date, progress=False)
    return date_str in market_data.index.strftime('%Y-%m-%d')

def is_trading_day_for_symbol(symbol, date_str):
    if is_weekend(date_str):
        return False
    if not is_market_open(date_str):
        return False
    start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)
    return not stock_data.empty and date_str in stock_data.index.strftime('%Y-%m-%d')

def check_symbol_exists(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        company_name = info.get('shortName', None)
        asset_type = info.get('quoteType', None)
        
        if not company_name or not asset_type:
            return company_name, asset_type, 'N/A', 'N/A', 'N/A', "Invalid"
        
        hist = stock.history(period='5d')
        if hist.empty:
            return company_name, asset_type, 'N/A', 'N/A', 'N/A', "Valid but Not Traded"

        last_traded_date = hist.index.max().strftime('%Y-%m-%d')
        last_volume = hist['Volume'].iloc[-1]
        last_close = hist['Close'].iloc[-1]

        if last_traded_date == datetime.now().strftime('%Y-%m-%d') and last_volume > 0:
            return company_name, asset_type, last_traded_date, last_volume, last_close, "Valid and Traded"
        elif last_volume == 0:
            return company_name, asset_type, last_traded_date, last_volume, last_close, "Valid but Not Traded"
        elif last_close == hist['Close'].max() and hist['Close'].nunique() == 1:
            return company_name, asset_type, last_traded_date, last_volume, last_close, "Valid but Not Traded"
        else:
            return company_name, asset_type, last_traded_date, last_volume, last_close, "Valid"
    except Exception:
        return None, None, 'N/A', 'N/A', 'N/A', "Invalid"
