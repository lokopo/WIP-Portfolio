#!/bin/bash

# Kill any existing instances
pkill -f bluetooth_gui.py

# Wait a moment for processes to terminate
sleep 1

# Start Bluetooth Headphone Monitor
cd "/home/luke-thomas/Desktop/Projects/Personal/Desktop Widgets/bluetooth"
./bluetooth_gui.py & 