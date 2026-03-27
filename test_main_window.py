#!/usr/bin/env python3
"""
Test main window creation
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing main window creation...")

try:
    from src.ui.main_window import MainWindow
    import customtkinter as ctk
    
    print("[OK] Imports successful")
    
    # Create main window directly
    print("Creating main window...")
    window = MainWindow(
        server_url="http://192.168.100.13:8008",
        auth_token="test-token-123",
        user_email="test@example.com"
    )
    
    print("[OK] Main window created successfully!")
    print("Window should be visible now. Close it to exit.")
    
    window.mainloop()
    
    print("[OK] Test complete!")
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
