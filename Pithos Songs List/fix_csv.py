#!/usr/bin/env python3

import csv
import os
from datetime import datetime

# Path to the CSV file
csv_file = os.path.expanduser("~/pithos_songs.csv")
backup_file = os.path.expanduser("~/pithos_songs_backup.csv")

# Create a backup of the original file
if os.path.exists(csv_file):
    with open(csv_file, 'r') as original:
        with open(backup_file, 'w') as backup:
            backup.write(original.read())
    print(f"Backup created at {backup_file}")

# Now fix the CSV file
try:
    # Read all entries, normalizing the format
    unique_songs = {}  # Use a dict to track unique songs
    
    # First, try to parse the file as a proper CSV
    with open(csv_file, 'r', newline='') as f:
        content = f.read()
        
        # Fix backslash escaped commas
        content = content.replace('\\,', ',')
        
        # Write to a temporary file for proper CSV parsing
        temp_file = os.path.expanduser("~/temp_pithos_songs.csv")
        with open(temp_file, 'w') as tf:
            tf.write(content)
        
        # Now read the corrected file
        songs = []
        with open(temp_file, 'r', newline='') as tf:
            try:
                reader = csv.reader(tf)
                header = next(reader, ["Title", "Artist", "Album", "Timestamp"])
                
                for row in reader:
                    if len(row) >= 4:
                        title = row[0].strip()
                        artist = row[1].strip()
                        album = row[2].strip()
                        timestamp = row[3].strip()
                        
                        # Create a key for deduplication (case insensitive)
                        key = (title.lower(), artist.lower(), album.lower())
                        
                        # Only keep the most recent entry for each song
                        if key not in unique_songs:
                            unique_songs[key] = (title, artist, album, timestamp)
            except Exception as e:
                print(f"Error parsing CSV: {str(e)}")
        
        # Clean up temporary file
        os.remove(temp_file)
    
    # Convert the dictionary values to a list for writing
    songs = list(unique_songs.values())
    
    # Write back to the file with proper quoting
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Title", "Artist", "Album", "Timestamp"])
        writer.writerows(songs)
    
    print(f"CSV file fixed successfully. {len(songs)} unique songs.")
    
except Exception as e:
    print(f"Error fixing CSV file: {str(e)}")
    print("You can restore from the backup if needed.") 