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
            df['remove_date'] = df['remove_date'].replace('NaT', '-')
            
            # Create a copy of the dataframe for display
            display_df = df.copy()
            display_df['action'] = 'Delete'
            
            # Display the table
            st.table(display_df)
            
            # Handle delete actions
            for index, row in df.iterrows():
                col1, col2, col3 = st.columns([6, 1, 1])
                with col3:
                    if st.button('🗑️', key=f"delete_{row['symbol']}", help="Delete"):
                        st.session_state[f"delete_confirmation_{row['symbol']}"] = True
                        st.rerun()
                
                if st.session_state.get(f"delete_confirmation_{row['symbol']}", False):
                    with col1:
                        st.warning(f"Are you sure you want to delete {row['symbol']}?")
                    with col2:
                        if st.button('Yes', key=f"confirm_{row['symbol']}"):
                            result = delete_symbol(st.session_state.selected_basket, row['symbol'])
                            st.success(result)
                            del st.session_state[f"delete_confirmation_{row['symbol']}"]
                            st.session_state.refresh_key += 1  # Increment refresh key
                            st.rerun()
                    with col3:
                        if st.button('No', key=f"cancel_{row['symbol']}"):
                            del st.session_state[f"delete_confirmation_{row['symbol']}"]
                            st.rerun()
        else:
            st.info("This basket is empty.")
    else:
        st.info("Select a basket to view contents.")