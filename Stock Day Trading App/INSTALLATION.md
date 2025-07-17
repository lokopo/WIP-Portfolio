# Installation Guide - Stock Day Trading App

## System Requirements

### Operating System
- **Windows 10/11** (Recommended)
- **macOS 10.14+**
- **Linux** (Ubuntu 18.04+, CentOS 7+)

### Python Requirements
- **Python 3.8 or higher**
- **pip** (Python package installer)

### Hardware Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Display**: 1024x768 minimum resolution
- **Internet**: Required for market data

## Installation Steps

### Step 1: Install Python
1. **Download Python** from [python.org](https://www.python.org/downloads/)
2. **Install Python** with pip included
3. **Verify installation**:
   ```bash
   python --version
   pip --version
   ```

### Step 2: Download the App
1. **Clone or download** the project files
2. **Navigate to the project directory**:
   ```bash
   cd "Stock Day Trading App"
   ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment (Optional)
1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```
2. **Edit .env** with your settings (optional)

### Step 5: Run the Application
```bash
python run.py
```

## Troubleshooting Installation

### Common Issues

#### Python Not Found
```bash
# Windows
python --version
# If not found, try:
py --version

# macOS/Linux
python3 --version
```

#### Permission Errors
```bash
# Windows: Run as Administrator
# macOS/Linux:
sudo pip install -r requirements.txt
```

#### Package Installation Errors
```bash
# Upgrade pip first
pip install --upgrade pip

# Install packages individually if needed
pip install customtkinter
pip install pyautogui
pip install yfinance
# ... etc
```

#### Display Issues (Linux)
```bash
# Install required system packages
sudo apt-get install python3-tk
sudo apt-get install python3-dev
```

### Platform-Specific Instructions

#### Windows
1. **Install Python** from python.org
2. **Add Python to PATH** during installation
3. **Run Command Prompt as Administrator** if needed
4. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

#### macOS
1. **Install Python** using Homebrew (recommended):
   ```bash
   brew install python
   ```
2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

#### Linux (Ubuntu/Debian)
1. **Install system dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-tk
   ```
2. **Install Python packages**:
   ```bash
   pip3 install -r requirements.txt
   ```

## Verification

### Test Installation
1. **Run the launcher**:
   ```bash
   python run.py
   ```
2. **Check for errors** in the console
3. **Verify GUI loads** correctly
4. **Test basic functionality**:
   - Click "Add Click Position"
   - Move mouse to see coordinates
   - Check if markers appear

### Test Market Data
1. **Go to Charts tab**
2. **Select a symbol** (e.g., AAPL)
3. **Verify chart loads** with data

## Security Considerations

### File Permissions
- **Keep the app directory secure**
- **Don't share your .env file**
- **Use strong passwords** for trading accounts

### Network Security
- **Use secure internet connection**
- **Consider VPN** for additional security
- **Don't run on public networks**

### Trading Security
- **Use paper trading first**
- **Start with small amounts**
- **Monitor all automated trades**
- **Have emergency stop procedures**

## Uninstallation

### Remove Python Packages
```bash
pip uninstall -r requirements.txt
```

### Remove Application Files
```bash
# Delete the entire project directory
rm -rf "Stock Day Trading App"
```

### Clean Up Configuration
```bash
# Remove saved configuration files
rm -f commands.json
rm -f trading_config.json
rm -f window_state.json
```

## Support

### Getting Help
1. **Check the Quick Start Guide** (QUICK_START.md)
2. **Read the main README** (README.md)
3. **Review error messages** carefully
4. **Test with paper trading first**

### Common Solutions
- **Restart the application** if it freezes
- **Check internet connection** for market data
- **Verify screen resolution** for automation
- **Update Python packages** if needed

---

**Installation Complete! 🎉**

Now proceed to the Quick Start Guide to begin using the app.