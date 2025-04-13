#!/bin/bash

# Get the script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to script directory
cd "$DIR"

echo "Starting Desktop Shortcut Creator..."

# Ensure system dependencies are installed
echo "Checking and installing required dependencies..."
sudo apt-get update -q
sudo apt-get install -y python3-pyqt6 python3-magic python3-pil python3-pil.imagetk libmagic1

# Make sure scripts are executable
chmod +x shortcut_creator_pyqt.py

# Ask the user to check if a window appeared
echo "Launching Desktop Shortcut Creator..."
echo "If no window appears, press Ctrl+C and try running 'python3 shortcut_creator_pyqt.py' directly."

# Run the GUI application using system Python and packages
python3 shortcut_creator_pyqt.py

echo "Thank you for using Desktop Shortcut Creator!"
