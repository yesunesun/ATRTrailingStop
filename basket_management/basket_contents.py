import streamlit as st
import pandas as pd
from basket_utils import get_basket_contents, delete_symbol, get_basket_json

def render_basket_contents():
    st.header("Basket Contents")
    if st.session_state.selected_basket:
        # Add the download icon at the top right
        col1, col2 = st.columns([3, 1])
        with col2:
            json_str = get_basket_json(st.session_state.selected_basket)
            st.download_button(
                label="📥",  # Download icon
                data=json_str,
                file_name=f"{st.session_state.selected_basket}_contents.json",
                mime="application/json",
                help="Download Basket as JSON"  # Tooltip text
            )
        
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