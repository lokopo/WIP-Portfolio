#!/usr/bin/env python3

import subprocess
import time
import os
import sys
import logging
import threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QLabel, QWidget, QTextEdit,
                            QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QColor

# Set up logging
log_dir = os.path.expanduser("~/.logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "bluetooth_connector.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Color for terminal output
class Colors:
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'

# Signal class for thread-safe GUI updates
class LogSignals(QObject):
    update_log = pyqtSignal(str, str)  # message, level
    update_status = pyqtSignal(bool)   # connected status

class BluetoothConnector:
    def __init__(self):
        self.signals = LogSignals()
        self.is_running = False
        self.thread = None
        self.device_name = "Momentum 4"  # Default device
        self.mac_address = None
        # Keep trying frequently
        self.retry_interval = 5  # seconds between retry attempts
        self.check_interval = 10  # seconds between connection checks
        self.stop_requested = False
        self.connected = False
        self.connection_attempts = 0
        self.max_attempts_before_reset = 3  # Reset more frequently
        self.connection_timeout = 15
        self.scan_duration = 30
        self.permanent_retry = True
        self.aggressive_reset_interval = 60  # Reset every minute if needed
        self.last_aggressive_reset_time = 0
        self.pairing_attempts = 0
        self.prevent_disconnection = True

    def run_command(self, command):
        """Run a command and return the output"""
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    def get_device_info(self, device_name):
        """Get MAC address of the Bluetooth device by name"""
        returncode, output, _ = self.run_command("bluetoothctl devices | grep -i \"" + device_name + "\"")
        if returncode != 0 or not output:
            # PASSIVE: Try a direct scan but be more patient
            self.log_message(f"Device '{device_name}' not found in paired devices. Scanning...", "warning")
            self.run_command("bluetoothctl scan on")
            time.sleep(10)  # Longer scan
            self.run_command("bluetoothctl scan off")
            # Try again
            returncode, output, _ = self.run_command("bluetoothctl devices | grep -i \"" + device_name + "\"")
            if returncode != 0 or not output:
                return None
        
        # Output format: "Device XX:XX:XX:XX:XX:XX Device Name"
        parts = output.strip().split(' ', 2)
        if len(parts) >= 2:
            return parts[1]  # MAC address
        return None

    def is_device_connected(self, mac_address):
        """Check if device is truly connected"""
        # First check basic connection status
        returncode, output, _ = self.run_command(f"bluetoothctl info {mac_address} | grep 'Connected: yes'")
        if returncode != 0 or "Connected: yes" not in output:
            return False
            
        # Then verify the connection is actually working
        returncode, output, _ = self.run_command(f"bluetoothctl info {mac_address}")
        if returncode != 0:
            return False
            
        # Check for actual connection indicators
        if "Connected: yes" in output and "Paired: yes" in output and "Trusted: yes" in output:
            # Double check with system audio
            returncode, output, _ = self.run_command("pactl list sinks | grep -i 'bluetooth'")
            if returncode == 0 and output.strip():
                self.log_message(f"Device is connected and audio sink is available.", "success")
                return True
            else:
                self.log_message(f"Device shows as connected but no audio sink found.", "warning")
                return False
                
        return False

    def verify_true_connection(self, mac_address):
        """PASSIVE: Trust system connection completely - no verification attempts"""
        # Just return the basic connection status without extra checks
        return self.is_device_connected(mac_address)

    def force_disconnect_device(self, mac_address):
        """PASSIVE: Disabled disconnect to prevent interruptions"""
        if self.prevent_disconnection:
            self.log_message(f"Active disconnection disabled - letting system handle connection", "info")
            return False
        
        # This code will not run if prevent_disconnection is True
        self.log_message(f"Attempting gentle disconnect without unpairing...", "warning")
        self.run_command(f"bluetoothctl disconnect {mac_address}")
        time.sleep(1)
        return True

    def connect_device(self, mac_address, device_name):
        """Connect to device"""
        self.log_message(f"Attempting to connect to {device_name}...", "info")
        
        # Try to pair and trust
        self.run_command(f"bluetoothctl pair {mac_address}")
        self.run_command(f"bluetoothctl trust {mac_address}")
        
        # Connect
        self.run_command(f"bluetoothctl connect {mac_address}")
        time.sleep(5)  # Give it time to connect
        
        # Check if connected
        if self.is_device_connected(mac_address):
            self.log_message(f"Successfully connected to {device_name}.", "success")
            return True
        
        self.log_message(f"Failed to connect.", "error")
        return False

    def activate_audio_profile(self, mac_address, device_name):
        """Check audio profile status without interfering"""
        # Check current audio status
        _, card_info, _ = self.run_command("pactl list cards | grep -A 30 'Name: bluez_card'")
        
        # If we see audio profiles available, everything is fine
        if 'a2dp-sink' in card_info.lower() or 'headset-head-unit' in card_info.lower():
            self.log_message("Audio profiles are available.", "success")
            return True
        
        # Only try to fix if we don't see any audio profiles
        self.log_message("No audio profiles detected, attempting to reconnect...", "warning")
        self.run_command(f"bluetoothctl disconnect {mac_address}")
        time.sleep(2)
        self.run_command(f"bluetoothctl connect {mac_address}")
        return False

    def gentle_reset(self):
        """PASSIVE: Much gentler reset that preserves connections"""
        self.log_message("Performing gentle Bluetooth refresh without disconnecting devices...", "warning")
        
        # Just power cycle without stopping services or unpairing
        self.run_command("bluetoothctl power off")
        time.sleep(3)  # Give time for clean shutdown
        self.run_command("bluetoothctl power on")
        time.sleep(5)  # Give time to initialize
        
        # Ensure discoverable and pairable mode
        self.run_command("bluetoothctl discoverable on")
        self.run_command("bluetoothctl pairable on")
        
        self.log_message("Gentle Bluetooth refresh completed.", "info")

    def thorough_reset(self):
        """PASSIVE: Method kept for extreme cases but not used in normal operation"""
        # This method is preserved but not used in the passive approach
        self.log_message("This method is disabled in passive mode", "info")
        return

    def log_message(self, message, level="info"):
        """Log a message to both file and GUI"""
        if level == "info":
            logging.info(message)
        elif level == "warning":
            logging.warning(message)
        elif level == "error":
            logging.error(message)
        elif level == "success":
            logging.info(message)  # Log success as info in file
        
        # Send to GUI
        self.signals.update_log.emit(message, level)

    def enable_pairing_mode(self):
        """Put Bluetooth in pairing mode and scan for devices"""
        self.log_message("Entering Bluetooth pairing mode...", "info")
        
        # Make adapter discoverable and pairable
        self.run_command("bluetoothctl discoverable on")
        self.run_command("bluetoothctl pairable on")
        
        # Start scanning for devices
        self.log_message(f"Scanning for devices for {self.scan_duration} seconds...", "info")
        
        # First, stop any existing scan
        self.run_command("bluetoothctl scan off")
        time.sleep(1)
        
        # Start a new scan
        scan_process = subprocess.Popen(
            "bluetoothctl scan on",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        # Keep scanning for the specified duration with checks
        start_time = time.time()
        
        # Check periodically for target device while scanning
        while time.time() - start_time < self.scan_duration and not self.stop_requested:
            # Check if our target device has appeared
            found_mac = self.get_device_info(self.device_name)
            if found_mac:
                self.log_message(f"Found {self.device_name} during scan with MAC: {found_mac}", "success")
                self.mac_address = found_mac  # Update the MAC address
                
                # Try to pair
                self.pair_with_device(found_mac)
                scan_process.terminate()
                self.run_command("bluetoothctl scan off")
                return found_mac
            
            # Sleep before checking again
            time.sleep(2)  # Check more frequently
        
        # Stop scanning
        scan_process.terminate()
        self.run_command("bluetoothctl scan off")
        
        # Final check for device
        found_mac = self.get_device_info(self.device_name)
        if found_mac:
            self.log_message(f"Found {self.device_name} at end of scan with MAC: {found_mac}", "success")
            self.mac_address = found_mac  # Update the MAC address
            self.pair_with_device(found_mac)
            return found_mac
        
        self.log_message(f"Could not find {self.device_name} during pairing scan. Will try again later.", "warning")
        return None
    
    def pair_with_device(self, mac_address):
        """PASSIVE: Pair with device but don't force it if already paired"""
        self.log_message(f"Attempting to pair with device at {mac_address}...", "info")
        
        # First check if already paired to avoid unnecessary operations
        _, paired_output, _ = self.run_command(f"bluetoothctl info {mac_address} | grep 'Paired: yes'")
        if "Paired: yes" in paired_output:
            self.log_message(f"Device is already paired. Proceeding with connection.", "success")
            
            # Ensure it's trusted
            self.run_command(f"bluetoothctl trust {mac_address}")
            
            # Try to connect directly
            return self.connect_device(mac_address, self.device_name)
        
        # If not paired, proceed with pairing
        self.log_message(f"Device not paired. Attempting pairing...", "info")
        
        # Try to pair with the device
        returncode, output, error = self.run_command(f"bluetoothctl pair {mac_address}")
        
        if returncode == 0 and ("Pairing successful" in output or "successful" in output):
            self.log_message(f"Successfully paired with device.", "success")
            
            # Trust the device for future connections
            self.run_command(f"bluetoothctl trust {mac_address}")
            self.log_message(f"Device added to trusted devices.", "success")
            
            # Try to connect
            return self.connect_device(mac_address, self.device_name)
        else:
            self.log_message(f"Pairing attempt failed. Will try again later.", "warning")
            if error and error.strip():
                self.log_message(f"Error: {error.strip()}", "error")
            return False

    def monitor_connection(self):
        """Monitor headphone connection"""
        # Start timestamp for the log
        start_time = datetime.now()
        self.log_message(f"=== Starting Bluetooth monitor at {start_time} ===", "info")
        
        # Check if bluetoothctl is available
        returncode, _, _ = self.run_command("which bluetoothctl")
        if returncode != 0:
            self.log_message("bluetoothctl not found. Please install bluez utilities.", "error")
            return
        
        # Enable discoverable and pairable mode
        self.run_command("bluetoothctl discoverable on")
        self.run_command("bluetoothctl pairable on")
        
        self.stop_requested = False
        
        while not self.stop_requested:
            # Get the MAC address for the device
            self.mac_address = self.get_device_info(self.device_name)
            
            if self.mac_address:
                # Check connection status
                if not self.is_device_connected(self.mac_address):
                    self.log_message(f"Device disconnected, attempting to reconnect...", "info")
                    if self.connect_device(self.mac_address, self.device_name):
                        self.connected = True
                        self.signals.update_status.emit(True)
            else:
                self.log_message(f"Searching for {self.device_name}...", "info")
                self.enable_pairing_mode()
            
            # Wait between checks
            time.sleep(5)
        
        self.log_message("Bluetooth monitor stopped.", "info")
        self.is_running = False

    def start(self):
        """Start the connector in a separate thread"""
        if not self.is_running:
            self.is_running = True
            self.stop_requested = False  # Reset stop flag
            self.thread = threading.Thread(target=self.monitor_connection)
            self.thread.daemon = True
            self.thread.start()
            return True
        return False

    def stop(self):
        """Stop the connector thread"""
        if self.is_running:
            self.log_message("Stop requested. Shutting down...", "info")
            self.stop_requested = True
            return True
        return False


class BluetoothConnectorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.connector = BluetoothConnector()
        self.connector.signals.update_log.connect(self.update_log)
        self.connector.signals.update_status.connect(self.update_status)
        self.init_ui()
        self.init_tray()
        
        # Set up a timer to periodically update button states based on actual thread state
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_button_states)
        self.update_timer.start(1000)  # Check button states every second
        
        # Start monitoring automatically
        self.start_connector()

    def init_ui(self):
        self.setWindowTitle(f"Headphone Monitor - {self.connector.device_name}")
        self.setGeometry(300, 300, 500, 300)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Status display
        self.status_label = QLabel("Status: Checking...")
        self.status_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.start_connector)
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.clicked.connect(self.stop_connector)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        # Log display
        log_label = QLabel("Connection Log:")
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        # Add all widgets to main layout
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_display)
        
        # Set the main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def init_tray(self):
        """Initialize system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("bluetooth"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def update_button_states(self):
        """Update button states based on the actual running state of the connector thread"""
        if self.connector.is_running:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def start_connector(self):
        """Start the Bluetooth connector"""
        if self.connector.is_running:
            self.log_display.append("Monitor is already running.")
            return
            
        success = self.connector.start()
        if success:
            self.log_display.append("Starting trusting headphone connection monitor...")
            # Button states will be updated by the timer
        else:
            self.log_display.append("Failed to start monitoring.")

    def stop_connector(self):
        """Stop the Bluetooth connector"""
        if not self.connector.is_running:
            self.log_display.append("Monitor is not running.")
            return
            
        if self.connector.stop():
            self.log_display.append("Stopping headphone connection monitor...")
            # Force update buttons immediately
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            # Also add a timeout for safety
            QTimer.singleShot(5000, self.force_stop_if_needed)
        else:
            self.log_display.append("Failed to stop monitoring.")
    
    def force_stop_if_needed(self):
        """Force stop after timeout if thread is still running"""
        if self.connector.is_running:
            self.log_display.append("Force stopping monitor thread...")
            self.connector.is_running = False
            self.update_button_states()

    @pyqtSlot(bool)
    def update_status(self, connected):
        """Update the connection status display"""
        if connected:
            self.status_label.setText("Status: CONNECTED")
            self.status_label.setStyleSheet("padding: 10px; border: 1px solid #00aa00; border-radius: 5px; background-color: #ddffdd; color: #00aa00;")
            self.tray_icon.setToolTip(f"{self.connector.device_name}: Connected")
        else:
            self.status_label.setText("Status: DISCONNECTED")
            self.status_label.setStyleSheet("padding: 10px; border: 1px solid #aa0000; border-radius: 5px; background-color: #ffdddd; color: #aa0000;")
            self.tray_icon.setToolTip(f"{self.connector.device_name}: Disconnected")

    @pyqtSlot(str, str)
    def update_log(self, message, level):
        """Update the log display with a new message"""
        # Save current position
        scrollbar = self.log_display.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()
        
        # Format message based on level
        if level == "error":
            formatted_message = f"<span style='color:red'>{message}</span>"
        elif level == "warning":
            formatted_message = f"<span style='color:orange'>{message}</span>"
        elif level == "success":
            formatted_message = f"<span style='color:green'>{message}</span>"
        else:  # info
            formatted_message = message
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {formatted_message}"
        
        # Append to log
        self.log_display.append(log_entry)
        
        # If we were at the bottom, scroll to the bottom again
        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())
        
        # If connector has stopped, update UI
        if "Bluetooth monitor stopped" in message or "Stop requested" in message:
            # Wait a moment for is_running to be updated
            QTimer.singleShot(500, self.update_button_states)

    def closeEvent(self, event):
        """Handle window close event - full application exit"""
        # Properly close the application instead of minimizing to tray
        self.close_application()
        event.accept()  # Accept the close event to allow the window to close

    def close_application(self):
        """Properly close the application"""
        if self.connector.is_running:
            self.connector.stop()
            # Wait a bit for the thread to stop
            for _ in range(5):
                if not self.connector.is_running:
                    break
                time.sleep(0.1)
        self.tray_icon.hide()
        QApplication.quit()


if __name__ == "__main__":
    # Check if another instance is already running
    import subprocess
    import sys
    import os
    
    # Get the name of this script without path
    script_name = os.path.basename(__file__)
    
    # Check if there's already a running instance
    process = subprocess.Popen(['pgrep', '-f', script_name], stdout=subprocess.PIPE)
    output, _ = process.communicate()
    
    running_pids = [int(pid) for pid in output.decode().split()]
    current_pid = os.getpid()
    
    # Remove our own PID from the list
    if current_pid in running_pids:
        running_pids.remove(current_pid)
    
    # If there are other instances running, exit
    if running_pids:
        print(f"Another instance of {script_name} is already running. Exiting.")
        sys.exit(0)
    
    # No other instances found, proceed with normal startup
    app = QApplication(sys.argv)
    window = BluetoothConnectorGUI()
    window.show()
    sys.exit(app.exec_()) 