#!/usr/bin/env python3

import sys
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Import pandas_ta only when needed to avoid initialization issues
# import pandas_ta as ta

class TradingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AMD Stock Trading Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize data
        self.symbol = "AMD"
        self.df = None
        self.position = 0  # 0: no position, 1: long, -1: short
        self.cash = 10000  # Starting with $10,000
        self.shares = 0
        
        # Alpha Vantage API key - you'll need to get your own free key from alphavantage.co
        self.api_key = "YOUR_API_KEY"  # Replace with your actual API key
        
        self.init_ui()
        self.update_data()
        
        # Set up timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(60000)  # Update every minute
        
    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Top section with controls
        controls_layout = QHBoxLayout()
        
        # Position and cash info
        self.position_label = QLabel(f"Position: {'None' if self.position == 0 else 'Long' if self.position == 1 else 'Short'}")
        self.cash_label = QLabel(f"Cash: ${self.cash:.2f}")
        self.shares_label = QLabel(f"Shares: {self.shares}")
        
        controls_layout.addWidget(self.position_label)
        controls_layout.addWidget(self.cash_label)
        controls_layout.addWidget(self.shares_label)
        
        # Trading buttons
        self.buy_button = QPushButton("Buy")
        self.sell_button = QPushButton("Sell")
        self.buy_button.clicked.connect(self.buy)
        self.sell_button.clicked.connect(self.sell)
        
        controls_layout.addWidget(self.buy_button)
        controls_layout.addWidget(self.sell_button)
        
        layout.addLayout(controls_layout)
        
        # Price and indicators section
        info_layout = QHBoxLayout()
        
        self.price_label = QLabel("Current Price: --")
        self.rsi_label = QLabel("RSI: --")
        self.signal_label = QLabel("Signal: --")
        
        info_layout.addWidget(self.price_label)
        info_layout.addWidget(self.rsi_label)
        info_layout.addWidget(self.signal_label)
        
        layout.addLayout(info_layout)
        
        # Create matplotlib figure for price chart
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Create table for recent trades
        self.trade_table = QTableWidget()
        self.trade_table.setColumnCount(4)
        self.trade_table.setHorizontalHeaderLabels(["Time", "Type", "Price", "Shares"])
        layout.addWidget(self.trade_table)
        
    def fetch_stock_data(self):
        """Fetch stock data using Alpha Vantage API"""
        try:
            # Get intraday data (1-minute intervals)
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={self.symbol}&interval=1min&apikey={self.api_key}"
            response = requests.get(url)
            data = response.json()
            
            if "Time Series (1min)" in data:
                # Convert to DataFrame
                df = pd.DataFrame.from_dict(data["Time Series (1min)"], orient="index")
                df.index = pd.to_datetime(df.index)
                df = df.astype(float)
                df.columns = ["Open", "High", "Low", "Close", "Volume"]
                return df
            else:
                QMessageBox.warning(self, "Error", "Failed to fetch data from Alpha Vantage")
                return None
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error fetching data: {str(e)}")
            return None
        
    def calculate_rsi(self, data, periods=14):
        """Calculate RSI manually to avoid pandas_ta initialization issues"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def update_chart(self):
        """Update the price chart"""
        if self.df is not None and len(self.df) > 0:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(self.df.index, self.df['Close'], 'b-')
            ax.set_title(f"{self.symbol} Price Chart")
            ax.set_xlabel("Time")
            ax.set_ylabel("Price ($)")
            self.figure.tight_layout()
            self.canvas.draw()
        
    def update_data(self):
        try:
            # Fetch latest data
            self.df = self.fetch_stock_data()
            
            if self.df is not None and len(self.df) > 0:
                # Update price
                current_price = self.df['Close'].iloc[-1]
                self.price_label.setText(f"Current Price: ${current_price:.2f}")
                
                # Calculate indicators
                # Import pandas_ta only when needed
                import pandas_ta as ta
                self.df['RSI'] = self.calculate_rsi(self.df['Close'])
                rsi = self.df['RSI'].iloc[-1] if not pd.isna(self.df['RSI'].iloc[-1]) else 50
                self.rsi_label.setText(f"RSI: {rsi:.2f}")
                
                # Generate signal
                signal = "NEUTRAL"
                if rsi < 30:
                    signal = "BUY"
                elif rsi > 70:
                    signal = "SELL"
                self.signal_label.setText(f"Signal: {signal}")
                
                # Update chart
                self.update_chart()
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update data: {str(e)}")
    
    def buy(self):
        if self.df is None or len(self.df) == 0:
            QMessageBox.warning(self, "Error", "No data available")
            return
            
        current_price = self.df['Close'].iloc[-1]
        shares_to_buy = 1  # Simplified: buy 1 share at a time
        
        if self.cash >= current_price * shares_to_buy:
            self.cash -= current_price * shares_to_buy
            self.shares += shares_to_buy
            self.position = 1
            
            # Update UI
            self.update_position_info()
            self.add_trade_to_table("BUY", current_price, shares_to_buy)
        else:
            QMessageBox.warning(self, "Error", "Insufficient funds")
    
    def sell(self):
        if self.df is None or len(self.df) == 0:
            QMessageBox.warning(self, "Error", "No data available")
            return
            
        if self.shares <= 0:
            QMessageBox.warning(self, "Error", "No shares to sell")
            return
            
        current_price = self.df['Close'].iloc[-1]
        shares_to_sell = 1  # Simplified: sell 1 share at a time
        
        self.cash += current_price * shares_to_sell
        self.shares -= shares_to_sell
        self.position = 0 if self.shares == 0 else self.position
        
        # Update UI
        self.update_position_info()
        self.add_trade_to_table("SELL", current_price, shares_to_sell)
    
    def update_position_info(self):
        self.position_label.setText(f"Position: {'None' if self.position == 0 else 'Long' if self.position == 1 else 'Short'}")
        self.cash_label.setText(f"Cash: ${self.cash:.2f}")
        self.shares_label.setText(f"Shares: {self.shares}")
    
    def add_trade_to_table(self, trade_type, price, shares):
        row_position = self.trade_table.rowCount()
        self.trade_table.insertRow(row_position)
        
        self.trade_table.setItem(row_position, 0, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
        self.trade_table.setItem(row_position, 1, QTableWidgetItem(trade_type))
        self.trade_table.setItem(row_position, 2, QTableWidgetItem(f"${price:.2f}"))
        self.trade_table.setItem(row_position, 3, QTableWidgetItem(str(shares)))

def main():
    app = QApplication(sys.argv)
    window = TradingApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 