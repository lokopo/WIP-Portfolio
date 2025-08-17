#!/usr/bin/env python3

import sys
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox)
from PySide6.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
import yfinance as yf
from typing import Optional
from click_points import click_index, scripts_dir_exists, script_exists, set_scripts_dir
import csv
import json

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
        
        # Persistence
        self.config_path = os.path.join(os.path.dirname(__file__), "trading_config.json")
        self.trades_csv = os.path.join(os.path.dirname(__file__), "trades.csv")
        
        # Auto-trading config
        self.auto_trading_enabled = True
        self.buy_interval_minutes = 15
        self.sell_profit_multiplier = 1.05  # 5% target
        self.open_lot_prices = []  # Track per-share buy prices
        self.market_hours_only = True
        self.last_buy_dt: Optional[datetime] = None
        
        # Click points configuration
        scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Pyautogui Suped Up", "scripts"))
        set_scripts_dir(scripts_dir)
        self.click_actions = {
            "buy": {"script": "buy", "index": 0, "enabled": True},
            "sell": {"script": "sell", "index": 0, "enabled": True}
        }
        
        # Load persisted config if present
        self.load_config()
        
        self.init_ui()
        self.update_data()
        
        # Set up timer for periodic data updates (every minute)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(60000)
        
        # Set up timer for auto-buy every 15 minutes
        self.buy_timer = QTimer()
        self.buy_timer.timeout.connect(self.auto_buy_share)
        self.buy_timer.start(self.buy_interval_minutes * 60 * 1000)

    def _write_csv_trade(self, trade_type: str, price: float, shares: int) -> None:
        header_needed = not os.path.isfile(self.trades_csv)
        try:
            with open(self.trades_csv, "a", newline="") as f:
                writer = csv.writer(f)
                if header_needed:
                    writer.writerow(["timestamp", "symbol", "type", "price", "shares"]) 
                writer.writerow([datetime.now().isoformat(), self.symbol, trade_type, f"{price:.2f}", shares])
        except Exception:
            pass

    def save_config(self) -> None:
        data = {
            "symbol": self.symbol,
            "auto_trading_enabled": self.auto_trading_enabled,
            "buy_interval_minutes": self.buy_interval_minutes,
            "sell_profit_multiplier": self.sell_profit_multiplier,
            "market_hours_only": self.market_hours_only,
            "cash": self.cash
        }
        try:
            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def load_config(self) -> None:
        try:
            if os.path.isfile(self.config_path):
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                self.symbol = data.get("symbol", self.symbol)
                self.auto_trading_enabled = bool(data.get("auto_trading_enabled", self.auto_trading_enabled))
                self.buy_interval_minutes = int(data.get("buy_interval_minutes", self.buy_interval_minutes))
                self.sell_profit_multiplier = float(data.get("sell_profit_multiplier", self.sell_profit_multiplier))
                self.market_hours_only = bool(data.get("market_hours_only", self.market_hours_only))
                self.cash = float(data.get("cash", self.cash))
        except Exception:
            pass

    def is_market_open(self, now: Optional[datetime] = None) -> bool:
        # Simple US market hours gate: 9:30-16:00 ET, Mon-Fri; assumes local time is ET
        # Adjust as needed for your timezone/broker
        now = now or datetime.now()
        if now.weekday() >= 5:
            return False
        minutes = now.hour * 60 + now.minute
        return 9 * 60 + 30 <= minutes <= 16 * 60

    def next_buy_in_text(self) -> str:
        if not self.last_buy_dt:
            return "ready"
        delta = datetime.now() - self.last_buy_dt
        remain = max(0, self.buy_interval_minutes * 60 - int(delta.total_seconds()))
        m, s = divmod(remain, 60)
        return f"{m:02d}:{s:02d}"
    
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
        
        # Symbol controls
        symbol_layout = QHBoxLayout()
        self.symbol_input = QLineEdit(self.symbol)
        self.symbol_input.setPlaceholderText("Symbol (e.g., AMD)")
        apply_symbol_btn = QPushButton("Set Symbol")
        apply_symbol_btn.clicked.connect(self._apply_symbol)
        symbol_layout.addWidget(QLabel("Symbol:"))
        symbol_layout.addWidget(self.symbol_input)
        symbol_layout.addWidget(apply_symbol_btn)
        layout.addLayout(symbol_layout)
        
        # Strategy settings
        settings_layout = QHBoxLayout()
        self.auto_checkbox = QCheckBox("Auto Trading")
        self.auto_checkbox.setChecked(self.auto_trading_enabled)
        self.auto_checkbox.stateChanged.connect(self._toggle_auto)
        
        self.market_hours_checkbox = QCheckBox("Market Hours Only")
        self.market_hours_checkbox.setChecked(self.market_hours_only)
        self.market_hours_checkbox.stateChanged.connect(self._toggle_market_hours)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 240)
        self.interval_spin.setValue(self.buy_interval_minutes)
        self.interval_spin.setSuffix(" min buy")
        self.interval_spin.valueChanged.connect(self._change_interval)
        
        self.take_profit_spin = QDoubleSpinBox()
        self.take_profit_spin.setRange(1.0, 100.0)
        self.take_profit_spin.setValue((self.sell_profit_multiplier - 1.0) * 100.0)
        self.take_profit_spin.setSuffix(" % TP")
        self.take_profit_spin.valueChanged.connect(self._change_tp)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_config)
        
        settings_layout.addWidget(self.auto_checkbox)
        settings_layout.addWidget(self.market_hours_checkbox)
        settings_layout.addWidget(QLabel("Interval:"))
        settings_layout.addWidget(self.interval_spin)
        settings_layout.addWidget(QLabel("Profit Target:"))
        settings_layout.addWidget(self.take_profit_spin)
        settings_layout.addWidget(save_btn)
        layout.addLayout(settings_layout)
        
        # Trading buttons
        self.buy_button = QPushButton("Buy")
        self.sell_button = QPushButton("Sell")
        self.buy_button.clicked.connect(lambda: self.buy())
        self.sell_button.clicked.connect(lambda: self.sell())
        
        controls_layout.addWidget(self.buy_button)
        controls_layout.addWidget(self.sell_button)
        
        # Click-point quick tests
        test_buy_btn = QPushButton("Test Buy Click")
        test_buy_btn.clicked.connect(lambda: self._maybe_click_action("buy"))
        test_sell_btn = QPushButton("Test Sell Click")
        test_sell_btn.clicked.connect(lambda: self._maybe_click_action("sell"))
        controls_layout.addWidget(test_buy_btn)
        controls_layout.addWidget(test_sell_btn)
        
        layout.addLayout(controls_layout)
        
        # Status row
        status_layout = QHBoxLayout()
        self.next_buy_label = QLabel("Next buy: ready")
        self.market_status_label = QLabel("Market: unknown")
        self.avg_cost_label = QLabel("Avg cost: --")
        self.unreal_pnl_label = QLabel("Unrealized P&L: --")
        status_layout.addWidget(self.next_buy_label)
        status_layout.addWidget(self.market_status_label)
        status_layout.addWidget(self.avg_cost_label)
        status_layout.addWidget(self.unreal_pnl_label)
        layout.addLayout(status_layout)
        
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

    def _apply_symbol(self):
        val = self.symbol_input.text().strip().upper()
        if not val:
            return
        self.symbol = val
        self.save_config()
        self.update_data()

    def _toggle_auto(self):
        self.auto_trading_enabled = self.auto_checkbox.isChecked()
        self.save_config()

    def _toggle_market_hours(self):
        self.market_hours_only = self.market_hours_checkbox.isChecked()
        self.save_config()

    def _change_interval(self):
        self.buy_interval_minutes = int(self.interval_spin.value())
        # restart timer with new interval
        self.buy_timer.stop()
        self.buy_timer.start(self.buy_interval_minutes * 60 * 1000)
        self.save_config()

    def _change_tp(self):
        self.sell_profit_multiplier = 1.0 + float(self.take_profit_spin.value()) / 100.0
        self.save_config()
    
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
        
    def get_current_price(self) -> Optional[float]:
        """Return the current market price using yfinance as primary source."""
        try:
            ticker = yf.Ticker(self.symbol)
            price = ticker.info.get('regularMarketPrice')
            if price is None and self.df is not None and len(self.df) > 0:
                return float(self.df['Close'].iloc[-1])
            return float(price) if price is not None else None
        except Exception:
            try:
                if self.df is not None and len(self.df) > 0:
                    return float(self.df['Close'].iloc[-1])
            except Exception:
                pass
            return None
    
    def calculate_rsi(self, data, periods=14):
        """Calculate RSI manually"""
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
            
            # Update market status and next buy label regardless of df
            is_open = self.is_market_open() if self.market_hours_only else True
            self.market_status_label.setText(f"Market: {'open' if is_open else 'closed'}")
            self.next_buy_label.setText(f"Next buy: {self.next_buy_in_text()}")
            
            if self.df is not None and len(self.df) > 0:
                # Update price
                current_price = self.df['Close'].iloc[-1]
                self.price_label.setText(f"Current Price: ${current_price:.2f}")
                
                # Calculate indicators
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
                
                # Update avg cost and unrealized P&L
                if self.shares > 0 and self.open_lot_prices:
                    avg_cost = sum(self.open_lot_prices) / len(self.open_lot_prices)
                    unreal = (current_price - avg_cost) * self.shares
                    self.avg_cost_label.setText(f"Avg cost: ${avg_cost:.2f}")
                    self.unreal_pnl_label.setText(f"Unrealized P&L: ${unreal:.2f}")
                else:
                    self.avg_cost_label.setText("Avg cost: --")
                    self.unreal_pnl_label.setText("Unrealized P&L: --")
                
                # Check auto-sell condition each update
                self.auto_sell_check()
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update data: {str(e)}")
    
    def auto_buy_share(self):
        if not self.auto_trading_enabled:
            return
        if self.market_hours_only and not self.is_market_open():
            return
        current_price = self.get_current_price()
        if current_price is None:
            return
        self.buy(current_price=current_price)
    
    def _maybe_click_action(self, action_key: str) -> None:
        cfg = self.click_actions.get(action_key)
        if not cfg:
            return
        if not cfg.get("enabled", False):
            return
        script = cfg.get("script")
        index = int(cfg.get("index", 0))
        if not scripts_dir_exists() or not script_exists(script):
            return
        try:
            click_index(script, index)
        except Exception:
            pass
    
    def buy(self, current_price: Optional[float] = None):
        if self.df is None or len(self.df) == 0:
            # Allow buy if we have a current_price supplied
            if current_price is None:
                QMessageBox.warning(self, "Error", "No data available")
                return
        
        if current_price is None:
            current_price = float(self.df['Close'].iloc[-1])
        
        shares_to_buy = 1  # Buy 1 share at a time
        
        if self.cash >= current_price * shares_to_buy:
            self.cash -= current_price * shares_to_buy
            self.shares += shares_to_buy
            self.position = 1
            
            # Track lot
            self.open_lot_prices.append(current_price)
            
            # Update UI
            self.update_position_info()
            self.add_trade_to_table("BUY", current_price, shares_to_buy)
            self._write_csv_trade("BUY", current_price, shares_to_buy)
            self.last_buy_dt = datetime.now()
            
            # Execute external click point for buy
            self._maybe_click_action("buy")
        else:
            QMessageBox.warning(self, "Error", "Insufficient funds")
    
    def sell(self, current_price: Optional[float] = None):
        if self.df is None or len(self.df) == 0:
            if current_price is None:
                QMessageBox.warning(self, "Error", "No data available")
                return
        
        if self.shares <= 0:
            QMessageBox.warning(self, "Error", "No shares to sell")
            return
        
        if current_price is None:
            current_price = float(self.df['Close'].iloc[-1])
        
        shares_to_sell = 1  # Sell 1 share at a time
        
        self.cash += current_price * shares_to_sell
        self.shares -= shares_to_sell
        self.position = 0 if self.shares == 0 else self.position
        
        # Remove one lot price if tracked
        if self.open_lot_prices:
            self.open_lot_prices.pop(0)
        
        # Update UI
        self.update_position_info()
        self.add_trade_to_table("SELL", current_price, shares_to_sell)
        self._write_csv_trade("SELL", current_price, shares_to_sell)
        
        # Execute external click point for sell
        self._maybe_click_action("sell")
    
    def auto_sell_check(self) -> None:
        if not self.auto_trading_enabled or not self.open_lot_prices:
            return
        current_price = self.get_current_price()
        if current_price is None:
            return
        # Sell one share if any lot has reached 5% profit
        for buy_price in list(self.open_lot_prices):
            target_price = float(buy_price) * self.sell_profit_multiplier
            if current_price >= target_price and self.shares > 0:
                self.sell(current_price=current_price)
                break  # Sell one per check
    
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