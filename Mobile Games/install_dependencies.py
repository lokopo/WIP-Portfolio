#!/usr/bin/env python3
"""
Mobile Games - Dependency Installer
===================================

This script automatically installs all required dependencies for the Mobile Games collection.
Run this script in Pydroid 3 to set up everything you need.

Usage:
1. Open this file in Pydroid 3
2. Tap the play button to run
3. Wait for installation to complete
4. Run game_launcher.py to start playing!
"""

import subprocess
import sys
import os

def print_banner():
    """Print a nice banner."""
    print("=" * 50)
    print("🎮 MOBILE GAMES DEPENDENCY INSTALLER")
    print("=" * 50)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ ERROR: Python 3.6+ is required!")
        print("   Please update Python or use a newer version of Pydroid 3.")
        return False
    else:
        print("✅ Python version is compatible!")
        return True

def install_package(package_name):
    """Install a package using pip."""
    print(f"📦 Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error installing {package_name}: {e}")
        return False

def check_package_installed(package_name):
    """Check if a package is already installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install all required dependencies."""
    print("🔧 Installing game dependencies...")
    print()
    
    # List of required packages
    packages = [
        ("pygame", "pygame"),
        ("numpy", "numpy")
    ]
    
    success_count = 0
    total_packages = len(packages)
    
    for package_name, import_name in packages:
        if check_package_installed(import_name):
            print(f"✅ {package_name} is already installed!")
            success_count += 1
        else:
            if install_package(package_name):
                success_count += 1
        print()
    
    return success_count == total_packages

def test_imports():
    """Test if all packages can be imported."""
    print("🧪 Testing package imports...")
    
    packages_to_test = [
        ("pygame", "Pygame (graphics and game engine)"),
        ("numpy", "NumPy (mathematical operations)")
    ]
    
    all_success = True
    
    for package, description in packages_to_test:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError as e:
            print(f"❌ {package} - Failed to import: {e}")
            all_success = False
    
    return all_success

def check_game_files():
    """Check if game files are present."""
    print("🎮 Checking game files...")
    
    # Check for main launcher
    if os.path.exists("game_launcher.py"):
        print("✅ Game launcher found!")
    else:
        print("❌ Game launcher (game_launcher.py) not found!")
        print("   Make sure you're running this script from the Mobile Games folder.")
        return False
    
    # Check for game directories
    game_dirs = [
        "snake_classic",
        "tetris_mobile", 
        "space_invaders",
        "puzzle_slider",
        "memory_match",
        "breakout"
    ]
    
    found_games = 0
    for game_dir in game_dirs:
        if os.path.exists(game_dir):
            found_games += 1
            print(f"✅ {game_dir} found!")
        else:
            print(f"⚠️  {game_dir} not found (optional)")
    
    print(f"📊 Found {found_games}/{len(game_dirs)} games")
    return found_games > 0

def main():
    """Main installation function."""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    print()
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("❌ Some dependencies failed to install!")
        print("   You may need to install them manually:")
        print("   1. Open Pydroid 3 terminal")
        print("   2. Type: pip install pygame numpy")
        input("\nPress Enter to exit...")
        return
    
    print()
    
    # Step 3: Test imports
    if not test_imports():
        print("❌ Some packages failed to import!")
        print("   Try restarting Pydroid 3 and running this script again.")
        input("\nPress Enter to exit...")
        return
    
    print()
    
    # Step 4: Check game files
    if not check_game_files():
        print("❌ Game files not found!")
        print("   Make sure you downloaded and extracted all the game files.")
        input("\nPress Enter to exit...")
        return
    
    print()
    
    # Success!
    print("🎉 INSTALLATION COMPLETE!")
    print("=" * 50)
    print()
    print("✅ All dependencies installed successfully!")
    print("✅ All packages tested and working!")
    print("✅ Game files found!")
    print()
    print("🎮 Ready to play! Here's what to do next:")
    print("   1. Close this script")
    print("   2. Open 'game_launcher.py' in Pydroid 3")
    print("   3. Tap the play button to start gaming!")
    print()
    print("🎯 Pro tip: Try Snake Classic first - it's the easiest game!")
    print()
    print("Happy Gaming! 🎮")
    print("=" * 50)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()