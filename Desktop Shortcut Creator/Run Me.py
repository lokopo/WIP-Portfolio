#!/usr/bin/env python3

import os
import sys
import traceback

# Add the current directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    # Import the main script
    from shortcut_creator_pyqt import ShortcutCreatorWindow, QApplication
    
    # Run the GUI application
    app = QApplication(sys.argv)
    window = ShortcutCreatorWindow()
    window.show()
    sys.exit(app.exec())
    
except Exception as e:
    print(f"Error running the application: {e}")
    print("Traceback:")
    traceback.print_exc()
    
    # Keep the window open if there's an error
    input("Press Enter to exit...") 