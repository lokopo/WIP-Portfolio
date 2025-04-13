#!/bin/bash

# Create output directory if it doesn't exist
OUTPUT_DIR="$HOME/Desktop/Monitor_EDID_Info"
mkdir -p "$OUTPUT_DIR"

echo "Extracting EDID information from connected monitors..."

# Get raw EDID data using get-edid
echo "Extracting raw EDID data..."
sudo get-edid | tee "$OUTPUT_DIR/edid_raw_output.txt" | parse-edid > "$OUTPUT_DIR/edid_parsed.txt" 2>&1

# Extract EDID data for each connected monitor using xrandr
echo "Extracting EDID data for each connected monitor..."
xrandr --prop | grep -A40 "connected" | grep -A40 "EDID" > "$OUTPUT_DIR/all_monitors_edid.txt"

# Extract EDID specifically for the 4K monitor (HDMI-0)
echo "Extracting EDID data for 4K monitor (HDMI-0)..."
xrandr --prop | grep -A40 "HDMI-0" | grep -A40 "EDID" > "$OUTPUT_DIR/hdmi0_edid.txt"

# Use edid-decode if available
if command -v edid-decode &> /dev/null; then
    echo "Decoding EDID data using edid-decode..."
    # Extract binary EDID data
    xrandr --prop | grep -A20 "EDID" | grep -v "EDID" | grep -v "\-\-" | tr -d ' \t' | xxd -r -p > "$OUTPUT_DIR/edid.bin"
    # Decode the binary data
    edid-decode "$OUTPUT_DIR/edid.bin" > "$OUTPUT_DIR/edid_decoded.txt" 2>&1
else
    echo "edid-decode not found. Installing..."
    sudo apt-get install -y edid-decode
    if [ $? -eq 0 ]; then
        echo "Decoding EDID data using edid-decode..."
        # Extract binary EDID data
        xrandr --prop | grep -A20 "EDID" | grep -v "EDID" | grep -v "\-\-" | tr -d ' \t' | xxd -r -p > "$OUTPUT_DIR/edid.bin"
        # Decode the binary data
        edid-decode "$OUTPUT_DIR/edid.bin" > "$OUTPUT_DIR/edid_decoded.txt" 2>&1
    else
        echo "Failed to install edid-decode. Skipping detailed decoding."
    fi
fi

# Create a summary file
echo "Creating summary file..."
{
    echo "=== Monitor EDID Information Summary ==="
    echo "Date: $(date)"
    echo ""
    echo "=== Connected Monitors ==="
    xrandr | grep " connected" | cat
    echo ""
    echo "=== Monitor Details ==="
    xrandr --prop | grep -A2 "connected" | cat
    echo ""
    echo "Files generated:"
    ls -l "$OUTPUT_DIR" | cat
} > "$OUTPUT_DIR/summary.txt"

echo "EDID information extraction complete!"
echo "Results saved to: $OUTPUT_DIR"
ls -l "$OUTPUT_DIR" 