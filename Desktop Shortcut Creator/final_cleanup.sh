#!/bin/bash

echo "Performing final cleanup of Desktop Shortcut Creator..."

# Move the original CLI script to obsolete
echo "Moving CLI script to obsolete directory..."
mv shortcut_creator.py obsolete/

# Update the PyQt run script to include CLI functionality
echo "Updating run script to handle CLI mode..."
cat > run_shortcut_creator.sh << EOL
#!/bin/bash

# Get the script directory
DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"

# Change to script directory
cd "\$DIR"

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

# Make sure scripts are executable
chmod +x shortcut_creator_pyqt.py

# Run the application
if [ "\$1" == "--cli" ]; then
    # CLI mode - use the PyQt script with CLI argument
    python3 shortcut_creator_pyqt.py --cli "\${@:2}"
else
    # GUI mode
    python3 shortcut_creator_pyqt.py
fi

# Deactivate virtual environment when done
deactivate
EOL

# Make it executable
chmod +x run_shortcut_creator.sh

# Update the PyQt script to handle CLI mode
echo "Updating the main script to include CLI functionality..."

# First, let's check if the main method already handles CLI arguments
CLI_CHECK=$(grep -c "if len(sys.argv) > 1 and sys.argv\[1\] != '--gui'" shortcut_creator_pyqt.py)

if [ "$CLI_CHECK" -gt 0 ]; then
    # Already has CLI handling, just update it
    sed -i 's/if len(sys.argv) > 1 and sys.argv\[1\] != '\''--gui'\''/if len(sys.argv) > 1 and sys.argv[1] == '\''--cli'\''/g' shortcut_creator_pyqt.py
else
    # Add CLI functionality to the script
    echo "Warning: Could not automatically update the script for CLI mode."
    echo "Please update shortcut_creator_pyqt.py manually to add CLI support."
fi

# Remove the redundant PyQt-specific scripts
echo "Renaming and cleaning up redundant scripts..."
mv run_shortcut_creator_pyqt.sh obsolete/
mv create_pyqt_shortcut.sh create_shortcut.sh

# Update desktop shortcut script
echo "Updating desktop shortcut creation script..."
sed -i 's/run_shortcut_creator_pyqt.sh/run_shortcut_creator.sh/g' create_shortcut.sh
sed -i 's/desktop-shortcut-creator-pyqt/desktop-shortcut-creator/g' create_shortcut.sh
sed -i 's/Desktop Shortcut Creator (PyQt)/Desktop Shortcut Creator/g' create_shortcut.sh

# Remove initial cleanup script
echo "Removing initial cleanup script..."
mv cleanup.sh obsolete/

# Update README
echo "Updating README.md..."
sed -i 's/run_shortcut_creator_pyqt.sh/run_shortcut_creator.sh/g' README.md
sed -i 's/create_pyqt_shortcut.sh/create_shortcut.sh/g' README.md
sed -i 's/ (PyQt)//g' README.md

# Update docs/index.md
echo "Updating docs/index.md..."
cat > docs/index.md << EOL
# Desktop Shortcut Creator - File Index

## Active Files

- \`shortcut_creator_pyqt.py\`: Main application with PyQt6 GUI and CLI functionality
- \`run_shortcut_creator.sh\`: Universal script to launch either GUI or CLI mode
- \`create_shortcut.sh\`: Script to create a desktop shortcut
- \`requirements.txt\`: Python dependencies
- \`README.md\`: Project documentation

## Obsolete Files (in obsolete/ directory)

- \`shortcut_creator.py\`: Old CLI-only version
- \`shortcut_creator_gui.py\`: Old Tkinter GUI version
- \`run_shortcut_creator_pyqt.sh\`: Former PyQt-specific run script
- \`run_shortcut_creator.sh\`: Script for the Tkinter version
- \`create_desktop_shortcut.sh\`: Shortcut creation for the Tkinter version
- \`install_dependencies.sh\`: Old dependency installation script
- \`cleanup.sh\`: Initial cleanup script

## Directory Structure

- \`/\`: Main project directory with active files
- \`/obsolete/\`: Contains deprecated files that are kept for reference
- \`/docs/\`: Contains documentation and reference materials
- \`/venv/\`: Python virtual environment (if created)
EOL

echo "Final cleanup complete!"
echo ""
echo "The project now has a simplified structure with:"
echo "- shortcut_creator_pyqt.py (main script with GUI and CLI support)"
echo "- run_shortcut_creator.sh (universal launcher script)"
echo "- create_shortcut.sh (desktop shortcut creator)"
echo ""
echo "Run the app with: ./run_shortcut_creator.sh"
echo "Create a desktop shortcut with: ./create_shortcut.sh"
echo ""
echo "You can also run in CLI mode with: ./run_shortcut_creator.sh --cli [args]" 