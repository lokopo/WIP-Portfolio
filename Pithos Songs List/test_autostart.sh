#!/bin/bash

# Test script for Pithos Song Logger autostart

echo "Testing Pithos Song Logger autostart..."

# Check if autostart entry exists and is properly configured
AUTOSTART_FILE="/home/luke-thomas/.config/autostart/pithos-song-logger-autostart.desktop"

if [ -f "$AUTOSTART_FILE" ]; then
    echo "✓ Autostart file exists at: $AUTOSTART_FILE"
    
    # Check if it's executable
    if [ -x "$AUTOSTART_FILE" ]; then
        echo "✓ Autostart file is executable"
    else
        echo "✗ Autostart file is not executable. Setting executable permissions..."
        chmod +x "$AUTOSTART_FILE"
        echo "  ✓ Fixed: Autostart file is now executable"
    fi
    
    # Check Exec path
    EXEC_PATH=$(grep "^Exec=" "$AUTOSTART_FILE" | cut -d= -f2)
    echo "✓ Exec path: $EXEC_PATH"
    
    # Check if X-GNOME-Autostart-enabled is set to true
    if grep -q "X-GNOME-Autostart-enabled=true" "$AUTOSTART_FILE"; then
        echo "✓ Autostart is enabled"
    else
        echo "✗ Autostart is not enabled. Fixing..."
        sed -i 's/X-GNOME-Autostart-enabled=false/X-GNOME-Autostart-enabled=true/g' "$AUTOSTART_FILE"
        echo "  ✓ Fixed: Autostart is now enabled"
    fi
else
    echo "✗ Autostart file does not exist. Creating it..."
    cat > "$AUTOSTART_FILE" << EOL
[Desktop Entry]
Type=Application
Name=Pithos Song Logger
Comment=Automatically logs and tracks songs playing on Pithos
Exec=/usr/bin/python3 "/home/luke-thomas/Desktop/Projects/Personal/Pithos Songs List/pithos_logger_gui_modern.py"
Terminal=false
Icon=audio-headphones
Categories=AudioVideo;Audio;
StartupNotify=false
X-GNOME-Autostart-enabled=true
Hidden=false
EOL
    chmod +x "$AUTOSTART_FILE"
    echo "  ✓ Fixed: Created autostart file and made it executable"
fi

# Check if the main script exists and is executable
MAIN_SCRIPT="/home/luke-thomas/Desktop/Projects/Personal/Pithos Songs List/pithos_logger_gui_modern.py"

if [ -f "$MAIN_SCRIPT" ]; then
    echo "✓ Main script exists at: $MAIN_SCRIPT"
    
    # Check if it's executable
    if [ -x "$MAIN_SCRIPT" ]; then
        echo "✓ Main script is executable"
    else
        echo "✗ Main script is not executable. Setting executable permissions..."
        chmod +x "$MAIN_SCRIPT"
        echo "  ✓ Fixed: Main script is now executable"
    fi
    
    # Check shebang line
    SHEBANG=$(head -n 1 "$MAIN_SCRIPT")
    if [[ "$SHEBANG" == "#!/usr/bin/env python3" ]]; then
        echo "✓ Main script has correct shebang line"
    else
        echo "✗ Main script has incorrect shebang line. Fixing..."
        sed -i '1s/^.*$/\#!\/usr\/bin\/env python3/' "$MAIN_SCRIPT"
        echo "  ✓ Fixed: Main script now has correct shebang line"
    fi
else
    echo "✗ Main script not found at: $MAIN_SCRIPT"
    echo "  Please check if the path is correct"
fi

# Check if the logger shell script exists and is executable
LOGGER_SCRIPT="/home/luke-thomas/Desktop/Projects/Personal/Pithos Songs List/pithos_song_logger.sh"

if [ -f "$LOGGER_SCRIPT" ]; then
    echo "✓ Logger script exists at: $LOGGER_SCRIPT"
    
    # Check if it's executable
    if [ -x "$LOGGER_SCRIPT" ]; then
        echo "✓ Logger script is executable"
    else
        echo "✗ Logger script is not executable. Setting executable permissions..."
        chmod +x "$LOGGER_SCRIPT"
        echo "  ✓ Fixed: Logger script is now executable"
    fi
else
    echo "✗ Logger script not found at: $LOGGER_SCRIPT"
    echo "  Please check if the path is correct"
fi

echo "All checks complete. Try running the script directly to test:"
echo "python3 \"$MAIN_SCRIPT\""
echo 
echo "To test autostart without restarting:"
echo "dbus-launch --exit-with-session \"$AUTOSTART_FILE\"" 