#!/usr/bin/env python3
"""
Stock Day Trading App Launcher
Simple script to launch the main application.
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'customtkinter',
        'pyautogui',
        'yfinance',
        'pandas',
        'numpy',
        'matplotlib',
        'ta',
        'keyboard',
        'mouse',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstalling missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install packages. Please install them manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def main():
    """Main launcher function"""
    print("🚀 Stock Day Trading App Launcher")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies. Exiting.")
        sys.exit(1)
    
    # Check if main.py exists
    if not os.path.exists('main.py'):
        print("❌ main.py not found. Please ensure you're in the correct directory.")
        sys.exit(1)
    
    # Launch the application
    print("✅ Starting Stock Day Trading App...")
    print("⚠️  Remember: This is for educational purposes only!")
    print("🚨 Emergency Stop: Ctrl+Shift+X")
    print("-" * 40)
    
    try:
        import main
        main.main()
    except KeyboardInterrupt:
        print("\n👋 Application closed by user.")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()