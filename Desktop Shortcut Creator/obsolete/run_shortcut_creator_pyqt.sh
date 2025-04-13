#!/bin/bash

# Get the script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to script directory
cd "$DIR"

# Check if system dependencies are installed
if ! dpkg -l | grep -q libmagic1; then
    echo "Installing required system dependencies..."
    sudo apt-get update && sudo apt-get install -y libmagic1
fi

# Check if PyQt6 is installed via system packages
if ! dpkg -l | grep -q "python3-pyqt6"; then
    echo "Installing PyQt6 system package..."
    sudo apt-get install -y python3-pyqt6 python3-pyqt6-sip
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # If PyQt6 install failed in pip, try system PyQt6
    if ! python3 -c "import PyQt6" &>/dev/null; then
        echo "Using system PyQt6..."
        ln -sf /usr/lib/python3/dist-packages/PyQt6 venv/lib/python*/site-packages/
        ln -sf /usr/lib/python3/dist-packages/PyQt6_sip*.so venv/lib/python*/site-packages/
    fi
else
    source venv/bin/activate
    
    # Check if dependencies are installed correctly
    if ! python3 -c "import magic" &>/dev/null; then
        echo "Reinstalling dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # If still fails, try direct installation
        if ! python3 -c "import magic" &>/dev/null; then
            echo "Trying alternative installation method..."
            pip install python-magic-bin
        fi
    fi
    
    # Check for PyQt6
    if ! python3 -c "import PyQt6" &>/dev/null; then
        echo "Installing PyQt6..."
        pip install PyQt6
        
        # If that fails, try to use system PyQt
        if ! python3 -c "import PyQt6" &>/dev/null; then
            echo "Using system PyQt6..."
            sudo apt-get install -y python3-pyqt6 python3-pyqt6-sip
            ln -sf /usr/lib/python3/dist-packages/PyQt6 venv/lib/python*/site-packages/
            ln -sf /usr/lib/python3/dist-packages/PyQt6_sip*.so venv/lib/python*/site-packages/
        fi
    fi
fi

# Make sure the scripts are executable
chmod +x shortcut_creator.py shortcut_creator_pyqt.py

# Run the PyQt GUI version
python3 shortcut_creator_pyqt.py

# Deactivate virtual environment when done
deactivate 