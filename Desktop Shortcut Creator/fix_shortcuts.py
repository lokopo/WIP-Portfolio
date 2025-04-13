#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse

def create_shortcut(file_path, name, description, categories, terminal=True):
    """
    Create a desktop shortcut with virtual environment activation.
    
    Args:
        file_path (str): Path to the Python script
        name (str): Name of the shortcut
        description (str): Description of the application
        categories (str): Categories for the application
        terminal (bool): Whether to run in terminal
    """
    # Get absolute paths
    file_path = os.path.abspath(file_path)
    working_dir = os.path.dirname(file_path)
    script_name = os.path.basename(file_path)
    
    # Create desktop entry content
    desktop_entry = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={name}",
        f"Exec=bash -c \"cd '{working_dir}' && source venv/bin/activate && python3 '{script_name}'\"",
        f"Comment={description}",
        "Icon=/usr/share/icons/Adwaita/48x48/mimetypes/text-x-python.png",
        f"Terminal={'true' if terminal else 'false'}",
        f"Categories={categories};",
        f"Path={working_dir}",
        "StartupNotify=false"
    ]
    
    # Create the desktop file
    desktop_file = f"{name.lower().replace(' ', '-')}.desktop"
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Not working", desktop_file)
    
    # Ensure the Not working directory exists
    os.makedirs(os.path.dirname(desktop_path), exist_ok=True)
    
    # Write the desktop file
    with open(desktop_path, 'w') as f:
        f.write('\n'.join(desktop_entry))
    
    # Make it executable
    os.chmod(desktop_path, 0o755)
    
    print(f"Created shortcut: {desktop_path}")

def main():
    parser = argparse.ArgumentParser(description='Create desktop shortcuts with virtual environment activation')
    parser.add_argument('--file', required=True, help='Path to the Python script')
    parser.add_argument('--name', required=True, help='Name of the shortcut')
    parser.add_argument('--description', required=True, help='Description of the application')
    parser.add_argument('--categories', required=True, help='Categories for the application')
    parser.add_argument('--terminal', action='store_true', help='Run in terminal')
    
    args = parser.parse_args()
    
    create_shortcut(
        args.file,
        args.name,
        args.description,
        args.categories,
        args.terminal
    )

if __name__ == '__main__':
    main() 