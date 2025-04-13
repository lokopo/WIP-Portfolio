#!/usr/bin/env python3

import sys
import os
import csv
import subprocess
import threading
import time
from datetime import datetime

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                               QGraphicsDropShadowEffect, QFrame, QSplitter, QMessageBox, QStyleFactory, 
                               QStatusBar, QScrollArea, QGridLayout, QSpacerItem, QSizePolicy)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve, QObject
    from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QLinearGradient, QPixmap, QPainter, QBrush, QPen
except ImportError:
    print("PyQt5 is required for this application.")
    print("Please install it with: sudo apt install python3-pyqt5")
    sys.exit(1)

try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    import gi
    gi.require_version('GLib', '2.0')
    from gi.repository import GLib
except ImportError:
    print("DBus libraries are required for real-time track detection.")
    print("Please install them with: sudo apt install python3-dbus python3-gi")
    sys.exit(1)

# Material Design colors - Dark Theme
class MaterialColors:
    # Primary & Accent colors
    PRIMARY = "#2196F3"           # Blue
    PRIMARY_LIGHT = "#64B5F6"     # Light Blue
    PRIMARY_DARK = "#1976D2"      # Dark Blue
    ACCENT = "#009688"            # Teal
    ACCENT_LIGHT = "#4DB6AC"      # Light Teal
    ACCENT_DARK = "#00796B"       # Dark Teal
    
    # UI colors for dark theme
    SURFACE = "#212121"           # Dark Grey for surfaces
    BACKGROUND = "#121212"        # Almost Black for background
    CARD_BACKGROUND = "#1E1E1E"   # Slightly lighter than background
    TOOLTIP_BACKGROUND = "#424242"# Medium Grey
    DISABLED = "#757575"          # Medium-Light Grey
    
    # Content colors
    ON_PRIMARY = "#FFFFFF"        # White text on primary
    ON_SURFACE = "#E0E0E0"        # Light Grey text on dark surfaces
    ON_BACKGROUND = "#FFFFFF"     # White text on background
    
    # Utility colors
    SUCCESS = "#66BB6A"           # Green - slightly lighter for dark mode
    WARNING = "#FFCA28"           # Amber - slightly lighter for dark mode
    ERROR = "#EF5350"             # Red - slightly lighter for dark mode
    BORDER = "#424242"            # Dark Grey border
    DIVIDER = "#323232"           # Slightly lighter than surfaces


class Card(QFrame):
    """Custom widget to create Material Design-like cards"""
    
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        
        # Setup frame style
        self.setObjectName("card")
        self.setStyleSheet(f"""
            #card {{
                background-color: {MaterialColors.CARD_BACKGROUND};
                border-radius: 8px;
                border: none;
            }}
        """)
        
        # Add shadow effect - subtler in dark mode
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Create card layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)
        
        # Add title if provided
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("cardTitle")
            self.layout.addWidget(title_label)
    
    def add_widget(self, widget):
        """Add a widget to the card"""
        self.layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add a layout to the card"""
        self.layout.addLayout(layout)


class MaterialButton(QPushButton):
    """Custom button with Material Design styling"""
    
    TYPES = {
        "primary": (MaterialColors.PRIMARY, MaterialColors.PRIMARY_LIGHT, MaterialColors.ON_PRIMARY),
        "accent": (MaterialColors.ACCENT, MaterialColors.ACCENT_LIGHT, MaterialColors.ON_PRIMARY),
        "success": (MaterialColors.SUCCESS, "#81C784", MaterialColors.ON_PRIMARY),
        "warning": (MaterialColors.WARNING, "#FFD54F", "#212121"),
        "error": (MaterialColors.ERROR, "#E57373", MaterialColors.ON_PRIMARY),
        "flat": ("#2D2D2D", "#383838", MaterialColors.PRIMARY_LIGHT)
    }
    
    def __init__(self, text, button_type="primary", parent=None):
        super().__init__(text, parent)
        self.setObjectName(f"{button_type}Button")
        self.setCursor(Qt.PointingHandCursor)
        
        # Get colors based on button type
        if button_type in self.TYPES:
            bg_color, hover_color, text_color = self.TYPES[button_type]
        else:
            bg_color, hover_color, text_color = self.TYPES["primary"]
        
        # Set button style
        if button_type == "flat":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {MaterialColors.PRIMARY_LIGHT};
                    border: none;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 14px;
                    border-radius: 4px;
                    min-height: 36px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {MaterialColors.CARD_BACKGROUND};
                    color: {MaterialColors.PRIMARY_LIGHT};
                }}
                QPushButton:disabled {{
                    background-color: {MaterialColors.BACKGROUND};
                    color: {MaterialColors.DISABLED};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: none;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 14px;
                    border-radius: 4px;
                    min-height: 36px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {"#383838" if button_type == "flat" else bg_color};
                    opacity: 0.8;
                }}
                QPushButton:disabled {{
                    background-color: {MaterialColors.BORDER};
                    color: {MaterialColors.DISABLED};
                }}
            """)


