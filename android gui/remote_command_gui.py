#!/usr/bin/env python3
"""
Remote Command GUI - Desktop Application
Receives commands from Android via Google Sheets/Excel Online
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import os
import sys
import json
import logging
from datetime import datetime
import requests
from typing import Dict, List, Optional

# Google Sheets API imports
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# Excel Online API imports
try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('remote_commands.log'),
        logging.StreamHandler()
    ]
)

class RemoteCommandGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Command Executor")
        self.root.geometry("800x600")
        
        # Configuration
        self.config = self.load_config()
        self.running = False
        self.command_history = []
        
        # Initialize spreadsheet clients
        self.google_client = None
        self.excel_client = None
        
        self.setup_gui()
        self.setup_spreadsheet_clients()
        
    def load_config(self) -> Dict:
        """Load configuration from file"""
        config_file = "config.json"
        default_config = {
            "google_sheets": {
                "spreadsheet_id": "",
                "worksheet_name": "Commands",
                "credentials_file": "credentials.json"
            },
            "excel_online": {
                "client_id": "",
                "tenant_id": "",
                "workbook_id": "",
                "worksheet_name": "Commands"
            },
            "polling_interval": 5,
            "allowed_commands": [
                "ls", "pwd", "whoami", "date", "uptime",
                "df -h", "free -h", "ps aux", "top -n 1",
                "systemctl status", "netstat -tuln"
            ],
            "max_history": 100
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            # Create default config
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def save_config(self):
        """Save current configuration"""
        with open("config.json", 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Main")
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        self.refresh_button = ttk.Button(control_frame, text="Refresh Now", command=self.check_for_commands)
        self.refresh_button.pack(side="left", padx=5)
        
        # Status
        self.status_label = ttk.Label(control_frame, text="Status: Stopped")
        self.status_label.pack(side="right", padx=5)
        
        # Log display
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=5)
        
        ttk.Label(log_frame, text="Command Log:").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20)
        self.log_text.pack(fill="both", expand=True)
        
        # Configuration tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        self.setup_config_tab(config_frame)
        
        # Help tab
        help_frame = ttk.Frame(notebook)
        notebook.add(help_frame, text="Help")
        self.setup_help_tab(help_frame)
    
    def setup_config_tab(self, parent):
        """Setup configuration tab"""
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Google Sheets configuration
        gs_frame = ttk.LabelFrame(scrollable_frame, text="Google Sheets Configuration")
        gs_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(gs_frame, text="Spreadsheet ID:").pack(anchor="w")
        self.gs_spreadsheet_id = ttk.Entry(gs_frame, width=60)
        self.gs_spreadsheet_id.pack(fill="x", padx=5, pady=2)
        self.gs_spreadsheet_id.insert(0, self.config["google_sheets"]["spreadsheet_id"])
        
        ttk.Label(gs_frame, text="Worksheet Name:").pack(anchor="w")
        self.gs_worksheet_name = ttk.Entry(gs_frame, width=30)
        self.gs_worksheet_name.pack(fill="x", padx=5, pady=2)
        self.gs_worksheet_name.insert(0, self.config["google_sheets"]["worksheet_name"])
        
        # Excel Online configuration
        excel_frame = ttk.LabelFrame(scrollable_frame, text="Excel Online Configuration")
        excel_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(excel_frame, text="Client ID:").pack(anchor="w")
        self.excel_client_id = ttk.Entry(excel_frame, width=60)
        self.excel_client_id.pack(fill="x", padx=5, pady=2)
        self.excel_client_id.insert(0, self.config["excel_online"]["client_id"])
        
        ttk.Label(excel_frame, text="Tenant ID:").pack(anchor="w")
        self.excel_tenant_id = ttk.Entry(excel_frame, width=60)
        self.excel_tenant_id.pack(fill="x", padx=5, pady=2)
        self.excel_tenant_id.insert(0, self.config["excel_online"]["tenant_id"])
        
        ttk.Label(excel_frame, text="Workbook ID:").pack(anchor="w")
        self.excel_workbook_id = ttk.Entry(excel_frame, width=60)
        self.excel_workbook_id.pack(fill="x", padx=5, pady=2)
        self.excel_workbook_id.insert(0, self.config["excel_online"]["workbook_id"])
        
        # General settings
        general_frame = ttk.LabelFrame(scrollable_frame, text="General Settings")
        general_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(general_frame, text="Polling Interval (seconds):").pack(anchor="w")
        self.polling_interval = ttk.Entry(general_frame, width=10)
        self.polling_interval.pack(anchor="w", padx=5, pady=2)
        self.polling_interval.insert(0, str(self.config["polling_interval"]))
        
        # Allowed commands
        ttk.Label(general_frame, text="Allowed Commands (one per line):").pack(anchor="w")
        self.allowed_commands = scrolledtext.ScrolledText(general_frame, height=8)
        self.allowed_commands.pack(fill="x", padx=5, pady=2)
        self.allowed_commands.insert("1.0", "\n".join(self.config["allowed_commands"]))
        
        # Save button
        save_frame = ttk.Frame(scrollable_frame)
        save_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(save_frame, text="Save Configuration", command=self.save_configuration).pack(side="left", padx=5)
        ttk.Button(save_frame, text="Test Google Sheets", command=self.test_google_sheets).pack(side="left", padx=5)
        ttk.Button(save_frame, text="Test Excel Online", command=self.test_excel_online).pack(side="left", padx=5)
    
    def setup_help_tab(self, parent):
        """Setup help tab with instructions"""
        help_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD)
        help_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_content = """
