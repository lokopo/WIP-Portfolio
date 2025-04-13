#!/usr/bin/env python3

import os
import re
import subprocess
import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Pango
import difflib  # For fuzzy matching

class MintSettingsBrowser(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Linux Mint Settings Browser")
        self.set_default_size(800, 600)
        self.set_border_width(10)
        
        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.main_box)
        
        # Search bar and system actions
        self.search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.main_box.pack_start(self.search_box, False, False, 0)
        
        # System actions dropdown
        self.create_system_actions_menu()
        self.search_box.pack_start(self.system_button, False, False, 0)
        
        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search settings...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_entry.connect("key-press-event", self.on_search_key_press)
        self.search_box.pack_start(self.search_entry, True, True, 0)
        
        # Settings list (with scrolling)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_box.pack_start(scrolled_window, True, True, 0)
        
        # List store and view
        # Name, Description, Module, Icon, Command, Parent Module, Keywords, Type, NameMarkup, DescMarkup, Relevance
        self.settings_store = Gtk.ListStore(str, str, str, GdkPixbuf.Pixbuf, str, str, str, str, str, str, float)
        self.settings_view = Gtk.TreeView(model=self.settings_store)
        self.settings_view.set_headers_visible(True)
        self.settings_view.connect("row-activated", self.on_setting_activated)
        
        # Set up columns
        icon_renderer = Gtk.CellRendererPixbuf()
        icon_column = Gtk.TreeViewColumn("", icon_renderer, pixbuf=3)
        self.settings_view.append_column(icon_column)
        
        # Name column with markup support for highlighting
        name_renderer = Gtk.CellRendererText()
        name_renderer.set_property("ellipsize", Pango.EllipsizeMode.END)
        name_column = Gtk.TreeViewColumn("Setting", name_renderer, markup=8)
        name_column.set_sort_column_id(0)
        name_column.set_resizable(True)
        name_column.set_expand(True)
        self.settings_view.append_column(name_column)
        
        # Description column with markup support for highlighting
        desc_renderer = Gtk.CellRendererText()
        desc_renderer.set_property("ellipsize", Pango.EllipsizeMode.END)
        desc_column = Gtk.TreeViewColumn("Description", desc_renderer, markup=9)
        desc_column.set_sort_column_id(1)
        desc_column.set_resizable(True)
        desc_column.set_expand(True)
        self.settings_view.append_column(desc_column)
        
        # Relevance column (visible only during search)
        relevance_renderer = Gtk.CellRendererProgress()
        self.relevance_column = Gtk.TreeViewColumn("Relevance", relevance_renderer, value=10)
        self.relevance_column.set_sort_column_id(10)
        self.relevance_column.set_resizable(True)
        self.relevance_column.set_visible(False)
        self.settings_view.append_column(self.relevance_column)
        
        type_renderer = Gtk.CellRendererText()
        type_column = Gtk.TreeViewColumn("Type", type_renderer, text=7)
        type_column.set_sort_column_id(7)
        type_column.set_resizable(True)
        self.settings_view.append_column(type_column)
        
        module_renderer = Gtk.CellRendererText()
        module_column = Gtk.TreeViewColumn("Module", module_renderer, text=2)
        module_column.set_sort_column_id(2)
        module_column.set_resizable(True)
        self.settings_view.append_column(module_column)
        
        parent_renderer = Gtk.CellRendererText()
        parent_column = Gtk.TreeViewColumn("Parent", parent_renderer, text=5)
        parent_column.set_sort_column_id(5)
        parent_column.set_resizable(True)
        self.settings_view.append_column(parent_column)
        
        scrolled_window.add(self.settings_view)
        
        # Status bar
        self.statusbar = Gtk.Statusbar()
        self.main_box.pack_start(self.statusbar, False, False, 0)
        
        # Initialize statusbar context ID
        self.context_id = self.statusbar.get_context_id("Settings Count")
        
        # Store current sort option
        self.current_sort = "relevance"
        
        # Load all settings
        self.all_settings = []
        self.load_settings()
        
        # Sort options - create after settings_store and all_settings are initialized
        self.create_sort_button()
        self.search_box.pack_start(self.sort_button, False, False, 0)
        
        # Populate the settings store
        self.populate_settings_store()
        
        # Update status bar
        self.update_status()
    
    def create_system_actions_menu(self):
        # Create menu button
        self.system_button = Gtk.MenuButton()
        self.system_button.set_tooltip_text("System Actions")
        
        # Set button icon
        icon = Gtk.Image.new_from_icon_name("system-shutdown", Gtk.IconSize.LARGE_TOOLBAR)
        self.system_button.set_image(icon)
        
        # Create menu
        menu = Gtk.Menu()
        
        # Create menu items
        restart_item = Gtk.MenuItem(label="Restart System")
        restart_item.connect("activate", self.on_restart_clicked)
        menu.append(restart_item)
        
        shutdown_item = Gtk.MenuItem(label="Shutdown System")
        shutdown_item.connect("activate", self.on_shutdown_clicked)
        menu.append(shutdown_item)
        
        # Add separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Add logout option
        logout_item = Gtk.MenuItem(label="Log Out")
        logout_item.connect("activate", self.on_logout_clicked)
        menu.append(logout_item)
        
        # Show all menu items
        menu.show_all()
        
        # Attach menu to button
        self.system_button.set_popup(menu)
    
    def on_restart_clicked(self, widget):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Restart System"
        )
        dialog.format_secondary_text("Are you sure you want to restart the system?")
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            subprocess.Popen(["systemctl", "reboot"])
    
    def on_shutdown_clicked(self, widget):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Shutdown System"
        )
        dialog.format_secondary_text("Are you sure you want to shutdown the system?")
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            subprocess.Popen(["systemctl", "poweroff"])
    
    def on_logout_clicked(self, widget):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Log Out"
        )
        dialog.format_secondary_text("Are you sure you want to log out?")
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            subprocess.Popen(["cinnamon-session-quit", "--logout", "--no-prompt"])
    
    def load_settings(self):
        # Cinnamon Settings
        self.load_cinnamon_settings()
        
        # Additional system settings
        self.load_additional_settings()
        
        # Load common utilities for Linux Mint
        self.load_mint_utilities()
        
        # Load detailed individual settings
        self.load_detailed_settings()
        
        # Add fallback entries for important settings if they weren't found
        self.add_fallback_entries()
        
        # Sort settings by name
        self.all_settings.sort(key=lambda x: x['name'].lower())
    
    def load_cinnamon_settings(self):
        # Find all Cinnamon settings modules
        modules_dir = "/usr/share/cinnamon/cinnamon-settings/modules"
        if os.path.exists(modules_dir):
            for filename in os.listdir(modules_dir):
                if filename.startswith("cs_") and filename.endswith(".py"):
                    module_name = filename[3:-3]  # Remove 'cs_' prefix and '.py' suffix
                    
                    # Get desktop file info if available
                    desktop_file = f"/usr/share/applications/cinnamon-settings-{module_name}.desktop"
                    name = module_name.capitalize().replace("-", " ")
                    description = ""
                    icon_name = "preferences-system"
                    keywords = module_name
                    
                    if os.path.exists(desktop_file):
                        with open(desktop_file, 'r') as f:
                            content = f.read()
                            name_match = re.search(r'^Name=(.+)$', content, re.MULTILINE)
                            if name_match:
                                name = name_match.group(1)
                            
                            comment_match = re.search(r'^Comment=(.+)$', content, re.MULTILINE)
                            if comment_match:
                                description = comment_match.group(1)
                            
                            icon_match = re.search(r'^Icon=(.+)$', content, re.MULTILINE)
                            if icon_match:
                                icon_name = icon_match.group(1)
                                
                            keywords_match = re.search(r'^Keywords=(.+)$', content, re.MULTILINE)
                            if keywords_match:
                                keywords += ";" + keywords_match.group(1)
                    
                    self.all_settings.append({
                        'name': name,
                        'description': description,
                        'module': module_name,
                        'icon': icon_name,
                        'command': f"cinnamon-settings {module_name}",
                        'parent': "",
                        'keywords': keywords,
                        'type': 'Setting'
                    })
    
    def load_additional_settings(self):
        # Find other settings applications
        apps_dir = "/usr/share/applications"
        for filename in os.listdir(apps_dir):
            if filename.endswith(".desktop") and "settings" in filename.lower() and not filename.startswith("cinnamon-settings"):
                desktop_file = os.path.join(apps_dir, filename)
                
                with open(desktop_file, 'r') as f:
                    content = f.read()
                    
                    # Skip if NoDisplay=true
                    if re.search(r'^NoDisplay=true$', content, re.MULTILINE):
                        continue
                    
                    name_match = re.search(r'^Name=(.+)$', content, re.MULTILINE)
                    name = filename[:-8].capitalize().replace("-", " ")  # Default
                    if name_match:
                        name = name_match.group(1)
                    
                    description = ""
                    comment_match = re.search(r'^Comment=(.+)$', content, re.MULTILINE)
                    if comment_match:
                        description = comment_match.group(1)
                    
                    icon_name = "preferences-system"
                    icon_match = re.search(r'^Icon=(.+)$', content, re.MULTILINE)
                    if icon_match:
                        icon_name = icon_match.group(1)
                    
                    exec_match = re.search(r'^Exec=(.+)$', content, re.MULTILINE)
                    command = ""
                    if exec_match:
                        command = exec_match.group(1)
                        # Remove field codes like %f, %u, etc.
                        command = re.sub(r'%[fFuUdDnNickvm]', '', command).strip()
                    
                    module = filename[:-8]  # Remove .desktop
                    
                    keywords = module
                    keywords_match = re.search(r'^Keywords=(.+)$', content, re.MULTILINE)
                    if keywords_match:
                        keywords += ";" + keywords_match.group(1)
                    
                    self.all_settings.append({
                        'name': name,
                        'description': description,
                        'module': module,
                        'icon': icon_name,
                        'command': command,
                        'parent': "",
                        'keywords': keywords,
                        'type': 'Setting'
                    })
    
    def load_mint_utilities(self):
        # List of common Linux Mint utilities to include
        mint_utilities = [
            {
                'desktop_file': 'mintupdate.desktop',
                'keywords': 'update;upgrade;software;package;manager;apt;security;maintenance'
            },
            {
                'desktop_file': 'mintinstall.desktop',
                'keywords': 'software;store;install;remove;programs;applications;packages;apps'
            },
            {
                'desktop_file': 'mintsources.desktop',
                'keywords': 'sources;repositories;ppa;software;package;apt;mirrors;update'
            },
            {
                'desktop_file': 'mintbackup.desktop',
                'keywords': 'backup;restore;archive;data;settings;save;recovery'
            },
            {
                'desktop_file': 'mintreport.desktop',
                'keywords': 'system;report;crash;logs;errors;problems;diagnostics'
            },
            {
                'desktop_file': 'mintupload.desktop',
                'keywords': 'upload;file sharing;ftp;transfer;cloud'
            },
            {
                'desktop_file': 'mintdrivers.desktop',
                'keywords': 'drivers;hardware;devices;proprietary;nvidia;amd;wifi;network'
            },
            {
                'desktop_file': 'mintwelcome.desktop',
                'keywords': 'welcome;introduction;start;help;guide;first steps'
            },
            {
                'desktop_file': 'mintlocale.desktop',
                'keywords': 'language;locale;region;input;keyboard;translation'
            },
            # Add Bluetooth settings - check for different possible desktop files
            # Prioritize dedicated Bluetooth managers first
            {
                'desktop_file': 'blueberry.desktop',
                'keywords': 'bluetooth;wireless;devices;transfer;audio;headphones;speakers;mouse;keyboard;pairing;connect',
                'direct_command': 'blueberry',
                'priority': 1
            },
            {
                'desktop_file': 'blueman-manager.desktop',
                'keywords': 'bluetooth;wireless;devices;transfer;audio;headphones;speakers;mouse;keyboard;pairing;connect',
                'direct_command': 'blueman-manager',
                'priority': 2
            },
            {
                'desktop_file': 'bluetooth-sendto.desktop',
                'keywords': 'bluetooth;wireless;devices;transfer;send;file;share',
                'direct_command': 'bluetooth-sendto',
                'priority': 3
            },
            {
                'desktop_file': 'cinnamon-settings-bluetooth.desktop',
                'keywords': 'bluetooth;wireless;devices;transfer;audio;headphones;speakers;mouse;keyboard;pairing;connect',
                'direct_command': 'cinnamon-settings bluetooth',
                'priority': 4
            },
            {
                'desktop_file': 'gnome-bluetooth-panel.desktop',
                'keywords': 'bluetooth;wireless;devices;transfer;audio;headphones;speakers;mouse;keyboard;pairing;connect',
                'direct_command': 'gnome-control-center bluetooth',
                'priority': 5
            },
            {
                'desktop_file': 'bluetooth-properties.desktop',
                'keywords': 'bluetooth;wireless;devices;transfer;audio;headphones;speakers;mouse;keyboard;pairing;connect',
                'direct_command': 'bluetooth-properties',
                'priority': 6
            },
            {
                'desktop_file': 'gnome-system-monitor.desktop',
                'keywords': 'system;monitor;process;task;manager;cpu;memory;network;performance'
            },
            {
                'desktop_file': 'timeshift-gtk.desktop',
                'keywords': 'backup;restore;system;snapshot;recovery;rsync;btrfs'
            },
            {
                'desktop_file': 'synaptic.desktop',
                'keywords': 'package;manager;software;apt;advanced;dependencies'
            },
            {
                'desktop_file': 'gparted.desktop',
                'keywords': 'partition;disk;drive;format;resize;mount;usb;storage'
            },
            {
                'desktop_file': 'gufw.desktop',
                'keywords': 'firewall;security;network;protection;ports;ufw;rules'
            },
            {
                'desktop_file': 'users-admin.desktop',
                'keywords': 'user;account;password;permissions;group;sudo'
            },
            {
                'desktop_file': 'cinnamon-settings-users.desktop',
                'keywords': 'user;account;password;permissions;group;sudo'
            },
            {
                'desktop_file': 'xed.desktop',
                'keywords': 'text;editor;documents;plain;scripts;programming'
            },
            {
                'desktop_file': 'nemo.desktop',
                'keywords': 'file;manager;browser;folders;files;explorer'
            },
            {
                'desktop_file': 'system-config-printer.desktop',
                'keywords': 'printer;printing;scanner;drivers;cups;add printer'
            }
        ]
        
        # Add each utility if the desktop file exists
        apps_dir = "/usr/share/applications"
        
        # Keep track of the first found Bluetooth tool
        first_bluetooth_tool = None
        
        for utility in mint_utilities:
            desktop_file = os.path.join(apps_dir, utility['desktop_file'])
            if os.path.exists(desktop_file):
                with open(desktop_file, 'r') as f:
                    content = f.read()
                    
                    # Skip if NoDisplay=true
                    if re.search(r'^NoDisplay=true$', content, re.MULTILINE):
                        continue
                    
                    name_match = re.search(r'^Name=(.+)$', content, re.MULTILINE)
                    name = utility['desktop_file'][:-8].capitalize().replace("-", " ")  # Default
                    if name_match:
                        name = name_match.group(1)
                    
                    description = ""
                    comment_match = re.search(r'^Comment=(.+)$', content, re.MULTILINE)
                    if comment_match:
                        description = comment_match.group(1)
                    
                    icon_name = "application-x-executable"
                    icon_match = re.search(r'^Icon=(.+)$', content, re.MULTILINE)
                    if icon_match:
                        icon_name = icon_match.group(1)
                    
                    exec_match = re.search(r'^Exec=(.+)$', content, re.MULTILINE)
                    command = ""
                    if exec_match:
                        command = exec_match.group(1)
                        # Remove field codes like %f, %u, etc.
                        command = re.sub(r'%[fFuUdDnNickvm]', '', command).strip()
                    
                    # Use direct command if specified (primarily for Bluetooth tools)
                    if 'direct_command' in utility:
                        command = utility['direct_command']
                    
                    module = utility['desktop_file'][:-8]  # Remove .desktop
                    
                    keywords = utility['keywords']
                    keywords_match = re.search(r'^Keywords=(.+)$', content, re.MULTILINE)
                    if keywords_match:
                        keywords += ";" + keywords_match.group(1)
                    
                    # For Bluetooth utilities, set a special type and track the first one found
                    utility_type = "Utility"
                    if "bluetooth" in keywords.lower() and "bluetooth" in module.lower():
                        utility_type = "Bluetooth Manager"
                        if first_bluetooth_tool is None and 'priority' in utility:
                            first_bluetooth_tool = {
                                'name': name,
                                'description': description,
                                'module': module,
                                'icon': icon_name,
                                'command': command,
                                'parent': "",
                                'keywords': keywords,
                                'type': utility_type,
                                'priority': utility.get('priority', 99)
                            }
                    
                    # Add with type 'Utility' to distinguish from settings
                    self.all_settings.append({
                        'name': name,
                        'description': description,
                        'module': module,
                        'icon': icon_name,
                        'command': command,
                        'parent': "",
                        'keywords': keywords,
                        'type': utility_type
                    })
        
        # If we found multiple Bluetooth tools, ensure the best one is clearly named
        if first_bluetooth_tool is not None:
            # Add a special "Bluetooth Manager" entry that points to the best tool
            self.all_settings.append({
                'name': 'Bluetooth Manager',
                'description': 'Connect and manage Bluetooth devices',
                'module': 'bluetooth-manager',
                'icon': 'bluetooth',
                'command': first_bluetooth_tool['command'],
                'parent': "",
                'keywords': 'bluetooth;wireless;devices;pair;connect;headphones;speakers;mouse;keyboard',
                'type': 'Bluetooth Manager'
            })
                    
        # Also look for any administrative tools that might not be in our list
        for filename in os.listdir(apps_dir):
            if filename.endswith(".desktop") and not any(util['desktop_file'] == filename for util in mint_utilities):
                desktop_file = os.path.join(apps_dir, filename)
                with open(desktop_file, 'r') as f:
                    content = f.read()
                    
                    # Skip if NoDisplay=true
                    if re.search(r'^NoDisplay=true$', content, re.MULTILINE):
                        continue
                    
                    # Look for admin or system tools by checking categories
                    categories_match = re.search(r'^Categories=(.+)$', content, re.MULTILINE)
                    if categories_match:
                        categories = categories_match.group(1).lower()
                        if (('admin' in categories or 'system' in categories) and 
                            'settings' not in categories and
                            not filename.startswith('cinnamon-settings')):
                            
                            name_match = re.search(r'^Name=(.+)$', content, re.MULTILINE)
                            name = filename[:-8].capitalize().replace("-", " ")  # Default
                            if name_match:
                                name = name_match.group(1)
                            
                            description = ""
                            comment_match = re.search(r'^Comment=(.+)$', content, re.MULTILINE)
                            if comment_match:
                                description = comment_match.group(1)
                            
                            icon_name = "application-x-executable"
                            icon_match = re.search(r'^Icon=(.+)$', content, re.MULTILINE)
                            if icon_match:
                                icon_name = icon_match.group(1)
                            
                            exec_match = re.search(r'^Exec=(.+)$', content, re.MULTILINE)
                            command = ""
                            if exec_match:
                                command = exec_match.group(1)
                                # Remove field codes like %f, %u, etc.
                                command = re.sub(r'%[fFuUdDnNickvm]', '', command).strip()
                            
                            module = filename[:-8]  # Remove .desktop
                            
                            keywords = module + ";" + categories
                            keywords_match = re.search(r'^Keywords=(.+)$', content, re.MULTILINE)
                            if keywords_match:
                                keywords += ";" + keywords_match.group(1)
                            
                            # Don't add duplicates
                            if not any(s['module'] == module for s in self.all_settings):
                                self.all_settings.append({
                                    'name': name,
                                    'description': description,
                                    'module': module,
                                    'icon': icon_name,
                                    'command': command,
                                    'parent': "",
                                    'keywords': keywords,
                                    'type': 'System Tool'
                                })
    
    def load_detailed_settings(self):
        # Dictionary of module settings metadata
        # This is where we define detailed settings and their associated keywords
        detailed_settings = {
            'windows': [
                {
                    'name': 'Window Focus Mode',
                    'description': 'Choose how windows receive focus (click or mouse-over)',
                    'keywords': 'mouse;focus;hover;sloppy;click to focus;automatically raise windows;raise on focus;window behavior'
                },
                {
                    'name': 'Title Bar Actions',
                    'description': 'Configure mouse actions on window title bars',
                    'keywords': 'double click;titlebar;maximize;shade;roll up;window action'
                },
                {
                    'name': 'Alt-Tab Behavior',
                    'description': 'Customize how Alt-Tab window switching works',
                    'keywords': 'switch;task switcher;application switcher;thumbnails;icons;preview'
                }
            ],
            'mouse': [
                {
                    'name': 'Mouse Speed',
                    'description': 'Adjust pointer speed and acceleration',
                    'keywords': 'pointer;cursor;speed;sensitivity;acceleration'
                },
                {
                    'name': 'Double-Click Timeout',
                    'description': 'Set the maximum time between clicks for double-clicking',
                    'keywords': 'click;double-click;timeout;speed'
                },
                {
                    'name': 'Mouse Handedness',
                    'description': 'Switch between left and right-handed mouse configuration',
                    'keywords': 'left handed;right handed;button mapping;primary button'
                }
            ],
            'keyboard': [
                {
                    'name': 'Keyboard Shortcuts',
                    'description': 'Customize keyboard shortcuts for various actions',
                    'keywords': 'hotkeys;shortcuts;keybindings;keyboard bindings'
                },
                {
                    'name': 'Typing Settings',
                    'description': 'Configure typing behavior including delay and speed',
                    'keywords': 'repeat delay;repeat interval;cursor blink time;typing'
                }
            ],
            'power': [
                {
                    'name': 'Power Button Action',
                    'description': 'Configure what happens when the power button is pressed',
                    'keywords': 'suspend;hibernate;shutdown;power off;button'
                },
                {
                    'name': 'Screen Power Saving',
                    'description': 'Configure when to dim or turn off the screen',
                    'keywords': 'screen;display;power;saving;blank;dim;suspend;sleep'
                }
            ],
            'notifications': [
                {
                    'name': 'Notification Display',
                    'description': 'Configure how notifications appear on screen',
                    'keywords': 'popups;alerts;position;duration;timeout'
                }
            ],
            'hotcorner': [
                {
                    'name': 'Hot Corner Actions',
                    'description': 'Configure actions when moving mouse to screen corners',
                    'keywords': 'mouse;corner;corners;edge;screen;trigger;expose;desktop;workspace'
                }
            ],
            'effects': [
                {
                    'name': 'Desktop Effects',
                    'description': 'Configure visual effects for windows and desktop',
                    'keywords': 'animations;transitions;effects;eye candy;fade;zoom;visual'
                }
            ],
            'desktop': [
                {
                    'name': 'Desktop Icons',
                    'description': 'Configure which icons appear on the desktop',
                    'keywords': 'icons;desktop;home;trash;mounted;volumes;network'
                }
            ],
            'themes': [
                {
                    'name': 'Widget Theme',
                    'description': 'Change the appearance of application controls',
                    'keywords': 'buttons;controls;theme;skin;appearance;widgets;look and feel'
                },
                {
                    'name': 'Window Theme',
                    'description': 'Change the appearance of window borders',
                    'keywords': 'windows;borders;decorations;titlebar;theme;appearance'
                },
                {
                    'name': 'Icon Theme',
                    'description': 'Change how icons look',
                    'keywords': 'icons;theme;appearance;symbol;graphics'
                }
            ],
            'fonts': [
                {
                    'name': 'Font Selection',
                    'description': 'Choose system fonts for various interface elements',
                    'keywords': 'text;typography;font family;size;monospace;document'
                },
                {
                    'name': 'Font Rendering',
                    'description': 'Configure how fonts are displayed',
                    'keywords': 'antialiasing;hinting;subpixel;smoothing;rendering;text;crisp'
                }
            ],
            'screensaver': [
                {
                    'name': 'Lock Screen Settings',
                    'description': 'Configure screen locking behavior and appearance',
                    'keywords': 'lock;security;password;timeout;screensaver'
                }
            ],
            'privacy': [
                {
                    'name': 'Usage Data',
                    'description': 'Configure what usage data is collected',
                    'keywords': 'privacy;data;collection;analytics;usage;history'
                },
                {
                    'name': 'Recent Files',
                    'description': 'Manage settings for recently used files',
                    'keywords': 'privacy;recent;history;files;documents;clear'
                }
            ],
            'startup': [
                {
                    'name': 'Startup Applications',
                    'description': 'Manage programs that start automatically',
                    'keywords': 'autostart;boot;login;startup;applications;programs'
                }
            ],
            'workspaces': [
                {
                    'name': 'Workspace Management',
                    'description': 'Configure virtual workspace behavior',
                    'keywords': 'workspaces;virtual desktops;pager;number;layout;switch'
                }
            ],
            'panel': [
                {
                    'name': 'Panel Layout',
                    'description': 'Configure the layout and appearance of panels',
                    'keywords': 'taskbar;panel;applets;position;size;autohide'
                }
            ],
            # Add Bluetooth detailed settings
            'bluetooth': [
                {
                    'name': 'Bluetooth Pairing',
                    'description': 'Pair and connect to Bluetooth devices',
                    'keywords': 'pair;connect;bluetooth;wireless;devices;headphones;speakers;mouse;keyboard'
                },
                {
                    'name': 'Bluetooth Visibility',
                    'description': 'Control whether your computer is visible to other Bluetooth devices',
                    'keywords': 'visibility;discoverable;bluetooth;wireless;detection'
                },
                {
                    'name': 'Bluetooth Power Management',
                    'description': 'Control when Bluetooth is enabled or disabled',
                    'keywords': 'power;on;off;enable;disable;bluetooth;adapter;battery'
                }
            ]
        }
        
        # Add detailed settings to the list
        theme = Gtk.IconTheme.get_default()
        for module_name, settings in detailed_settings.items():
            # Find the parent module info
            parent_module = next((s for s in self.all_settings if s['module'] == module_name), None)
            
            if parent_module:
                parent_name = parent_module['name']
                parent_icon = parent_module['icon']
                
                # Get the icon
                try:
                    if parent_icon.endswith(('.png', '.svg', '.xpm')):
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(parent_icon, 24, 24)
                    else:
                        pixbuf = theme.load_icon(parent_icon, 24, 0)
                except:
                    try:
                        pixbuf = theme.load_icon("preferences-system", 24, 0)
                    except:
                        pixbuf = None
                
                # Add each detailed setting
                for setting in settings:
                    self.all_settings.append({
                        'name': setting['name'],
                        'description': setting['description'],
                        'module': module_name + ":" + setting['name'].lower().replace(' ', '-'),
                        'icon': parent_icon,
                        'command': f"cinnamon-settings {module_name}",
                        'parent': parent_name,
                        'keywords': setting['keywords'] + ";" + module_name + ";" + parent_name,
                        'type': 'Specific Setting'
                    })
    
    def create_sort_button(self):
        # Create sort button with options
        self.sort_button = Gtk.MenuButton()
        self.sort_button.set_tooltip_text("Sort Options")
        
        # Set button icon
        icon = Gtk.Image.new_from_icon_name("view-sort-ascending", Gtk.IconSize.LARGE_TOOLBAR)
        self.sort_button.set_image(icon)
        
        # Create menu
        menu = Gtk.Menu()
        
        # Create menu items for different sort options
        relevance_item = Gtk.RadioMenuItem(label="Sort by Relevance")
        relevance_item.connect("toggled", self.on_sort_option_toggled, "relevance")
        relevance_item.set_active(True)  # Default sort
        menu.append(relevance_item)
        
        name_item = Gtk.RadioMenuItem.new_with_label_from_widget(relevance_item, "Sort by Name")
        name_item.connect("toggled", self.on_sort_option_toggled, "name")
        menu.append(name_item)
        
        type_item = Gtk.RadioMenuItem.new_with_label_from_widget(relevance_item, "Sort by Type")
        type_item.connect("toggled", self.on_sort_option_toggled, "type")
        menu.append(type_item)
        
        module_item = Gtk.RadioMenuItem.new_with_label_from_widget(relevance_item, "Sort by Module")
        module_item.connect("toggled", self.on_sort_option_toggled, "module")
        menu.append(module_item)
        
        # Store current sort option
        self.current_sort = "relevance"
        
        # Show all menu items
        menu.show_all()
        
        # Attach menu to button
        self.sort_button.set_popup(menu)
    
    def on_sort_option_toggled(self, widget, sort_option):
        # Only handle the active toggle
        if widget.get_active():
            self.current_sort = sort_option
            # Refresh the current search/display with new sort
            self.on_search_changed(self.search_entry)
    
    def on_search_key_press(self, widget, event):
        """Handle keyboard navigation in search results"""
        keyval = event.keyval
        keyname = Gdk.keyval_name(keyval)
        
        # If no items in the list, do nothing
        if len(self.settings_store) == 0:
            return False
            
        # Get current selection
        selection = self.settings_view.get_selection()
        model, treeiter = selection.get_selected()
        
        # Down arrow - move to next item
        if keyname == "Down":
            if treeiter is None:
                # No selection, select first item
                self.settings_view.set_cursor(Gtk.TreePath.new_first())
            else:
                # Try to move to next item
                path = model.get_path(treeiter)
                next_path = Gtk.TreePath.new_from_indices([path.get_indices()[0] + 1])
                if next_path.get_indices()[0] < len(model):
                    self.settings_view.set_cursor(next_path)
            return True
            
        # Up arrow - move to previous item
        elif keyname == "Up":
            if treeiter is not None:
                path = model.get_path(treeiter)
                if path.get_indices()[0] > 0:
                    prev_path = Gtk.TreePath.new_from_indices([path.get_indices()[0] - 1])
                    self.settings_view.set_cursor(prev_path)
            return True
            
        # Enter - activate selected item
        elif keyname == "Return" or keyname == "KP_Enter":
            if treeiter is not None:
                path = model.get_path(treeiter)
                self.on_setting_activated(self.settings_view, path, None)
            return True
            
        # Let other keys be handled normally
        return False
    
    def populate_settings_store(self, filter_text=None):
        self.settings_store.clear()
        
        displayed_settings = []
        search_terms = []
        scored_settings = []
        
        if filter_text:
            # Clean and process the search text
            search_text = filter_text.lower().strip()
            search_terms = search_text.split()
            
            # Search with relevance scoring
            for setting in self.all_settings:
                score = self.calculate_relevance_score(setting, search_terms)
                if score > 0:
                    scored_settings.append((setting, score))
            
            # Sort by relevance by default, but respect user's sort preference
            if self.current_sort == "relevance":
                scored_settings.sort(key=lambda x: x[1], reverse=True)
            elif self.current_sort == "name":
                scored_settings.sort(key=lambda x: x[0]['name'].lower())
            elif self.current_sort == "type":
                scored_settings.sort(key=lambda x: x[0]['type'].lower())
            elif self.current_sort == "module":
                scored_settings.sort(key=lambda x: x[0]['module'].lower())
            
            displayed_settings = [item[0] for item in scored_settings]
            
            # Determine max score for percentage calculation
            max_score = scored_settings[0][1] if scored_settings else 0
            
            # Show relevance column only when sorted by relevance
            self.relevance_column.set_visible(self.current_sort == "relevance")
        else:
            # No search filter, show all and sort by name by default
            displayed_settings = sorted(self.all_settings.copy(), key=lambda x: x['name'].lower())
            # Hide relevance column when not searching
            self.relevance_column.set_visible(False)
            max_score = 0
        
        theme = Gtk.IconTheme.get_default()
        for i, setting in enumerate(displayed_settings):
            try:
                if setting['icon'].endswith(('.png', '.svg', '.xpm')):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(setting['icon'], 24, 24)
                else:
                    pixbuf = theme.load_icon(setting['icon'], 24, 0)
            except:
                try:
                    pixbuf = theme.load_icon("preferences-system", 24, 0)
                except:
                    pixbuf = None
            
            # Create highlighted text if searching
            name_markup = self.highlight_text(setting['name'], search_terms)
            desc_markup = self.highlight_text(setting['description'], search_terms)
            
            # Determine relevance percentage for progress bar
            relevance_pct = 0
            if filter_text and max_score > 0:
                if i < len(scored_settings):
                    relevance_pct = min(100, int((scored_settings[i][1] / max_score) * 100))
            
            self.settings_store.append([
                setting['name'],
                setting['description'],
                setting['module'],
                pixbuf,
                setting['command'],
                setting['parent'],
                setting['keywords'],
                setting['type'],
                name_markup,
                desc_markup,
                float(relevance_pct)
            ])
        
        self.update_status(len(displayed_settings))
    
    def calculate_relevance_score(self, setting, search_terms):
        """
        Calculate a relevance score based on how well the setting matches search terms.
        Returns a score > 0 if there's a match, 0 if no match.
        """
        if not search_terms:
            return 0
            
        total_score = 0
        setting_name = setting['name'].lower()
        setting_desc = setting['description'].lower()
        setting_module = setting['module'].lower()
        setting_keywords = setting['keywords'].lower()
        
        # Give each field a different weight for scoring
        name_weight = 10.0
        description_weight = 5.0
        module_weight = 3.0
        keywords_weight = 8.0
        
        # Check each search term
        for term in search_terms:
            # Exact matches get higher scores
            name_score = 0
            if term in setting_name:
                # Exact match in name gets higher score
                name_score = name_weight
                # Even higher score for exact word match or starts with the term
                if term == setting_name or setting_name.startswith(term):
                    name_score *= 2
                # Words in the name that start with the term
                elif any(word.startswith(term) for word in setting_name.split()):
                    name_score *= 1.5
            # Fuzzy matching for names that are close but not exact
            elif len(term) > 2:  # Only do fuzzy match for terms with 3+ chars
                name_similarity = difflib.SequenceMatcher(None, term, setting_name).ratio()
                if name_similarity > 0.6:  # Adjust threshold as needed
                    name_score = name_weight * name_similarity
            
            # Description score
            desc_score = 0
            if term in setting_desc:
                desc_score = description_weight
                # Higher score if it's a word match
                if any(term == word for word in setting_desc.split()):
                    desc_score *= 1.5
            
            # Module score
            module_score = 0
            if term in setting_module:
                module_score = module_weight
                if setting_module.startswith(term):
                    module_score *= 1.5
            
            # Keywords score
            keywords_score = 0
            if term in setting_keywords:
                keywords_score = keywords_weight
                # Higher score for exact keyword matches
                keyword_list = setting_keywords.split(';')
                if any(term == keyword.strip() for keyword in keyword_list):
                    keywords_score *= 2
                elif any(keyword.strip().startswith(term) for keyword in keyword_list):
                    keywords_score *= 1.5
            
            # Add scores from all fields for this term
            term_score = name_score + desc_score + module_score + keywords_score
            
            # If at least one field matched, count this term
            if term_score > 0:
                total_score += term_score
        
        # If all terms have some match, give a bonus (improves multi-term search)
        if total_score > 0 and all(any(term in field for field in [setting_name, setting_desc, setting_module, setting_keywords]) for term in search_terms):
            total_score *= 1.2
            
        return total_score
    
    def highlight_text(self, text, search_terms):
        """Highlight matching terms in text using Pango markup"""
        if not search_terms or not text:
            return GLib.markup_escape_text(text)
            
        # Escape text for markup
        escaped_text = GLib.markup_escape_text(text)
        
        # For each search term, highlight matches
        for term in search_terms:
            if not term:
                continue
                
            # Prepare for case-insensitive replacement with regex
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            
            # Replace with highlighted version
            escaped_text = pattern.sub(f'<span background="#FFFF66" foreground="#000000">\\g<0></span>', escaped_text)
            
        return escaped_text
    
    def update_status(self, count=None):
        if count is None:
            count = len(self.all_settings)
        
        search_text = self.search_entry.get_text()
        if search_text:
            self.statusbar.pop(self.context_id)
            self.statusbar.push(self.context_id, f"Found {count} settings matching '{search_text}' (out of {len(self.all_settings)} total)")
        else:
            self.statusbar.pop(self.context_id)
            self.statusbar.push(self.context_id, f"Displaying all {count} settings")
    
    def on_search_changed(self, widget):
        search_text = widget.get_text()
        self.populate_settings_store(search_text)
        
        # If we have search results, make the first item active
        if search_text and len(self.settings_store) > 0:
            # Select the first item to make navigation easier
            self.settings_view.set_cursor(Gtk.TreePath.new_first())
    
    def on_setting_activated(self, treeview, path, column):
        model = treeview.get_model()
        command = model[path][4]
        module_info = model[path][2]
        setting_name = model[path][0]
        setting_type = model[path][7]
        
        if command:
            try:
                # Special handling for Bluetooth settings
                if setting_type == "Bluetooth Manager" or "bluetooth" in module_info.lower():
                    # Use the command directly - should be a bluetooth manager already
                    subprocess.Popen(command.split())
                    return
                elif "bluetooth" in setting_name.lower():
                    # For any other setting with bluetooth in the name, try to find a good manager
                    bluetooth_commands = [
                        "blueberry", 
                        "blueman-manager",
                        "bluetooth-sendto",
                        "cinnamon-settings bluetooth",
                        "gnome-control-center bluetooth"
                    ]
                    
                    bt_command = None
                    for cmd in bluetooth_commands:
                        cmd_path = cmd.split()[0]
                        if os.path.exists(f"/usr/bin/{cmd_path}") or os.path.exists(f"/usr/sbin/{cmd_path}"):
                            bt_command = cmd
                            break
                    
                    if bt_command:
                        subprocess.Popen(bt_command.split())
                        return
                
                # Standard handling for other settings
                if ":" in module_info:
                    # For now, we just launch the parent module
                    subprocess.Popen(command.split())
                else:
                    # Launch the setting
                    subprocess.Popen(command.split())
            except Exception as e:
                self.show_error_dialog(str(e))
    
    def show_error_dialog(self, message):
        error_dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error launching setting"
        )
        error_dialog.format_secondary_text(message)
        error_dialog.run()
        error_dialog.destroy()
    
    def add_fallback_entries(self):
        """Add fallback entries for important settings if they weren't found"""
        # Check if Bluetooth is already in our settings as a manager
        bluetooth_manager_exists = any(
            ("bluetooth" in setting['keywords'].lower() or "bluetooth" in setting['name'].lower()) and 
            setting['command'] and 
            (setting['type'] == "Bluetooth Manager" or 
             any(cmd in setting['command'].lower() for cmd in ["blueberry", "blueman", "bluetooth-"]))
            for setting in self.all_settings
        )
        
        if not bluetooth_manager_exists:
            # Try different commands to find which one is available
            bluetooth_commands = [
                "blueberry", 
                "blueman-manager",
                "bluetooth-sendto",
                "cinnamon-settings bluetooth",
                "gnome-control-center bluetooth"
            ]
            
            command = None
            for cmd in bluetooth_commands:
                cmd_path = cmd.split()[0]
                if os.path.exists(f"/usr/bin/{cmd_path}") or os.path.exists(f"/usr/sbin/{cmd_path}"):
                    command = cmd
                    break
            
            if command:
                self.all_settings.append({
                    'name': 'Bluetooth Manager',
                    'description': 'Configure and connect to Bluetooth devices',
                    'module': 'bluetooth-manager',
                    'icon': 'bluetooth',
                    'command': command,
                    'parent': "",
                    'keywords': 'bluetooth;wireless;devices;transfer;audio;headphones;speakers;mouse;keyboard;pairing;connect',
                    'type': 'Bluetooth Manager'
                })

def main():
    win = MintSettingsBrowser()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main() 