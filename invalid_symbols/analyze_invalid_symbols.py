import streamlit as st
import pandas as pd
import json
from datetime import datetime
from business_logic import check_symbol_exists

# Set the page title
st.set_page_config(page_title="Invalid Symbol Analyzer")

# Custom CSS to reduce the space between the sidebar and content and increase content width
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

# Sidebar for explanations and conditions used
st.sidebar.title("Filtering Conditions and Logic")
st.sidebar.write("""
We use the following financial and data conditions to determine whether a symbol is considered valid or traded:

1. **Symbol Existence**: We use the `yfinance` API to check whether a symbol exists. If the symbol exists in the financial market data, it is considered valid.
2. **Last Traded Date**: We fetch the most recent historical trading data to determine when the symbol was last traded. If there is no historical data or the volume is zero, we consider it not traded.
3. **Volume Check**: We verify the trading volume for the last trading date. If the volume is zero or unavailable, we assume that the stock was not actively traded on that day.
4. **Price Stability**: If the stock’s close price has remained unchanged over several days, it is likely that no trades occurred during those days. This suggests inactivity in the market.
5. **Link to Yahoo Finance**: Regardless of whether the symbol is valid or traded, we provide a link to Yahoo Finance for further investigation.
""")

# Create file uploader
uploaded_file = st.file_uploader("Upload a text file", type="txt")

def extract_date(content):
    try:
        date_str = content.split(' at ')[1].split(' GMT')[0]
        date_obj = datetime.strptime(date_str, '%a %b %d %Y %H:%M:%S')
        return date_obj.strftime('%Y-%m-%d')
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    date_to_check = extract_date(content)
    start_index = content.find('[')
    json_data = content[start_index:].strip()

    try:
        symbols_data = json.loads(json_data)
        df = pd.DataFrame(symbols_data)
        df['id'] = df['id'].astype(str)

        company_names = []
        asset_types = []
        last_traded_dates = []
        last_volumes = []
        last_closes = []
        yahoo_links = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        total_symbols = len(df)
        for idx, symbol in enumerate(df['symbol']):
            progress = (idx + 1) / total_symbols
            progress_bar.progress(progress)
            status_text.text(f"Validating symbol {idx + 1} of {total_symbols}: {symbol}")

            # Call the business logic to validate the symbol
            company_name, asset_type, last_traded_date, last_volume, last_close, _ = check_symbol_exists(symbol)

            yahoo_link = f'<a href="https://finance.yahoo.com/quote/{symbol}" target="_blank">Yahoo Finance</a>'
            yahoo_links.append(yahoo_link)

            company_names.append(company_name if company_name else "N/A")
            asset_types.append(asset_type if asset_type else "N/A")
            last_traded_dates.append(last_traded_date if last_traded_date else "N/A")
            last_volumes.append(last_volume if last_volume else "N/A")
            last_closes.append(last_close if last_close else "N/A")

        df['Company Name'] = company_names
        df['Asset Type'] = asset_types
        df['Last Traded Date'] = last_traded_dates
        df['Last Volume'] = last_volumes
        df['Last Close'] = last_closes
        df['Yahoo Finance Link'] = yahoo_links

        progress_bar.empty()
        status_text.empty()

        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    except json.JSONDecodeError as e:
        st.error(f"Error parsing the JSON data: {e}")
else:
    st.write("Please upload a valid text file with the symbols data.")