REMOTE COMMAND EXECUTOR - SETUP INSTRUCTIONS

=== OVERVIEW ===
This application allows you to remotely execute commands on your desktop computer from your Android device using Pydroid. Commands are sent via Google Sheets or Excel Online.

=== REQUIREMENTS ===
1. Python 3.6+
2. Required Python packages (install with: pip install -r requirements.txt)
3. Google Sheets API credentials OR Microsoft Graph API credentials
4. Pydroid app on Android device

=== GOOGLE SHEETS SETUP ===
1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Create service account credentials
5. Download credentials JSON file and rename to 'credentials.json'
6. Place credentials.json in the same folder as this program
7. Create a Google Sheet with columns: Timestamp, Command, Status, Output, Device
8. Share the sheet with the service account email
9. Copy the spreadsheet ID from the URL and paste in configuration

=== EXCEL ONLINE SETUP ===
1. Go to Azure Portal (https://portal.azure.com/)
2. Register a new application in Azure Active Directory
3. Note down Application (client) ID and Directory (tenant) ID
4. Add Microsoft Graph API permissions: Files.ReadWrite
5. Create a workbook in Excel Online
6. Get the workbook ID from the URL
7. Enter the IDs in the configuration tab

=== ANDROID SETUP (Pydroid) ===
1. Install Pydroid 3 from Google Play Store
2. Install required packages: pip install requests gspread google-auth
3. Copy the android_client.py script to your Pydroid
4. Edit the script with your spreadsheet details
5. Run the script to send commands

=== USAGE ===
1. Configure either Google Sheets or Excel Online (or both)
2. Click "Start Monitoring" to begin checking for commands
3. From Android, run the client script to send commands
4. Commands will be executed and results sent back to spreadsheet

=== SECURITY NOTES ===
- Only whitelisted commands can be executed
- All commands are logged with timestamps
- Use strong authentication for your cloud accounts
- Consider using VPN for additional security

=== TROUBLESHOOTING ===
- Check the log file 'remote_commands.log' for errors
- Ensure credentials files are in the correct location
- Verify spreadsheet sharing permissions
- Test API connections using the test buttons

=== SPREADSHEET FORMAT ===
Columns should be:
A: Timestamp
B: Command
C: Status (pending/executed/error)
D: Output
E: Device ID
        """
        
        help_text.insert("1.0", help_content)
        help_text.config(state="disabled")
    
    def save_configuration(self):
        """Save configuration from GUI"""
        self.config["google_sheets"]["spreadsheet_id"] = self.gs_spreadsheet_id.get()
        self.config["google_sheets"]["worksheet_name"] = self.gs_worksheet_name.get()
        self.config["excel_online"]["client_id"] = self.excel_client_id.get()
        self.config["excel_online"]["tenant_id"] = self.excel_tenant_id.get()
        self.config["excel_online"]["workbook_id"] = self.excel_workbook_id.get()
        
        try:
            self.config["polling_interval"] = int(self.polling_interval.get())
        except ValueError:
            self.config["polling_interval"] = 5
        
        self.config["allowed_commands"] = [
            cmd.strip() for cmd in self.allowed_commands.get("1.0", "end").split("\n") 
            if cmd.strip()
        ]
        
        self.save_config()
        messagebox.showinfo("Success", "Configuration saved successfully!")
        self.setup_spreadsheet_clients()
    
    def setup_spreadsheet_clients(self):
        """Initialize spreadsheet clients"""
        # Google Sheets
        if GSPREAD_AVAILABLE and self.config["google_sheets"]["spreadsheet_id"]:
            try:
                credentials_file = self.config["google_sheets"]["credentials_file"]
                if os.path.exists(credentials_file):
                    scope = ['https://spreadsheets.google.com/feeds',
                            'https://www.googleapis.com/auth/drive']
                    creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
                    self.google_client = gspread.authorize(creds)
                    self.log_message("Google Sheets client initialized")
                else:
                    self.log_message("Google Sheets credentials file not found")
            except Exception as e:
                self.log_message(f"Error initializing Google Sheets: {e}")
        
        # Excel Online - placeholder for now
        if MSAL_AVAILABLE and self.config["excel_online"]["client_id"]:
            self.log_message("Excel Online setup - implementation pending")
    
    def test_google_sheets(self):
        """Test Google Sheets connection"""
        if not self.google_client:
            messagebox.showerror("Error", "Google Sheets client not initialized")
            return
        
        try:
            sheet = self.google_client.open_by_key(self.config["google_sheets"]["spreadsheet_id"])
            worksheet = sheet.worksheet(self.config["google_sheets"]["worksheet_name"])
            messagebox.showinfo("Success", "Google Sheets connection successful!")
        except Exception as e:
            messagebox.showerror("Error", f"Google Sheets test failed: {e}")
    
    def test_excel_online(self):
        """Test Excel Online connection"""
        messagebox.showinfo("Info", "Excel Online integration coming soon!")
    
    def log_message(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        
        logging.info(message)
    
    def start_monitoring(self):
        """Start monitoring for commands"""
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="Status: Running")
        
        self.log_message("Started monitoring for commands")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_commands, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring for commands"""
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Status: Stopped")
        
        self.log_message("Stopped monitoring for commands")
    
    def monitor_commands(self):
        """Monitor spreadsheet for new commands"""
        while self.running:
            try:
                self.check_for_commands()
                time.sleep(self.config["polling_interval"])
            except Exception as e:
                self.log_message(f"Error in monitoring: {e}")
                time.sleep(5)
    
    def check_for_commands(self):
        """Check spreadsheet for new commands"""
        if self.google_client:
            self.check_google_sheets()
        # Add Excel Online check here when implemented
    
    def check_google_sheets(self):
        """Check Google Sheets for new commands"""
        try:
            sheet = self.google_client.open_by_key(self.config["google_sheets"]["spreadsheet_id"])
            worksheet = sheet.worksheet(self.config["google_sheets"]["worksheet_name"])
            
            # Get all records
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):  # Start from row 2
                if record.get('Status') == 'pending':
                    command = record.get('Command', '').strip()
                    if command:
                        self.execute_command(command, worksheet, i)
            
        except Exception as e:
            self.log_message(f"Error checking Google Sheets: {e}")
    
    def execute_command(self, command: str, worksheet, row: int):
        """Execute a command and update the spreadsheet"""
        self.log_message(f"Executing command: {command}")
        
        # Check if command is allowed
        if not self.is_command_allowed(command):
            error_msg = f"Command not allowed: {command}"
            self.log_message(error_msg)
            self.update_spreadsheet_row(worksheet, row, "error", error_msg)
            return
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout if result.stdout else result.stderr
            status = "executed" if result.returncode == 0 else "error"
            
            self.log_message(f"Command result: {output[:100]}...")
            self.update_spreadsheet_row(worksheet, row, status, output)
            
        except subprocess.TimeoutExpired:
            error_msg = "Command timed out"
            self.log_message(error_msg)
            self.update_spreadsheet_row(worksheet, row, "error", error_msg)
        except Exception as e:
            error_msg = f"Command execution error: {e}"
            self.log_message(error_msg)
            self.update_spreadsheet_row(worksheet, row, "error", error_msg)
    
    def is_command_allowed(self, command: str) -> bool:
        """Check if command is in allowed list"""
        return any(command.startswith(allowed) for allowed in self.config["allowed_commands"])
    
    def update_spreadsheet_row(self, worksheet, row: int, status: str, output: str):
        """Update spreadsheet row with command result"""
        try:
            worksheet.update_cell(row, 3, status)  # Status column
            worksheet.update_cell(row, 4, output[:1000])  # Output column (truncated)
            worksheet.update_cell(row, 5, os.uname().nodename)  # Device column
        except Exception as e:
            self.log_message(f"Error updating spreadsheet: {e}")

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = RemoteCommandGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()