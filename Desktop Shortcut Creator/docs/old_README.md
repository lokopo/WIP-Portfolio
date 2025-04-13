# Desktop Shortcut Creator

A Python utility for reliably creating desktop shortcuts for applications on Linux systems. This tool offers both a simple GUI interface and a command-line interface.

## Features

- Automatic file type detection
- Automatic icon selection based on file type
- Drag and drop support for files and folders
- Simple, user-friendly interface
- Creates standard-compliant .desktop files
- Command-line interface for advanced users

## Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Make the scripts executable:
```bash
chmod +x shortcut_creator.py shortcut_creator_gui.py
```

## GUI Usage

The GUI version is designed to be very simple to use:

1. Run the GUI version:
```bash
./shortcut_creator_gui.py
```

2. Either:
   - Click the "Browse" button to select a file or folder
   - Or drag and drop a file or folder onto the application

3. The application will automatically detect the file type and suggest appropriate settings

4. Verify or modify any settings as needed

5. Click "Create Shortcut" and you're done!

![GUI Screenshot](screenshot.png)

### Automatic Detection

The GUI version automatically:
- Determines if the target is a file or folder
- Selects appropriate icons based on file type
- Determines if a terminal is needed (for scripts)
- Sets up the correct command to launch the target
- Assigns appropriate categories for menu organization

## Command Line Usage

For advanced users, the command-line interface is still available:

Basic usage:
```bash
./shortcut_creator.py --name "My Application" --exec "/path/to/executable"
```

Full options:
```bash
./shortcut_creator.py --name "My Application" \
                     --exec "/path/to/executable" \
                     --icon "/path/to/icon.png" \
                     --desc "Description of my application" \
                     --terminal \
                     --categories "Development,Utility" \
                     --working-dir "/path/to/working/directory"
```

### Parameters

- `--name`, `-n`: Name of the application (required)
- `--exec`, `-e`: Path to the executable (required)
- `--icon`, `-i`: Path to the icon file
- `--desc`, `-d`: Description of the application
- `--terminal`, `-t`: Run in terminal (flag, no value needed)
- `--categories`, `-c`: Categories (comma-separated)
- `--working-dir`, `-w`: Working directory

## What it does

This script:
1. Creates a `.desktop` file in `~/.local/share/applications/`
2. Creates a symlink to this file on your Desktop
3. Updates the desktop database

## Example

Create a shortcut for Firefox:
```bash
./shortcut_creator.py --name "Firefox" --exec "/usr/bin/firefox" --icon "/usr/share/icons/hicolor/128x128/apps/firefox.png" --desc "Web Browser" --categories "Network,WebBrowser"
```

Create a shortcut for a Python script:
```bash
./shortcut_creator.py --name "My Python App" --exec "/path/to/myscript.py" --terminal --categories "Development,Utility"
``` 