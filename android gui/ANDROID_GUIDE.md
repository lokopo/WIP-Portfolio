# Android Setup Guide for Pydroid

This guide will help you set up the Android client for remote command execution using Pydroid.

## Requirements

- Android device
- Pydroid 3 app (free from Google Play Store)
- Internet connection
- Google Sheets API credentials (same as desktop)

## Step-by-Step Setup

### 1. Install Pydroid 3

1. Open Google Play Store on your Android device
2. Search for "Pydroid 3"
3. Install the app by IIEC

### 2. Install Required Packages

1. Open Pydroid 3
2. Go to the **Terminal** tab (bottom menu)
3. Run these commands one by one:

```bash
pip install gspread
pip install google-auth
pip install requests
```

### 3. Transfer Files to Android

You need to copy these files to your Android device:

- `android_client.py` - The main client application
- `credentials.json` - Your Google API credentials

**Methods to transfer files:**

**Option A: Using Cloud Storage**
1. Upload files to Google Drive, Dropbox, or OneDrive
2. Download them to your Android device
3. Move them to Pydroid's files folder

**Option B: Using USB Cable**
1. Connect your Android to computer via USB
2. Copy files to Android storage
3. Move them to Pydroid's working directory

**Option C: Using Email**
1. Email the files to yourself
2. Download attachments on Android
3. Move to Pydroid folder

### 4. Configure the Client

1. Open Pydroid 3
2. Navigate to your files and open `android_client.py`
3. Find the `load_config` function (around line 30)
4. Update the configuration:

```python
def load_config(self):
    return {
        "google_sheets": {
            "spreadsheet_id": "YOUR_ACTUAL_SPREADSHEET_ID",
            "worksheet_name": "Commands",
            "credentials_file": "credentials.json"
        },
        "device_id": "my_android_phone"  # Change this to identify your device
    }
```

### 5. Get Your Spreadsheet ID

1. Open your Google Sheet in a web browser
2. Look at the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
3. Copy the long string between `/d/` and `/edit`
4. This is your spreadsheet ID

### 6. First Run

1. In Pydroid, run `android_client.py`
2. Enter your spreadsheet ID in the configuration field
3. Enter a unique device ID (e.g., "my_android", "phone1")
4. Click "Connect to Sheets"
5. If successful, you'll see "Status: Connected"

## Using the Android Client

### Sending Commands

1. **Quick Commands**: Use the preset buttons for common commands
2. **Custom Commands**: Type any command in the text field
3. **Send**: Click "Send Command" or press Enter

### Available Quick Commands

- **System Info**: Get system information
- **Disk Usage**: Check disk space
- **Memory**: Check memory usage
- **Processes**: List running processes
- **Network**: Show network connections
- **Uptime**: Show system uptime

### Viewing Results

1. Click "Refresh Results" to see command outputs
2. Enable "Auto-refresh" for automatic updates
3. Results show the last 10 commands for your device

## Troubleshooting

### Common Issues

**"gspread not found"**
- Solution: Install gspread in Pydroid terminal: `pip install gspread`

**"Credentials file not found"**
- Solution: Make sure `credentials.json` is in the same folder as `android_client.py`

**"Permission denied"**
- Solution: Check that your Google Sheet is shared with the service account email

**"Connection failed"**
- Solution: Verify your spreadsheet ID and internet connection

### Testing Your Setup

1. Send a simple command like "date" or "whoami"
2. Check your Google Sheet - you should see the command with "pending" status
3. On your desktop, the command should be executed and results updated

## Security Notes

- Only use on networks you trust
- The desktop application filters commands for security
- Don't share your credentials.json file
- Use a unique device ID for each Android device

## File Locations in Pydroid

Pydroid typically stores files in:
- Internal storage: `/sdcard/Android/data/ru.iiec.pydroid3/files/`
- You can also use the built-in file manager in Pydroid

## Next Steps

1. Set up your desktop application (see main README.md)
2. Start monitoring on desktop
3. Send test commands from Android
4. Check results in Google Sheets

## Advanced Usage

### Multiple Devices

You can use multiple Android devices by:
1. Using different device IDs for each
2. Installing the client on each device
3. All devices can use the same Google Sheet

### Custom Commands

Add your own quick command buttons by editing the `quick_commands` list in `android_client.py`:

```python
quick_commands = [
    ("Custom Command", "your_command_here"),
    ("System Info", "uname -a"),
    # Add more commands here
]
```

## Support

If you encounter issues:
1. Check the console output in Pydroid
2. Verify your Google Sheets setup
3. Ensure internet connectivity
4. Check the main README.md for detailed troubleshooting