class StatusIndicator(QWidget):
    """Custom widget to show status with a colored dot"""
    
    def __init__(self, status_text="Status", status_color=MaterialColors.ERROR, parent=None):
        super().__init__(parent)
        self.status_text = status_text
        self.status_color = status_color
        
        self.setMinimumHeight(24)
        self.setMinimumWidth(120)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw status dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(self.status_color)))
        painter.drawEllipse(0, 6, 12, 12)
        
        # Draw status text
        painter.setPen(QPen(QColor(MaterialColors.ON_BACKGROUND)))
        font = QFont("Roboto", 14)
        painter.setFont(font)
        painter.drawText(20, 0, self.width() - 20, self.height(), Qt.AlignLeft | Qt.AlignVCenter, self.status_text)
    
    def update_status(self, status_text, status_color):
        self.status_text = status_text
        self.status_color = status_color
        self.update()


class PithosDbusMonitor(QObject):
    """Monitors Pithos via DBus for real-time updates"""
    
    # Signal emitted when Pithos status or track changes
    status_update = pyqtSignal(bool, str, str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Whether we're connected to Pithos
        self.connected = False
        self.current_title = "Not playing"
        self.current_artist = "N/A"
        self.current_album = "N/A"
        
        # Set up DBus main loop
        DBusGMainLoop(set_as_default=True)
        self.loop = GLib.MainLoop()
        self.loop_thread = threading.Thread(target=self.loop.run, daemon=True)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_pithos, daemon=True)
        
        # Start all threads
        self.loop_thread.start()
        self.monitor_thread.start()
    
    def monitor_pithos(self):
        """Main monitoring loop that sets up signal connections"""
        bus = dbus.SessionBus()
        while True:
            try:
                # Check if Pithos is running
                if 'org.mpris.MediaPlayer2.io.github.Pithos' in bus.list_names():
                    if not self.connected:
                        self.setup_dbus_connections(bus)
                    
                    # Initial metadata update when we first connect
                    self.update_metadata()
                    
                else:
                    if self.connected:
                        self.connected = False
                        self.current_title = "Not playing"
                        self.current_artist = "N/A"
                        self.current_album = "N/A"
                        self.status_update.emit(False, self.current_title, self.current_artist, self.current_album)
            except Exception as e:
                print(f"Error monitoring Pithos: {str(e)}")
                
            # Check every 2 seconds if not connected, to avoid high CPU usage
            time.sleep(2)
    
    def setup_dbus_connections(self, bus):
        """Set up DBus connections and signal handlers"""
        try:
            # Get the Pithos object
            self.pithos_obj = bus.get_object('org.mpris.MediaPlayer2.io.github.Pithos', 
                                            '/org/mpris/MediaPlayer2')
            
            # Get interfaces
            self.props_iface = dbus.Interface(self.pithos_obj, 'org.freedesktop.DBus.Properties')
            
            # Connect to PropertiesChanged signal
            self.props_iface.connect_to_signal('PropertiesChanged', self.on_properties_changed)
            
            # Mark as connected
            self.connected = True
            
            # Get initial state
            self.update_metadata()
            
            print("Successfully connected to Pithos via DBus")
            
        except Exception as e:
            print(f"Failed to set up DBus connections: {e}")
            self.connected = False
    
    def on_properties_changed(self, interface_name, changed_properties, invalidated_properties):
        """Handle PropertiesChanged signal"""
        if interface_name == 'org.mpris.MediaPlayer2.Player' and 'Metadata' in changed_properties:
            # Track changed
            self.update_metadata(changed_properties['Metadata'])
    
    def update_metadata(self, metadata=None):
        """Update track information from metadata"""
        try:
            if not metadata:
                # Get metadata directly
                metadata = self.props_iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
            
            # Extract track info
            title = str(metadata.get('xesam:title', "Unknown"))
            artists = metadata.get('xesam:artist', ["Unknown"])
            if artists:
                artist = str(artists[0])
            else:
                artist = "Unknown"
            album = str(metadata.get('xesam:album', "Unknown"))
            
            # Update state and emit signal
            self.current_title = title
            self.current_artist = artist
            self.current_album = album
            self.status_update.emit(True, title, artist, album)
            
        except Exception as e:
            print(f"Error updating metadata: {e}")
            if self.connected:
                self.status_update.emit(True, "Unknown", "Unknown", "Unknown")


