#!/bin/bash

# Create output directory if it doesn't exist
OUTPUT_DIR="$HOME/Desktop/Monitor_EDID_Info"
mkdir -p "$OUTPUT_DIR"

echo "Creating Windows-compatible EDID files..."

# Create Windows directory
WINDOWS_DIR="$OUTPUT_DIR/Windows"
mkdir -p "$WINDOWS_DIR"

# Extract EDID specifically for the 4K monitor (HDMI-0) and convert to binary
echo "Creating binary EDID file for HDMI-0..."
xrandr --prop | grep -A40 "HDMI-0" | grep -A40 "EDID:" | grep -v "EDID:" | grep -v "\-\-" | tr -d ' \t\n' | xxd -r -p > "$WINDOWS_DIR/hdmi0_edid.bin"

# Create a standard 128-byte EDID binary file (first block only)
echo "Creating standard 128-byte EDID binary file..."
xrandr --prop | grep -A40 "HDMI-0" | grep -A40 "EDID:" | grep -v "EDID:" | grep -v "\-\-" | tr -d ' \t\n' | head -c 256 | xxd -r -p > "$WINDOWS_DIR/edid_128byte.bin"

# Create a registry file format
echo "Creating Windows registry file format..."
{
    echo "Windows Registry Editor Version 5.00"
    echo ""
    echo "[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\DISPLAY\\K3-3\\Custom_EDID]"
    echo "\"EDID\"=hex:"
    
    # Convert binary to hex registry format
    xxd -p "$WINDOWS_DIR/hdmi0_edid.bin" | tr -d '\n' | sed 's/\(..\)/\1,/g' | sed 's/,$//g' | fold -w 75 | sed 's/^/  /g' | sed '$ ! s/$/\\/g'
    
    echo ""
} > "$WINDOWS_DIR/edid_hdmi0.reg"

# Create INF file format
echo "Creating Windows INF file format..."
{
    echo "[Version]"
    echo "Signature=\"$WINDOWS NT$\""
    echo "Class=Monitor"
    echo "ClassGUID={4d36e96e-e325-11ce-bfc1-08002be10318}"
    echo "Provider=%MFG%"
    echo "DriverVer=03/09/2025,1.0.0.0"
    echo ""
    echo "[SourceDisksNames]"
    echo "1=%DiskName%,,,\"\""
    echo ""
    echo "[SourceDisksFiles]"
    echo "K3-3.icm=1"
    echo ""
    echo "[DestinationDirs]"
    echo "DefaultDestDir=10,System32\\spool\\drivers\\color"
    echo ""
    echo "[Manufacturer]"
    echo "%MFG%=Models,NTamd64"
    echo ""
    echo "[Models]"
    echo "%MONITOR%=K3-3.Install, Monitor\\K3-3"
    echo ""
    echo "[Models.NTamd64]"
    echo "%MONITOR%=K3-3.Install, Monitor\\K3-3"
    echo ""
    echo "[K3-3.Install]"
    echo "DelReg=DEL_CURRENT_REG"
    echo "AddReg=K3-3.AddReg, 4K_EDID"
    echo "CopyFiles=K3-3.CopyFiles"
    echo ""
    echo "[K3-3.AddReg]"
    echo "HKR,\"MODES\\2560,1440\",Mode1,,%MODE_2560_1440%"
    echo "HKR,\"MODES\\3840,2160\",Mode1,,%MODE_3840_2160%"
    echo ""
    echo "[4K_EDID]"
    echo "HKR,\"EDID_OVERRIDE\",\"0\",1,"
    
    # Convert binary to hex INF format
    xxd -p "$WINDOWS_DIR/hdmi0_edid.bin" | tr -d '\n' | sed 's/\(..\)/\1,/g' | sed 's/,$//g' | fold -w 75 | sed 's/^/  /g' | sed '$ ! s/$/\\/g'
    
    echo ""
    echo "[DEL_CURRENT_REG]"
    echo "HKR,,MaxResolution"
    echo "HKR,,MODES"
    echo "HKR,,EDID_OVERRIDE"
    echo ""
    echo "[K3-3.CopyFiles]"
    echo "K3-3.icm"
    echo ""
    echo "[Strings]"
    echo "MFG=\"DZX\""
    echo "MONITOR=\"K3-3 4K Monitor\""
    echo "DiskName=\"K3-3 Monitor Installation Disk\""
    echo "MODE_2560_1440=\"2560,1440,60\""
    echo "MODE_3840_2160=\"3840,2160,60\""
} > "$WINDOWS_DIR/K3-3_monitor.inf"

# Create a hex dump for verification
xxd "$WINDOWS_DIR/hdmi0_edid.bin" > "$WINDOWS_DIR/hdmi0_edid_hex.txt"

# Create a text file with instructions
{
    echo "# Windows EDID Files for K3-3 4K Monitor"
    echo ""
    echo "This directory contains EDID files in formats compatible with Windows tools for uploading EDID data to a monitor."
    echo ""
    echo "## Files Included:"
    echo ""
    echo "- **hdmi0_edid.bin**: Raw binary EDID data from your 4K monitor (HDMI-0)"
    echo "- **edid_128byte.bin**: Standard 128-byte EDID binary file (first block only)"
    echo "- **edid_hdmi0.reg**: Windows Registry file format for importing EDID data"
    echo "- **K3-3_monitor.inf**: Windows INF file for driver installation with custom EDID"
    echo "- **hdmi0_edid_hex.txt**: Hexadecimal representation of the EDID data for verification"
    echo ""
    echo "## How to Use These Files in Windows:"
    echo ""
    echo "### Using Registry Editor:"
    echo "1. Copy the edid_hdmi0.reg file to your Windows system"
    echo "2. Double-click the file to import the EDID data into the Windows Registry"
    echo "3. Restart your computer for the changes to take effect"
    echo ""
    echo "### Using Custom Resolution Utility (CRU):"
    echo "1. Download and install CRU from https://www.monitortests.com/forum/Thread-Custom-Resolution-Utility-CRU"
    echo "2. Run CRU and select your monitor"
    echo "3. Click 'Import' and select the hdmi0_edid.bin file"
    echo "4. Click 'OK' and restart your computer"
    echo ""
    echo "### Using Monitor Asset Manager:"
    echo "1. Download Monitor Asset Manager"
    echo "2. Use the 'Import EDID' function and select the hdmi0_edid.bin file"
    echo "3. Follow the program's instructions to upload the EDID to your monitor"
    echo ""
    echo "### Using INF File for Driver Installation:"
    echo "1. Copy the K3-3_monitor.inf file to your Windows system"
    echo "2. Right-click on the file and select 'Install'"
    echo "3. Follow the driver installation wizard"
    echo "4. Restart your computer for the changes to take effect"
} > "$WINDOWS_DIR/README.txt"

# Check file sizes
echo "File sizes:"
ls -la "$WINDOWS_DIR"

echo "Windows-compatible EDID files created successfully!"
echo "Files saved to: $WINDOWS_DIR"
echo "See the README.txt file for instructions on how to use these files in Windows." 