# Stock Day Trading App

A comprehensive automated stock day trading application that combines advanced screen automation with real-time market data analysis and automated trading strategies.

## Features

### 🎯 Core Automation
- **Screen Automation**: Click on specific screen coordinates for trading platform interactions
- **Hotkey Support**: Execute keyboard shortcuts and combinations
- **Text Input**: Automatically type text into trading platforms
- **Delay Management**: Precise timing control for automation sequences
- **Visual Markers**: On-screen markers for easy position identification

### 📊 Trading Analysis
- **Real-time Data**: Live stock price feeds using yfinance
- **Technical Indicators**: RSI, MACD, Moving Averages, Bollinger Bands
- **Pattern Recognition**: Support for common chart patterns
- **Risk Management**: Stop-loss and take-profit automation
- **Portfolio Tracking**: Real-time P&L monitoring

### 🤖 Automated Strategies
- **Scalping Bot**: Quick in-and-out trades based on momentum
- **Swing Trading**: Medium-term position holding
- **Mean Reversion**: Trading based on price deviations
- **Breakout Trading**: Trading breakouts from support/resistance
- **Custom Strategies**: User-defined trading algorithms

### 🖥️ User Interface
- **Modern GUI**: Clean, dark-themed interface using CustomTkinter
- **Real-time Charts**: Interactive price charts with indicators
- **Strategy Builder**: Visual strategy creation interface
- **Backtesting**: Historical strategy performance testing
- **Logging**: Comprehensive trade and system logs

## Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Quick Start

1. **Launch the app**: Run `python main.py`
2. **Configure trading platform**: Set up screen coordinates for your trading platform
3. **Select strategy**: Choose from built-in strategies or create custom ones
4. **Set parameters**: Configure risk management and trading parameters
5. **Start automation**: Begin automated trading with real-time monitoring

## Safety Features

- **Emergency Stop**: Hotkey to immediately stop all automation
- **Risk Limits**: Maximum position sizes and daily loss limits
- **Manual Override**: Ability to take manual control at any time
- **Trade Confirmation**: Visual confirmation before executing trades
- **Error Handling**: Robust error handling and recovery

## Disclaimer

⚠️ **Trading involves substantial risk of loss and is not suitable for all investors. This software is for educational purposes only. Always test thoroughly on paper trading before using real money.**

## License

This project is for educational purposes. Use at your own risk.

## Support

For issues and feature requests, please check the documentation or create an issue in the repository.