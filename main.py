#!/usr/bin/env python3
"""
WACSA-MD2 UI Application - New Version
Modern WhatsApp-like interface with login-first flow
"""

import sys
import os
import customtkinter as ctk

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow

# Set appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class WacsaApp:
    """Main application controller"""
    
    def __init__(self):
        self.root = None
        self.login_window = None
        self.main_window = None
        
    def start(self):
        """Start application with login flow"""
        # Create hidden root window
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide root window
        
        # Check for saved credentials
        saved_creds = LoginWindow.load_credentials()
        
        if saved_creds and saved_creds.get('remember'):
            # Try auto-login
            self.show_main_window(
                saved_creds.get('server_url'),
                'wacsa-logged-in-token',  # Token from saved session
                saved_creds.get('email')
            )
        else:
            # Show login window
            self.show_login_window()
        
        # Start main loop
        self.root.mainloop()
    
    def show_login_window(self):
        """Show login window"""
        self.login_window = LoginWindow(self.root, self.on_login_success)
        
    def on_login_success(self, server_url, auth_token, user_email):
        """Handle successful login"""
        # Close login window if exists
        if self.login_window:
            self.login_window.destroy()
            self.login_window = None
        
        # Show main window
        self.show_main_window(server_url, auth_token, user_email)
    
    def show_main_window(self, server_url, auth_token, user_email):
        """Show main application window"""
        # Destroy root and create new main window
        if self.root:
            self.root.destroy()
        
        # Create main window
        self.main_window = MainWindow(server_url, auth_token, user_email)


def main():
    """Main entry point"""
    try:
        app = WacsaApp()
        app.start()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
