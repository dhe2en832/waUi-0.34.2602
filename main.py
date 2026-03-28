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
        self.force_show_login = False  # Force show login after logout
        
    def start(self):
        """Start application with login flow"""
        # Create hidden root window
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide root window
        
        # Check for saved credentials and auto-login (unless forced to show login)
        saved_creds = LoginWindow.load_credentials()
        
        if saved_creds and saved_creds.get('remember') and saved_creds.get('token') and not self.force_show_login:
            # Try auto-login with saved token
            try:
                self.show_main_window(
                    saved_creds.get('server_url'),
                    saved_creds.get('token'),  # Use saved token
                    saved_creds.get('email')
                )
            except Exception as e:
                # If auto-login fails, show login window
                print(f"Auto-login failed: {e}")
                self.show_login_window()
        else:
            # Show login window
            self.show_login_window()
        
        # Start main loop
        self.root.mainloop()
    
    def show_login_window(self):
        """Show login window with pre-filled credentials if available"""
        self.login_window = LoginWindow(self.root, self.on_login_success)
        
        # Ensure window is ready
        self.login_window.update()
        
        # Pre-fill credentials if available
        saved_creds = LoginWindow.load_credentials()
        if saved_creds:
            print(f"DEBUG: Pre-filling with saved creds: {saved_creds.get('server_url')}")
            if saved_creds.get('server_url'):
                self.login_window.server_entry.delete(0, 'end')
                self.login_window.server_entry.insert(0, saved_creds.get('server_url'))
            if saved_creds.get('email'):
                self.login_window.email_entry.delete(0, 'end')
                self.login_window.email_entry.insert(0, saved_creds.get('email'))
            if saved_creds.get('password'):
                self.login_window.password_entry.delete(0, 'end')
                self.login_window.password_entry.insert(0, saved_creds.get('password'))
            if saved_creds.get('token'):
                self.login_window.token_entry.delete(0, 'end')
                self.login_window.token_entry.insert(0, saved_creds.get('token'))
            # Set remember checkbox from saved value
            self.login_window.remember_var.set(saved_creds.get('remember', True))
        
        # Handle window close button (X) properly
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_login_window_close)
        
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
        try:
            # Create main window with logout callback
            self.main_window = MainWindow(server_url, auth_token, user_email, on_logout=self.logout)
            
            # Ensure window is visible and focused
            self.main_window.deiconify()  # Make sure window is not minimized
            self.main_window.lift()  # Bring window to front
            self.main_window.focus_force()  # Force focus on window
            self.main_window.attributes('-topmost', True)  # Temporarily set topmost
            self.main_window.after(100, lambda: self.main_window.attributes('-topmost', False))  # Remove topmost after 100ms
            
            # Withdraw root window after main window is shown
            if self.root:
                self.root.withdraw()
            
            # When main window closes, quit the application
            self.main_window.protocol("WM_DELETE_WINDOW", self.on_main_window_close)
        except Exception as e:
            print(f"Error creating main window: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def on_main_window_close(self):
        """Handle main window close"""
        if self.main_window:
            self.main_window.destroy()
        if self.root:
            self.root.quit()
    
    def on_login_window_close(self):
        """Handle login window close - quit entire app"""
        if self.login_window:
            self.login_window.destroy()
        if self.root:
            self.root.quit()
        sys.exit(0)
    
    def logout(self):
        """Handle logout - return to login window"""
        # Destroy main window
        if self.main_window:
            self.main_window.destroy()
            self.main_window = None
        
        # Set flag to force show login (skip auto-login)
        self.force_show_login = True
        
        # Show login window again
        self.show_login_window()


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
