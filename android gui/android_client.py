#!/usr/bin/env python3
"""
Android Client Script for Pydroid
Sends commands to desktop via Google Sheets
"""

import requests
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import os

class AndroidRemoteClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Command Sender")
        self.root.geometry("400x600")
        
        # Load configuration
        self.config = self.load_config()
        self.google_client = None
        
        self.setup_gui()
        self.setup_google_sheets()
    
    def load_config(self):
        """Load configuration"""
        return {
            "google_sheets": {
                "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE",
                "worksheet_name": "Commands",
                "credentials_file": "credentials.json"
            },
            "device_id": "android_device_1"
        }
    
    def setup_gui(self):
        """Setup the GUI"""
        # Title
        title_label = ttk.Label(self.root, text="Remote Command Sender", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(self.root, text="Configuration")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(config_frame, text="Spreadsheet ID:").pack(anchor="w")
        self.spreadsheet_id_entry = ttk.Entry(config_frame, width=40)
        self.spreadsheet_id_entry.pack(fill="x", padx=5, pady=2)
        self.spreadsheet_id_entry.insert(0, self.config["google_sheets"]["spreadsheet_id"])
        
        ttk.Label(config_frame, text="Device ID:").pack(anchor="w")
        self.device_id_entry = ttk.Entry(config_frame, width=30)
        self.device_id_entry.pack(fill="x", padx=5, pady=2)
        self.device_id_entry.insert(0, self.config["device_id"])
        
        # Connect button
        self.connect_button = ttk.Button(config_frame, text="Connect to Sheets", 
                                        command=self.connect_to_sheets)
        self.connect_button.pack(pady=5)
        
        # Status
        self.status_label = ttk.Label(config_frame, text="Status: Not connected")
        self.status_label.pack(pady=2)
        
        # Command input frame
        cmd_frame = ttk.LabelFrame(self.root, text="Send Command")
        cmd_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(cmd_frame, text="Command:").pack(anchor="w")
        self.command_entry = ttk.Entry(cmd_frame, width=40)
        self.command_entry.pack(fill="x", padx=5, pady=2)
        
        # Quick command buttons
        quick_frame = ttk.Frame(cmd_frame)
        quick_frame.pack(fill="x", padx=5, pady=5)
        
        quick_commands = [
            ("System Info", "uname -a"),
            ("Disk Usage", "df -h"),
            ("Memory", "free -h"),
            ("Processes", "ps aux"),
            ("Network", "netstat -tuln"),
            ("Uptime", "uptime")
        ]
        
        for i, (name, cmd) in enumerate(quick_commands):
            if i % 2 == 0:
                row_frame = ttk.Frame(quick_frame)
                row_frame.pack(fill="x", pady=2)
            
            btn = ttk.Button(row_frame, text=name, width=15,
                           command=lambda c=cmd: self.set_command(c))
            btn.pack(side="left", padx=2)
        
        # Send button
        send_frame = ttk.Frame(cmd_frame)
        send_frame.pack(fill="x", padx=5, pady=5)
        
        self.send_button = ttk.Button(send_frame, text="Send Command", 
                                     command=self.send_command, state="disabled")
        self.send_button.pack(side="left", padx=5)
        
        self.clear_button = ttk.Button(send_frame, text="Clear", 
                                      command=self.clear_command)
        self.clear_button.pack(side="left", padx=5)
        
        # Response frame
        response_frame = ttk.LabelFrame(self.root, text="Command History")
        response_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.response_text = scrolledtext.ScrolledText(response_frame, height=15)
        self.response_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Refresh button
        refresh_frame = ttk.Frame(response_frame)
        refresh_frame.pack(fill="x", padx=5, pady=5)
        
        self.refresh_button = ttk.Button(refresh_frame, text="Refresh Results", 
                                        command=self.refresh_results, state="disabled")
        self.refresh_button.pack(side="left", padx=5)
        
        self.auto_refresh_var = tk.BooleanVar()
        self.auto_refresh_check = ttk.Checkbutton(refresh_frame, text="Auto-refresh", 
                                                 variable=self.auto_refresh_var,
                                                 command=self.toggle_auto_refresh)
        self.auto_refresh_check.pack(side="left", padx=5)
        
        # Bind Enter key to send command
        self.command_entry.bind('<Return>', lambda e: self.send_command())
    
    def setup_google_sheets(self):
        """Setup Google Sheets connection"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.config["google_sheets"]["credentials_file"]):
                self.log_message("Credentials file not found. Please place credentials.json in the same folder.")
                return
            
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(
                self.config["google_sheets"]["credentials_file"], 
                scopes=scope
            )
            self.google_client = gspread.authorize(creds)
            self.log_message("Google Sheets client initialized")
            
        except Exception as e:
            self.log_message(f"Error initializing Google Sheets: {e}")
    
    def connect_to_sheets(self):
        """Connect to Google Sheets"""
        try:
            self.config["google_sheets"]["spreadsheet_id"] = self.spreadsheet_id_entry.get()
            self.config["device_id"] = self.device_id_entry.get()
            
            if not self.google_client:
                self.setup_google_sheets()
            
            if not self.google_client:
                messagebox.showerror("Error", "Google Sheets client not available")
                return
            
            # Test connection
            sheet = self.google_client.open_by_key(self.config["google_sheets"]["spreadsheet_id"])
            worksheet = sheet.worksheet(self.config["google_sheets"]["worksheet_name"])
            
            self.status_label.config(text="Status: Connected")
            self.send_button.config(state="normal")
            self.refresh_button.config(state="normal")
            
            self.log_message("Successfully connected to Google Sheets")
            
            # Setup headers if needed
            self.setup_worksheet_headers(worksheet)
            
        except Exception as e:
            self.status_label.config(text="Status: Connection failed")
            messagebox.showerror("Error", f"Failed to connect: {e}")
    
    def setup_worksheet_headers(self, worksheet):
        """Setup worksheet headers if they don't exist"""
        try:
            # Check if headers exist
            headers = worksheet.row_values(1)
            if not headers or len(headers) < 5:
                # Add headers
                worksheet.update('A1:E1', [['Timestamp', 'Command', 'Status', 'Output', 'Device']])
                self.log_message("Headers added to worksheet")
        except Exception as e:
            self.log_message(f"Error setting up headers: {e}")
    
    def set_command(self, command):
        """Set command in the entry field"""
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, command)
    
    def clear_command(self):
        """Clear command entry"""
        self.command_entry.delete(0, tk.END)
    
    def send_command(self):
        """Send command to spreadsheet"""
        command = self.command_entry.get().strip()
        if not command:
            messagebox.showwarning("Warning", "Please enter a command")
            return
        
        if not self.google_client:
            messagebox.showerror("Error", "Not connected to Google Sheets")
            return
        
        try:
            sheet = self.google_client.open_by_key(self.config["google_sheets"]["spreadsheet_id"])
            worksheet = sheet.worksheet(self.config["google_sheets"]["worksheet_name"])
            
            # Add command to spreadsheet
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [timestamp, command, "pending", "", self.config["device_id"]]
            
            worksheet.append_row(row_data)
            
            self.log_message(f"Command sent: {command}")
            self.command_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")
    
    def refresh_results(self):
        """Refresh command results from spreadsheet"""
        if not self.google_client:
            return
        
        try:
            sheet = self.google_client.open_by_key(self.config["google_sheets"]["spreadsheet_id"])
            worksheet = sheet.worksheet(self.config["google_sheets"]["worksheet_name"])
            
            # Get all records
            records = worksheet.get_all_records()
            
            # Filter records for this device
            device_records = [r for r in records if r.get('Device') == self.config["device_id"]]
            
            # Display recent commands
            self.response_text.delete(1.0, tk.END)
            for record in device_records[-10:]:  # Show last 10 commands
                timestamp = record.get('Timestamp', '')
                command = record.get('Command', '')
                status = record.get('Status', '')
                output = record.get('Output', '')
                
                self.response_text.insert(tk.END, f"[{timestamp}] {command}\n")
                self.response_text.insert(tk.END, f"Status: {status}\n")
                if output:
                    self.response_text.insert(tk.END, f"Output: {output}\n")
                self.response_text.insert(tk.END, "-" * 50 + "\n")
            
            self.response_text.see(tk.END)
            
        except Exception as e:
            self.log_message(f"Error refreshing results: {e}")
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh"""
        if self.auto_refresh_var.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Start auto-refresh timer"""
        self.auto_refresh_timer = threading.Timer(10.0, self.auto_refresh_callback)
        self.auto_refresh_timer.start()
    
    def stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if hasattr(self, 'auto_refresh_timer'):
            self.auto_refresh_timer.cancel()
    
    def auto_refresh_callback(self):
        """Auto-refresh callback"""
        if self.auto_refresh_var.get():
            self.refresh_results()
            self.start_auto_refresh()
    
    def log_message(self, message):
        """Log message to response text"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.response_text.insert(tk.END, log_entry)
        self.response_text.see(tk.END)

def main():
    """Main function for Android client"""
    root = tk.Tk()
    app = AndroidRemoteClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()