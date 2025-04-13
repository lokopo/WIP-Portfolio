# Pithos Song Logger

This tool automatically logs songs played through Pithos to a CSV file for future reference.

## Features

- Modern dark mode interface with Material Design
- Real-time song change detection (no polling)
- Automatic Pithos launching - starts Pithos when the logger starts
- Starts automatically on system boot (without starting Pithos separately)
- Shows currently playing song information
- Logs song title, artist, album, and timestamp to a CSV file
- Avoids duplicate entries

## How to Use

Run the application by double-clicking the "Pithos Song Logger (Ultra Modern)" icon on your desktop, or with:

```
python3 pithos_logger_gui_modern.py
```

The interface provides:
- Current Pithos status with visual indicators
- Real-time display of the currently playing song
- Song history table showing all logged songs
- Controls for logging and data management
- Button to manually launch Pithos if needed

## Automatic Startup

The application is configured to:
1. Start automatically when you log in to your computer
2. Launch Pithos automatically when the logger starts
3. Disable Pithos from starting separately (to avoid duplicate instances)

This ensures you'll always have your songs logged without needing to remember to start anything manually.

## CSV File

The CSV file is created at `~/pithos_songs.csv` and contains the following columns:
- title - The song title
- artist - The artist name
- album - The album name
- timestamp - When the song was first recorded (YYYY-MM-DD HH:MM:SS)

## Requirements

- Python 3 with PyQt5 (`sudo apt install python3-pyqt5`)
- Python D-Bus bindings (`sudo apt install python3-dbus python3-gi`)
- Pithos music player

## Background Logging

The application can run in the background and log songs automatically. To start logging:

1. Launch the application (happens automatically on startup)
2. Click the "Start Logging" button
3. The application will log songs even when you're not actively using it

You can minimize the window and continue using your computer while logging runs in the background. 