# Android Setup Guide

## Step-by-Step Installation

### 1. Install Pydroid 3

1. Open **Google Play Store** on your Android device
2. Search for "**Pydroid 3**"
3. Install the app (it's free)
4. Open Pydroid 3 and complete the initial setup

### 2. Download the Games

#### Option A: Download from GitHub (Recommended)
1. Open your mobile browser
2. Go to your GitHub repository
3. Click the **green "Code" button**
4. Select **"Download ZIP"**
5. Extract the ZIP file using your file manager
6. Move the "Mobile Games" folder to your device's storage

#### Option B: Clone with Git (Advanced)
If you have Git installed in Termux:
```bash
git clone https://github.com/yourusername/mobile-games.git
```

### 3. Install Dependencies

1. Open **Pydroid 3**
2. Go to **Terminal** (bottom menu)
3. Type the following commands:
```bash
pip install pygame
pip install numpy
```
4. Wait for installation to complete

### 4. Run Your First Game

1. In Pydroid 3, tap the **folder icon** (top left)
2. Navigate to the **Mobile Games** folder
3. Open any game folder (e.g., `snake_classic`)
4. Tap on the `.py` file to open it
5. Tap the **play button** to run the game

## Troubleshooting Common Issues

### "Module not found" Error
- **Solution**: Make sure you installed pygame using pip
- **Command**: `pip install pygame numpy`

### Game Won't Start
- **Solution**: Check that you're running the main `.py` file
- **Look for**: Files named like `snake_game.py`, `tetris_game.py`, etc.

### Touch Controls Not Working
- **Solution**: Make sure you're using the latest version of Pydroid 3
- **Alternative**: Try restarting the app

### Performance Issues
- **Solution**: Close other apps running in the background
- **Tip**: Restart Pydroid 3 between games

## File Manager Tips

### Best File Managers for Android:
- **Files by Google** (recommended)
- **ES File Explorer**
- **Solid Explorer**

### Organizing Your Games:
1. Create a dedicated folder: `/sdcard/Python Games/`
2. Keep all game folders organized
3. Create shortcuts on your home screen

## Advanced Setup

### Using Termux (Alternative Method)
1. Install **Termux** from F-Droid
2. Install Python: `pkg install python`
3. Install dependencies: `pip install pygame numpy`
4. Download and run games from command line

### Performance Optimization
- Close unnecessary background apps
- Use Game Mode if available on your device
- Ensure sufficient storage space (at least 100MB free)

## Updating Games

### Auto-Update Feature
Each game checks for updates when connected to the internet. Simply run any game and it will prompt you if updates are available.

### Manual Update
1. Re-download the ZIP file from GitHub
2. Extract and replace the old files
3. Your save data will be preserved

## Getting Help

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the main README.md file
3. Make sure all dependencies are installed
4. Try restarting Pydroid 3

Happy gaming! 🎮