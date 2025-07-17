#!/usr/bin/env python3
"""
Stock Day Trading App - Main Application
Combines screen automation with real-time trading analysis and automated strategies.
"""

import customtkinter as ctk
from tkinter import messagebox, simpledialog, ttk
import pyautogui
import json
import time
import keyboard
import mouse
import threading
import os
import sys
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum, auto
import tkinter as tk
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set appearance mode and default color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# File paths for saving data
COMMANDS_FILE = "commands.json"
WINDOW_STATE_FILE = "window_state.json"
TRADING_CONFIG_FILE = "trading_config.json"
TRADE_LOG_FILE = "trade_log.json"

class CommandType(Enum):
    CLICK = auto()
    TYPE = auto()
    HOTKEY = auto()
    DELAY = auto()

class TradingStrategy(Enum):
    SCALPING = auto()
    SWING = auto()
    MEAN_REVERSION = auto()
    BREAKOUT = auto()
    CUSTOM = auto()

@dataclass
class Command:
    type: CommandType
    x: Optional[int] = None
    y: Optional[int] = None
    offset_x: int = 0
    offset_y: int = 0
    text: Optional[str] = None
    keys: Optional[str] = None
    seconds: Optional[float] = None

@dataclass
class Trade:
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: int
    price: float
    timestamp: datetime
    strategy: str
    status: str = 'PENDING'  # PENDING, EXECUTED, CANCELLED, CLOSED
    pnl: float = 0.0

class StockDayTradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Stock Day Trading App - Automated Trading Platform")
        
        # Load window state if available
        self.load_window_state()
        
        # Store commands, markers, and trading data
        self.commands = []
        self.markers = []
        self.marker_counter = 1
        self.running = False
        self.trading_active = False
        self.current_strategy = None
        self.trades = []
        self.watchlist = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        self.current_symbol = 'AAPL'
        
        # Daily buy tracking
        self.daily_buys = {}  # Track daily purchases by date
        self.open_positions = {}  # Track open positions with buy prices
        
        # Trading configuration
        self.trading_config = {
            'max_position_size': 1000,
            'daily_loss_limit': 500,
            'stop_loss_percent': 5.0,
            'take_profit_percent': 5.0,
            'auto_trading': False,
            'daily_buy_enabled': True,
            'shares_per_day': 1
        }
        
        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(self.main_container)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_automation_tab()
        self.create_trading_tab()
        self.create_charts_tab()
        self.create_settings_tab()
        
        # Create status bar
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.status_bar.pack(fill="x", padx=10, pady=5)
        
        # Screen marker windows
        self.screen_markers = []
        self.dragging_marker = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Load saved data
        self.load_commands()
        self.load_trading_config()
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind emergency stop
        keyboard.add_hotkey('ctrl+shift+x', self.emergency_stop)
        
        # Start market data thread
        self.start_market_data_thread()
        
    def load_window_state(self):
        try:
            if os.path.exists(WINDOW_STATE_FILE):
                with open(WINDOW_STATE_FILE, "r") as f:
                    state = json.load(f)
                    self.geometry(f"{state['width']}x{state['height']}+{state['x']}+{state['y']}")
                    if state.get('zoomed', False):
                        self.state('zoomed')
                    elif state.get('iconic', False):
                        self.state('iconic')
            else:
                self.geometry("1200x800")
                self.minsize(800, 600)
        except Exception as e:
            self.geometry("1200x800")
            self.minsize(800, 600)
            print(f"Error loading window state: {e}")
            
    def save_window_state(self):
        try:
            state = {
                'width': self.winfo_width(),
                'height': self.winfo_height(),
                'x': self.winfo_x(),
                'y': self.winfo_y(),
                'zoomed': self.state() == 'zoomed',
                'iconic': self.state() == 'iconic'
            }
            with open(WINDOW_STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error saving window state: {e}")
            
    def on_closing(self):
        self.save_window_state()
        self.save_commands()
        self.save_trading_config()
        self.destroy()
        
    def create_automation_tab(self):
        """Create the automation tab with command editing capabilities"""
        automation_frame = self.notebook.add("🤖 Automation")
        
        # Create left panel for command list
        left_panel = ctk.CTkFrame(automation_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Command list label
        ctk.CTkLabel(left_panel, text="Automation Commands", font=("Arial", 16, "bold")).pack(pady=5)
        
        # Create scrollable frame for command list
        self.command_list_frame = ctk.CTkScrollableFrame(left_panel)
        self.command_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create right panel for controls
        right_panel = ctk.CTkFrame(automation_frame)
        right_panel.pack(side="right", fill="y", padx=5, pady=5)
        
        # Control buttons
        self.create_automation_buttons(right_panel)
        
    def create_automation_buttons(self, parent):
        """Create automation control buttons"""
        # Add Click Position button
        self.add_click_btn = ctk.CTkButton(
            parent,
            text="🖱️ Add Click Position",
            command=self.add_screen_click,
            fg_color="#4B8BBE",
            hover_color="#306998"
        )
        self.add_click_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Type Text button
        self.add_type_btn = ctk.CTkButton(
            parent,
            text="⌨️ Add Type Text",
            command=self.add_type_command,
            fg_color="#2E8B57",
            hover_color="#1E6B47"
        )
        self.add_type_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Hotkey button
        self.add_hotkey_btn = ctk.CTkButton(
            parent,
            text="🔑 Add Hotkey",
            command=self.add_hotkey_command,
            fg_color="#8B4513",
            hover_color="#6B3513"
        )
        self.add_hotkey_btn.pack(fill="x", padx=5, pady=5)
        
        # Add Delay button
        self.add_delay_btn = ctk.CTkButton(
            parent,
            text="⏱️ Add Delay",
            command=self.add_delay_command,
            fg_color="#4682B4",
            hover_color="#3672A4"
        )
        self.add_delay_btn.pack(fill="x", padx=5, pady=5)
        
        # Separator
        separator = ctk.CTkFrame(parent, height=2, fg_color="gray")
        separator.pack(fill="x", padx=5, pady=10)
        
        # Run button
        self.run_btn = ctk.CTkButton(
            parent,
            text="▶️ Run Automation",
            command=self.run_commands,
            fg_color="#228B22",
            hover_color="#128B12"
        )
        self.run_btn.pack(fill="x", padx=5, pady=5)
        
        # Stop button
        self.stop_btn = ctk.CTkButton(
            parent,
            text="⏹️ Stop",
            command=self.stop_automation,
            fg_color="#DC143C",
            hover_color="#B22222"
        )
        self.stop_btn.pack(fill="x", padx=5, pady=5)
        
        # Separator
        separator2 = ctk.CTkFrame(parent, height=2, fg_color="gray")
        separator2.pack(fill="x", padx=5, pady=10)
        
        # Save/Load buttons
        self.save_btn = ctk.CTkButton(
            parent,
            text="💾 Save Commands",
            command=self.save_commands,
            fg_color="#4169E1",
            hover_color="#3159D1"
        )
        self.save_btn.pack(fill="x", padx=5, pady=5)
        
        self.load_btn = ctk.CTkButton(
            parent,
            text="📂 Load Commands",
            command=self.load_commands,
            fg_color="#9370DB",
            hover_color="#8360CB"
        )
        self.load_btn.pack(fill="x", padx=5, pady=5)
        
    def create_trading_tab(self):
        """Create the trading tab with strategy selection and monitoring"""
        trading_frame = self.notebook.add("📈 Trading")
        
        # Create left panel for strategy and controls
        left_panel = ctk.CTkFrame(trading_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Strategy selection
        strategy_frame = ctk.CTkFrame(left_panel)
        strategy_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(strategy_frame, text="Trading Strategy", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.strategy_var = ctk.StringVar(value="DAILY_BUY")
        strategy_combo = ctk.CTkComboBox(
            strategy_frame,
            values=["DAILY_BUY", "PROFIT_TAKE"],
            variable=self.strategy_var,
            command=self.on_strategy_change
        )
        strategy_combo.pack(fill="x", padx=10, pady=5)
        
        # Symbol selection
        symbol_frame = ctk.CTkFrame(left_panel)
        symbol_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(symbol_frame, text="Trading Symbol", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.symbol_var = ctk.StringVar(value="AAPL")
        symbol_combo = ctk.CTkComboBox(
            symbol_frame,
            values=self.watchlist,
            variable=self.symbol_var,
            command=self.on_symbol_change
        )
        symbol_combo.pack(fill="x", padx=10, pady=5)
        
        # Trading controls
        controls_frame = ctk.CTkFrame(left_panel)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(controls_frame, text="Trading Controls", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Auto trading toggle
        self.auto_trading_var = ctk.BooleanVar(value=False)
        auto_trading_switch = ctk.CTkSwitch(
            controls_frame,
            text="Auto Trading",
            variable=self.auto_trading_var,
            command=self.toggle_auto_trading
        )
        auto_trading_switch.pack(padx=10, pady=5)
        
        # Manual trade buttons
        manual_frame = ctk.CTkFrame(controls_frame)
        manual_frame.pack(fill="x", padx=10, pady=5)
        
        self.buy_btn = ctk.CTkButton(
            manual_frame,
            text="🟢 BUY",
            command=self.manual_buy,
            fg_color="#228B22",
            hover_color="#128B12"
        )
        self.buy_btn.pack(side="left", fill="x", expand=True, padx=2, pady=5)
        
        self.sell_btn = ctk.CTkButton(
            manual_frame,
            text="🔴 SELL",
            command=self.manual_sell,
            fg_color="#DC143C",
            hover_color="#B22222"
        )
        self.sell_btn.pack(side="right", fill="x", expand=True, padx=2, pady=5)
        
        # Create right panel for trade history and P&L
        right_panel = ctk.CTkFrame(trading_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # P&L display
        pnl_frame = ctk.CTkFrame(right_panel)
        pnl_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(pnl_frame, text="Portfolio P&L", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.pnl_label = ctk.CTkLabel(pnl_frame, text="$0.00", font=("Arial", 24, "bold"))
        self.pnl_label.pack(pady=5)
        
        # Open positions
        positions_frame = ctk.CTkFrame(right_panel)
        positions_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(positions_frame, text="Open Positions", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Create treeview for open positions
        self.positions_tree = ttk.Treeview(positions_frame, columns=("Symbol", "Qty", "Buy Price", "Target", "Current", "P&L"), show="headings", height=3)
        self.positions_tree.heading("Symbol", text="Symbol")
        self.positions_tree.heading("Qty", text="Qty")
        self.positions_tree.heading("Buy Price", text="Buy Price")
        self.positions_tree.heading("Target", text="Target (5%)")
        self.positions_tree.heading("Current", text="Current")
        self.positions_tree.heading("P&L", text="P&L")
        
        # Configure column widths
        self.positions_tree.column("Symbol", width=80)
        self.positions_tree.column("Qty", width=50)
        self.positions_tree.column("Buy Price", width=80)
        self.positions_tree.column("Target", width=80)
        self.positions_tree.column("Current", width=80)
        self.positions_tree.column("P&L", width=80)
        
        self.positions_tree.pack(fill="x", padx=5, pady=5)
        
        # Daily buy status
        daily_status_frame = ctk.CTkFrame(right_panel)
        daily_status_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(daily_status_frame, text="Daily Buy Status", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.daily_status_label = ctk.CTkLabel(daily_status_frame, text="Ready to buy today", font=("Arial", 12))
        self.daily_status_label.pack(pady=5)
        
        # Trade history
        history_frame = ctk.CTkFrame(right_panel)
        history_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(history_frame, text="Trade History", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Create treeview for trade history
        self.trade_tree = ttk.Treeview(history_frame, columns=("Time", "Symbol", "Side", "Qty", "Price", "P&L"), show="headings")
        self.trade_tree.heading("Time", text="Time")
        self.trade_tree.heading("Symbol", text="Symbol")
        self.trade_tree.heading("Side", text="Side")
        self.trade_tree.heading("Qty", text="Qty")
        self.trade_tree.heading("Price", text="Price")
        self.trade_tree.heading("P&L", text="P&L")
        
        # Configure column widths
        self.trade_tree.column("Time", width=100)
        self.trade_tree.column("Symbol", width=80)
        self.trade_tree.column("Side", width=60)
        self.trade_tree.column("Qty", width=60)
        self.trade_tree.column("Price", width=80)
        self.trade_tree.column("P&L", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.trade_tree.yview)
        self.trade_tree.configure(yscrollcommand=scrollbar.set)
        
        self.trade_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
    def create_charts_tab(self):
        """Create the charts tab with real-time price charts"""
        charts_frame = self.notebook.add("📊 Charts")
        
        # Chart controls
        controls_frame = ctk.CTkFrame(charts_frame)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Timeframe selection
        timeframe_frame = ctk.CTkFrame(controls_frame)
        timeframe_frame.pack(side="left", padx=5, pady=5)
        
        ctk.CTkLabel(timeframe_frame, text="Timeframe:").pack(side="left", padx=5)
        
        self.timeframe_var = ctk.StringVar(value="1m")
        timeframe_combo = ctk.CTkComboBox(
            timeframe_frame,
            values=["1m", "5m", "15m", "1h", "1d"],
            variable=self.timeframe_var,
            command=self.update_chart
        )
        timeframe_combo.pack(side="left", padx=5)
        
        # Chart canvas
        self.chart_frame = ctk.CTkFrame(charts_frame)
        self.chart_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialize chart
        self.create_chart()
        
    def create_settings_tab(self):
        """Create the settings tab for configuration"""
        settings_frame = self.notebook.add("⚙️ Settings")
        
        # Trading configuration
        config_frame = ctk.CTkFrame(settings_frame)
        config_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(config_frame, text="Trading Configuration", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Max position size
        pos_size_frame = ctk.CTkFrame(config_frame)
        pos_size_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(pos_size_frame, text="Max Position Size ($):").pack(side="left", padx=5)
        self.max_pos_size_var = ctk.StringVar(value=str(self.trading_config['max_position_size']))
        max_pos_entry = ctk.CTkEntry(pos_size_frame, textvariable=self.max_pos_size_var)
        max_pos_entry.pack(side="right", padx=5)
        
        # Daily loss limit
        loss_limit_frame = ctk.CTkFrame(config_frame)
        loss_limit_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(loss_limit_frame, text="Daily Loss Limit ($):").pack(side="left", padx=5)
        self.daily_loss_var = ctk.StringVar(value=str(self.trading_config['daily_loss_limit']))
        daily_loss_entry = ctk.CTkEntry(loss_limit_frame, textvariable=self.daily_loss_var)
        daily_loss_entry.pack(side="right", padx=5)
        
        # Stop loss percentage
        stop_loss_frame = ctk.CTkFrame(config_frame)
        stop_loss_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(stop_loss_frame, text="Stop Loss (%):").pack(side="left", padx=5)
        self.stop_loss_var = ctk.StringVar(value=str(self.trading_config['stop_loss_percent']))
        stop_loss_entry = ctk.CTkEntry(stop_loss_frame, textvariable=self.stop_loss_var)
        stop_loss_entry.pack(side="right", padx=5)
        
        # Take profit percentage
        take_profit_frame = ctk.CTkFrame(config_frame)
        take_profit_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(take_profit_frame, text="Take Profit (%):").pack(side="left", padx=5)
        self.take_profit_var = ctk.StringVar(value=str(self.trading_config['take_profit_percent']))
        take_profit_entry = ctk.CTkEntry(take_profit_frame, textvariable=self.take_profit_var)
        take_profit_entry.pack(side="right", padx=5)
        
        # Daily buy settings
        daily_buy_frame = ctk.CTkFrame(config_frame)
        daily_buy_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(daily_buy_frame, text="Daily Buy Strategy", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Daily buy toggle
        self.daily_buy_var = ctk.BooleanVar(value=self.trading_config.get('daily_buy_enabled', True))
        daily_buy_switch = ctk.CTkSwitch(
            daily_buy_frame,
            text="Enable Daily Buy",
            variable=self.daily_buy_var
        )
        daily_buy_switch.pack(padx=10, pady=5)
        
        # Shares per day
        shares_frame = ctk.CTkFrame(daily_buy_frame)
        shares_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(shares_frame, text="Shares per day:").pack(side="left", padx=5)
        self.shares_per_day_var = ctk.StringVar(value=str(self.trading_config.get('shares_per_day', 1)))
        shares_entry = ctk.CTkEntry(shares_frame, textvariable=self.shares_per_day_var)
        shares_entry.pack(side="right", padx=5)
        
        # Save settings button
        save_settings_btn = ctk.CTkButton(
            config_frame,
            text="💾 Save Settings",
            command=self.save_trading_config
        )
        save_settings_btn.pack(pady=10)
        
        # Emergency stop info
        emergency_frame = ctk.CTkFrame(settings_frame)
        emergency_frame.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkLabel(emergency_frame, text="🚨 Emergency Stop: Ctrl+Shift+X", 
                    font=("Arial", 14, "bold"), text_color="#DC143C").pack(pady=10)
        
    def add_screen_click(self):
        """Add a screen click command"""
        # Get current mouse position
        x, y = pyautogui.position()
        
        # Create command
        command = Command(type=CommandType.CLICK, x=x, y=y)
        self.commands.append(command)
        
        # Create visual marker
        self.create_screen_marker(x, y, len(self.commands) - 1)
        
        # Update command list
        self.update_command_list()
        
        self.status_bar.configure(text=f"Added click command at ({x}, {y})")
        
    def create_screen_marker(self, x, y, index):
        """Create a visual marker on screen"""
        marker = tk.Toplevel()
        marker.overrideredirect(True)
        marker.attributes('-topmost', True)
        marker.geometry(f"30x30+{x-15}+{y-15}")
        marker.configure(bg='red')
        
        # Add label
        label = tk.Label(marker, text=str(index + 1), bg='red', fg='white', font=('Arial', 12, 'bold'))
        label.pack(expand=True)
        
        # Bind events for dragging
        label.bind('<Button-1>', lambda e, m=marker: self.start_drag(e, m))
        label.bind('<B1-Motion>', self.drag)
        label.bind('<ButtonRelease-1>', self.stop_drag)
        
        # Add close button
        close_btn = tk.Button(marker, text='X', bg='red', fg='white', 
                            command=lambda m=marker: self.close_marker(m))
        close_btn.pack(side='top', anchor='ne')
        
        self.screen_markers.append(marker)
        
    def start_drag(self, event, marker):
        """Start dragging a marker"""
        self.dragging_marker = marker
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
    def drag(self, event):
        """Drag a marker"""
        if self.dragging_marker:
            x = self.dragging_marker.winfo_x() + event.x - self.drag_start_x
            y = self.dragging_marker.winfo_y() + event.y - self.drag_start_y
            self.dragging_marker.geometry(f"+{x}+{y}")
            
    def stop_drag(self, event):
        """Stop dragging a marker"""
        if self.dragging_marker:
            # Update command coordinates
            marker_index = self.screen_markers.index(self.dragging_marker)
            if marker_index < len(self.commands):
                self.commands[marker_index].x = self.dragging_marker.winfo_x() + 15
                self.commands[marker_index].y = self.dragging_marker.winfo_y() + 15
            self.dragging_marker = None
            
    def close_marker(self, marker):
        """Close a marker"""
        marker_index = self.screen_markers.index(marker)
        marker.destroy()
        self.screen_markers.pop(marker_index)
        
        # Remove corresponding command
        if marker_index < len(self.commands):
            self.commands.pop(marker_index)
            self.update_command_list()
            
    def add_type_command(self):
        """Add a type text command"""
        text = simpledialog.askstring("Add Type Command", "Enter text to type:")
        if text:
            command = Command(type=CommandType.TYPE, text=text)
            self.commands.append(command)
            self.update_command_list()
            self.status_bar.configure(text=f"Added type command: {text}")
            
    def add_hotkey_command(self):
        """Add a hotkey command"""
        keys = simpledialog.askstring("Add Hotkey Command", "Enter hotkey (e.g., ctrl+c):")
        if keys:
            command = Command(type=CommandType.HOTKEY, keys=keys)
            self.commands.append(command)
            self.update_command_list()
            self.status_bar.configure(text=f"Added hotkey command: {keys}")
            
    def add_delay_command(self):
        """Add a delay command"""
        seconds = simpledialog.askfloat("Add Delay Command", "Enter delay in seconds:")
        if seconds:
            command = Command(type=CommandType.DELAY, seconds=seconds)
            self.commands.append(command)
            self.update_command_list()
            self.status_bar.configure(text=f"Added delay command: {seconds}s")
            
    def update_command_list(self):
        """Update the command list display"""
        # Clear existing widgets
        for widget in self.command_list_frame.winfo_children():
            widget.destroy()
            
        # Add commands
        for i, command in enumerate(self.commands):
            command_frame = ctk.CTkFrame(self.command_list_frame)
            command_frame.pack(fill="x", padx=5, pady=2)
            
            # Command info
            if command.type == CommandType.CLICK:
                info_text = f"Click at ({command.x}, {command.y})"
            elif command.type == CommandType.TYPE:
                info_text = f"Type: {command.text}"
            elif command.type == CommandType.HOTKEY:
                info_text = f"Hotkey: {command.keys}"
            elif command.type == CommandType.DELAY:
                info_text = f"Delay: {command.seconds}s"
                
            ctk.CTkLabel(command_frame, text=info_text).pack(side="left", padx=5)
            
            # Control buttons
            ctk.CTkButton(command_frame, text="✏️", width=30, 
                         command=lambda idx=i: self.edit_command(idx)).pack(side="right", padx=2)
            ctk.CTkButton(command_frame, text="🗑️", width=30,
                         command=lambda idx=i: self.remove_command_at_index(idx)).pack(side="right", padx=2)
            
    def remove_command_at_index(self, index):
        """Remove command at specific index"""
        if 0 <= index < len(self.commands):
            self.commands.pop(index)
            self.update_command_list()
            
    def edit_command(self, index):
        """Edit a command"""
        if 0 <= index < len(self.commands):
            command = self.commands[index]
            # Implementation for editing commands
            pass
            
    def run_commands(self):
        """Run the automation commands"""
        if not self.commands:
            messagebox.showwarning("Warning", "No commands to run!")
            return
            
        if self.running:
            messagebox.showwarning("Warning", "Automation already running!")
            return
            
        self.running = True
        self.status_bar.configure(text="Running automation...")
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_commands_thread)
        thread.daemon = True
        thread.start()
        
    def run_commands_thread(self):
        """Run commands in separate thread"""
        try:
            for i, command in enumerate(self.commands):
                if not self.running:
                    break
                    
                if command.type == CommandType.CLICK:
                    pyautogui.click(command.x + command.offset_x, command.y + command.offset_y)
                elif command.type == CommandType.TYPE:
                    pyautogui.typewrite(command.text)
                elif command.type == CommandType.HOTKEY:
                    pyautogui.hotkey(*command.keys.split('+'))
                elif command.type == CommandType.DELAY:
                    time.sleep(command.seconds)
                    
                # Small delay between commands
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error running commands: {e}")
            self.status_bar.configure(text=f"Error: {e}")
        finally:
            self.running = False
            self.status_bar.configure(text="Automation completed")
            
    def stop_automation(self):
        """Stop automation"""
        self.running = False
        self.status_bar.configure(text="Automation stopped")
        
    def emergency_stop(self):
        """Emergency stop all automation and trading"""
        self.running = False
        self.trading_active = False
        self.auto_trading_var.set(False)
        self.status_bar.configure(text="🚨 EMERGENCY STOP ACTIVATED")
        messagebox.showwarning("Emergency Stop", "All automation and trading has been stopped!")
        
    def save_commands(self):
        """Save commands to file"""
        try:
            commands_data = []
            for command in self.commands:
                cmd_data = {
                    'type': command.type.name,
                    'x': command.x,
                    'y': command.y,
                    'offset_x': command.offset_x,
                    'offset_y': command.offset_y,
                    'text': command.text,
                    'keys': command.keys,
                    'seconds': command.seconds
                }
                commands_data.append(cmd_data)
                
            with open(COMMANDS_FILE, 'w') as f:
                json.dump(commands_data, f, indent=2)
                
            self.status_bar.configure(text="Commands saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save commands: {e}")
            
    def load_commands(self):
        """Load commands from file"""
        try:
            if os.path.exists(COMMANDS_FILE):
                with open(COMMANDS_FILE, 'r') as f:
                    commands_data = json.load(f)
                    
                self.commands = []
                for cmd_data in commands_data:
                    command = Command(
                        type=CommandType[cmd_data['type']],
                        x=cmd_data.get('x'),
                        y=cmd_data.get('y'),
                        offset_x=cmd_data.get('offset_x', 0),
                        offset_y=cmd_data.get('offset_y', 0),
                        text=cmd_data.get('text'),
                        keys=cmd_data.get('keys'),
                        seconds=cmd_data.get('seconds')
                    )
                    self.commands.append(command)
                    
                self.update_command_list()
                self.status_bar.configure(text="Commands loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load commands: {e}")
            
    def save_trading_config(self):
        """Save trading configuration"""
        try:
            self.trading_config.update({
                'max_position_size': float(self.max_pos_size_var.get()),
                'daily_loss_limit': float(self.daily_loss_var.get()),
                'stop_loss_percent': float(self.stop_loss_var.get()),
                'take_profit_percent': float(self.take_profit_var.get()),
                'auto_trading': self.auto_trading_var.get(),
                'daily_buy_enabled': self.daily_buy_var.get(),
                'shares_per_day': int(self.shares_per_day_var.get())
            })
            
            with open(TRADING_CONFIG_FILE, 'w') as f:
                json.dump(self.trading_config, f, indent=2)
                
            self.status_bar.configure(text="Trading configuration saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            
    def load_trading_config(self):
        """Load trading configuration"""
        try:
            if os.path.exists(TRADING_CONFIG_FILE):
                with open(TRADING_CONFIG_FILE, 'r') as f:
                    self.trading_config = json.load(f)
                    
                # Update UI
                self.max_pos_size_var.set(str(self.trading_config.get('max_position_size', 1000)))
                self.daily_loss_var.set(str(self.trading_config.get('daily_loss_limit', 500)))
                self.stop_loss_var.set(str(self.trading_config.get('stop_loss_percent', 2.0)))
                self.take_profit_var.set(str(self.trading_config.get('take_profit_percent', 5.0)))
                self.auto_trading_var.set(self.trading_config.get('auto_trading', False))
        except Exception as e:
            print(f"Failed to load trading configuration: {e}")
            
    def on_strategy_change(self, value):
        """Handle strategy change"""
        self.current_strategy = value
        self.status_bar.configure(text=f"Strategy changed to: {value}")
        
    def on_symbol_change(self, value):
        """Handle symbol change"""
        self.current_symbol = value
        self.update_chart()
        self.status_bar.configure(text=f"Symbol changed to: {value}")
        
    def toggle_auto_trading(self):
        """Toggle auto trading"""
        if self.auto_trading_var.get():
            self.start_auto_trading()
        else:
            self.stop_auto_trading()
            
    def start_auto_trading(self):
        """Start automated trading"""
        self.trading_active = True
        self.status_bar.configure(text="Auto trading started")
        
        # Start trading thread
        thread = threading.Thread(target=self.auto_trading_thread)
        thread.daemon = True
        thread.start()
        
    def stop_auto_trading(self):
        """Stop automated trading"""
        self.trading_active = False
        self.status_bar.configure(text="Auto trading stopped")
        
    def auto_trading_thread(self):
        """Automated trading thread"""
        while self.trading_active:
            try:
                # Get current market data
                ticker = yf.Ticker(self.current_symbol)
                current_price = ticker.info.get('regularMarketPrice', 0)
                
                if current_price > 0:
                    # Implement trading strategy
                    self.execute_strategy(current_price)
                    
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error in auto trading: {e}")
                time.sleep(10)
                
    def execute_strategy(self, current_price):
        """Execute trading strategy"""
        strategy = self.current_strategy
        current_date = datetime.now().date()
        
        if strategy == "DAILY_BUY":
            # Check if we already bought today
            if current_date not in self.daily_buys:
                self.daily_buys[current_date] = []
            
            # Check if we already bought this symbol today
            if self.current_symbol not in [buy['symbol'] for buy in self.daily_buys[current_date]]:
                # Buy 1 share
                self.place_trade("BUY", 1, current_price)
                # Track the purchase
                self.daily_buys[current_date].append({
                    'symbol': self.current_symbol,
                    'quantity': 1,
                    'price': current_price,
                    'timestamp': datetime.now()
                })
                # Track open position
                self.open_positions[self.current_symbol] = {
                    'buy_price': current_price,
                    'quantity': 1,
                    'buy_date': current_date
                }
                self.status_bar.configure(text=f"Daily buy executed: 1 share of {self.current_symbol} @ ${current_price:.2f}")
        
        elif strategy == "PROFIT_TAKE":
            # Check if we have an open position for this symbol
            if self.current_symbol in self.open_positions:
                buy_price = self.open_positions[self.current_symbol]['buy_price']
                target_price = buy_price * 1.05  # 5% profit target
                
                if current_price >= target_price:
                    # Sell the position
                    quantity = self.open_positions[self.current_symbol]['quantity']
                    self.place_trade("SELL", quantity, current_price)
                    # Remove from open positions
                    del self.open_positions[self.current_symbol]
                    self.status_bar.configure(text=f"Profit target reached: Sold {quantity} share(s) of {self.current_symbol} @ ${current_price:.2f}")
                else:
                    self.status_bar.configure(text=f"Waiting for 5% profit: {current_price:.2f} < {target_price:.2f}")
            
    def manual_buy(self):
        """Manual buy order"""
        quantity = simpledialog.askinteger("Buy Order", "Enter quantity:")
        if quantity:
            ticker = yf.Ticker(self.current_symbol)
            current_price = ticker.info.get('regularMarketPrice', 0)
            if current_price > 0:
                self.place_trade("BUY", quantity, current_price)
                
    def manual_sell(self):
        """Manual sell order"""
        quantity = simpledialog.askinteger("Sell Order", "Enter quantity:")
        if quantity:
            ticker = yf.Ticker(self.current_symbol)
            current_price = ticker.info.get('regularMarketPrice', 0)
            if current_price > 0:
                self.place_trade("SELL", quantity, current_price)
                
    def place_trade(self, side, quantity, price):
        """Place a trade"""
        trade = Trade(
            symbol=self.current_symbol,
            side=side,
            quantity=quantity,
            price=price,
            timestamp=datetime.now(),
            strategy=self.current_strategy or "MANUAL"
        )
        
        self.trades.append(trade)
        self.update_trade_history()
        self.status_bar.configure(text=f"{side} order placed: {quantity} {self.current_symbol} @ ${price:.2f}")
        
    def update_trade_history(self):
        """Update trade history display"""
        # Clear existing items
        for item in self.trade_tree.get_children():
            self.trade_tree.delete(item)
            
        # Add trades
        for trade in reversed(self.trades[-50:]):  # Show last 50 trades
            self.trade_tree.insert("", "end", values=(
                trade.timestamp.strftime("%H:%M:%S"),
                trade.symbol,
                trade.side,
                trade.quantity,
                f"${trade.price:.2f}",
                f"${trade.pnl:.2f}"
            ))
    
    def update_open_positions(self):
        """Update open positions display"""
        # Clear existing items
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
            
        # Get current prices for open positions
        for symbol, position in self.open_positions.items():
            try:
                ticker = yf.Ticker(symbol)
                current_price = ticker.info.get('regularMarketPrice', position['buy_price'])
                
                buy_price = position['buy_price']
                quantity = position['quantity']
                target_price = buy_price * 1.05
                current_pnl = (current_price - buy_price) * quantity
                
                self.positions_tree.insert("", "end", values=(
                    symbol,
                    quantity,
                    f"${buy_price:.2f}",
                    f"${target_price:.2f}",
                    f"${current_price:.2f}",
                    f"${current_pnl:.2f}"
                ))
            except Exception as e:
                print(f"Error updating position for {symbol}: {e}")
    
    def update_daily_status(self):
        """Update daily buy status"""
        current_date = datetime.now().date()
        
        if current_date in self.daily_buys:
            bought_symbols = [buy['symbol'] for buy in self.daily_buys[current_date]]
            if self.current_symbol in bought_symbols:
                self.daily_status_label.configure(text=f"Already bought {self.current_symbol} today")
            else:
                self.daily_status_label.configure(text=f"Ready to buy {self.current_symbol} today")
        else:
            self.daily_status_label.configure(text=f"Ready to buy {self.current_symbol} today")
            
    def create_chart(self):
        """Create price chart"""
        try:
            # Get historical data
            ticker = yf.Ticker(self.current_symbol)
            data = ticker.history(period="1d", interval="1m")
            
            if not data.empty:
                # Create matplotlib figure
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(data.index, data['Close'])
                ax.set_title(f"{self.current_symbol} Price Chart")
                ax.set_xlabel("Time")
                ax.set_ylabel("Price ($)")
                ax.grid(True)
                
                # Create canvas
                canvas = FigureCanvasTkAgg(fig, self.chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
                
        except Exception as e:
            print(f"Error creating chart: {e}")
            
    def update_chart(self, timeframe=None):
        """Update the chart"""
        # Implementation for updating chart
        pass
        
    def start_market_data_thread(self):
        """Start market data update thread"""
        thread = threading.Thread(target=self.market_data_thread)
        thread.daemon = True
        thread.start()
        
    def market_data_thread(self):
        """Market data update thread"""
        while True:
            try:
                # Update P&L
                total_pnl = sum(trade.pnl for trade in self.trades)
                self.pnl_label.configure(text=f"${total_pnl:.2f}")
                
                # Update open positions
                self.update_open_positions()
                
                # Update daily status
                self.update_daily_status()
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Error in market data thread: {e}")
                time.sleep(10)

def main():
    """Main function"""
    app = StockDayTradingApp()
    app.mainloop()

if __name__ == "__main__":
    main()