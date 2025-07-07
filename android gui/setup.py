#!/usr/bin/env python3
"""
Setup script for Remote Command Executor
Automates the installation and configuration process
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def create_config_file():
    """Create initial configuration file"""
    config_file = "config.json"
    sample_config = "sample_config.json"
    
    if os.path.exists(config_file):
        print(f"✅ {config_file} already exists")
        return True
    
    if os.path.exists(sample_config):
        shutil.copy(sample_config, config_file)
        print(f"✅ Created {config_file} from sample")
        return True
    
    # Create basic config
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
    
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print(f"✅ Created {config_file}")
    return True

def check_credentials():
    """Check if credentials file exists"""
    credentials_file = "credentials.json"
    if os.path.exists(credentials_file):
        print(f"✅ {credentials_file} found")
        return True
    else:
        print(f"⚠️  {credentials_file} not found")
        print("   Please download your Google Sheets API credentials")
        print("   and save them as 'credentials.json' in this folder")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing imports...")
    required_modules = [
        'tkinter',
        'requests',
        'threading',
        'subprocess',
        'json',
        'os',
        'sys',
        'logging',
        'datetime'
    ]
    
    optional_modules = [
        ('gspread', 'Google Sheets support'),
        ('google.oauth2.service_account', 'Google authentication'),
        ('msal', 'Microsoft Graph support')
    ]
    
    # Test required modules
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - Required module missing")
            return False
    
    # Test optional modules
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError:
            print(f"⚠️  {module} - {description} (optional)")
    
    return True

def create_desktop_launcher():
    """Create desktop launcher for Linux systems"""
    if sys.platform.startswith('linux'):
        desktop_dir = Path.home() / "Desktop"
        if desktop_dir.exists():
            launcher_content = f"""[Desktop Entry]
Name=Remote Command Executor
Comment=Execute commands remotely via Google Sheets
Exec=python3 {os.path.abspath('remote_command_gui.py')}
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;System;
"""
            launcher_file = desktop_dir / "remote_command_executor.desktop"
            with open(launcher_file, 'w') as f:
                f.write(launcher_content)
            
            # Make executable
            os.chmod(launcher_file, 0o755)
            print(f"✅ Created desktop launcher: {launcher_file}")
            return True
    
    return False

def run_basic_test():
    """Run basic functionality test"""
    print("\n🧪 Running basic test...")
    try:
        # Test GUI creation
        import tkinter as tk
        from tkinter import ttk
        
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Test basic widgets
        frame = ttk.Frame(root)
        label = ttk.Label(frame, text="Test")
        button = ttk.Button(frame, text="Test")
        
        root.destroy()
        print("✅ GUI components test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Remote Command Executor Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed during package installation")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Setup failed during import testing")
        sys.exit(1)
    
    # Create configuration
    create_config_file()
    
    # Check credentials
    has_credentials = check_credentials()
    
    # Create desktop launcher
    create_desktop_launcher()
    
    # Run basic test
    run_basic_test()
    
    # Final instructions
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Set up Google Sheets API credentials if you haven't already")
    print("2. Run: python remote_command_gui.py")
    print("3. Configure your Google Sheets settings in the Configuration tab")
    print("4. Start monitoring for commands")
    
    if not has_credentials:
        print("\n⚠️  Don't forget to add your credentials.json file!")
    
    print("\nFor detailed instructions, see README.md")

if __name__ == "__main__":
    main()