import streamlit as st
import pandas as pd
from datetime import datetime
from basket_utils import (
    create_basket, add_symbol, remove_symbol, delete_symbol, get_basket_json, get_active_symbols, get_basket_contents
)

# Custom CSS to adjust layout
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-left: 20px;
        padding-right: 20px;
        max-width: 100%;
    }
    .stButton > button {
        width: 100%;
    }
    .custom-column-left {
        width: 55% !important;
        margin-right: 2% !important;
    }
    .custom-column-right {
        width: 43% !important;
    }
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

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

# Sidebar for Basket Creation
with st.sidebar:
    st.header("Basket Creation")
    new_basket_name = st.text_input("Basket Name")
    new_basket_date = st.date_input("Creation Date", value=datetime.now().date())
    new_basket_time = st.time_input("Creation Time", value=st.session_state.new_basket_time)
    st.session_state.new_basket_time = new_basket_time
    if st.button("Create Basket", type="primary"):
        if new_basket_name:
            create_basket(new_basket_name, new_basket_date, new_basket_time)
            refresh_app()
        else:
            st.error("Please enter a basket name.")

# Main content area
st.title("Stocks Basket Manager")

# Use the refresh key to force a rerun
_ = st.empty().text(st.session_state.refresh_key)

# Two-column layout with custom widths
col1, col2 = st.columns([55, 45])

with col1:
    st.markdown('<div class="custom-column-left">', unsafe_allow_html=True)
    st.header("Basket Management")
    selected_basket = st.selectbox("Select Basket", ["Choose an option"] + list(st.session_state.baskets.keys()), key="basket_selector")
    st.session_state.selected_basket = selected_basket if selected_basket != "Choose an option" else None

    if st.session_state.selected_basket:
        basket = st.session_state.baskets[st.session_state.selected_basket]
        st.write(f"Created: {basket['creation_date'].strftime('%d-%b-%Y %H:%M:%S')}")
        st.write(f"ID: {basket['id']}")

        with st.expander("Add Symbol", expanded=True):
            new_symbol = st.text_input("Symbol").upper()
            add_date = st.date_input("Date", value=basket['creation_date'].date(), min_value=basket['creation_date'].date())
            add_time = st.time_input("Time", value=basket['creation_date'].time())
            if st.button("Add", type="primary"):
                if new_symbol:
                    add_symbol(st.session_state.selected_basket, new_symbol, datetime.combine(add_date, add_time))
                    refresh_app()
                else:
                    st.error("Enter a symbol.")

        with st.expander("Remove Symbol", expanded=True):
            active_symbols = get_active_symbols(basket)
            symbol_to_remove = st.selectbox("Symbol", ["No options to select."] + active_symbols if not active_symbols else active_symbols, key="remove_symbol")
            remove_date = st.date_input("Date", value=basket['creation_date'].date(), min_value=basket['creation_date'].date(), key="remove_date")
            remove_time = st.time_input("Time", value=datetime.now().time(), key="remove_time")
            if st.button("Remove", type="primary"):
                if symbol_to_remove and symbol_to_remove != "No options to select.":
                    remove_symbol(st.session_state.selected_basket, symbol_to_remove, datetime.combine(remove_date, remove_time))
                    refresh_app()
                else:
                    st.error("Select a symbol.")

        # Download JSON button
        json_str = get_basket_json(st.session_state.selected_basket)
        st.download_button(
            label="Download as JSON",
            data=json_str,
            file_name=f"{st.session_state.selected_basket}_contents.json",
            mime="application/json"
        )
    else:
        st.info("Select a basket to manage symbols.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-column-right">', unsafe_allow_html=True)
    st.header("Basket Contents")
    if st.session_state.selected_basket:
        df = get_basket_contents(st.session_state.selected_basket)
        if not df.empty:
            for index, row in df.iterrows():
                with st.container():
                    cols = st.columns([3, 4, 2, 3])
                    cols[0].write(row['symbol'])
                    cols[1].write(row['add_date'])
                    cols[2].write(row['status'])
                    if not st.session_state.delete_confirmation.get(row['symbol'], False):
                        if cols[3].button('Delete', key=f"delete_{row['symbol']}", help="Delete"):
                            st.session_state.delete_confirmation[row['symbol']] = True
                            refresh_app()
                    else:
                        confirm_col, cancel_col = cols[3].columns(2)
                        if confirm_col.button('Confirm', key=f"confirm_{row['symbol']}", type="primary"):
                            result = delete_symbol(st.session_state.selected_basket, row['symbol'])
                            st.success(result)
                            del st.session_state.delete_confirmation[row['symbol']]
                            refresh_app()
                        if cancel_col.button('Cancel', key=f"cancel_{row['symbol']}"):
                            del st.session_state.delete_confirmation[row['symbol']]
                            refresh_app()
                st.divider()
        else:
            st.info("This basket is empty.")
    else:
        st.info("Select a basket to view contents.")
    st.markdown('</div>', unsafe_allow_html=True)