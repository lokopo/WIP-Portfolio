#!/usr/bin/env python3

import os
import sys
import subprocess
import mimetypes
from pathlib import Path

# Try to import optional dependencies with fallbacks
try:
    import magic
except ImportError:
    print("Warning: python-magic not found. Using mimetypes only for file detection.")
    magic = None

try:
    from PIL import Image
except ImportError:
    print("Warning: Pillow not found. Icon preview will be disabled.")
    Image = None

# Import PyQt6
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                QFileDialog, QCheckBox, QGroupBox, QMessageBox,
                                QStatusBar, QFormLayout)
    from PyQt6.QtGui import QIcon, QPixmap, QDragEnterEvent, QDropEvent
    from PyQt6.QtCore import Qt, QMimeData
    HAS_PYQT = True
except ImportError:
    print("Error: PyQt6 is required for this application.")
    print("Please install it with: sudo apt-get install python3-pyqt6")
    print("Attempting to install dependencies automatically...")
    try:
        subprocess.run(['sudo', 'apt-get', 'update', '-q'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-pyqt6', 
                      'python3-magic', 'python3-pil', 'python3-pil.imagetk'], check=True)
        print("Dependencies installed. Please restart the application.")
    except Exception as e:
        print(f"Failed to install dependencies: {e}")
    sys.exit(1)


