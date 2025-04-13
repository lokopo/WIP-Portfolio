#!/bin/bash

# Create output directory if it doesn't exist
OUTPUT_DIR="$HOME/Desktop/Monitor_EDID_Info"
mkdir -p "$OUTPUT_DIR"

echo "Extracting raw binary EDID data from HDMI-0 (4K monitor)..."

# Extract EDID specifically for the 4K monitor (HDMI-0) and convert to binary
echo "Creating binary EDID file for HDMI-0..."
xrandr --prop | grep -A40 "HDMI-0" | grep -A40 "EDID:" | grep -v "EDID:" | grep -v "\-\-" | tr -d ' \t\n' | xxd -r -p > "$OUTPUT_DIR/hdmi0_edid.bin"

# Also create a standard 128-byte or 256-byte EDID binary file
echo "Creating standard EDID binary file..."
xrandr --prop | grep -A40 "HDMI-0" | grep -A40 "EDID:" | grep -v "EDID:" | grep -v "\-\-" | tr -d ' \t\n' | xxd -r -p > "$OUTPUT_DIR/edid_hdmi0_windows.bin"

# Create a hex dump for verification
xxd "$OUTPUT_DIR/hdmi0_edid.bin" > "$OUTPUT_DIR/hdmi0_edid_hex.txt"

# Check file size
FILESIZE=$(stat -c%s "$OUTPUT_DIR/hdmi0_edid.bin")
echo "EDID binary file size: $FILESIZE bytes"

echo "Raw binary EDID extraction complete!"
echo "Files saved to: $OUTPUT_DIR"
echo "The file 'edid_hdmi0_windows.bin' should be compatible with Windows EDID upload tools." 