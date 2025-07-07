# Pydroid Troubleshooting Guide

## Common Issues and Solutions

### 🚨 **Games Crashing on Startup**

#### Quick Fixes:
1. **Update Pydroid 3** to the latest version from Google Play Store
2. **Restart Pydroid 3** completely (force close and reopen)
3. **Clear Pydroid 3's cache** in Android settings
4. **Install dependencies properly**:
   ```bash
   python install_dependencies.py
   ```

#### Common Crash Causes:

**1. Pygame Not Properly Installed**
- **Error**: `ModuleNotFoundError: No module named 'pygame'`
- **Solution**: 
  ```bash
  pip install pygame==2.1.0
  pip install numpy
  ```

**2. Font Loading Issues**
- **Error**: Game crashes when displaying text
- **Solution**: The updated code now includes fallback fonts that should work

**3. Display Initialization Problems**
- **Error**: `pygame.error: No available video device`
- **Solution**: 
  - Try restarting Pydroid 3
  - Check if other apps are using the display
  - Ensure screen orientation is unlocked

### 📱 **Screen Size Problems**

#### **Problem**: Games don't fill the entire screen

**Solutions:**
1. **Rotate your device** - The games now auto-detect screen size
2. **Check screen orientation** - Unlock auto-rotation in Android settings
3. **Close other apps** - Free up memory and display resources
4. **Try different screen modes** - Some devices have display scaling options

#### **Problem**: Games appear too small or too large

**Solutions:**
1. **Updated games automatically scale** - The new code adapts to your screen size
2. **Check device DPI settings** - Some devices have custom DPI settings
3. **Try landscape mode** - May provide better scaling on some devices

### 🔧 **Installation Issues**

#### **Problem**: "Permission denied" errors
**Solution:**
```bash
pip install --user pygame numpy
```

#### **Problem**: "No module named 'pip'"
**Solution:**
1. Update Pydroid 3 to the latest version
2. Reinstall Pydroid 3 if necessary
3. Try using the package manager in Pydroid 3 settings

#### **Problem**: "Connection timeout" during installation
**Solution:**
1. Check your internet connection
2. Try installing one package at a time:
   ```bash
   pip install pygame
   pip install numpy
   ```

### 🎮 **Gameplay Issues**

#### **Problem**: Touch controls not working
**Solution:**
1. **Swipe gestures**: Make sure you're swiping, not just tapping
2. **Button areas**: Tap directly on the visible buttons
3. **Screen calibration**: Check if your device's touch screen needs calibration

#### **Problem**: Games running too fast or too slow
**Solution:**
- The updated code now includes adaptive frame rates
- Performance depends on your device's capabilities
- Close other running apps for better performance

### 🚀 **Performance Optimization**

#### **For Better Performance:**
1. **Close background apps** - Free up RAM
2. **Reduce screen brightness** - Save battery and reduce heat
3. **Use airplane mode** - Disable network when not needed
4. **Restart device** - Clear memory leaks
5. **Check available storage** - Ensure at least 1GB free space

#### **Device-Specific Tips:**
- **Low-end devices**: Games may run slower but should still work
- **High-end devices**: Should run smoothly with full screen support
- **Tablets**: May have better performance and screen real estate

### 🆘 **Emergency Fixes**

#### **If Nothing Works:**
1. **Complete reinstall**:
   ```bash
   pip uninstall pygame
   pip install pygame==2.1.0
   ```

2. **Check Python version**:
   ```bash
   python --version
   ```
   Should be Python 3.6 or higher

3. **Try alternative installation**:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install pygame numpy
   ```

4. **Manual file check**:
   - Ensure all game files are in the correct directories
   - Check that `game_launcher.py` exists
   - Verify individual game files (like `snake_game.py`) are present

### 📋 **Step-by-Step Setup (If All Else Fails)**

1. **Update Pydroid 3** from Google Play Store
2. **Open Pydroid 3** and wait for it to fully load
3. **Open Terminal** (bottom menu in Pydroid 3)
4. **Install dependencies**:
   ```bash
   pip install pygame==2.1.0
   pip install numpy
   ```
5. **Download game files** to your device storage
6. **Open the Mobile Games folder** in Pydroid 3
7. **Run the installer**:
   ```bash
   python install_dependencies.py
   ```
8. **Launch games**:
   ```bash
   python game_launcher.py
   ```

### 🔍 **Debugging Information**

#### **To Get Help, Provide:**
1. **Device information**: Model, Android version
2. **Pydroid 3 version**: Check in app settings
3. **Error messages**: Copy the exact error text
4. **When it crashes**: During startup, gameplay, or specific actions

#### **Common Error Messages:**
- `ModuleNotFoundError` → Install missing packages
- `pygame.error` → Display or audio issues
- `FileNotFoundError` → Missing game files
- `PermissionError` → File access issues

### 🎯 **Testing Your Installation**

Run this simple test to verify everything works:
```python
import pygame
pygame.init()
info = pygame.display.Info()
print(f"Screen: {info.current_w}x{info.current_h}")
pygame.quit()
print("✓ Pygame is working!")
```

### 💡 **Additional Tips**

- **Battery optimization**: Disable battery optimization for Pydroid 3
- **Storage**: Keep at least 1GB free space on your device
- **Updates**: Regularly update both Pydroid 3 and your games
- **Backup**: Keep a backup of your game files
- **Network**: Some features may require internet connection

---

## 📞 **Still Having Issues?**

If you're still experiencing problems:
1. Check the main `README.md` file for additional information
2. Review the `setup_android.md` file for detailed setup instructions
3. Try running the `install_dependencies.py` script again
4. Consider asking for help in Python or Pydroid communities

**Remember**: The games have been updated with better error handling and screen size detection, so most issues should be resolved automatically!