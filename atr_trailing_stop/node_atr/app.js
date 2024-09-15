const express = require('express');
const alphaVantage = require('alpha-vantage-cli').AlphaVantageAPI;
const { ATR } = require('technicalindicators');
const app = express();
const port = 3000;

// Your Alpha Vantage API Key
const apiKey = 'YOUR_ALPHA_VANTAGE_API_KEY';
const alpha = new alphaVantage(apiKey, 'compact', true);

// Function to calculate ATR using the exponential moving average
function calculateATR(data, period) {
  const highPrices = data.map(item => item.high);
  const lowPrices = data.map(item => item.low);
  const closePrices = data.map(item => item.close);

  return ATR.calculate({ high: highPrices, low: lowPrices, close: closePrices, period });
}

// Function to calculate the trailing stop loss for both long and short positions
function calculateTrailingStop(data, atrValues, multiplier) {
  const atrTrailingStop = [];

  for (let i = 1; i < data.length; i++) {
    const previousStop = atrTrailingStop[i - 1] || data[i].close - atrValues[i] * multiplier;
    if (data[i].close > previousStop) {
      atrTrailingStop.push(Math.max(previousStop, data[i].close - atrValues[i] * multiplier));
    } else if (data[i].close < previousStop) {
      atrTrailingStop.push(Math.min(previousStop, data[i].close + atrValues[i] * multiplier));
    } else {
      atrTrailingStop.push(previousStop);
    }
  }

  return atrTrailingStop;
}

// Route to handle ATR Trailing Stop calculation
app.get('/atr-trailing-stop', async (req, res) => {
    const symbol = req.query.symbol || 'AAPL';
    const period = parseInt(req.query.atrPeriod) || 21;
    const multiplier = parseFloat(req.query.multiplier) || 3.0;
    let startDate = req.query.startDate || '2024-01-01';
    const endDate = req.query.endDate || new Date().toISOString().split('T')[0]; // Today by default

    // Adjust start date to ensure we have enough data points for ATR calculation
    const bufferDays = period + 10; // Additional days for ATR calculation
    const startDateObj = new Date(startDate);
    startDateObj.setDate(startDateObj.getDate() - bufferDays); // Go back by bufferDays
    startDate = startDateObj.toISOString().split('T')[0]; // Format the new start date

    try {
        console.log(`Fetching data for symbol: ${symbol}, Start Date: ${startDate}, End Date: ${endDate}`);

        // Fetch historical data using Alpha Vantage
        const data = await alpha.getDailyData(symbol);

        const formattedData = data.map(item => ({
            date: new Date(item.timestamp),
            high: parseFloat(item.high),
            low: parseFloat(item.low),
            close: parseFloat(item.close),
        }));

        if (formattedData.length < period) {
            return res.status(400).send('Not enough data to calculate ATR.');
        }

        // Filter data to only include the requested date range (after adjusting for buffer)
        const filteredData = formattedData.filter(item => new Date(item.date) >= new Date(req.query.startDate));

        // Calculate ATR
        const atrValues = calculateATR(filteredData, period);

        // Calculate Trailing Stop
        const trailingStopValues = calculateTrailingStop(filteredData, atrValues, multiplier);

        // Prepare response data
        const result = filteredData.map((item, index) => ({
            date: item.date,
            high: item.high,
            low: item.low,
            close: item.close,
            atr: atrValues[index] || null,
            atrTrailingStop: trailingStopValues[index] || null,
        }));

        res.json(result);
    } catch (error) {
        console.error('Error fetching data:', error);
        res.status(500).send('Error fetching data.');
    }
});

// Start server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
