import streamlit as st
import pandas as pd
import json
from datetime import datetime
import uuid
import yfinance as yf

def create_basket(name, creation_date, creation_time):
    creation_datetime = datetime.combine(creation_date, creation_time)
    basket_id = str(uuid.uuid4())
    st.session_state.baskets[name] = {
        'id': basket_id,
        'creation_date': creation_datetime,
        'symbols': []
    }
    st.sidebar.success(f"Basket '{name}' created successfully!")
    st.session_state.selected_basket = name

def is_valid_symbol(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return 'symbol' in info and info['symbol'] == symbol
    except:
        return False

def is_valid_add_date(basket, symbol, add_datetime):
    symbol_history = [s for s in basket['symbols'] if s['symbol'] == symbol]
    for entry in symbol_history:
        remove_datetime = entry['remove_date'] or datetime.max
        if entry['add_date'] <= add_datetime < remove_datetime:
            return False
    return True

def add_symbol(basket_name, symbol, add_datetime):
    symbol = symbol.upper()  # Convert symbol to uppercase
    basket = st.session_state.baskets[basket_name]
    if not add_datetime:
        add_datetime = datetime.now()
    
    if add_datetime < basket['creation_date']:
        st.error("Symbol add date/time cannot be before basket creation date/time.")
        return

    if not is_valid_symbol(symbol):
        st.error(f"'{symbol}' is not a valid stock symbol.")
        return

    if not is_valid_add_date(basket, symbol, add_datetime):
        st.error(f"Cannot add {symbol} on {add_datetime.strftime('%d-%b-%Y %H:%M:%S')} as it overlaps with a previous entry.")
        return

    active_symbols = [s for s in basket['symbols'] if s['status'] == 'active' and s['symbol'] == symbol]
    if active_symbols:
        st.error(f"Symbol '{symbol}' is already active in the basket.")
        return

    basket['symbols'].append({
        'symbol': symbol,
        'add_date': add_datetime,
        'remove_date': None,
        'status': 'active'
    })
    st.success(f"Symbol '{symbol}' added to basket '{basket_name}'.")

def remove_symbol(basket_name, symbol, remove_datetime):
    symbol = symbol.upper()  # Convert symbol to uppercase
    basket = st.session_state.baskets[basket_name]
    if not remove_datetime:
        remove_datetime = datetime.now()

    for s in basket['symbols']:
        if s['symbol'] == symbol and s['status'] == 'active':
            if remove_datetime < s['add_date'] or remove_datetime < basket['creation_date']:
                st.error("Symbol remove date/time cannot be before its add date/time or basket creation date/time.")
                return
            s['remove_date'] = remove_datetime
            s['status'] = 'removed'
            st.success(f"Symbol '{symbol}' removed from basket '{basket_name}'.")
            return

    st.error(f"Active symbol '{symbol}' not found in basket '{basket_name}'.")

def delete_symbol(basket_name, symbol):
    symbol = symbol.upper()  # Convert symbol to uppercase
    basket = st.session_state.baskets[basket_name]
    basket['symbols'] = [s for s in basket['symbols'] if s['symbol'] != symbol]
    return f"Symbol '{symbol}' completely removed from basket '{basket_name}'."

def get_basket_contents(basket_name):
    basket = st.session_state.baskets[basket_name]
    df = pd.DataFrame(basket['symbols'])
    if not df.empty:
        df['add_date'] = pd.to_datetime(df['add_date']).dt.strftime('%d-%b-%Y %H:%M:%S')
        df['remove_date'] = pd.to_datetime(df['remove_date']).dt.strftime('%d-%b-%Y %H:%M:%S')
    return df

def get_basket_json(basket_name):
    basket = st.session_state.baskets[basket_name]
    active_symbols = []
    removed_symbols = []
    
    for symbol in basket['symbols']:
        symbol_data = {
            'symbol': symbol['symbol'],
            'add_date': symbol['add_date'].strftime('%d-%b-%Y %H:%M:%S'),
        }
        if symbol['remove_date']:
            symbol_data['remove_date'] = symbol['remove_date'].strftime('%d-%b-%Y %H:%M:%S')
            removed_symbols.append(symbol_data)
        else:
            active_symbols.append(symbol_data)
    
    basket_data = {
        'name': basket_name,
        'id': basket['id'],
        'creation_date': basket['creation_date'].strftime('%d-%b-%Y %H:%M:%S'),
        'active_symbols': active_symbols,
        'removed_symbols': removed_symbols
    }
    return json.dumps(basket_data, indent=2)

def get_active_symbols(basket):
    return [s['symbol'] for s in basket['symbols'] if s['status'] == 'active']