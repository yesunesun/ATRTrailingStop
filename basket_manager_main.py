import streamlit as st
import pandas as pd
from datetime import datetime
from basket_utils import (
    create_basket, add_symbol, remove_symbol, delete_symbol, get_basket_json, get_active_symbols, get_basket_contents
)

# Initialize session state
if 'baskets' not in st.session_state:
    st.session_state.baskets = {}
if 'new_basket_time' not in st.session_state:
    st.session_state.new_basket_time = datetime.now().time()
if 'selected_basket' not in st.session_state:
    st.session_state.selected_basket = None
if 'delete_confirmation' not in st.session_state:
    st.session_state.delete_confirmation = {}
if 'refresh_key' not in st.session_state:
    st.session_state.refresh_key = 0

# Function to increment refresh key
def refresh_app():
    st.session_state.refresh_key += 1

# Main app
st.title("Stocks Basket Manager")

# Use the refresh key to force a rerun
_ = st.empty().text(st.session_state.refresh_key)

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
    new_symbol = st.text_input("Symbol to Add").upper()
    min_date = basket['creation_date'].date()
    add_date = st.date_input("Symbol Add Date", value=min_date, min_value=min_date)
    add_time = st.time_input("Symbol Add Time", value=basket['creation_date'].time())
    if st.button("Add Symbol", type="primary"):
        if new_symbol:
            add_symbol(selected_basket, new_symbol, datetime.combine(add_date, add_time))
            refresh_app()
        else:
            st.error("Please enter a symbol.")

    st.subheader("Remove Symbol")
    st.write("Mark a symbol as removed from the basket.")
    active_symbols = get_active_symbols(basket)
    symbol_to_remove = st.selectbox("Symbol to Remove", active_symbols, key="remove_symbol")
    remove_date = st.date_input("Symbol Remove Date", value=basket['creation_date'].date(), min_value=basket['creation_date'].date())
    remove_time = st.time_input("Symbol Remove Time", value=datetime.now().time())
    if st.button("Remove Symbol", type="primary"):
        if symbol_to_remove:
            remove_symbol(selected_basket, symbol_to_remove, datetime.combine(remove_date, remove_time))
            refresh_app()
        else:
            st.error("Please select a symbol to remove.")

    # Basket Contents with Delete Option
    st.subheader("Basket Contents")
    df = get_basket_contents(selected_basket)
    if not df.empty:
        for index, row in df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 3, 1, 1, 2])
            with col1:
                st.write(row['symbol'])
            with col2:
                st.write(row['add_date'])
            with col3:
                st.write(row['remove_date'] if pd.notna(row['remove_date']) else 'Active')
            with col4:
                st.write(row['status'])
            with col5:
                if st.button('🗑️', key=f"delete_{row['symbol']}", help="Delete this symbol"):
                    st.session_state.delete_confirmation[row['symbol']] = True
                    refresh_app()
            with col6:
                if st.session_state.delete_confirmation.get(row['symbol'], False):
                    if st.button('Confirm Delete', key=f"confirm_{row['symbol']}", type="primary"):
                        result = delete_symbol(selected_basket, row['symbol'])
                        st.success(result)
                        del st.session_state.delete_confirmation[row['symbol']]
                        refresh_app()
                    if st.button('Cancel', key=f"cancel_{row['symbol']}"):
                        del st.session_state.delete_confirmation[row['symbol']]
                        refresh_app()
    else:
        st.info("This basket is empty.")

    # Download JSON button
    json_str = get_basket_json(selected_basket)
    st.download_button(
        label="Download Basket as JSON",
        data=json_str,
        file_name=f"{selected_basket}_contents.json",
        mime="application/json"
    )
else:
    st.info("Select a basket to view its contents and manage symbols.")