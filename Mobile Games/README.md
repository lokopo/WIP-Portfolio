# Mobile Games Collection

A collection of Python-based mobile games designed to run on Android devices using Pydroid 3 or similar Python environments.

## 🎮 Games Included

1. **Snake Classic** - The timeless snake game with touch controls
2. **Tetris Mobile** - Block-stacking puzzle game optimized for mobile
3. **Space Invaders** - Classic arcade shooter with mobile controls
4. **Puzzle Slider** - Number sliding puzzle game
5. **Memory Match** - Card matching memory game
6. **Breakout** - Ball and paddle arcade game

## 📱 Running on Android

### Method 1: Using Pydroid 3 (Recommended)

1. **Install Pydroid 3** from Google Play Store
2. **Download the games**:
   - Option A: Clone from GitHub (if you have Git installed)
   - Option B: Download individual game files
3. **Install dependencies** in Pydroid 3:
   ```bash
   pip install pygame
   pip install numpy
   ```
4. **Run any game** by opening the `.py` file in Pydroid 3

### Method 2: Using Termux + Python

1. Install Termux from F-Droid
2. Install Python and dependencies:
   ```bash
   pkg install python
   pip install pygame numpy
   ```
3. Download and run the games

### Method 3: Direct Download from GitHub

1. Go to: `https://github.com/yourusername/mobile-games`
2. Click "Code" → "Download ZIP"
3. Extract on your device
4. Open individual game files in Pydroid 3

## 🔧 Requirements

- **Python 3.6+**
- **Pygame** (for graphics and input)
- **NumPy** (for mathematical operations)
- **Android 5.0+** (for Pydroid 3)

## 🎯 Controls

All games are optimized for touch input:
- **Touch/Tap**: Primary action
- **Swipe**: Directional movement
- **Touch and Hold**: Continuous action
- **Back Button**: Exit game

## 📂 Project Structure

```
Mobile Games/
├── README.md
├── requirements.txt
├── setup_android.md
├── snake_classic/
│   ├── snake_game.py
│   └── assets/
├── tetris_mobile/
│   ├── tetris_game.py
│   └── assets/
├── space_invaders/
│   ├── space_game.py
│   └── assets/
├── puzzle_slider/
│   ├── puzzle_game.py
│   └── assets/
├── memory_match/
│   ├── memory_game.py
│   └── assets/
└── breakout/
    ├── breakout_game.py
    └── assets/
```

## 🚀 Quick Start

1. **Install Pydroid 3** on your Android device
2. **Download this repository** to your device
3. **Open Pydroid 3** and navigate to the game folder
4. **Run any game** by opening the main `.py` file
5. **Enjoy playing!**

## 🔄 Auto-Update Feature

Each game includes an auto-update checker that can pull the latest version from GitHub when connected to the internet.

## 🐛 Troubleshooting

- **Import errors**: Make sure pygame is installed via pip
- **Touch not working**: Ensure you're using the latest Pydroid 3
- **Game too slow**: Close other apps and restart Pydroid 3
- **Audio issues**: Check device volume and audio permissions

## 📝 License

MIT License - Feel free to modify and distribute these games!