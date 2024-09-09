import streamlit as st
import pandas as pd
import json
from datetime import datetime
import uuid

# Initialize session state
if 'baskets' not in st.session_state:
    st.session_state.baskets = {}
if 'new_basket_time' not in st.session_state:
    st.session_state.new_basket_time = datetime.now().time()
if 'selected_basket' not in st.session_state:
    st.session_state.selected_basket = None

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

def is_valid_add_date(basket, symbol, add_date):
    symbol_history = [s for s in basket['symbols'] if s['symbol'] == symbol]
    for entry in symbol_history:
        if entry['add_date'] <= add_date <= (entry['remove_date'] or datetime.max):
            return False
    return True

def add_symbol(basket_name, symbol, add_date):
    basket = st.session_state.baskets[basket_name]
    if not add_date:
        add_date = datetime.now()
    
    if add_date < basket['creation_date']:
        st.error("Symbol add date cannot be before basket creation date.")
        return

    if not is_valid_add_date(basket, symbol, add_date):
        st.error(f"Cannot add {symbol} on {add_date.strftime('%d-%b-%Y')} as it overlaps with a previous entry.")
        return

    active_symbols = [s for s in basket['symbols'] if s['status'] == 'active' and s['symbol'] == symbol]
    if active_symbols:
        st.error(f"Symbol '{symbol}' is already active in the basket.")
        return

    basket['symbols'].append({
        'symbol': symbol,
        'add_date': add_date,
        'remove_date': None,
        'status': 'active'
    })
    st.success(f"Symbol '{symbol}' added to basket '{basket_name}'.")

def remove_symbol(basket_name, symbol, remove_date):
    basket = st.session_state.baskets[basket_name]
    if not remove_date:
        remove_date = datetime.now()

    for s in basket['symbols']:
        if s['symbol'] == symbol and s['status'] == 'active':
            if remove_date < s['add_date'] or remove_date < basket['creation_date']:
                st.error("Symbol remove date cannot be before its add date or basket creation date.")
                return
            s['remove_date'] = remove_date
            s['status'] = 'removed'
            st.success(f"Symbol '{symbol}' removed from basket '{basket_name}'.")
            return

    st.error(f"Active symbol '{symbol}' not found in basket '{basket_name}'.")

def delete_symbol(basket_name, symbol):
    basket = st.session_state.baskets[basket_name]
    basket['symbols'] = [s for s in basket['symbols'] if s['symbol'] != symbol]
    st.success(f"Symbol '{symbol}' completely removed from basket '{basket_name}'.")

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

# Left Sidebar for Basket Creation
st.sidebar.header("Basket Creation")
st.sidebar.write("Create a new basket with a name and creation date/time.")
new_basket_name = st.sidebar.text_input("Basket Name")
new_basket_date = st.sidebar.date_input("Basket Creation Date", value=datetime.now().date())
new_basket_time = st.sidebar.time_input("Basket Creation Time", value=st.session_state.new_basket_time)
st.session_state.new_basket_time = new_basket_time
if st.sidebar.button("Create Basket", type="primary"):
    if new_basket_name:
        create_basket(new_basket_name, new_basket_date, new_basket_time)
    else:
        st.sidebar.error("Please enter a basket name.")

# Main app
st.title("Stocks Basket Manager")

# Basket Management
st.header("Basket Management")
st.write("Select a basket to manage its symbols and view details.")
selected_basket = st.selectbox("Select Basket", list(st.session_state.baskets.keys()), key="basket_selector")
st.session_state.selected_basket = selected_basket

if selected_basket:
    basket = st.session_state.baskets[selected_basket]
    st.write(f"Creation Date: {basket['creation_date'].strftime('%d-%b-%Y %H:%M:%S')}")
    st.write(f"Basket ID: {basket['id']}")

    st.subheader("Add Symbol")
    st.write("Add a new symbol to the selected basket.")
    new_symbol = st.text_input("Symbol to Add")
    min_date = basket['creation_date'].date()
    add_date = st.date_input("Symbol Add Date", value=min_date, min_value=min_date)
    add_time = st.time_input("Symbol Add Time", value=basket['creation_date'].time())
    if st.button("Add Symbol", type="primary"):
        if new_symbol:
            add_symbol(selected_basket, new_symbol, datetime.combine(add_date, add_time))
        else:
            st.error("Please enter a symbol.")

    st.subheader("Remove Symbol")
    st.write("Mark a symbol as removed from the basket.")
    active_symbols = [s['symbol'] for s in basket['symbols'] if s['status'] == 'active']
    symbol_to_remove = st.selectbox("Symbol to Remove", active_symbols, key="remove_symbol")
    remove_date = st.date_input("Symbol Remove Date", value=datetime.now().date(), min_value=min_date)
    remove_time = st.time_input("Symbol Remove Time", value=datetime.now().time())
    if st.button("Remove Symbol", type="primary"):
        if symbol_to_remove:
            remove_symbol(selected_basket, symbol_to_remove, datetime.combine(remove_date, remove_time))
        else:
            st.error("Please select a symbol to remove.")

    st.subheader("Delete Symbol")
    st.write("Deletes the symbol permanently from the basket.")
    all_symbols = list(set([s['symbol'] for s in basket['symbols']]))
    symbol_to_delete = st.selectbox("Symbol to Delete", all_symbols, key="delete_symbol")
    if st.button("Delete Symbol", type="secondary"):
        if symbol_to_delete:
            if st.button(f"Confirm deletion of {symbol_to_delete}", type="secondary"):
                delete_symbol(selected_basket, symbol_to_delete)
        else:
            st.error("Please select a symbol to delete.")

# Right Sidebar for Basket Contents
st.sidebar.header("Basket Contents", anchor="right")
st.sidebar.write("View and download the contents of the selected basket.")
view_basket = st.session_state.selected_basket
if view_basket:
    basket = st.session_state.baskets[view_basket]
    st.sidebar.subheader(f"{view_basket} Contents")
    df = pd.DataFrame(basket['symbols'])
    if not df.empty:
        df['add_date'] = pd.to_datetime(df['add_date']).dt.strftime('%d-%b-%Y %H:%M:%S')
        df['remove_date'] = pd.to_datetime(df['remove_date']).dt.strftime('%d-%b-%Y %H:%M:%S')
        st.sidebar.dataframe(df)
        
        # Download JSON button
        json_str = get_basket_json(view_basket)
        st.sidebar.download_button(
            label="Download Basket as JSON",
            data=json_str,
            file_name=f"{view_basket}_contents.json",
            mime="application/json"
        )
    else:
        st.sidebar.info("This basket is empty.")
else:
    st.sidebar.info("Select a basket to view its contents.")