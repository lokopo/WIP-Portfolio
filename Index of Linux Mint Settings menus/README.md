# Mint Settings & Utilities Browser

A comprehensive, searchable GUI application that provides access to all Linux Mint settings and utilities in one place, similar to Windows' "God Mode" folder.

## Features

- Indexes all Cinnamon settings modules
- Includes other system settings applications
- Includes common Linux Mint utilities (Update Manager, Software Manager, etc.)
- Includes system administration tools
- Searchable interface with instant filtering
- Shows descriptions and icons
- Simple double-click to launch any setting or utility
- Categorizes entries by type (Setting, Utility, System Tool, Specific Setting)
- Sortable columns

## Requirements

- Python 3
- GTK 3
- Linux Mint Cinnamon desktop environment

## Installation

1. Clone or download this repository
2. Make the script executable: `chmod +x mint_settings_browser.py`
3. Optional: Copy the desktop file to your applications directory:
   ```
   cp mint-settings-browser.desktop ~/.local/share/applications/
   ```

## Usage

You can launch the application in one of these ways:

- From the terminal: `./mint_settings_browser.py`
- If you installed the desktop file, find "Mint Settings & Utilities Browser" in your applications menu
- From the desktop shortcut if you've created one

### Search Examples

The enhanced search allows you to find specific settings using related terms:

- Search for "update" to find the Update Manager and related tools
- Search for "mouse" to find not only the Mouse settings but also the Window Focus Mode (since it's related to mouse behavior)
- Search for "security" to find firewall tools, password settings, and more

## How It Works

The application scans multiple sources:

1. Cinnamon settings modules directory
2. System applications directory
3. Common Linux Mint utilities (Update Manager, Driver Manager, etc.)
4. System administration tools

It extracts information from .desktop files to display useful descriptions and icons, and enriches entries with keywords for better searchability.

When you double-click an entry, it launches the appropriate command to open that specific setting or utility.

## License

This software is released under the MIT License. 