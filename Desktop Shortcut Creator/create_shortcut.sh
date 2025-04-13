#!/bin/bash

# Get the script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create .desktop file for our shortcut creator
echo "Creating application entry in the applications menu..."
cat > ~/.local/share/applications/desktop-shortcut-creator.desktop << EOL
[Desktop Entry]
Type=Application
Name=Desktop Shortcut Creator
Comment=Create desktop shortcuts for any file or application
Exec=${DIR}/run_shortcut_creator.sh
Icon=/usr/share/icons/hicolor/48x48/apps/system-software-install.png
Terminal=false
Categories=Utility;Development;
StartupNotify=true
EOL

# Make it executable
chmod +x ~/.local/share/applications/desktop-shortcut-creator.desktop

# Create a direct copy on the desktop (not a symlink)
echo "Creating desktop icon without shortcut symbol..."
cat > ~/Desktop/desktop-shortcut-creator.desktop << EOL
[Desktop Entry]
Type=Application
Name=Desktop Shortcut Creator
Comment=Create desktop shortcuts for any file or application
Exec=${DIR}/run_shortcut_creator.sh
Icon=/usr/share/icons/hicolor/48x48/apps/system-software-install.png
Terminal=false
Categories=Utility;Development;
StartupNotify=true
EOL

# Make the desktop file executable
chmod +x ~/Desktop/desktop-shortcut-creator.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications

# Try to install required dependencies directly
echo "Installing required dependencies to ensure the app works correctly..."
sudo apt-get update
sudo apt-get install -y python3-pyqt6 python3-magic python3-pil python3-pil.imagetk libmagic1

echo "Desktop shortcut created successfully!"
echo "You can now launch Desktop Shortcut Creator from your applications menu or desktop."
echo "Note: The desktop icon doesn't have the shortcut symbol anymore." 