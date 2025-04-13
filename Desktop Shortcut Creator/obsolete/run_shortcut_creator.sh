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

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
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
fi

# Make sure the scripts are executable
chmod +x shortcut_creator.py shortcut_creator_gui.py

# Run the GUI version
python3 shortcut_creator_gui.py

# Deactivate virtual environment when done
deactivate 