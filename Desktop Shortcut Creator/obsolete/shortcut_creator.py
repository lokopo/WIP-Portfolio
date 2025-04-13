#!/usr/bin/env python3

import os
import argparse
import subprocess
from pathlib import Path


class DesktopShortcutCreator:
    """
    A utility for creating desktop shortcuts on Linux systems.
    """

    def __init__(self):
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.applications_path = os.path.join(os.path.expanduser("~"), ".local/share/applications")
        
        # Ensure the applications directory exists
        os.makedirs(self.applications_path, exist_ok=True)

    def create_shortcut(self, name, executable_path, icon_path=None, description=None, 
                         terminal=False, categories=None, working_dir=None):
        """
        Create a desktop shortcut for the specified application.
        
        Args:
            name (str): Name of the shortcut/application
            executable_path (str): Path to the executable
            icon_path (str, optional): Path to the icon file
            description (str, optional): Description for the application
            terminal (bool, optional): Whether the application runs in terminal
            categories (list, optional): List of application categories
            working_dir (str, optional): Working directory for the application
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Convert to absolute paths
        executable_path = os.path.abspath(executable_path)
        if icon_path:
            icon_path = os.path.abspath(icon_path)
        if working_dir:
            working_dir = os.path.abspath(working_dir)
        else:
            working_dir = os.path.dirname(executable_path)

        # Create desktop entry file content
        desktop_entry = [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={name}",
            f"Exec={executable_path}",
        ]
        
        if description:
            desktop_entry.append(f"Comment={description}")
        
        if icon_path:
            desktop_entry.append(f"Icon={icon_path}")
        
        desktop_entry.append(f"Terminal={'true' if terminal else 'false'}")
        
        if categories:
            desktop_entry.append(f"Categories={';'.join(categories)};")
        
        desktop_entry.append(f"Path={working_dir}")
        desktop_entry.append("StartupNotify=true")
        
        # Write to .desktop file in ~/.local/share/applications
        file_name = f"{name.lower().replace(' ', '-')}.desktop"
        application_file_path = os.path.join(self.applications_path, file_name)
        desktop_file_path = os.path.join(self.desktop_path, file_name)
        
        try:
            with open(application_file_path, 'w') as f:
                f.write('\n'.join(desktop_entry))
            
            # Make executable
            os.chmod(application_file_path, 0o755)
            
            # Create symlink on Desktop
            if os.path.exists(desktop_file_path):
                os.remove(desktop_file_path)
            os.symlink(application_file_path, desktop_file_path)
            
            # Update desktop database
            subprocess.run(['update-desktop-database', self.applications_path], 
                          check=True, stderr=subprocess.PIPE)
            
            print(f"Desktop shortcut created successfully: {desktop_file_path}")
            return True
            
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Create desktop shortcuts for applications')
    parser.add_argument('--name', '-n', required=True, help='Name of the application')
    parser.add_argument('--exec', '-e', required=True, help='Path to the executable')
    parser.add_argument('--icon', '-i', help='Path to the icon file')
    parser.add_argument('--desc', '-d', help='Description of the application')
    parser.add_argument('--terminal', '-t', action='store_true', help='Run in terminal')
    parser.add_argument('--categories', '-c', help='Categories (comma-separated)')
    parser.add_argument('--working-dir', '-w', help='Working directory')
    
    args = parser.parse_args()
    
    categories = args.categories.split(',') if args.categories else None
    
    creator = DesktopShortcutCreator()
    creator.create_shortcut(
        name=args.name,
        executable_path=args.exec,
        icon_path=args.icon,
        description=args.desc,
        terminal=args.terminal,
        categories=categories,
        working_dir=args.working_dir
    )


if __name__ == "__main__":
    main() 