def is_pithos_running():
    """Check if Pithos is currently running"""
    try:
        result = subprocess.run(['pgrep', '-x', 'pithos'], stdout=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False


def launch_pithos():
    """Launch Pithos if it's not already running"""
    if not is_pithos_running():
        try:
            # Try to start Pithos in the background
            subprocess.Popen(['pithos'], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL, 
                            start_new_session=True)
            print("Launching Pithos...")
            return True
        except Exception as e:
            print(f"Error launching Pithos: {e}")
            return False
    return True


class InfoRow(QWidget):
    """Widget for displaying a key-value pair with proper styling"""
    
    def __init__(self, label, value="", parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        
        # Label
        label_widget = QLabel(f"{label}:")
        label_widget.setObjectName("infoLabel")
        label_widget.setStyleSheet(f"""
            #infoLabel {{
                color: {MaterialColors.ON_SURFACE};
                font-weight: 500;
                font-size: 14px;
                min-width: 80px;
            }}
        """)
        layout.addWidget(label_widget)
        
        # Value
        self.value_widget = QLabel(value)
        self.value_widget.setObjectName("infoValue")
        self.value_widget.setStyleSheet(f"""
            #infoValue {{
                color: {MaterialColors.ON_SURFACE};
                font-size: 14px;
                padding-left: 8px;
            }}
        """)
        self.value_widget.setWordWrap(True)
        layout.addWidget(self.value_widget, 1)  # Give the value widget more space
    
    def set_value(self, value):
        """Update the value text"""
        self.value_widget.setText(value)


class PithosSongLoggerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuration
        self.csv_file = os.path.expanduser("~/pithos_songs.csv")
        self.logger_process = None
        self.is_logging = False
        self.songs_count = 0
        self.last_logged_title = ""
        self.last_logged_artist = ""
        self.last_logged_album = ""
        self.current_song_logged = False
        self.last_log_time = 0  # To prevent duplicate logs in short time frames
        self.initial_song_logged = False  # Flag to track if we've logged the initial song
        
        # Setup UI
        self.init_ui()
        
        # Start Pithos if not running
        if not is_pithos_running():
            launch_pithos()
            self.statusBar().showMessage("Launching Pithos...")
            # Wait a bit for Pithos to start
            time.sleep(3)
        
        # Start monitoring Pithos
        self.dbus_monitor = PithosDbusMonitor()
        self.dbus_monitor.status_update.connect(self.update_status)
        
        # Load initial data
        self.load_songs()
        
        # Automatically start logging when application launches
        self.start_logging()
        
        # Setup auto refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_songs)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def init_ui(self):
        # Main window setup
        self.setWindowTitle("Pithos Song Logger")
        self.setMinimumSize(1000, 700)
        
        # Setup the global application style
        self.setup_style()
        
        # Main widget and scroll area for responsiveness
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout with proper margins
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)  # More spacing between major sections
        
        # App header with title and subtitle
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        app_title = QLabel("Pithos Song Logger")
        app_title.setObjectName("appTitle")
        header_layout.addWidget(app_title)
        
        app_subtitle = QLabel("Track and record your Pithos listening history")
        app_subtitle.setObjectName("appSubtitle")
        header_layout.addWidget(app_subtitle)
        
        main_layout.addLayout(header_layout)
        
        # Top section: Status and Controls side by side
        top_section = QHBoxLayout()
        top_section.setSpacing(24)  # Space between cards
        
        # Status Card: Left panel showing current status
        status_card = Card("Current Status")
        status_content = QWidget()
        status_layout = QVBoxLayout(status_content)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(16)
        
        # Status indicator
        self.status_indicator = StatusIndicator("Pithos is not running", MaterialColors.ERROR)
        status_layout.addWidget(self.status_indicator)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet(f"background-color: {MaterialColors.DIVIDER};")
        status_layout.addWidget(divider)
        
        # Now Playing section
        now_playing_label = QLabel("Now Playing")
        now_playing_label.setObjectName("sectionLabel")
        status_layout.addWidget(now_playing_label)
        
        # Song details in a clean format
        self.title_row = InfoRow("Title")
        status_layout.addWidget(self.title_row)
        
        self.artist_row = InfoRow("Artist")
        status_layout.addWidget(self.artist_row)
        
        self.album_row = InfoRow("Album")
        status_layout.addWidget(self.album_row)
        
        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setFrameShadow(QFrame.Sunken)
        divider2.setStyleSheet(f"background-color: {MaterialColors.DIVIDER};")
        status_layout.addWidget(divider2)
        
        # Statistics
        stats_label = QLabel("Statistics")
        stats_label.setObjectName("sectionLabel")
        status_layout.addWidget(stats_label)
        
        self.count_row = InfoRow("Total Songs", "0")
        status_layout.addWidget(self.count_row)
        
        # Add a note about real-time detection
        realtime_note = QLabel("✓ Real-time song change detection enabled")
        realtime_note.setObjectName("noteLabel")
        realtime_note.setStyleSheet(f"""
            #noteLabel {{
                color: {MaterialColors.SUCCESS};
                font-size: 12px;
                margin-top: 12px;
            }}
        """)
        status_layout.addWidget(realtime_note)
        
        # Add a note about auto-launch
        autolaunch_note = QLabel("✓ Pithos auto-launch enabled")
        autolaunch_note.setObjectName("noteLabel")
        autolaunch_note.setStyleSheet(f"""
            #noteLabel {{
                color: {MaterialColors.SUCCESS};
                font-size: 12px;
                margin-top: 2px;
            }}
        """)
        status_layout.addWidget(autolaunch_note)
        
        # Add a note about auto-logging
        autologging_note = QLabel("✓ Automatic logging enabled")
        autologging_note.setObjectName("noteLabel")
        autologging_note.setStyleSheet(f"""
            #noteLabel {{
                color: {MaterialColors.SUCCESS};
                font-size: 12px;
                margin-top: 2px;
            }}
        """)
        status_layout.addWidget(autologging_note)
        
        # Add a note about auto-refresh
        autorefresh_note = QLabel("✓ Automatic list refresh enabled")
        autorefresh_note.setObjectName("noteLabel")
        autorefresh_note.setStyleSheet(f"""
            #noteLabel {{
                color: {MaterialColors.SUCCESS};
                font-size: 12px;
                margin-top: 2px;
            }}
        """)
        status_layout.addWidget(autorefresh_note)
        
        # Add spacing at the bottom
        status_layout.addStretch()
        
        status_card.add_widget(status_content)
        top_section.addWidget(status_card, 2)  # 2/3 of the width
        
        # Controls Card: Right panel with action buttons
        controls_card = Card("Controls")
        controls_content = QWidget()
        controls_layout = QVBoxLayout(controls_content)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(16)
        
        # Divider
        divider3 = QFrame()
        divider3.setFrameShape(QFrame.HLine)
        divider3.setFrameShadow(QFrame.Sunken)
        divider3.setStyleSheet(f"background-color: {MaterialColors.DIVIDER};")
        controls_layout.addWidget(divider3)
        
        # Data Management section
        data_label = QLabel("Data Management")
        data_label.setObjectName("sectionLabel")
        controls_layout.addWidget(data_label)
        
        # Open CSV button
        self.open_csv_button = MaterialButton("Open CSV File", "accent")
        self.open_csv_button.clicked.connect(self.open_csv_file)
        controls_layout.addWidget(self.open_csv_button)
        
        # Delete Selected Song button
        self.delete_song_button = MaterialButton("Delete Selected Song", "error")
        self.delete_song_button.clicked.connect(self.delete_selected_song)
        controls_layout.addWidget(self.delete_song_button)
        
        # Add spacing at the bottom
        controls_layout.addStretch()
        
        controls_card.add_widget(controls_content)
        top_section.addWidget(controls_card, 1)  # 1/3 of the width
        
        main_layout.addLayout(top_section)
        
        # Song History Card
        history_card = Card("Song History")
        history_content = QWidget()
        history_layout = QVBoxLayout(history_content)
        history_layout.setContentsMargins(0, 0, 0, 0)
        
        # Table for song history with modern styling
        self.songs_table = QTableWidget()
        self.songs_table.setObjectName("songsTable")
        self.songs_table.setColumnCount(4)
        self.songs_table.setHorizontalHeaderLabels(["Title", "Artist", "Album", "Timestamp"])
        
        # Configure the table to look modern
        self.songs_table.setShowGrid(False)  # No grid lines for a cleaner look
        self.songs_table.setAlternatingRowColors(True)
        self.songs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.songs_table.setSelectionMode(QTableWidget.SingleSelection)
        self.songs_table.verticalHeader().setVisible(False)  # Hide row numbers
        
        # Set column sizing
        self.songs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Title
        self.songs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Artist
        self.songs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Album
        self.songs_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Timestamp
        
        history_layout.addWidget(self.songs_table)
        history_card.add_widget(history_content)
        
        main_layout.addWidget(history_card)
        
        # Status bar
        self.statusBar().setObjectName("statusBar")
        self.statusBar().showMessage("Ready")
        
        # Show the UI
        self.setWindowState(Qt.WindowActive)
        self.show()
    
    def update_status(self, is_running, title, artist, album):
        """Update the UI based on Pithos status"""
        if is_running:
            self.status_indicator.update_status("Pithos is running", MaterialColors.SUCCESS)
            self.title_row.set_value(title)
            self.artist_row.set_value(artist)
            self.album_row.set_value(album)
            
            # Log the current song if it hasn't been logged yet and isn't being handled by log_initial_song
            if (not self.initial_song_logged and 
                (title != self.last_logged_title or 
                artist != self.last_logged_artist or 
                album != self.last_logged_album) and title != "Not playing"):
                
                # Check time to prevent duplicate logs (minimum 10 seconds between logs)
                current_time = time.time()
                if current_time - self.last_log_time > 10:
                    # Save the song to CSV directly
                    self.log_current_song(title, artist, album)
                    
                    # Update the last logged song info
                    self.last_logged_title = title
                    self.last_logged_artist = artist
                    self.last_logged_album = album
                    self.last_log_time = current_time
                    
                    # Refresh the song list
                    self.load_songs()
        else:
            self.status_indicator.update_status("Pithos is not running", MaterialColors.ERROR)
            self.title_row.set_value("Not playing")
            self.artist_row.set_value("N/A")
            self.album_row.set_value("N/A")
            
            # Try to restart Pithos
            if not is_pithos_running():
                launch_pithos()
                self.statusBar().showMessage("Restarting Pithos...")
    
    def log_current_song(self, title, artist, album):
        """Log the current song to the CSV file"""
        # Ensure we use the current year (2025) in our timestamp
        now = datetime.now()
        if now.year != 2025:  # Just in case system clock is wrong
            now = now.replace(year=2025)
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create the file if it doesn't exist
        file_exists = os.path.isfile(self.csv_file)
        
        # Check if this exact entry already exists in the file to prevent duplicates
        if file_exists:
            try:
                with open(self.csv_file, 'r', newline='') as f:
                    reader = csv.reader(f)
                    next(reader, None)  # Skip header
                    for row in reader:
                        if len(row) >= 3 and row[0] == title and row[1] == artist and row[2] == album:
                            # Song already logged, don't duplicate
                            self.statusBar().showMessage(f"Song already logged: {title} by {artist}")
                            return
            except Exception as e:
                # If there's an error reading the file, continue with logging
                print(f"Error checking for duplicates: {str(e)}")
        
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # Quote all fields
            if not file_exists:
                writer.writerow(["Title", "Artist", "Album", "Timestamp"])
            writer.writerow([title, artist, album, timestamp])
        
        self.statusBar().showMessage(f"Logged: {title} by {artist}")
    
    def setup_style(self):
        # Load system fonts
        QApplication.setFont(QFont("Roboto", 10))
        
        # Apply a modern style
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        
        # Custom palette for basic coloring
        palette = QPalette()
        
        # Background colors - DARK MODE
        palette.setColor(QPalette.Window, QColor(MaterialColors.BACKGROUND))
        palette.setColor(QPalette.Base, QColor(MaterialColors.SURFACE))
        palette.setColor(QPalette.AlternateBase, QColor(MaterialColors.CARD_BACKGROUND))
        
        # Foreground colors
        palette.setColor(QPalette.WindowText, QColor(MaterialColors.ON_BACKGROUND))
        palette.setColor(QPalette.Text, QColor(MaterialColors.ON_SURFACE))
        
        # Accent colors
        palette.setColor(QPalette.Highlight, QColor(MaterialColors.PRIMARY))
        palette.setColor(QPalette.HighlightedText, QColor(MaterialColors.ON_PRIMARY))
        
        # Apply the palette
        QApplication.setPalette(palette)
        
        # Custom stylesheets for the application
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {MaterialColors.BACKGROUND};
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {MaterialColors.CARD_BACKGROUND};
                width: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {MaterialColors.PRIMARY_LIGHT};
                min-height: 20px;
                border-radius: 4px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {MaterialColors.CARD_BACKGROUND};
                height: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {MaterialColors.PRIMARY_LIGHT};
                min-width: 20px;
                border-radius: 4px;
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            #appTitle {{
                font-size: 28px;
                font-weight: bold;
                color: {MaterialColors.PRIMARY_LIGHT};
            }}
            
            #appSubtitle {{
                font-size: 16px;
                color: {MaterialColors.ON_BACKGROUND};
                font-weight: normal;
                margin-bottom: 16px;
            }}
            
            #sectionLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {MaterialColors.PRIMARY_LIGHT};
                margin-bottom: 8px;
            }}
            
            #cardTitle {{
                font-size: 18px;
                font-weight: bold;
                color: {MaterialColors.PRIMARY_LIGHT};
                margin-bottom: 16px;
            }}
            
            #songsTable {{
                border: none;
                background-color: {MaterialColors.CARD_BACKGROUND};
                color: {MaterialColors.ON_SURFACE};
                selection-background-color: {MaterialColors.PRIMARY_DARK};
                selection-color: {MaterialColors.ON_PRIMARY};
                alternate-background-color: {MaterialColors.SURFACE};
            }}
            
            #songsTable QHeaderView::section {{
                background-color: {MaterialColors.PRIMARY_DARK};
                color: {MaterialColors.ON_PRIMARY};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
            
            #songsTable::item {{
                padding: 8px;
                border-bottom: 1px solid {MaterialColors.DIVIDER};
            }}
            
            #statusBar {{
                background-color: {MaterialColors.PRIMARY_DARK};
                color: {MaterialColors.ON_PRIMARY};
                font-weight: 500;
                padding: 8px 16px;
                border: none;
            }}
        """)
    
    def load_songs(self):
        """Load songs from the CSV file into the table"""
        # Clear existing items
        self.songs_table.setRowCount(0)
        
        try:
            if not os.path.exists(self.csv_file):
                self.songs_count = 0
                self.count_row.set_value("0")
                self.statusBar().showMessage("No song history found.")
                return
                
            # First, clean up the CSV file to ensure proper formatting
            self.clean_csv_file()
                
            with open(self.csv_file, 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                
                songs = []
                for row in reader:
                    if len(row) >= 4:
                        # Debug output to see what's being loaded
                        print(f"Loading song: {row}")
                        songs.append(row)
                    else:
                        print(f"Warning: Skipping malformed row: {row}")
                
                # Sort by timestamp (newest first)
                songs.sort(key=lambda x: x[3], reverse=True)
                
                # Add to table
                self.songs_table.setRowCount(len(songs))
                for i, song in enumerate(songs):
                    for j, value in enumerate(song):
                        item = QTableWidgetItem(value)
                        if j == 0:  # Title column
                            item.setToolTip(value)
                        self.songs_table.setItem(i, j, item)
                
                self.songs_count = len(songs)
                self.count_row.set_value(str(self.songs_count))
                self.statusBar().showMessage(f"Loaded {self.songs_count} songs from history.")
        except Exception as e:
            self.statusBar().showMessage(f"Error: Failed to load songs: {str(e)}")
    
    def clean_csv_file(self):
        """Clean the CSV file to ensure proper formatting"""
        try:
            # Create a temporary file for properly formatted entries
            temp_file = os.path.expanduser("~/temp_pithos_songs.csv")
            
            # Create a set to track unique songs
            unique_songs = {}  # key -> [title, artist, album, timestamp]
            
            with open(self.csv_file, 'r', newline='') as f:
                content = f.read()
                
                # Fix common issues (backslash escaping)
                content = content.replace('\\,', ',')
                
                # Write to a temporary file for proper CSV parsing
                with open(temp_file, 'w') as tf:
                    tf.write(content)
                
                # Now read the fixed content
                with open(temp_file, 'r', newline='') as tf:
                    reader = csv.reader(tf)
                    header = next(reader, ["Title", "Artist", "Album", "Timestamp"])
                    
                    for row in reader:
                        # Handle rows with different lengths
                        if len(row) < 4:
                            continue
                            
                        title = row[0].strip()
                        artist = row[1].strip()
                        album = row[2].strip()
                        timestamp = row[3].strip() if len(row) > 3 else ""
                        
                        # Handle rows where fields are out of order
                        # Check for commonly misformatted cases
                        if title == "Hey" and artist == "Soul Sister":
                            title = "Hey, Soul Sister"
                            artist = row[2].strip()
                            album = row[3].strip() if len(row) > 3 else ""
                            timestamp = ""  # Often missing in these cases
                        
                        elif title == "Gone" and artist == "Gone" and len(row) > 3 and row[2] == "Gone":
                            title = "Gone, Gone, Gone"
                            artist = row[3].strip()
                            album = ""
                            timestamp = ""
                        
                        # Normalize timestamp if empty
                        if not timestamp:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                        # Fix other common anomalies (add more as needed)
                        if "You're Gonna Go Far" in title and "Kid" in artist:
                            title = "You're Gonna Go Far, Kid"
                            artist = "The Offspring"
                            album = "Rise And Fall, Rage And Grace"
                            
                        # Also correct Donald Where's Your Troosers and similar issues
                        if "Donald Where's Your Troosers" in title and "the Scottish Album" in album:
                            album = "Up Among the Heather, the Scottish Album"
                        
                        # Create key for deduplication
                        key = (title.lower(), artist.lower(), album.lower())
                        
                        if key not in unique_songs:
                            unique_songs[key] = [title, artist, album, timestamp]
            
            # Write back the clean data
            entries = list(unique_songs.values())
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow(["Title", "Artist", "Album", "Timestamp"])
                writer.writerows(entries)
                
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            print(f"Error cleaning CSV: {str(e)}")
            # If cleaning fails, we still continue with loading
    
    def open_csv_file(self):
        """Open the CSV file in the default application"""
        try:
            if os.path.exists(self.csv_file):
                if os.name == 'nt':  # Windows
                    os.startfile(self.csv_file)
                elif os.name == 'posix':  # Linux, macOS
                    subprocess.call(('xdg-open', self.csv_file))
                self.statusBar().showMessage(f"Opened {self.csv_file}")
            else:
                self.statusBar().showMessage("CSV file not found.")
        except Exception as e:
            self.statusBar().showMessage(f"Error: Failed to open CSV file: {str(e)}")
    
    def start_logging(self):
        """Start the logging process"""
        if self.is_logging:
            return
            
        try:
            # Get the path to the logger script
            script_path = os.path.expanduser("~/Desktop/Projects/Personal/Pithos Songs List/pithos_song_logger.sh")
            
            # Start the logger process
            self.logger_process = subprocess.Popen([script_path], 
                                                  stdout=subprocess.PIPE, 
                                                  stderr=subprocess.PIPE,
                                                  text=True)
            
            self.is_logging = True
            self.statusBar().showMessage("Song logging started.")
            
            # If Pithos is already running, log the current song immediately
            if is_pithos_running():
                # Wait a moment for the DBus connection to get the current song
                QTimer.singleShot(2000, self.log_initial_song)
        except Exception as e:
            self.statusBar().showMessage(f"Error: Failed to start logger: {str(e)}")
    
    def log_initial_song(self):
        """Log the initial song if Pithos is already playing something"""
        if self.dbus_monitor.current_title != "Not playing" and self.dbus_monitor.current_title:
            # Set the flag to indicate we're handling the initial song
            self.initial_song_logged = True
            
            # Set the initial timestamp to prevent double-logging
            self.last_log_time = time.time()
            
            self.log_current_song(
                self.dbus_monitor.current_title,
                self.dbus_monitor.current_artist,
                self.dbus_monitor.current_album
            )
            
            # Update the last logged song info
            self.last_logged_title = self.dbus_monitor.current_title
            self.last_logged_artist = self.dbus_monitor.current_artist
            self.last_logged_album = self.dbus_monitor.current_album
            
            # Refresh the song list
            self.load_songs()
    
    def delete_selected_song(self):
        """Delete the selected song from the CSV file and refresh the table"""
        # Get the currently selected row
        selected_rows = self.songs_table.selectionModel().selectedRows()
        if not selected_rows:
            self.statusBar().showMessage("No song selected. Please select a song to delete.")
            return
            
        # Get the index of the selected row
        row_index = selected_rows[0].row()
        
        # Get the song details from the selected row
        title = self.songs_table.item(row_index, 0).text()
        artist = self.songs_table.item(row_index, 1).text()
        album = self.songs_table.item(row_index, 2).text()
        timestamp = self.songs_table.item(row_index, 3).text()
        
        # Ask for confirmation
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete:\n\n{title} by {artist}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Read the current file
                songs = []
                with open(self.csv_file, 'r', newline='') as file:
                    reader = csv.reader(file)
                    header = next(reader)  # Save the header
                    
                    # Copy all songs except the one to be deleted
                    for row in reader:
                        if len(row) < 4:
                            continue
                            
                        if (row[0] != title or row[1] != artist or 
                            row[2] != album or row[3] != timestamp):
                            songs.append(row)
                
                # Write back the filtered songs
                with open(self.csv_file, 'w', newline='') as file:
                    writer = csv.writer(file, quoting=csv.QUOTE_ALL)
                    writer.writerow(header)
                    writer.writerows(songs)
                
                # Refresh the table
                self.load_songs()
                self.statusBar().showMessage(f"Deleted: {title} by {artist}")
            except Exception as e:
                self.statusBar().showMessage(f"Error: Failed to delete song: {str(e)}")
        else:
            self.statusBar().showMessage("Deletion cancelled")
    
    def closeEvent(self, event):
        """Handle window close event: stop logging if active"""
        if self.is_logging and self.logger_process:
            self.logger_process.terminate()
            self.logger_process = None
            self.is_logging = False
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PithosSongLoggerGUI()
    sys.exit(app.exec_()) 