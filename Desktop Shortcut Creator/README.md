# Desktop Shortcut Creator

![Status: In Progress](https://img.shields.io/badge/Status-In%20Progress-yellow)

## Project Status
🚧 This project is currently under development. 🚧

### What's Working
- Modern PyQt6 interface
- Drag and drop support
- Automatic file type detection
- Basic shortcut creation

### In Progress
- Enhanced icon selection
- Custom shortcut naming
- Batch creation support

### Planned Features
- Template system
- Shortcut organization
- Backup/restore functionality
- Cross-platform support

## Description
A modern utility for creating desktop shortcuts on Linux with automatic file type detection. This tool provides a user-friendly interface for managing desktop shortcuts with smart features like automatic icon selection and file type detection.

## Features

- Modern PyQt6 interface
- Drag and drop support
- Automatic file type detection
- Smart icon selection
- Simple one-click shortcut creation

## Quick Start

Run the application:

```bash
./"Run Me"
```

Create a desktop shortcut for this application:

```bash
./create_shortcut.sh
```

## Usage

1. Select a file or folder by:
   - Dragging and dropping it onto the application
   - Clicking the "Browse" button
   - Typing the path directly

2. The application will automatically detect the file type and suggest appropriate settings

3. Adjust any settings if needed

4. Click "Create Shortcut" and you're done!

## Development

- The main application is in `shortcut_creator_pyqt.py`
- Command-line interface is in `shortcut_creator.py`
- Dependencies are managed in `requirements.txt`

## Contributing
Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License
MIT License

## Files

- `shortcut_creator_pyqt.py`: The main application (PyQt interface)
- `shortcut_creator.py`: Command-line interface (for backward compatibility)
- `run_shortcut_creator.sh`: Script to run the application
- `create_shortcut.sh`: Script to create a desktop shortcut for this application
- `requirements.txt`: List of Python dependencies
