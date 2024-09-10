import streamlit as st
import pandas as pd
from basket_utils import get_basket_contents, delete_symbol

def render_basket_contents():
    st.header("Basket Contents")
    if st.session_state.selected_basket:
        df = get_basket_contents(st.session_state.selected_basket)
        if not df.empty:
            # Ensure all required columns are present
            required_columns = ['symbol', 'add_date', 'remove_date', 'status']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Convert dates to string format for display
            df['add_date'] = pd.to_datetime(df['add_date']).dt.strftime('%d-%b-%Y %H:%M:%S')
            df['remove_date'] = pd.to_datetime(df['remove_date']).dt.strftime('%d-%b-%Y %H:%M:%S')
            df['remove_date'] = df['remove_date'].replace('NaT', 'nan')
            
            # Display table headers
            cols = st.columns([2, 3, 3, 2, 1])
            cols[0].write("**Symbol**")
            cols[1].write("**Add Date**")
            cols[2].write("**Remove Date**")
            cols[3].write("**Status**")
            cols[4].write("**Action**")
            
            # Display the table contents
            for index, row in df.iterrows():
                cols = st.columns([2, 3, 3, 2, 1])
                cols[0].write(row['symbol'])
                cols[1].write(row['add_date'])
                cols[2].write(row['remove_date'])
                cols[3].write(row['status'])
                if cols[4].button('🗑️', key=f"delete_{row['symbol']}", help="Delete"):
                    result = delete_symbol(st.session_state.selected_basket, row['symbol'])
                    st.success(result)
                    st.session_state.refresh_key += 1  # Increment refresh key
                    st.rerun()
            
        else:
            st.info("This basket is empty.")
    else:
        st.info("Select a basket to view contents.")