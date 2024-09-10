import streamlit as st
from datetime import datetime
from basket_utils import add_symbol, remove_symbol, get_active_symbols

def render_basket_management():
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
                    st.session_state.refresh_key += 1
                else:
                    st.error("Enter a symbol.")

        with st.expander("Remove Symbol", expanded=True):
            active_symbols = get_active_symbols(basket)
            symbol_options = ["Select Symbol to Remove"] + active_symbols
            symbol_to_remove = st.selectbox("Symbol", symbol_options, key="remove_symbol")
            remove_date = st.date_input("Date", value=basket['creation_date'].date(), min_value=basket['creation_date'].date(), key="remove_date")
            remove_time = st.time_input("Time", value=datetime.now().time(), key="remove_time")
            if st.button("Remove", type="primary"):
                if symbol_to_remove and symbol_to_remove != "Select Symbol to Remove":
                    remove_symbol(st.session_state.selected_basket, symbol_to_remove, datetime.combine(remove_date, remove_time))
                    st.session_state.refresh_key += 1
                else:
                    st.error("Select a symbol to remove.")
    else:
        st.info("Select a basket to manage symbols.")