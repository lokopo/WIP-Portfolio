# Window Text Sender

This application allows you to send text input to multiple windows simultaneously using a PyQt GUI.

## Requirements

- Python 3.6 or higher
- PyQt6
- python-xlib
- X11 window system (Linux/Unix)

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make the script executable:
```bash
chmod +x "Run Me"
```

## Usage

1. Run the application:
```bash
./"Run Me"
```

2. The application will show a list of all available windows on your system.

3. Select one or more windows from the list by holding Ctrl/Cmd and clicking on them.

4. Enter the text you want to send in the text input field.

5. Click "Send Text" to send the text to all selected windows.

6. Use the "Refresh Window List" button to update the list of available windows.

## Notes

- The application works by simulating keyboard input to the selected windows.
- Some applications may not accept simulated keyboard input for security reasons.
- The text is sent character by character with small delays to ensure reliability.
- Make sure the target windows are visible and not minimized when sending text. 