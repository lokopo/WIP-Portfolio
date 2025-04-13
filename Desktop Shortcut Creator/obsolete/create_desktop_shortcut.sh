#!/bin/bash

# Get the script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create .desktop file for our shortcut creator
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

# Create symlink on desktop
ln -sf ~/.local/share/applications/desktop-shortcut-creator.desktop ~/Desktop/desktop-shortcut-creator.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications

echo "Desktop shortcut created successfully!"
echo "You can now launch Desktop Shortcut Creator from your applications menu or desktop." 