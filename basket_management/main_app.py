import streamlit as st
from datetime import datetime
from basket_utils import create_basket
from basket_management import render_basket_management
from basket_contents import render_basket_contents

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
    render_basket_management()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-column-right">', unsafe_allow_html=True)
    render_basket_contents()
    st.markdown('</div>', unsafe_allow_html=True)