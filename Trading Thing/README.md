# Python Stock Trading Analysis

This is a basic stock trading analysis tool that demonstrates how to:
- Fetch stock data using yfinance
- Calculate technical indicators (RSI, MACD, Bollinger Bands)
- Generate trading signals based on technical analysis

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
.\venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python "Run Me"
```

The script will:
1. Fetch Apple (AAPL) stock data for the last year
2. Calculate technical indicators
3. Generate trading signals based on:
   - RSI (Relative Strength Index)
   - Bollinger Bands
4. Display the last 5 days of trading signals and basic statistics

## Customization

To analyze different stocks, modify the `symbol` variable in the `main()` function of `Run Me`.

## Note

This is a basic example for educational purposes. Real trading requires:
- More sophisticated strategies
- Risk management
- Proper backtesting
- Real-time data handling
- Broker integration
- Compliance with financial regulations 