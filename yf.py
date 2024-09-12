import yfinance as yf

trs = yf.Tickers('goog, aapl, msft')

print(trs.news())


# goog = yf.Ticker('NVDA')
# for k in goog.info:
#     print(k, goog.info[k])

# print(goog.info)

# hist = goog.history(period="max")
# print(hist)
# print(goog.dividends)
# print(type(goog.splits))
# print(goog.splits)

# for new in goog.news:
#     print(new)
# print(goog.news)
# print(goog.shares)