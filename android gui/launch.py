#!/usr/bin/env python3
"""
Simple launcher for Remote Command Executor
Provides a menu to choose between desktop app and Android client
"""

import os
import sys
import subprocess
from pathlib import Path

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("          REMOTE COMMAND EXECUTOR")
    print("=" * 60)
    print()

def check_file_exists(filename):
    """Check if a file exists"""
    return os.path.exists(filename)

def launch_desktop_app():
    """Launch the desktop application"""
    if not check_file_exists("remote_command_gui.py"):
        print("❌ Desktop application not found!")
        return False
    
    print("🖥️  Starting desktop application...")
    try:
        subprocess.run([sys.executable, "remote_command_gui.py"])
        return True
    except Exception as e:
        print(f"❌ Failed to start desktop app: {e}")
        return False

def launch_android_client():
    """Launch the Android client"""
    if not check_file_exists("android_client.py"):
        print("❌ Android client not found!")
        return False
    
    print("📱 Starting Android client...")
    try:
        subprocess.run([sys.executable, "android_client.py"])
        return True
    except Exception as e:
        print(f"❌ Failed to start Android client: {e}")
        return False

def run_setup():
    """Run the setup script"""
    if not check_file_exists("setup.py"):
        print("❌ Setup script not found!")
        return False
    
    print("⚙️  Running setup...")
    try:
        subprocess.run([sys.executable, "setup.py"])
        return True
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def show_status():
    """Show application status"""
    print("📊 Application Status:")
    print("-" * 30)
    
    files = [
        ("remote_command_gui.py", "Desktop Application"),
        ("android_client.py", "Android Client"),
        ("requirements.txt", "Dependencies"),
        ("config.json", "Configuration"),
        ("credentials.json", "Google API Credentials"),
        ("README.md", "Documentation")
    ]
    
    for filename, description in files:
        status = "✅" if check_file_exists(filename) else "❌"
        print(f"{status} {description}: {filename}")
    
    print()

def main():
    """Main launcher function"""
    while True:
        clear_screen()
        print_banner()
        
        print("Choose an option:")
        print("1. 🖥️  Launch Desktop Application")
        print("2. 📱 Launch Android Client")
        print("3. ⚙️  Run Setup")
        print("4. 📊 Show Status")
        print("5. 📖 View README")
        print("6. 🚪 Exit")
        print()
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            launch_desktop_app()
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            launch_android_client()
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            run_setup()
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            show_status()
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            if check_file_exists("README.md"):
                try:
                    with open("README.md", 'r') as f:
                        print(f.read())
                except Exception as e:
                    print(f"❌ Error reading README: {e}")
            else:
                print("❌ README.md not found!")
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()