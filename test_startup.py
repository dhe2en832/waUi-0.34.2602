#!/usr/bin/env python3
"""
Test script to verify components work
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing imports...")

try:
    import customtkinter as ctk
    print("[OK] customtkinter imported")
except Exception as e:
    print(f"[FAIL] customtkinter error: {e}")
    sys.exit(1)

try:
    from src.api.client import WACSAAPIClient, APIConfig
    print("[OK] API client imported")
except Exception as e:
    print(f"[FAIL] API client error: {e}")
    sys.exit(1)

try:
    from src.api.backup_reader import BackupLogReader
    print("[OK] Backup reader imported")
except Exception as e:
    print(f"[FAIL] Backup reader error: {e}")
    sys.exit(1)

try:
    from src.ui.login_window import LoginWindow
    print("[OK] Login window imported")
except Exception as e:
    print(f"[FAIL] Login window error: {e}")
    sys.exit(1)

try:
    from src.ui.main_window import MainWindow
    print("[OK] Main window imported")
except Exception as e:
    print(f"[FAIL] Main window error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll imports successful!")

# Test backup reader
print("\nTesting backup reader...")
try:
    reader = BackupLogReader()
    files = reader.get_file_list()
    print("[OK] Backup reader works")
    print(f"  - Received files: {len(files.get('received', []))}")
    print(f"  - Sent files: {len(files.get('sent', []))}")
    print(f"  - Stats files: {len(files.get('stats', []))}")
except Exception as e:
    print(f"[FAIL] Backup reader error: {e}")

# Test simple window
print("\nTesting simple window creation...")
try:
    root = ctk.CTk()
    root.title("Test Window")
    root.geometry("400x300")
    
    label = ctk.CTkLabel(root, text="If you see this, UI works!")
    label.pack(pady=20)
    
    def close_test():
        print("[OK] Window created and closed successfully")
        root.destroy()
    
    button = ctk.CTkButton(root, text="Close Test", command=close_test)
    button.pack(pady=10)
    
    print("[OK] Test window created - close it to continue")
    root.mainloop()
    
except Exception as e:
    print(f"[FAIL] Window creation error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")
