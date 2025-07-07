# 🎮 Mobile Games Collection for Android

> **A collection of 6 classic Python games optimized for Android devices using Pydroid 3**

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg) ![Android](https://img.shields.io/badge/Android-5.0+-green.svg) ![Pydroid](https://img.shields.io/badge/Pydroid-3-orange.svg)

## 📱 Quick Start Guide

### Step 1: Install Pydroid 3
1. Open **Google Play Store** on your Android device
2. Search for "**Pydroid 3**" 
3. Install the free app
4. Open it and complete the setup

### Step 2: Download the Games from GitHub

**🚨 Can't find the download button? Here's exactly where to look:**

1. **Open your mobile browser** (Chrome, Firefox, etc.)
2. **Go to the GitHub repository** (replace with your actual GitHub URL):
   ```
   https://github.com/yourusername/mobile-games
   ```
3. **Look for the GREEN "Code" button** - it's usually near the top right of the file list
4. **Tap the "Code" button** → Select **"Download ZIP"**
5. **Your browser will download** a file called `mobile-games-main.zip`
6. **Open your Downloads folder** and tap the ZIP file
7. **Extract/Unzip** the file (your phone will ask which app to use)
8. **Move the "Mobile Games" folder** to an easy-to-find location

### Step 3: Install Game Dependencies
1. **Open Pydroid 3**
2. **Tap the terminal icon** at the bottom
3. **Type these commands** (one at a time):
   ```bash
   pip install pygame
   ```
   ```bash
   pip install numpy
   ```
4. **Wait for installation** to complete

### Step 4: Play Your First Game!
1. **In Pydroid 3**, tap the **folder icon** (📁) in the top left
2. **Navigate to** your "Mobile Games" folder
3. **Tap on** `game_launcher.py` to open it
4. **Tap the play button** (▶️) to start
5. **Choose any game** from the launcher menu!

---

## 🎮 Games Included

| Game | Description | Difficulty | Controls |
|------|-------------|------------|----------|
| 🐍 **Snake Classic** | The timeless snake game | Easy | Swipe to change direction |
| 🧩 **Tetris Mobile** | Block-stacking puzzle | Medium | Tap to rotate, swipe to move |
| 👾 **Space Invaders** | Classic arcade shooter | Medium | Tap to shoot, tilt to move |
| 🔢 **Puzzle Slider** | Number sliding puzzle | Easy | Tap tiles to slide |
| 🧠 **Memory Match** | Card matching game | Easy | Tap cards to flip |
| 🎯 **Breakout** | Ball and paddle arcade | Medium | Slide finger to move paddle |

## � Alternative Installation Methods

### Method 1: Individual Game Files
If you only want specific games:
1. Go to the GitHub repository
2. Navigate to the game folder (e.g., `snake_classic/`)
3. Tap the game file (e.g., `snake_game.py`)
4. Tap **"Raw"** button
5. **Long-press → "Save as"** to download
6. Open in Pydroid 3

### Method 2: Using Termux (Advanced)
1. Install **Termux** from F-Droid
2. Run these commands:
   ```bash
   pkg install python git
   pip install pygame numpy
   git clone https://github.com/yourusername/mobile-games.git
   cd mobile-games/Mobile\ Games/
   python game_launcher.py
   ```

## 📱 Optimized for Mobile

### Touch Controls
- **Tap**: Select/Action
- **Swipe**: Directional movement
- **Drag**: Continuous movement
- **Pinch**: Zoom (where applicable)
- **Back Button**: Return to launcher

### Performance Tips
- **Close other apps** before playing
- **Use "Game Mode"** if your device has it
- **Ensure 100MB+ free storage**
- **Keep device plugged in** for extended play

## 🚨 Troubleshooting Common Issues

### "Can't find the download button!"
- Look for the **GREEN "Code" button** on GitHub
- It's located above the file list, to the right
- If you don't see it, try refreshing the page

### "Module not found" Error
```bash
# Run this in Pydroid 3 terminal:
pip install pygame numpy
```

### "Game won't start"
- Make sure you're running `game_launcher.py` first
- Check that both `pygame` and `numpy` are installed
- Try restarting Pydroid 3

### "Touch controls not working"
- Update Pydroid 3 to the latest version
- Restart the app
- Make sure you're not running in desktop mode

### "Games are too slow"
- Close background apps
- Restart Pydroid 3
- Free up device storage
- Try running individual games instead of the launcher

## 📂 Project Structure

```
Mobile Games/
├── 📄 README.md                 ← You are here
├── 📄 requirements.txt          ← Dependencies list
├── 🚀 game_launcher.py         ← START HERE - Main launcher
├── 📄 setup_android.md         ← Detailed setup guide
├── 📄 github_deployment_guide.md
├── 🐍 snake_classic/
│   └── snake_game.py
├── 🧩 tetris_mobile/
│   └── tetris_game.py
├── 👾 space_invaders/
│   └── space_game.py
├── 🔢 puzzle_slider/
│   └── puzzle_game.py
├── 🧠 memory_match/
│   └── memory_game.py
└── 🎯 breakout/
    └── breakout_game.py
```

## 🎯 Pro Tips

### For Beginners
1. **Start with the launcher** (`game_launcher.py`) - it's the easiest way
2. **Try Snake Classic first** - it's the simplest game
3. **Read the in-game instructions** - each game has help text

### For Advanced Users
1. **Modify the games** - all source code is available
2. **Create your own games** - use existing games as templates
3. **Add new games** to the launcher by editing `game_launcher.py`

### For Developers
1. **Fork the repository** to create your own version
2. **Submit pull requests** to contribute improvements
3. **Report issues** on GitHub if you find bugs

## 🔄 Keeping Games Updated

The games include an auto-update feature:
1. **Connect to WiFi**
2. **Run any game**
3. **Allow updates** when prompted
4. **Restart the game** after updating

## 📞 Getting Help

**Having trouble?** Try these steps:
1. ✅ **Check this README** - most issues are covered here
2. ✅ **Review the troubleshooting section** above
3. ✅ **Make sure Pydroid 3 is updated** to the latest version
4. ✅ **Try restarting your device**
5. ✅ **Check the GitHub issues page** for similar problems

## 🌟 Features

- ✅ **6 Complete Games** - Hours of entertainment
- ✅ **Touch Optimized** - Designed for mobile screens
- ✅ **Easy Installation** - Works with Pydroid 3
- ✅ **Offline Play** - No internet required after download
- ✅ **Open Source** - Learn from the code
- ✅ **Lightweight** - Under 50MB total
- ✅ **No Ads** - Pure gaming experience

## � License

MIT License - Feel free to modify, distribute, and learn from these games!

---

### 🎉 Ready to Play?

1. **Install Pydroid 3** from Google Play Store
2. **Download the ZIP** from GitHub (look for the green "Code" button!)
3. **Run the games** and have fun!

**Happy Gaming! 🎮**