class FileTypeDetector:
    """
    Detects file types and suggests appropriate shortcut configurations.
    """
    def __init__(self):
        self.mime = magic.Magic(mime=True) if magic else None
        mimetypes.init()
        
        # Common system icons
        self.system_icons = {
            'executable': '/usr/share/icons/Adwaita/48x48/mimetypes/application-x-executable.png',
            'python': '/usr/share/icons/Adwaita/48x48/mimetypes/text-x-python.png',
            'shell': '/usr/share/icons/Adwaita/48x48/mimetypes/text-x-script.png',
            'text': '/usr/share/icons/Adwaita/48x48/mimetypes/text-x-generic.png',
            'folder': '/usr/share/icons/Adwaita/48x48/places/folder.png',
            'image': '/usr/share/icons/Adwaita/48x48/mimetypes/image-x-generic.png',
            'audio': '/usr/share/icons/Adwaita/48x48/mimetypes/audio-x-generic.png',
            'video': '/usr/share/icons/Adwaita/48x48/mimetypes/video-x-generic.png',
            'pdf': '/usr/share/icons/Adwaita/48x48/mimetypes/application-pdf.png',
            'archive': '/usr/share/icons/Adwaita/48x48/mimetypes/package-x-generic.png',
            'default': '/usr/share/icons/Adwaita/48x48/mimetypes/application-x-executable.png'
        }
        
        # Make sure at least one icon exists, or fallback to a likely existing one
        icon_found = False
        for icon_type, path in self.system_icons.items():
            if os.path.exists(path):
                icon_found = True
                break
        
        if not icon_found:
            # Try to find any icon that exists as fallback
            for possible_path in [
                '/usr/share/icons/hicolor/48x48/apps/system-software-install.png',
                '/usr/share/icons/hicolor/48x48/apps/application-default-icon.png',
                '/usr/share/icons/hicolor/scalable/apps/application-default-icon.svg'
            ]:
                if os.path.exists(possible_path):
                    for key in self.system_icons:
                        self.system_icons[key] = possible_path
                    break
        
        # Category mappings
        self.category_map = {
            'text': ['Utility', 'TextEditor'],
            'image': ['Graphics'],
            'audio': ['Audio', 'AudioVideo'],
            'video': ['Video', 'AudioVideo'],
            'archive': ['Utility', 'Archiving'],
            'executable': ['Application'],
            'python': ['Development'],
            'folder': ['System', 'FileManager'],
            'pdf': ['Office', 'Viewer'],
        }

    def get_suggested_config(self, file_path):
        """
        Analyze file path and return suggested shortcut configuration.
        
        Returns:
            dict: Suggested configuration for the shortcut
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                'name': path.stem,
                'terminal': False,
                'icon': self.system_icons['default'],
                'description': 'Unknown file type',
                'categories': ['Utility']
            }
        
        # Default values
        config = {
            'name': path.stem,
            'terminal': False,
            'icon': self.system_icons['default'],
            'description': f'Shortcut to {path.name}',
            'categories': ['Utility']
        }
        
        # Check if it's a directory
        if path.is_dir():
            config['name'] = path.name
            config['icon'] = self.system_icons['folder']
            config['description'] = f'Open {path.name} folder'
            config['terminal'] = False
            config['categories'] = self.category_map['folder']
            # Use file manager to open folders
            config['executable'] = f"xdg-open '{file_path}'"
            return config
        
        # Get mime type
        mime_type = None
        try:
            if self.mime:
                mime_type = self.mime.from_file(str(path))
            else:
                mime_type = mimetypes.guess_type(str(path))[0]
        except Exception:
            mime_type = mimetypes.guess_type(str(path))[0]
        
        # Check if it's executable
        is_executable = os.access(file_path, os.X_OK)
        
        # Handle by extension
        extension = path.suffix.lower()
        
        # Python scripts
        if extension == '.py':
            config['terminal'] = True
            config['icon'] = self.system_icons['python']
            config['description'] = f'Python script: {path.name}'
            config['categories'] = self.category_map['python']
            
            # Check if it's a GUI script by looking for tkinter or PyQt imports
            try:
                with open(file_path, 'r') as f:
                    content = f.read().lower()
                    if 'tkinter' in content or 'pyqt' in content or 'pyside' in content or 'wx' in content:
                        config['terminal'] = False
            except:
                pass
            
            if is_executable:
                config['executable'] = f"'{file_path}'"
            else:
                config['executable'] = f"python3 '{file_path}'"
        
        # Shell scripts
        elif extension in ['.sh', '.bash']:
            config['terminal'] = True
            config['icon'] = self.system_icons['shell']
            config['description'] = f'Shell script: {path.name}'
            config['categories'] = ['System', 'TerminalEmulator']
            
            if is_executable:
                config['executable'] = f"'{file_path}'"
            else:
                config['executable'] = f"bash '{file_path}'"
        
        # Binary executables
        elif is_executable or (mime_type and 'executable' in str(mime_type).lower()):
            config['icon'] = self.system_icons['executable']
            config['description'] = f'Application: {path.name}'
            config['terminal'] = False
            config['categories'] = self.category_map['executable']
            config['executable'] = f"'{file_path}'"
            
            # Try to get icon from the executable itself
            try:
                # Check common desktop entry locations
                app_name = path.stem.lower()
                for icon_path in [
                    f"/usr/share/icons/hicolor/48x48/apps/{app_name}.png",
                    f"/usr/share/pixmaps/{app_name}.png",
                    f"/usr/share/icons/hicolor/128x128/apps/{app_name}.png"
                ]:
                    if os.path.exists(icon_path):
                        config['icon'] = icon_path
                        break
            except:
                pass
                
        # Handle by mime type
        elif mime_type:
            mime_cat = mime_type.split('/')[0]
            
            if mime_cat == 'text':
                config['icon'] = self.system_icons['text']
                config['categories'] = self.category_map['text']
                config['executable'] = f"xdg-open '{file_path}'"
                
            elif mime_cat == 'image':
                config['icon'] = self.system_icons['image']
                config['categories'] = self.category_map['image']
                config['executable'] = f"xdg-open '{file_path}'"
                
                # Use the image itself as an icon if small enough
                if os.path.getsize(file_path) < 1024 * 1024:  # 1MB max
                    config['icon'] = file_path
                
            elif mime_cat == 'audio':
                config['icon'] = self.system_icons['audio']
                config['categories'] = self.category_map['audio']
                config['executable'] = f"xdg-open '{file_path}'"
                
            elif mime_cat == 'video':
                config['icon'] = self.system_icons['video']
                config['categories'] = self.category_map['video']
                config['executable'] = f"xdg-open '{file_path}'"
                
            elif 'pdf' in mime_type:
                config['icon'] = self.system_icons['pdf']
                config['categories'] = self.category_map['pdf']
                config['executable'] = f"xdg-open '{file_path}'"
                
            elif 'zip' in mime_type or 'tar' in mime_type or 'compress' in mime_type:
                config['icon'] = self.system_icons['archive']
                config['categories'] = self.category_map['archive']
                config['executable'] = f"xdg-open '{file_path}'"
            
            else:
                # Default to opening with system default app
                config['executable'] = f"xdg-open '{file_path}'"
        
        else:
            # Default to opening with system default app
            config['executable'] = f"xdg-open '{file_path}'"
        
        return config


class DesktopShortcutCreator:
    """
    A utility for creating desktop shortcuts on Linux systems.
    """

    def __init__(self):
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.applications_path = os.path.join(os.path.expanduser("~"), ".local/share/applications")
        
        # Ensure the applications directory exists
        os.makedirs(self.applications_path, exist_ok=True)

    def create_shortcut(self, name, executable, icon_path=None, description=None, 
                        terminal=False, categories=None, working_dir=None, use_symlink=False):
        """
        Create a desktop shortcut for the specified application.
        
        Args:
            name (str): Name of the shortcut/application
            executable (str): Command to execute
            icon_path (str, optional): Path to the icon file
            description (str, optional): Description for the application
            terminal (bool, optional): Whether the application runs in terminal
            categories (list, optional): List of application categories
            working_dir (str, optional): Working directory for the application
            use_symlink (bool, optional): Whether to create a symlink (with shortcut icon) 
                                        or direct .desktop file (no shortcut icon)
        
        Returns:
            tuple: (success, result_message)
        """
        # Handle working directory
        if working_dir:
            working_dir = os.path.abspath(working_dir)
        elif ' ' in executable and "'" in executable:
            # Extract path from executable command if it's a file path
            path_match = executable.split("'")[1]
            if os.path.exists(path_match):
                working_dir = os.path.dirname(path_match)
        
        # Create desktop entry file content
        desktop_entry = [
            "[Desktop Entry]",
            "Type=Application",
            f"Name={name}",
            f"Exec={executable}",
        ]
        
        if description:
            desktop_entry.append(f"Comment={description}")
        
        if icon_path:
            desktop_entry.append(f"Icon={icon_path}")
        
        desktop_entry.append(f"Terminal={'true' if terminal else 'false'}")
        
        if categories:
            desktop_entry.append(f"Categories={';'.join(categories)};")
        
        if working_dir:
            desktop_entry.append(f"Path={working_dir}")
            
        desktop_entry.append("StartupNotify=true")
        
        # File name for the desktop shortcut
        file_name = f"{name.lower().replace(' ', '-')}.desktop"
        application_file_path = os.path.join(self.applications_path, file_name)
        desktop_file_path = os.path.join(self.desktop_path, file_name)
        
        try:
            # Create the .desktop file in the applications directory
            with open(application_file_path, 'w') as f:
                f.write('\n'.join(desktop_entry))
            
            # Make executable
            os.chmod(application_file_path, 0o755)
            
            # Create desktop shortcut (symlink or direct file)
            if use_symlink:
                # Create symlink on Desktop (will show shortcut icon)
                if os.path.exists(desktop_file_path):
                    os.remove(desktop_file_path)
                os.symlink(application_file_path, desktop_file_path)
            else:
                # Create direct .desktop file (no shortcut icon)
                with open(desktop_file_path, 'w') as f:
                    f.write('\n'.join(desktop_entry))
                os.chmod(desktop_file_path, 0o755)
            
            # Update desktop database
            subprocess.run(['update-desktop-database', self.applications_path], 
                           check=True, stderr=subprocess.PIPE)
            
            return True, desktop_file_path
            
        except Exception as e:
            return False, str(e)


class FileDropWidget(QWidget):
    """Widget that accepts drag and drop file operations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        # Create a layout for this widget
        self.layout = QVBoxLayout(self)
        
        # Create a label to instruct users
        self.label = QLabel("Drop a file or folder here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed #aaa; padding: 25px; border-radius: 5px;")
        
        self.layout.addWidget(self.label)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        mime_data = event.mimeData()
        if mime_data.hasUrls() and len(mime_data.urls()) == 1:
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        mime_data = event.mimeData()
        if mime_data.hasUrls() and len(mime_data.urls()) == 1:
            file_path = mime_data.urls()[0].toLocalFile()
            self.parent().set_file(file_path)
            event.acceptProposedAction()


