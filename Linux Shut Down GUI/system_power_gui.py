#!/usr/bin/env python3
import sys
import os
import time
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QRadioButton, QButtonGroup, QSpinBox, QLabel,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont

class SystemPowerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = None
        self.countdown_seconds = 0
        self.action_in_progress = False

    def initUI(self):
        self.setWindowTitle('System Power Controls')
        self.setGeometry(300, 300, 500, 350)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Action selection group
        action_group_box = QGroupBox("System Action")
        action_layout = QVBoxLayout()
        
        # Radio buttons for actions
        self.action_group = QButtonGroup(self)
        
        self.shutdown_radio = QRadioButton("Shutdown")
        self.restart_radio = QRadioButton("Restart")
        self.logout_radio = QRadioButton("Log Out")
        
        self.shutdown_radio.setChecked(True)
        
        self.action_group.addButton(self.shutdown_radio)
        self.action_group.addButton(self.restart_radio)
        self.action_group.addButton(self.logout_radio)
        
        action_layout.addWidget(self.shutdown_radio)
        action_layout.addWidget(self.restart_radio)
        action_layout.addWidget(self.logout_radio)
        
        action_group_box.setLayout(action_layout)
        
        # Timing options group
        timing_group_box = QGroupBox("Timing Options")
        timing_layout = QVBoxLayout()
        
        # Instant action
        self.instant_radio = QRadioButton("Immediate Action")
        
        # Timer action
        self.timer_radio = QRadioButton("Set Timer")
        self.instant_radio.setChecked(True)
        
        # Timer spinner
        timer_layout = QHBoxLayout()
        timer_layout.addWidget(self.timer_radio)
        
        self.minute_spinner = QSpinBox()
        self.minute_spinner.setRange(0, 60)
        self.minute_spinner.setValue(1)
        self.minute_spinner.setEnabled(False)
        
        timer_layout.addWidget(self.minute_spinner)
        timer_layout.addWidget(QLabel("minutes"))
        
        # Add radio buttons to a group
        self.timing_group = QButtonGroup(self)
        self.timing_group.addButton(self.instant_radio)
        self.timing_group.addButton(self.timer_radio)
        
        timing_layout.addWidget(self.instant_radio)
        timing_layout.addLayout(timer_layout)
        
        timing_group_box.setLayout(timing_layout)
        
        # Connect radio button to enable/disable spinner
        self.timer_radio.toggled.connect(self.toggle_timer_spinner)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Cancel button (hidden initially)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_action)
        self.cancel_button.setVisible(False)
        
        # Execute button
        execute_button = QPushButton("Execute")
        execute_button.clicked.connect(self.execute_action)
        execute_button.setMinimumHeight(50)
        
        # Add widgets to main layout
        main_layout.addWidget(action_group_box)
        main_layout.addWidget(timing_group_box)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.cancel_button)
        main_layout.addWidget(execute_button)
        
        self.show()
    
    def toggle_timer_spinner(self, checked):
        self.minute_spinner.setEnabled(checked)
    
    def execute_action(self):
        if self.action_in_progress:
            return
            
        # Get selected action
        if self.shutdown_radio.isChecked():
            action = "shutdown"
            action_name = "Shutdown"
        elif self.restart_radio.isChecked():
            action = "reboot"
            action_name = "Restart"
        elif self.logout_radio.isChecked():
            action = "logout"
            action_name = "Log Out"
        
        # Get timing option
        if self.instant_radio.isChecked():
            # Confirm before immediate action
            reply = QMessageBox.question(
                self, 'Confirm Action',
                f'Are you sure you want to {action_name.lower()} now?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.perform_action(action, 0)
        else:
            # Get minutes from spinner
            minutes = self.minute_spinner.value()
            if minutes == 0:
                QMessageBox.warning(self, 'Warning', 'Please set a time greater than 0 minutes or select immediate action.')
                return
                
            self.action_in_progress = True
            self.countdown_seconds = minutes * 60
            self.status_label.setText(f"{action_name} in {minutes} minute(s)...")
            self.cancel_button.setVisible(True)
            
            # Start countdown
            self.timer = QTimer()
            self.timer.timeout.connect(lambda: self.update_countdown(action))
            self.timer.start(1000)  # Update every second
    
    def update_countdown(self, action):
        self.countdown_seconds -= 1
        
        minutes = self.countdown_seconds // 60
        seconds = self.countdown_seconds % 60
        
        self.status_label.setText(f"Action in {minutes:02d}:{seconds:02d}")
        
        if self.countdown_seconds <= 0:
            self.timer.stop()
            self.perform_action(action, 0)
    
    def cancel_action(self):
        if self.timer:
            self.timer.stop()
        
        self.action_in_progress = False
        self.status_label.setText("Action cancelled")
        self.cancel_button.setVisible(False)
    
    def perform_action(self, action, delay_minutes):
        # Build the command based on the selected action
        if action == "shutdown":
            if delay_minutes > 0:
                cmd = f"shutdown -h {delay_minutes}"
            else:
                cmd = "shutdown -h now"
        elif action == "reboot":
            if delay_minutes > 0:
                cmd = f"shutdown -r {delay_minutes}"
            else:
                cmd = "shutdown -r now"
        elif action == "logout":
            # For logout, we'll use different commands depending on the desktop environment
            # This is a simplified version, might need adjustments based on your desktop environment
            cmd = "gnome-session-quit --no-prompt"
        
        try:
            if delay_minutes == 0:
                self.status_label.setText(f"Executing {action} now...")
                # Run in a separate thread to not block the UI
                threading.Thread(target=lambda: os.system(cmd)).start()
            else:
                self.status_label.setText(f"Scheduled {action} in {delay_minutes} minutes")
                threading.Thread(target=lambda: os.system(cmd)).start()
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.action_in_progress = False
            self.cancel_button.setVisible(False)

def main():
    app = QApplication(sys.argv)
    ex = SystemPowerGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 