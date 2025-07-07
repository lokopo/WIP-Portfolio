#!/usr/bin/env python3
"""
Mobile Games - Dependency Installation Script
Automatically installs and configures dependencies for Android/Pydroid compatibility
"""

import subprocess
import sys
import os
import platform
import importlib.util

def check_environment():
    """Check if running on Android/Pydroid"""
    is_android = ('ANDROID_DATA' in os.environ or 
                  'ANDROID_ROOT' in os.environ or
                  platform.system() == 'Linux' and 'pydroid' in sys.executable.lower())
    
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print(f"Android/Pydroid detected: {is_android}")
    print(f"Python executable: {sys.executable}")
    return is_android

def install_package(package_name, version=None):
    """Install a package using pip with error handling"""
    try:
        package_spec = f"{package_name}=={version}" if version else package_name
        print(f"Installing {package_spec}...")
        
        # Try different pip commands
        pip_commands = [
            [sys.executable, "-m", "pip", "install", package_spec],
            ["pip", "install", package_spec],
            ["pip3", "install", package_spec]
        ]
        
        for cmd in pip_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print(f"✓ Successfully installed {package_name}")
                    return True
                else:
                    print(f"Failed with command {' '.join(cmd)}")
                    print(f"Error: {result.stderr}")
            except subprocess.TimeoutExpired:
                print(f"Timeout installing {package_name}")
            except FileNotFoundError:
                print(f"Command not found: {' '.join(cmd)}")
                continue
        
        return False
        
    except Exception as e:
        print(f"Error installing {package_name}: {e}")
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except ImportError:
        return False

def test_pygame():
    """Test pygame installation and basic functionality"""
    try:
        import pygame
        pygame.init()
        
        # Test display
        try:
            info = pygame.display.Info()
            print(f"Display info: {info.current_w}x{info.current_h}")
        except:
            print("Warning: Could not get display info")
        
        # Test font system
        try:
            font = pygame.font.Font(None, 24)
            print("✓ Font system working")
        except:
            print("Warning: Font system may have issues")
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"Pygame test failed: {e}")
        return False

def configure_android():
    """Configure Android-specific settings"""
    print("Configuring Android settings...")
    
    # Set environment variables that can help with pygame
    os.environ['SDL_VIDEODRIVER'] = 'android'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    
    # Create a simple configuration file
    config_path = os.path.join(os.path.dirname(__file__), 'android_config.txt')
    with open(config_path, 'w') as f:
        f.write("# Android Configuration\n")
        f.write("# This file indicates Android mode is enabled\n")
        f.write(f"platform={platform.system()}\n")
        f.write(f"python_executable={sys.executable}\n")
    
    print("✓ Android configuration complete")

def main():
    print("=" * 60)
    print("Mobile Games - Dependency Installation")
    print("=" * 60)
    
    # Check environment
    is_android = check_environment()
    print()
    
    # Required packages
    packages = [
        ("pygame", "2.1.0"),  # Specific version for better compatibility
        ("numpy", None),       # Latest version
    ]
    
    print("Checking and installing packages...")
    print("-" * 40)
    
    success_count = 0
    for package_name, version in packages:
        if check_package(package_name):
            print(f"✓ {package_name} is already installed")
            success_count += 1
        else:
            print(f"Installing {package_name}...")
            if install_package(package_name, version):
                success_count += 1
            else:
                print(f"✗ Failed to install {package_name}")
    
    print("-" * 40)
    print(f"Installation complete: {success_count}/{len(packages)} packages")
    print()
    
    # Test pygame
    if check_package("pygame"):
        print("Testing pygame...")
        if test_pygame():
            print("✓ Pygame is working correctly")
        else:
            print("⚠ Pygame may have issues")
    
    # Android-specific configuration
    if is_android:
        configure_android()
        print()
        print("Android/Pydroid Setup Instructions:")
        print("1. Make sure you have the latest version of Pydroid 3")
        print("2. If games don't fill the screen, try rotating your device")
        print("3. For best performance, close other apps")
        print("4. Use touch controls - swipe to move in games")
    
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("Run 'python game_launcher.py' to start playing")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Try running the script again or install pygame manually:")
        print("pip install pygame numpy")