class ShortcutCreatorWindow(QMainWindow):
    """Main window for the shortcut creator application"""
    
    def __init__(self):
        super().__init__()
        
        # Set up the window
        self.setWindowTitle("Desktop Shortcut Creator")
        self.setMinimumSize(600, 500)
        
        # Set window icon
        app_icon = '/usr/share/icons/hicolor/48x48/apps/system-software-install.png'
        if os.path.exists(app_icon):
            self.setWindowIcon(QIcon(app_icon))
        
        # Initialize components
        self.detector = FileTypeDetector()
        self.creator = DesktopShortcutCreator()
        self.selected_file = None
        
        # Create the central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Add the file selection section
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Add file path input and browse button
        file_input_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Path to file or folder...")
        self.file_path_input.textChanged.connect(self.update_file_path)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        
        file_input_layout.addWidget(self.file_path_input)
        file_input_layout.addWidget(browse_button)
        
        # Add drag and drop area
        self.drop_area = FileDropWidget(self)
        
        file_layout.addLayout(file_input_layout)
        file_layout.addWidget(self.drop_area)
        
        # Add the shortcut details section
        details_group = QGroupBox("Shortcut Details")
        details_layout = QFormLayout(details_group)
        
        # Name field
        self.name_input = QLineEdit()
        details_layout.addRow("Name:", self.name_input)
        
        # Icon field and preview
        icon_layout = QHBoxLayout()
        self.icon_input = QLineEdit()
        browse_icon_button = QPushButton("Browse...")
        browse_icon_button.clicked.connect(self.browse_icon)
        icon_layout.addWidget(self.icon_input)
        icon_layout.addWidget(browse_icon_button)
        
        details_layout.addRow("Icon:", icon_layout)
        
        # Icon preview
        icon_preview_layout = QHBoxLayout()
        self.icon_preview = QLabel()
        self.icon_preview.setFixedSize(48, 48)
        self.icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_preview_layout.addWidget(self.icon_preview)
        icon_preview_layout.addStretch()
        
        details_layout.addRow("Preview:", icon_preview_layout)
        
        # Description field
        self.description_input = QLineEdit()
        details_layout.addRow("Description:", self.description_input)
        
        # Terminal checkbox
        self.terminal_checkbox = QCheckBox("Run in Terminal")
        details_layout.addRow("Options:", self.terminal_checkbox)
        
        # Add symlink checkbox
        self.symlink_checkbox = QCheckBox("Create as symlink (with shortcut symbol)")
        self.symlink_checkbox.setChecked(False)
        self.symlink_checkbox.setToolTip("When unchecked, creates a direct .desktop file without the shortcut symbol")
        details_layout.addRow("Shortcut style:", self.symlink_checkbox)
        
        # Categories field
        self.categories_input = QLineEdit()
        details_layout.addRow("Categories:", self.categories_input)
        
        # Command field
        self.command_input = QLineEdit()
        details_layout.addRow("Command:", self.command_input)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_form)
        
        self.create_button = QPushButton("Create Shortcut")
        self.create_button.clicked.connect(self.create_shortcut)
        self.create_button.setStyleSheet("font-weight: bold;")
        
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.create_button)
        
        # Add all sections to the main layout
        main_layout.addWidget(file_group)
        main_layout.addWidget(details_group)
        main_layout.addLayout(button_layout)
        
        # Set the central widget
        self.setCentralWidget(central_widget)
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready to create shortcuts")
        
        # Initialize the form
        self.reset_form()
        
        # Check for missing dependencies
        self.check_dependencies()
    
    def check_dependencies(self):
        """Check for missing dependencies and show warnings if needed"""
        missing_deps = []
        if magic is None:
            missing_deps.append("python-magic")
        if Image is None:
            missing_deps.append("Pillow")
        
        if missing_deps:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Missing Dependencies")
            msg.setText("Some features may be limited")
            msg.setInformativeText("The following dependencies are missing:\n" + 
                                  "\n".join([f"- {dep}" for dep in missing_deps]))
            msg.exec()
    
    def set_file(self, file_path):
        """Set the selected file and update the form"""
        self.file_path_input.setText(file_path)
    
    def update_file_path(self, file_path):
        """Handle updates to the file path input"""
        self.selected_file = file_path
        if os.path.exists(file_path):
            self.detect_file_type()
    
    def browse_file(self):
        """Open file dialog to select a file or folder"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*)"
        )
        
        if file_path:
            self.set_file(file_path)
    
    def browse_icon(self):
        """Open file dialog to select an icon"""
        icon_path, _ = QFileDialog.getOpenFileName(
            self, "Select Icon", "", "Image Files (*.png *.jpg *.jpeg *.ico *.svg)"
        )
        
        if icon_path:
            self.icon_input.setText(icon_path)
            self.update_icon_preview(icon_path)
    
    def update_icon_preview(self, icon_path):
        """Update the icon preview"""
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
                self.icon_preview.setPixmap(pixmap)
                return
            
        # Clear the preview if the icon couldn't be loaded
        self.icon_preview.clear()
    
    def detect_file_type(self):
        """Detect file type and set suggested values"""
        if not self.selected_file or not os.path.exists(self.selected_file):
            self.statusBar.showMessage("Please select a valid file or folder")
            return
        
        # Get suggested configuration
        config = self.detector.get_suggested_config(self.selected_file)
        
        # Update the form with suggested values
        self.name_input.setText(config['name'])
        self.description_input.setText(config['description'])
        self.icon_input.setText(config['icon'])
        self.terminal_checkbox.setChecked(config['terminal'])
        self.categories_input.setText(', '.join(config['categories']))
        self.command_input.setText(config.get('executable', f"'{self.selected_file}'"))
        
        # Update icon preview
        self.update_icon_preview(config['icon'])
        
        self.statusBar.showMessage(f"Detected {os.path.basename(self.selected_file)}")
    
    def create_shortcut(self):
        """Create the shortcut with the current settings"""
        if not self.selected_file or not os.path.exists(self.selected_file):
            QMessageBox.critical(self, "Error", "Please select a valid file or folder")
            return
        
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.critical(self, "Error", "Please enter a name for the shortcut")
            return
        
        # Get values from form
        icon_path = self.icon_input.text().strip()
        description = self.description_input.text().strip()
        terminal = self.terminal_checkbox.isChecked()
        use_symlink = self.symlink_checkbox.isChecked()
        
        # Handle categories
        categories_text = self.categories_input.text().strip()
        categories = [cat.strip() for cat in categories_text.split(',')] if categories_text else None
        
        # Get command
        command = self.command_input.text().strip()
        if not command:
            QMessageBox.critical(self, "Error", "Please enter a command to execute")
            return
        
        # Create the shortcut
        success, result = self.creator.create_shortcut(
            name=name,
            executable=command,
            icon_path=icon_path if icon_path else None,
            description=description if description else None,
            terminal=terminal,
            categories=categories,
            use_symlink=use_symlink
        )
        
        if success:
            shortcut_type = "symlink" if use_symlink else "direct .desktop file"
            self.statusBar.showMessage(f"Shortcut created as {shortcut_type}: {result}")
            QMessageBox.information(self, "Success", 
                                  f"Shortcut created successfully as {shortcut_type}:\n{result}")
        else:
            self.statusBar.showMessage(f"Error: {result}")
            QMessageBox.critical(self, "Error", f"Failed to create shortcut:\n{result}")
    
    def reset_form(self):
        """Reset all form fields"""
        self.file_path_input.clear()
        self.name_input.clear()
        self.icon_input.clear()
        self.description_input.clear()
        self.terminal_checkbox.setChecked(False)
        self.symlink_checkbox.setChecked(False)
        self.categories_input.clear()
        self.command_input.clear()
        self.icon_preview.clear()
        self.selected_file = None
        self.statusBar.showMessage("Form reset. Please select a file or folder.")


def main():
    # If there's a direct file argument, create a shortcut for it immediately
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        try:
            file_path = os.path.abspath(sys.argv[1])
            print(f"Creating shortcut for: {file_path}")
            
            creator = DesktopShortcutCreator()
            detector = FileTypeDetector()
            
            # Get suggested configuration
            config = detector.get_suggested_config(file_path)
            
            # Create the shortcut
            success, result = creator.create_shortcut(
                name=config['name'],
                executable=config.get('executable', f"'{file_path}'"),
                icon_path=config['icon'],
                description=config['description'],
                terminal=config['terminal'],
                categories=config['categories'],
                use_symlink=False
            )
            
            if success:
                print(f"Shortcut created successfully: {result}")
                return 0
            else:
                print(f"Error creating shortcut: {result}")
                return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    # Check for CLI mode
    elif len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # CLI mode
        try:
            from shortcut_creator import main as cli_main
            cli_main()
        except ImportError:
            print("CLI version not available. Using GUI version.")
        
        return
    
    try:
        # Create the application
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show the main window
        window = ShortcutCreatorWindow()
        window.show()
        
        # Run the application event loop
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting the application: {e}")
        print("This might be due to missing dependencies. Try running:")
        print("sudo apt-get install -y python3-pyqt6 python3-magic python3-pil python3-pil.imagetk libmagic1")
        sys.exit(1)


if __name__ == "__main__":
    main() 