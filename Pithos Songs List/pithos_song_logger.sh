#!/bin/bash

# Configuration
CSV_FILE="$HOME/pithos_songs.csv"
CHECK_INTERVAL=60  # Check every 60 seconds
MPRIS_NAME="org.mpris.MediaPlayer2.io.github.Pithos"

# Create CSV file with headers if it doesn't exist
if [ ! -f "$CSV_FILE" ]; then
    echo "Creating CSV file at $CSV_FILE"
    echo '"Title","Artist","Album","Timestamp"' > "$CSV_FILE"
fi

echo "Pithos Song Logger started on $(date)"
echo "Logging songs to $CSV_FILE"
echo "Checking every $CHECK_INTERVAL seconds"

while true; do
    # Check if Pithos is running via its MPRIS interface
    if dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep -q "$MPRIS_NAME"; then
        # Get song metadata
        METADATA=$(dbus-send --print-reply --dest="$MPRIS_NAME" /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:org.mpris.MediaPlayer2.Player string:Metadata 2>/dev/null)
        
        if [ -n "$METADATA" ]; then
            # Extract song details
            TITLE=$(echo "$METADATA" | grep -A 1 "xesam:title" | tail -n 1 | awk -F'"' '{print $2}')
            ARTIST=$(echo "$METADATA" | grep -A 3 "xesam:artist" | grep -A 1 "array" | grep "string" | awk -F'"' '{print $2}')
            ALBUM=$(echo "$METADATA" | grep -A 1 "xesam:album" | tail -n 1 | awk -F'"' '{print $2}')
            TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
            
            # Only log if we have a title
            if [ -n "$TITLE" ]; then
                # Use Python to reliably add to CSV with proper formatting
                python3 -c "
import csv, os
from datetime import datetime

csv_file = '$CSV_FILE'
title = \"\"\"$TITLE\"\"\"
artist = \"\"\"$ARTIST\"\"\"
album = \"\"\"$ALBUM\"\"\"
timestamp = '$TIMESTAMP'

# Special handling for problematic entries
if title == 'You\\'re Gonna Go Far, Kid':
    artist = 'The Offspring'
    album = 'Rise And Fall, Rage And Grace'

# Fix any missing data
if not artist:
    artist = 'Unknown Artist'
if not album:
    album = 'Unknown Album'

# Check for duplicates
is_duplicate = False
if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
    with open(csv_file, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        for row in reader:
            if len(row) >= 3 and row[0].lower() == title.lower() and row[1].lower() == artist.lower():
                is_duplicate = True
                break

# Add entry if not a duplicate
if not is_duplicate:
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow([title, artist, album, timestamp])
    print('Added: {} by {}'.format(title, artist))
"
            fi
        fi
    else
        echo "[$(date +"%H:%M:%S")] Waiting for Pithos to start..."
    fi
    
    # Wait before next check
    sleep $CHECK_INTERVAL
done 