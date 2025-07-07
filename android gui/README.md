# Remote Command Executor

A Python application that allows you to remotely execute commands on your desktop computer from your Android device using Pydroid. Commands are sent via Google Sheets or Excel Online.

## Features

- 🖥️ **Desktop GUI** - User-friendly interface for monitoring and configuration
- 📱 **Android Client** - Send commands from your phone using Pydroid
- 📊 **Google Sheets Integration** - Use Google Sheets as communication medium
- 🔒 **Security** - Whitelist allowed commands for safety
- 📝 **Command History** - View execution results and logs
- ⚡ **Real-time Monitoring** - Automatic polling for new commands

## Requirements

### Desktop (Linux/Windows/macOS)
- Python 3.6+
- Internet connection
- Google Sheets API access

### Android
- Pydroid 3 app from Google Play Store
- Internet connection

## Installation

### 1. Desktop Setup

1. **Install Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Google Sheets API Setup:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API
   - Create service account credentials
   - Download credentials JSON file and rename to `credentials.json`
   - Place `credentials.json` in the same folder as the scripts

3. **Create Google Sheet:**
   - Create a new Google Sheet
   - Add columns: `Timestamp`, `Command`, `Status`, `Output`, `Device`
   - Share the sheet with the service account email (found in credentials.json)
   - Copy the spreadsheet ID from the URL

4. **Run the application:**
   ```bash
   python remote_command_gui.py
   ```

### 2. Android Setup (Pydroid)

1. **Install Pydroid 3** from Google Play Store

2. **Install required packages in Pydroid:**
   ```python
   pip install gspread google-auth requests
   ```

3. **Transfer files to Android:**
   - Copy `android_client.py` to your Pydroid files
   - Copy `credentials.json` to the same folder as the client script

4. **Configure the client:**
   - Edit `android_client.py` and update the configuration section
   - Enter your spreadsheet ID and device ID

## Configuration

### Desktop Configuration

1. Launch the desktop application
2. Go to the **Configuration** tab
3. Enter your Google Sheets details:
   - **Spreadsheet ID**: Found in the Google Sheets URL
   - **Worksheet Name**: Usually "Commands" or "Sheet1"
4. Configure allowed commands (security feature)
5. Set polling interval (how often to check for new commands)
6. Click **Save Configuration**
7. Test the connection with **Test Google Sheets**

### Android Configuration

Update the configuration in `android_client.py`:

```python
def load_config(self):
    return {
        "google_sheets": {
            "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE",
            "worksheet_name": "Commands",
            "credentials_file": "credentials.json"
        },
        "device_id": "android_device_1"
    }
```

## Usage

### Desktop
1. Start the application: `python remote_command_gui.py`
2. Go to Configuration tab and set up your Google Sheets
3. Click **Start Monitoring** in the Main tab
4. The application will now check for new commands every 5 seconds

### Android
1. Open Pydroid 3
2. Run `android_client.py`
3. Enter your spreadsheet ID and device ID
4. Click **Connect to Sheets**
5. Use quick command buttons or type custom commands
6. Click **Send Command**
7. Use **Refresh Results** to see command output

## Security Features

- **Command Whitelist**: Only predefined commands can be executed
- **Logging**: All commands are logged with timestamps
- **Authentication**: Uses Google API authentication
- **Timeout**: Commands timeout after 30 seconds

### Default Allowed Commands
- `ls` - List files
- `pwd` - Print working directory
- `whoami` - Show current user
- `date` - Show current date/time
- `uptime` - Show system uptime
- `df -h` - Show disk usage
- `free -h` - Show memory usage
- `ps aux` - Show running processes
- `top -n 1` - Show top processes
- `systemctl status` - Show system service status
- `netstat -tuln` - Show network connections

## Troubleshooting

### Common Issues

1. **"Google Sheets client not initialized"**
   - Check that `credentials.json` exists in the correct location
   - Verify the service account has access to the spreadsheet

2. **"Permission denied" errors**
   - Make sure the Google Sheet is shared with the service account email
   - Check that the service account has edit permissions

3. **"Command not allowed"**
   - Add the command to the allowed commands list in configuration
   - Commands must start with an allowed prefix

4. **Connection timeouts**
   - Check internet connection
   - Verify Google Sheets API is enabled
   - Check firewall settings

### Debug Steps

1. **Check logs**: Look at `remote_commands.log` for error messages
2. **Test API**: Use the "Test Google Sheets" button in configuration
3. **Verify credentials**: Ensure `credentials.json` is valid
4. **Check permissions**: Verify sheet sharing settings

## Google Sheets API Setup (Detailed)

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "New Project"
   - Enter project name and click "Create"

2. **Enable Google Sheets API:**
   - In the project dashboard, go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click on it and press "Enable"

3. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service account"
   - Enter service account name
   - Click "Create and Continue"
   - Skip role assignment (click "Continue")
   - Skip granting users access (click "Done")

4. **Download Credentials:**
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select "JSON" and click "Create"
   - Save the downloaded file as `credentials.json`

5. **Share Spreadsheet:**
   - Open your Google Sheet
   - Click "Share" button
   - Enter the service account email (found in credentials.json)
   - Give "Editor" permissions
   - Click "Send"

## Excel Online Setup (Coming Soon)

Excel Online integration is planned for future versions. Currently, only Google Sheets is supported.

## File Structure

```
android gui/
├── remote_command_gui.py    # Desktop application
├── android_client.py        # Android client for Pydroid
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── credentials.json        # Google API credentials (you provide)
└── config.json            # Auto-generated configuration
```

## Contributing

Feel free to contribute improvements:
- Add new command types
- Improve security features
- Add Excel Online support
- Enhance the GUI
- Add error handling

## License

This project is open source. Use responsibly and ensure proper security measures are in place.

## Disclaimer

This tool allows remote command execution. Use only on systems you own and with proper security precautions. Always review and limit the allowed commands list.