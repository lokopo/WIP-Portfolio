# System Power Control GUI

A simple PyQt5 application that provides a graphical interface for system power operations such as shutdown, restart, and logout.

## Features

* Shutdown, restart, or log out your system
* Execute actions immediately or with a timer
* Countdown timer with a cancel option
* Simple and easy-to-use interface

## Requirements

* Python 3.6+
* PyQt5

## Installation

1. Clone this repository or download the files.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application with:

```bash
python system_power_gui.py
```

### Using the Application

1. Select the desired action (Shutdown, Restart, or Log Out)
2. Choose between immediate action or setting a timer
3. If using a timer, specify the number of minutes
4. Click "Execute" to perform the action

## Note

This application uses system commands to perform power operations. Admin/sudo privileges may be required for some actions. 