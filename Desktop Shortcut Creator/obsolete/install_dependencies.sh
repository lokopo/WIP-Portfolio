#!/bin/bash

echo "Installing system dependencies for Desktop Shortcut Creator..."

# Check if we're running as root
if [ "$EUID" -ne 0 ]; then
  echo "This script requires sudo privileges to install system packages."
  echo "Please enter your password when prompted."
fi

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip libmagic1 python3-tk

# Get the script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to script directory
cd "$DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Try alternative packages if main ones fail
if ! python3 -c "import magic" &>/dev/null; then
    echo "Installing alternative python-magic package..."
    pip install python-magic-bin
fi

if ! python3 -c "import PIL" &>/dev/null; then
    echo "Installing Pillow from system packages..."
    sudo apt-get install -y python3-pil python3-pil.imagetk
fi

if ! python3 -c "import tkinterdnd2" &>/dev/null; then
    echo "Note: Drag and drop support will be limited."
    echo "tkinterdnd2 installation is optional but recommended."
fi

# Make the scripts executable
chmod +x shortcut_creator.py shortcut_creator_gui.py run_shortcut_creator.sh create_desktop_shortcut.sh

echo "All dependencies installed successfully!"
echo "You can now run the Desktop Shortcut Creator using:"
echo "./run_shortcut_creator.sh"
echo ""
echo "Or create a desktop shortcut with:"
echo "./create_desktop_shortcut.sh"

# Deactivate virtual environment
deactivate 