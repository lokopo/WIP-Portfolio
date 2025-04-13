# PyAutoGUI Enhanced

![Status: In Progress](https://img.shields.io/badge/Status-In%20Progress-yellow)

## Project Status
🚧 This project is currently under development. 🚧

### What's Working
- Mouse position tracking
- Screen size detection
- Basic automation scripts
- Visual screen markers for click positions
- Custom offset support for each marker
- Command management with drag-and-drop reordering
- Script saving and loading
- Modern CustomTkinter-based interface
- No root privileges required
- Window stays visible during command execution
- Hotkey support for commands
- Custom text input support

### In Progress
- Enhanced error handling
- Additional automation features
- Configuration system

### Planned Features
- Macro recording
- Script scheduling
- Cross-platform compatibility improvements

## Features

- Visual screen markers for click positions
- Custom offset support for each marker
- Command management with drag-and-drop reordering
- Script saving and loading
- Modern CustomTkinter-based interface
- No root privileges required
- Window stays visible during command execution
- Hotkey support for commands
- Custom text input support

## Requirements

- Python 3.8 or higher
- Dependencies listed in requirements.txt

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python "Run Me.py"
```

2. Use the interface to:
   - Add click markers by clicking the "Add Click Marker" button
   - Set custom offsets for each marker
   - Add hotkey commands
   - Add text input commands
   - Save and load scripts
   - Reorder commands using drag and drop
   - Show/hide markers
   - Execute commands

## Notes

- The application uses a secondary invisible window for click capture
- No need to minimize the main window
- Markers persist between script loads
- Custom offsets are saved with scripts
- Window state is preserved between sessions

## Description
An enhanced version of PyAutoGUI with additional features for GUI automation. This tool extends the capabilities of PyAutoGUI with improved error handling, additional automation features, and a more user-friendly interface.

## Setup

1. Create a Python virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On Linux/Mac
# OR
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To run the application, make sure your virtual environment is activated, then run:
```bash
python "Run Me.py"
```

## Development

- The main script is `Run Me.py`
- Dependencies are managed in `requirements.txt`
- Remember to activate the virtual environment before running the script

## Contributing
Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License
MIT License 
