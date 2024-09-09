import streamlit as st
import pandas as pd

class BasketPerformance:
    def __init__(self, symbols, prices_df, shares_df):
        """
        :param symbols: List of stock symbols in the basket
        :param prices_df: DataFrame with historical stock prices (columns: Date, Symbol, Open, Close)
        :param shares_df: DataFrame with the number of shares held for each symbol (columns: Symbol, Shares)
        """
        self.symbols = symbols
        self.prices_df = prices_df
        self.shares_df = shares_df

    def daily_performance(self):
        """
        Calculate the daily performance as the percentage change in total basket value from the previous day.
        """
        self.prices_df['Basket Value'] = self.prices_df[self.symbols].sum(axis=1)
        self.prices_df['Daily Performance'] = self.prices_df['Basket Value'].pct_change() * 100
        return self.prices_df[['Date', 'Daily Performance']]

    def since_inception(self):
        """
        Calculate the since inception performance as the overall percentage change in basket value since inception.
        """
        initial_value = self.prices_df[self.symbols].iloc[0].sum()
        current_value = self.prices_df[self.symbols].iloc[-1].sum()
        since_inception_perf = ((current_value - initial_value) / initial_value) * 100
        return since_inception_perf

    def invested_amount(self):
        """
        Calculate the total invested amount based on the purchase price and number of shares.
        """
        invested_amount = 0
        for symbol in self.symbols:
            purchase_price = self.prices_df[self.prices_df['Date'] == self.prices_df['Date'].min()][symbol].values[0]
            shares = self.shares_df[self.shares_df['Symbol'] == symbol]['Shares'].values[0]
            invested_amount += purchase_price * shares
        return invested_amount

    def market_value(self):
        """
        Calculate the current market value of the basket by summing up the value of each symbol's shares at current prices.
        """
        market_value = 0
        for symbol in self.symbols:
            current_price = self.prices_df[self.prices_df['Date'] == self.prices_df['Date'].max()][symbol].values[0]
            shares = self.shares_df[self.shares_df['Symbol'] == symbol]['Shares'].values[0]
            market_value += current_price * shares
        return market_value

    def returns(self):
        """
        Calculate the returns as the percentage change from the invested amount to the current market value.
        """
        invested_amount = self.invested_amount()
        market_value = self.market_value()
        returns = ((market_value - invested_amount) / invested_amount) * 100
        return returns

# Streamlit app
st.title("Basket Performance Calculator")

# Sidebar for input
st.sidebar.header("Upload your data")

# Upload CSVs
prices_file = st.sidebar.file_uploader("Upload prices CSV", type=["csv"])
shares_file = st.sidebar.file_uploader("Upload shares CSV", type=["csv"])

if prices_file and shares_file:
    prices_df = pd.read_csv(prices_file, parse_dates=['Date'])
    shares_df = pd.read_csv(shares_file)

    symbols = list(prices_df.columns[1:])  # Assuming first column is 'Date'
    st.sidebar.write(f"Symbols detected: {symbols}")

    # Initialize BasketPerformance
    basket_performance = BasketPerformance(symbols, prices_df, shares_df)

    # Sidebar for selecting the performance metrics
    st.sidebar.subheader("Select metrics to calculate")
    calculate_daily_perf = st.sidebar.checkbox("Daily Performance")
    calculate_since_inception = st.sidebar.checkbox("Since Inception")
    calculate_invested_amount = st.sidebar.checkbox("Invested Amount")
    calculate_market_value = st.sidebar.checkbox("Market Value")
    calculate_returns = st.sidebar.checkbox("Returns")

    # Display the selected metrics
    if calculate_daily_perf:
        st.subheader("Daily Performance")
        daily_perf = basket_performance.daily_performance()
        st.dataframe(daily_perf)

    if calculate_since_inception:
        st.subheader("Since Inception Performance")
        since_inception_perf = basket_performance.since_inception()
        st.write(f"Since Inception Performance: {since_inception_perf:.2f}%")

    if calculate_invested_amount:
        st.subheader("Invested Amount")
        invested_amt = basket_performance.invested_amount()
        st.write(f"Invested Amount: ${invested_amt:.2f}")

    if calculate_market_value:
        st.subheader("Market Value")
        market_val = basket_performance.market_value()
        st.write(f"Current Market Value: ${market_val:.2f}")

    if calculate_returns:
        st.subheader("Returns")
        returns = basket_performance.returns()
        st.write(f"Returns: {returns:.2f}%")

else:
    st.info("Please upload both the prices and shares CSV files to proceed.")

# Sample format for prices CSV
st.sidebar.subheader("Sample CSV Format")
st.sidebar.markdown("""
**Prices CSV (with columns Date, Symbol Prices):**
