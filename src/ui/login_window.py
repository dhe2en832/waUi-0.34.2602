"""
Login Window - First screen shown to users
Handles authentication before accessing main application
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.api.client import WACSAAPIClient, APIConfig


class LoginWindow(ctk.CTkToplevel):
    """Login window that appears on startup"""
    
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        
        self.on_login_success = on_login_success
        self.auth_token = None
        self.user_email = None
        
        # Window configuration
        self.title("WACSA-MD2 Login")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup login UI"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(0, 30))
        
        title = ctk.CTkLabel(
            title_frame,
            text="WACSA-MD2",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#007AFF"
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="WhatsApp Client",
            font=ctk.CTkFont(size=14),
            text_color="#8E8E93"
        )
        subtitle.pack(pady=(5, 0))
        
        # Login form
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="both", expand=True, pady=20)
        
        # Server URL
        ctk.CTkLabel(
            form_frame,
            text="Server URL",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 5))
        
        self.server_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="http://192.168.100.13:8008",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.server_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.server_entry.insert(0, "http://192.168.100.13:8008")
        
        # Email
        ctk.CTkLabel(
            form_frame,
            text="Email",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your email",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.email_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.email_entry.insert(0, "wa@csacomputer.com")
        
        # Password
        ctk.CTkLabel(
            form_frame,
            text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your password",
            show="●",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.password_entry.insert(0, "csa2025")
        
        # Remember me
        self.remember_var = ctk.BooleanVar(value=True)
        remember_checkbox = ctk.CTkCheckBox(
            form_frame,
            text="Remember me",
            variable=self.remember_var,
            font=ctk.CTkFont(size=12)
        )
        remember_checkbox.pack(padx=20, pady=(0, 20), anchor="w")
        
        # Login button
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="Login",
            command=self.handle_login,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#007AFF",
            hover_color="#0051D5"
        )
        self.login_btn.pack(fill="x", padx=20, pady=(0, 15))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#FF3B30"
        )
        self.status_label.pack(pady=(0, 20))
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        
    def handle_login(self):
        """Handle login button click"""
        server_url = self.server_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Validation
        if not server_url:
            self.show_error("Please enter server URL")
            return
            
        if not email:
            self.show_error("Please enter email")
            return
            
        if not password:
            self.show_error("Please enter password")
            return
        
        # Disable button and show loading
        self.login_btn.configure(state="disabled", text="Logging in...")
        self.status_label.configure(text="Connecting to server...", text_color="#007AFF")
        self.update()
        
        try:
            # Create API client
            config = APIConfig(base_url=server_url)
            client = WACSAAPIClient(config)
            
            # Attempt login
            result = client.login(email, password)
            
            if result.get('status'):
                # Login successful
                self.status_label.configure(text="Login successful!", text_color="#34C759")
                self.update()
                
                # Store credentials if remember me is checked
                if self.remember_var.get():
                    self.save_credentials(server_url, email, password)
                
                # Generate token (in real scenario, server would return this)
                self.auth_token = "wacsa-logged-in-token"
                self.user_email = email
                
                # Call success callback
                self.after(500, lambda: self.on_login_success(server_url, self.auth_token, email))
                self.destroy()
            else:
                self.show_error("Invalid credentials")
                self.login_btn.configure(state="normal", text="Login")
                
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "refused" in error_msg:
                self.show_error("Cannot connect to server. Please check server URL.")
            elif "Authentication" in error_msg:
                self.show_error("Invalid email or password")
            else:
                self.show_error(f"Login failed: {error_msg}")
            
            self.login_btn.configure(state="normal", text="Login")
    
    def show_error(self, message):
        """Show error message"""
        self.status_label.configure(text=message, text_color="#FF3B30")
        
    def save_credentials(self, server_url, email, password):
        """Save credentials to config file"""
        try:
            import json
            config_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "credentials.json"
            )
            
            credentials = {
                "server_url": server_url,
                "email": email,
                "password": password,  # In production, encrypt this!
                "remember": True
            }
            
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(credentials, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save credentials: {e}")
    
    @staticmethod
    def load_credentials():
        """Load saved credentials"""
        try:
            import json
            config_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "credentials.json"
            )
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return None
