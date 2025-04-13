#!/usr/bin/env python3

import os
import sys
import subprocess
import mimetypes
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Try to import optional dependencies with fallbacks
try:
    import magic
except ImportError:
    print("Warning: python-magic not found. Using mimetypes only for file detection.")
    magic = None

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Warning: Pillow not found. Icon preview will be disabled.")
    Image = None
    ImageTk = None

# Flag to track if drag and drop is available
HAS_DND = False

# Try to import TkinterDnD for drag and drop support
try:
    from tkinterdnd2 import TkinterDnD
    HAS_DND = True
except ImportError:
    print("Note: Install tkinterdnd2 for drag-and-drop support")
    TkinterDnD = None


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
        elif is_executable or 'executable' in str(mime_type).lower():
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
                        terminal=False, categories=None, working_dir=None):
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
        
        Returns:
            bool: True if successful, False otherwise
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
            
            return True, desktop_file_path
            
        except Exception as e:
            return False, str(e)


class ShortcutCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop Shortcut Creator")
        self.root.geometry("600x520")
        self.root.resizable(True, True)
        
        # Set window icon
        try:
            icon_path = "/usr/share/icons/hicolor/48x48/apps/system-software-install.png"
            if os.path.exists(icon_path):
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except:
            pass
        
        # Initialize detector and creator
        self.detector = FileTypeDetector()
        self.creator = DesktopShortcutCreator()
        
        self.selected_file = None
        self.icon_preview_image = None
        
        # Create a frame with padding
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a style
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12))
        style.configure('TLabel', font=('Arial', 12))
        style.configure('TCheckbutton', font=('Arial', 12))
        style.configure('TEntry', font=('Arial', 12))
        
        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Select File or Folder:").pack(side=tk.LEFT, padx=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.browse_button = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        # Enable drag and drop if available
        if HAS_DND:
            self.file_entry.drop_target_register(tk.DND_FILES)
            self.file_entry.dnd_bind('<<Drop>>', self.drop)
        
        # Shortcut details frame
        details_frame = ttk.LabelFrame(main_frame, text="Shortcut Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Name
        name_frame = ttk.Frame(details_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Name:").pack(side=tk.LEFT, padx=5)
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Icon
        icon_frame = ttk.Frame(details_frame)
        icon_frame.pack(fill=tk.X, pady=5)
        ttk.Label(icon_frame, text="Icon:").pack(side=tk.LEFT, padx=5)
        self.icon_var = tk.StringVar()
        ttk.Entry(icon_frame, textvariable=self.icon_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(icon_frame, text="Browse", command=self.browse_icon).pack(side=tk.LEFT, padx=5)
        
        # Icon preview
        self.icon_preview = ttk.Label(details_frame)
        self.icon_preview.pack(pady=10)
        
        # Description
        desc_frame = ttk.Frame(details_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        ttk.Label(desc_frame, text="Description:").pack(side=tk.LEFT, padx=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(desc_frame, textvariable=self.desc_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Terminal checkbox
        term_frame = ttk.Frame(details_frame)
        term_frame.pack(fill=tk.X, pady=5)
        self.terminal_var = tk.BooleanVar()
        ttk.Checkbutton(term_frame, text="Run in Terminal", variable=self.terminal_var).pack(side=tk.LEFT, padx=5)
        
        # Categories
        cat_frame = ttk.Frame(details_frame)
        cat_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cat_frame, text="Categories:").pack(side=tk.LEFT, padx=5)
        self.categories_var = tk.StringVar()
        ttk.Entry(cat_frame, textvariable=self.categories_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Command
        cmd_frame = ttk.Frame(details_frame)
        cmd_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cmd_frame, text="Command:").pack(side=tk.LEFT, padx=5)
        self.command_var = tk.StringVar()
        ttk.Entry(cmd_frame, textvariable=self.command_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.create_button = ttk.Button(button_frame, text="Create Shortcut", command=self.create_shortcut)
        self.create_button.pack(side=tk.RIGHT, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_form)
        self.reset_button.pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to create shortcuts")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set up drag and drop support for the whole window if available
        if HAS_DND:
            self.root.drop_target_register(tk.DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.drop)
        
        # Initialize the UI
        self.reset_form()
        
        # If there are dependency issues, display a warning
        missing_deps = []
        if magic is None:
            missing_deps.append("python-magic")
        if Image is None:
            missing_deps.append("Pillow")
        if not HAS_DND:
            missing_deps.append("tkinterdnd2")
        
        if missing_deps:
            msg = "Some features may be limited. Missing dependencies:\n"
            msg += "\n".join([f"- {dep}" for dep in missing_deps])
            messagebox.showwarning("Missing Dependencies", msg)
    
    def drop(self, event):
        """Handle drag and drop events"""
        if not HAS_DND:
            return
            
        file_path = event.data
        
        # Clean up the file path (remove braces and quotes)
        file_path = file_path.strip('{}')
        if file_path.startswith('"') and file_path.endswith('"'):
            file_path = file_path[1:-1]
        
        self.file_path_var.set(file_path)
        self.selected_file = file_path
        self.detect_file_type()
    
    def browse_file(self):
        """Open file dialog to select file or folder"""
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("All Files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.selected_file = file_path
            self.detect_file_type()
    
    def browse_icon(self):
        """Open file dialog to select an icon"""
        icon_path = filedialog.askopenfilename(
            title="Select an icon",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.ico *.svg")]
        )
        
        if icon_path:
            self.icon_var.set(icon_path)
            self.update_icon_preview(icon_path)
    
    def update_icon_preview(self, icon_path):
        """Update the icon preview"""
        if not os.path.exists(icon_path) or Image is None:
            return
        
        try:
            img = Image.open(icon_path)
            img = img.resize((48, 48), Image.LANCZOS)
            self.icon_preview_image = ImageTk.PhotoImage(img)
            self.icon_preview.config(image=self.icon_preview_image)
        except Exception as e:
            print(f"Error loading icon: {e}")
    
    def detect_file_type(self):
        """Detect file type and set default values"""
        if not self.selected_file or not os.path.exists(self.selected_file):
            self.status_var.set("Please select a valid file or folder")
            return
        
        # Get suggested configuration
        config = self.detector.get_suggested_config(self.selected_file)
        
        # Update UI with detected values
        self.name_var.set(config['name'])
        self.desc_var.set(config['description'])
        self.icon_var.set(config['icon'])
        self.terminal_var.set(config['terminal'])
        self.categories_var.set(', '.join(config['categories']))
        self.command_var.set(config.get('executable', f"'{self.selected_file}'"))
        
        # Update icon preview
        self.update_icon_preview(config['icon'])
        
        self.status_var.set(f"Detected {os.path.basename(self.selected_file)}")
    
    def create_shortcut(self):
        """Create the shortcut with the current settings"""
        if not self.selected_file or not os.path.exists(self.selected_file):
            messagebox.showerror("Error", "Please select a valid file or folder")
            return
        
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name for the shortcut")
            return
        
        # Get values from form
        icon_path = self.icon_var.get().strip()
        description = self.desc_var.get().strip()
        terminal = self.terminal_var.get()
        
        # Handle categories
        categories_text = self.categories_var.get().strip()
        categories = [cat.strip() for cat in categories_text.split(',')] if categories_text else None
        
        # Get command
        command = self.command_var.get().strip()
        if not command:
            messagebox.showerror("Error", "Please enter a command to execute")
            return
        
        # Create the shortcut
        success, result = self.creator.create_shortcut(
            name=name,
            executable=command,
            icon_path=icon_path if icon_path else None,
            description=description if description else None,
            terminal=terminal,
            categories=categories
        )
        
        if success:
            self.status_var.set(f"Shortcut created: {result}")
            messagebox.showinfo("Success", f"Shortcut created successfully:\n{result}")
        else:
            self.status_var.set(f"Error: {result}")
            messagebox.showerror("Error", f"Failed to create shortcut:\n{result}")
    
    def reset_form(self):
        """Reset all form fields"""
        self.file_path_var.set("")
        self.name_var.set("")
        self.icon_var.set("")
        self.desc_var.set("")
        self.terminal_var.set(False)
        self.categories_var.set("")
        self.command_var.set("")
        self.icon_preview.config(image='')
        self.icon_preview_image = None
        self.selected_file = None
        self.status_var.set("Form reset. Please select a file or folder.")


def main():
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] != '--gui':
        # Use the CLI version for compatibility
        try:
            from shortcut_creator import main as cli_main
            cli_main()
        except ImportError:
            print("CLI version not available. Using GUI version.")
            # Continue with GUI
        return
    
    # Set up Tkinter
    root = tk.Tk()
    
    # Try to use TkinterDnD for drag and drop if available
    if HAS_DND:
        root = TkinterDnD.Tk()
    
    # Create application
    app = ShortcutCreatorGUI(root)
    
    # Run application
    root.mainloop()


if __name__ == "__main__":
    main() 