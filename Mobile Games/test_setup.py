#!/usr/bin/env python3
"""
Mobile Games - Setup Test Script
Quick test to verify installation and diagnose issues
"""

import sys
import os
import platform

def test_basic_python():
    """Test basic Python functionality"""
    print("Testing Python installation...")
    print(f"  Python version: {sys.version}")
    print(f"  Platform: {platform.system()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Python executable: {sys.executable}")
    
    # Check if running on Android/Pydroid
    is_android = ('ANDROID_DATA' in os.environ or 
                  'ANDROID_ROOT' in os.environ or
                  'pydroid' in sys.executable.lower())
    print(f"  Android/Pydroid detected: {is_android}")
    
    return True

def test_pygame():
    """Test pygame installation and functionality"""
    print("\nTesting pygame installation...")
    
    try:
        import pygame
        print("  ✓ pygame import successful")
        
        # Test initialization
        pygame.init()
        print("  ✓ pygame.init() successful")
        
        # Test display info
        try:
            info = pygame.display.Info()
            print(f"  ✓ Display info: {info.current_w}x{info.current_h}")
            
            # Test if we can create a display
            try:
                screen = pygame.display.set_mode((300, 200))
                print("  ✓ Display creation successful")
                pygame.display.quit()
            except Exception as e:
                print(f"  ⚠ Display creation failed: {e}")
                
        except Exception as e:
            print(f"  ⚠ Display info failed: {e}")
        
        # Test font system
        try:
            font = pygame.font.Font(None, 24)
            print("  ✓ Font system working")
        except Exception as e:
            print(f"  ⚠ Font system issue: {e}")
            
        pygame.quit()
        return True
        
    except ImportError as e:
        print(f"  ✗ pygame import failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ pygame test failed: {e}")
        return False

def test_numpy():
    """Test numpy installation"""
    print("\nTesting numpy installation...")
    
    try:
        import numpy as np
        print("  ✓ numpy import successful")
        
        # Test basic functionality
        arr = np.array([1, 2, 3])
        print(f"  ✓ numpy array creation: {arr}")
        
        return True
        
    except ImportError as e:
        print(f"  ✗ numpy import failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ numpy test failed: {e}")
        return False

def test_game_files():
    """Test if game files are present"""
    print("\nTesting game files...")
    
    # Check for main launcher
    if os.path.exists("game_launcher.py"):
        print("  ✓ game_launcher.py found")
    else:
        print("  ✗ game_launcher.py not found")
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
            print(f"  ✓ {game_dir} found")
        else:
            print(f"  ⚠ {game_dir} not found")
    
    print(f"  📊 Games found: {found_games}/{len(game_dirs)}")
    
    return found_games > 0

def test_screen_detection():
    """Test screen size detection"""
    print("\nTesting screen size detection...")
    
    try:
        import pygame
        pygame.init()
        
        # Test the same detection logic used in games
        try:
            display_info = pygame.display.Info()
            screen_width = display_info.current_w
            screen_height = display_info.current_h
            
            print(f"  Raw screen size: {screen_width}x{screen_height}")
            
            # Test Android detection
            is_android = ('ANDROID_DATA' in os.environ or 
                         'ANDROID_ROOT' in os.environ or
                         'pydroid' in sys.executable.lower())
            
            if is_android:
                final_width = min(screen_width, 1080) if screen_width > 0 else 480
                final_height = min(screen_height, 1920) if screen_height > 0 else 800
                print(f"  Android mode - Final size: {final_width}x{final_height}")
            else:
                final_width = min(screen_width - 100, 480) if screen_width > 0 else 480
                final_height = min(screen_height - 100, 800) if screen_height > 0 else 800
                print(f"  Desktop mode - Final size: {final_width}x{final_height}")
                
        except Exception as e:
            print(f"  ⚠ Screen detection failed: {e}")
            print("  Using fallback size: 480x800")
            
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"  ✗ Screen detection test failed: {e}")
        return False

def run_quick_game_test():
    """Run a very basic game test"""
    print("\nRunning quick game test...")
    
    try:
        import pygame
        pygame.init()
        
        # Create a small test window
        screen = pygame.display.set_mode((200, 200))
        pygame.display.set_caption("Test")
        
        # Fill with color
        screen.fill((0, 128, 0))
        pygame.display.flip()
        
        # Wait a moment
        pygame.time.wait(1000)
        
        pygame.quit()
        print("  ✓ Basic game test successful")
        return True
        
    except Exception as e:
        print(f"  ✗ Game test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Mobile Games - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Python", test_basic_python),
        ("Pygame", test_pygame),
        ("Numpy", test_numpy),
        ("Game Files", test_game_files),
        ("Screen Detection", test_screen_detection),
        ("Quick Game Test", run_quick_game_test)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ {test_name} test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your installation is working correctly.")
        print("You can now run: python game_launcher.py")
    else:
        print(f"\n⚠ {failed} TEST(S) FAILED!")
        print("Please check the errors above and:")
        print("1. Run: python install_dependencies.py")
        print("2. Check the PYDROID_TROUBLESHOOTING.md file")
        print("3. Make sure all game files are present")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check your Python installation")