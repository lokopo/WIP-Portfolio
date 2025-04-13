#!/bin/bash

echo "Cleaning up and organizing Desktop Shortcut Creator files..."

# Create directories for organization
mkdir -p obsolete
mkdir -p docs

# Move obsolete files to the obsolete directory
echo "Moving obsolete files..."
mv shortcut_creator_gui.py obsolete/
mv run_shortcut_creator.sh obsolete/
mv create_desktop_shortcut.sh obsolete/
mv install_dependencies.sh obsolete/

# Clean up requirements.txt
echo "Updating requirements.txt..."
cat > requirements.txt << EOL
# Dependencies for the Desktop Shortcut Creator (PyQt version)
python-magic>=0.4.24  # For file type detection
python-magic-bin>=0.4.14  # Alternative for python-magic that includes binaries
Pillow>=9.0.0  # For image handling and icons
PyQt6>=6.5.0  # Modern Qt framework for Python
EOL

# Update README.md
echo "Moving README.md to docs/ and creating new one..."
mv README.md docs/old_README.md

# Create a new README.md
cat > README.md << EOL
# Desktop Shortcut Creator (PyQt)

A modern utility for creating desktop shortcuts on Linux with automatic file type detection.

## Features

- Modern PyQt6 interface
- Drag and drop support
- Automatic file type detection
- Smart icon selection
- Simple one-click shortcut creation

## Quick Start

Run the application:

\`\`\`bash
./run_shortcut_creator_pyqt.sh
\`\`\`

Create a desktop shortcut for this application:

\`\`\`bash
./create_pyqt_shortcut.sh
\`\`\`

## Usage

1. Select a file or folder by:
   - Dragging and dropping it onto the application
   - Clicking the "Browse" button
   - Typing the path directly

2. The application will automatically detect the file type and suggest appropriate settings

3. Adjust any settings if needed

4. Click "Create Shortcut" and you're done!

## Files

- \`shortcut_creator_pyqt.py\`: The main application (PyQt interface)
- \`shortcut_creator.py\`: Command-line interface (for backward compatibility)
- \`run_shortcut_creator_pyqt.sh\`: Script to run the application
- \`create_pyqt_shortcut.sh\`: Script to create a desktop shortcut for this application
- \`requirements.txt\`: List of Python dependencies
EOL

# Create index file
echo "Creating index.md..."
cat > docs/index.md << EOL
# Desktop Shortcut Creator - File Index

## Active Files

- \`shortcut_creator_pyqt.py\`: Main application with PyQt6 GUI
- \`shortcut_creator.py\`: Command-line interface version
- \`run_shortcut_creator_pyqt.sh\`: Script to launch the PyQt GUI version
- \`create_pyqt_shortcut.sh\`: Script to create a desktop shortcut for the PyQt version
- \`requirements.txt\`: Python dependencies
- \`README.md\`: Project documentation

## Obsolete Files (Moved to obsolete/ directory)

- \`shortcut_creator_gui.py\`: Old Tkinter GUI version (replaced by PyQt version)
- \`run_shortcut_creator.sh\`: Script to run the old Tkinter version
- \`create_desktop_shortcut.sh\`: Script to create a shortcut for the old version
- \`install_dependencies.sh\`: Old dependency installation script (functionality incorporated into run script)

## Directory Structure

- \`/\`: Main project directory with active files
- \`/obsolete/\`: Contains deprecated files that are kept for reference
- \`/docs/\`: Contains documentation and reference materials
- \`/venv/\`: Python virtual environment (if created)
EOL

echo "Cleanup complete!"
echo "Active files remain in the main directory."
echo "Obsolete files have been moved to the 'obsolete/' directory."
echo "Documentation is in the 'docs/' directory." 