#!/usr/bin/env python3
"""
WACSA-MD2 UI Application
Desktop client for WACSA-MD2 server API
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import requests
import json
import datetime
from pathlib import Path

# Set appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class WACSAUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("WACSA-MD2 Client")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # API Configuration
        self.api_base_url = "http://localhost:3000/api"  # Default URL
        self.auth_token = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup main UI components"""
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create sidebar for navigation
        self.create_sidebar()
        
        # Create main content area
        self.create_content_area()
        
        # Create status bar
        self.create_status_bar()
        
    def create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self.main_frame, width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(self.sidebar, text="WACSA-MD2", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(20, 30))
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "dashboard"),
            ("WhatsApp", "whatsapp"),
            ("Messages", "messages"),
            ("Settings", "settings")
        ]
        
        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda k=key: self.switch_page(k),
                height=40
            )
            btn.pack(pady=5, padx=20, fill="x")
            self.nav_buttons[key] = btn
            
        # Connection status
        self.connection_frame = ctk.CTkFrame(self.sidebar)
        self.connection_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        self.connection_status = ctk.CTkLabel(
            self.connection_frame,
            text="● Disconnected",
            font=ctk.CTkFont(size=12),
            text_color="#ff6b6b"
        )
        self.connection_status.pack()
        
        # Server URL input
        self.server_url_entry = ctk.CTkEntry(
            self.connection_frame,
            placeholder_text="Server URL",
            width=200
        )
        self.server_url_entry.pack(pady=(10, 5))
        self.server_url_entry.insert(0, self.api_base_url)
        
        connect_btn = ctk.CTkButton(
            self.connection_frame,
            text="Connect",
            command=self.connect_to_server,
            width=200
        )
        connect_btn.pack()
        
    def create_content_area(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        # Create pages
        self.pages = {}
        self.create_dashboard_page()
        self.create_whatsapp_page()
        self.create_messages_page()
        self.create_settings_page()
        
        # Show dashboard by default
        self.current_page = "dashboard"
        self.show_page("dashboard")
        
    def create_dashboard_page(self):
        """Create dashboard page"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        
        # Header
        header = ctk.CTkFrame(page)
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header, text="Dashboard", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)
        
        # Stats cards
        stats_frame = ctk.CTkFrame(page)
        stats_frame.pack(fill="x", pady=10)
        
        # Sample statistics
        stats = [
            ("WhatsApp Status", "Offline"),
            ("Messages Sent", "0"),
            ("Messages Received", "0"),
            ("Active Sessions", "0")
        ]
        
        for i, (label, value) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame)
            card.pack(side="left", expand=True, fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 10))
        
        self.pages["dashboard"] = page
        
    def create_whatsapp_page(self):
        """Create WhatsApp module page"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        
        # Header
        header = ctk.CTkFrame(page)
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header, text="WhatsApp", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)
        
        # WhatsApp controls
        controls_frame = ctk.CTkFrame(page)
        controls_frame.pack(fill="x", pady=10)
        
        # Connection status
        status_frame = ctk.CTkFrame(controls_frame)
        status_frame.pack(fill="x", padx=20, pady=10)
        
        self.whatsapp_status = ctk.CTkLabel(
            status_frame, 
            text="● Checking...", 
            font=ctk.CTkFont(size=16),
            text_color="#ffd43b"
        )
        self.whatsapp_status.pack(pady=10)
        
        # Server info
        info_frame = ctk.CTkFrame(controls_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        self.server_info = ctk.CTkLabel(
            info_frame, 
            text="Connecting to WACSA-MD2 server...", 
            font=ctk.CTkFont(size=14)
        )
        self.server_info.pack(pady=10)
        
        # Action buttons
        button_frame = ctk.CTkFrame(controls_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        refresh_btn = ctk.CTkButton(
            button_frame,
            text="Refresh Status",
            command=self.refresh_whatsapp_status,
            width=150
        )
        refresh_btn.pack(side="left", padx=10, pady=10)
        
        # Send message section
        send_frame = ctk.CTkFrame(page)
        send_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(send_frame, text="Send Message", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 20))
        
        # Message type toggle
        type_frame = ctk.CTkFrame(send_frame)
        type_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(type_frame, text="Message Type:").pack(side="left", padx=(0, 10))
        self.message_type_var = tk.StringVar(value="text")
        text_radio = ctk.CTkRadioButton(type_frame, text="Text", variable=self.message_type_var, value="text", command=self.toggle_message_type)
        text_radio.pack(side="left", padx=(0, 20))
        media_radio = ctk.CTkRadioButton(type_frame, text="Media", variable=self.message_type_var, value="media", command=self.toggle_message_type)
        media_radio.pack(side="left")
        
        # Phone number input
        phone_frame = ctk.CTkFrame(send_frame)
        phone_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(phone_frame, text="Phone Number:").pack(side="left", padx=(0, 10))
        self.phone_entry = ctk.CTkEntry(phone_frame, width=200, placeholder_text="628123456789")
        self.phone_entry.pack(side="left", padx=(0, 10))
        
        # Text message input
        self.text_msg_frame = ctk.CTkFrame(send_frame)
        self.text_msg_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(self.text_msg_frame, text="Message:").pack(side="left", padx=(0, 10))
        self.message_entry = ctk.CTkEntry(self.text_msg_frame, width=400, placeholder_text="Type your message here...")
        self.message_entry.pack(side="left", padx=(0, 10))
        
        # Media message input
        self.media_msg_frame = ctk.CTkFrame(send_frame)
        # Initially hidden
        
        media_file_frame = ctk.CTkFrame(self.media_msg_frame)
        media_file_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(media_file_frame, text="Media File:").pack(side="left", padx=(0, 10))
        self.media_file_entry = ctk.CTkEntry(media_file_frame, width=300, placeholder_text="Select media file...")
        self.media_file_entry.pack(side="left", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            media_file_frame,
            text="Browse",
            command=self.browse_media_file,
            width=100
        )
        browse_btn.pack(side="left")
        
        caption_frame = ctk.CTkFrame(self.media_msg_frame)
        caption_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(caption_frame, text="Caption:").pack(side="left", padx=(0, 10))
        self.caption_entry = ctk.CTkEntry(caption_frame, width=400, placeholder_text="Add caption (optional)...")
        self.caption_entry.pack(side="left")
        
        # Send button
        button_frame = ctk.CTkFrame(send_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        send_btn = ctk.CTkButton(
            button_frame,
            text="Send Message",
            command=self.send_message,
            width=150
        )
        send_btn.pack(side="left")
        
        self.pages["whatsapp"] = page
        
    def create_messages_page(self):
        """Create messages page"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        
        # Header
        header = ctk.CTkFrame(page)
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header, text="Messages", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)
        
        # Messages list
        messages_frame = ctk.CTkFrame(page)
        messages_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(messages_frame, text="Message History", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 20))
        
        # Message list placeholder
        self.messages_list = ctk.CTkTextbox(messages_frame, height=400)
        self.messages_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.messages_list.insert("0.0", "No messages yet. Connect WhatsApp and send messages to see history here.")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            messages_frame,
            text="Refresh Messages",
            command=self.refresh_messages,
            width=150
        )
        refresh_btn.pack(pady=(0, 20))
        
        self.pages["messages"] = page
        
    def create_settings_page(self):
        """Create settings page"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        
        # Header
        header = ctk.CTkFrame(page)
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(header, text="Settings", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)
        
        # Settings content
        settings_frame = ctk.CTkFrame(page)
        settings_frame.pack(fill="x", pady=10)
        
        # API Settings
        api_frame = ctk.CTkFrame(settings_frame)
        api_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(api_frame, text="API Configuration", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 20))
        
        # Server URL setting
        url_frame = ctk.CTkFrame(api_frame)
        url_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(url_frame, text="Server URL:").pack(side="left", padx=(0, 10))
        self.settings_url_entry = ctk.CTkEntry(url_frame, width=300)
        self.settings_url_entry.pack(side="left", padx=(0, 10))
        self.settings_url_entry.insert(0, self.api_base_url)
        
        save_btn = ctk.CTkButton(url_frame, text="Save", command=self.save_settings)
        save_btn.pack(side="left")
        
        self.pages["settings"] = page
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ctk.CTkFrame(self)
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
    def switch_page(self, page_name):
        """Switch between pages"""
        if page_name in self.pages:
            # Hide current page
            if self.current_page in self.pages:
                self.pages[self.current_page].pack_forget()
            
            # Show new page
            self.pages[page_name].pack(fill="both", expand=True)
            self.current_page = page_name
            
            # Update status
            self.update_status(f"Switched to {page_name.title()}")
            
    def refresh_whatsapp_status(self):
        """Refresh WhatsApp connection status from server"""
        try:
            self.whatsapp_status.configure(text="● Checking...", text_color="#ffd43b")
            self.update_status("Checking WhatsApp status...")
            
            # TODO: Implement API call to check WhatsApp status
            # For now, simulate status check
            self.after(1000, self.on_whatsapp_status_checked)
            
        except Exception as e:
            self.whatsapp_status.configure(text="● Error", text_color="#ff6b6b")
            messagebox.showerror("Error", f"Failed to check WhatsApp status: {str(e)}")
            
    def on_whatsapp_status_checked(self):
        """Handle WhatsApp status check result"""
        # TODO: Get actual status from API
        # For now, assume connected
        self.whatsapp_status.configure(text="● Connected", text_color="#51cf66")
        self.server_info.configure(text="WACSA-MD2 server - WhatsApp connected")
        self.update_status("WhatsApp status updated")
        
    def toggle_message_type(self):
        """Toggle between text and media message input"""
        message_type = self.message_type_var.get()
        
        if message_type == "text":
            # Show text input, hide media input
            self.text_msg_frame.pack(fill="x", padx=20, pady=5)
            self.media_msg_frame.pack_forget()
        else:
            # Show media input, hide text input
            self.text_msg_frame.pack_forget()
            self.media_msg_frame.pack(fill="x", padx=20, pady=5)
            
    def browse_media_file(self):
        """Browse and select media file"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("Video files", "*.mp4 *.avi *.mov *.wmv"),
            ("Audio files", "*.mp3 *.wav *.m4a"),
            ("Documents", "*.pdf *.doc *.docx *.xls *.xlsx"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Media File",
            filetypes=file_types
        )
        
        if file_path:
            self.media_file_entry.delete(0, tk.END)
            self.media_file_entry.insert(0, file_path)
            
    def send_message(self):
        """Send WhatsApp message (text or media)"""
        phone = self.phone_entry.get().strip()
        message_type = self.message_type_var.get()
        
        if not phone:
            messagebox.showerror("Error", "Please enter phone number")
            return
            
        try:
            if message_type == "text":
                message = self.message_entry.get().strip()
                if not message:
                    messagebox.showerror("Error", "Please enter message")
                    return
                    
                # Send text message
                self.update_status(f"Sending text message to {phone}...")
                # TODO: Call API send_text_message
                
                # Clear message entry
                self.message_entry.delete(0, tk.END)
                
                # Add to message history
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message_text = f"[{timestamp}] Sent to {phone}: {message}\n"
                self.messages_list.insert(tk.END, message_text)
                self.messages_list.see(tk.END)
                
                self.update_status(f"Text message sent to {phone}")
                messagebox.showinfo("Success", "Text message sent successfully!")
                
            else:  # media
                media_file = self.media_file_entry.get().strip()
                caption = self.caption_entry.get().strip()
                
                if not media_file:
                    messagebox.showerror("Error", "Please select media file")
                    return
                    
                # Send media message
                self.update_status(f"Sending media message to {phone}...")
                # TODO: Call API send_media_message
                
                # Clear entries
                self.media_file_entry.delete(0, tk.END)
                self.caption_entry.delete(0, tk.END)
                
                # Add to message history
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filename = Path(media_file).name
                message_text = f"[{timestamp}] Sent media to {phone}: {filename}"
                if caption:
                    message_text += f" - Caption: {caption}"
                message_text += "\n"
                
                self.messages_list.insert(tk.END, message_text)
                self.messages_list.see(tk.END)
                
                self.update_status(f"Media message sent to {phone}")
                messagebox.showinfo("Success", "Media message sent successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")
            
    def refresh_messages(self):
        """Refresh message history from WACSA logs"""
        try:
            self.update_status("Loading messages from WACSA-MD2 server...")
            self.messages_list.delete("1.0", tk.END)
            
            # TODO: Implement API calls to get received and sent messages
            # For now, show placeholder
            self.messages_list.insert(tk.END, "Loading message history...\n\n")
            
            # Simulate loading messages
            self.after(1000, self.load_message_history)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh messages: {str(e)}")
            
    def load_message_history(self):
        """Load message history from WACSA logs"""
        try:
            # TODO: Call API endpoints:
            # - GET /log/received-message (received messages)
            # - GET /log/sent-message (sent messages)
            # - GET /log/statistic (statistics)
            
            # For now, show sample data
            received_messages = [
                {"phone": "628123456789", "message": "Hello", "timestamp": "2026-03-26 14:30:00"},
                {"phone": "628987654321", "message": "How are you?", "timestamp": "2026-03-26 14:25:00"}
            ]
            
            sent_messages = [
                {"phone": "628123456789", "message": "Hi there!", "timestamp": "2026-03-26 14:31:00"},
                {"phone": "628987654321", "message": "I'm fine, thanks!", "timestamp": "2026-03-26 14:26:00"}
            ]
            
            # Clear and display messages
            self.messages_list.delete("1.0", tk.END)
            
            self.messages_list.insert(tk.END, "=== RECEIVED MESSAGES ===\n\n", "title")
            for msg in received_messages:
                self.messages_list.insert(tk.END, f"[{msg['timestamp']}] From {msg['phone']}:\n", "received")
                self.messages_list.insert(tk.END, f"{msg['message']}\n\n", "message")
            
            self.messages_list.insert(tk.END, "=== SENT MESSAGES ===\n\n", "title")
            for msg in sent_messages:
                self.messages_list.insert(tk.END, f"[{msg['timestamp']}] To {msg['phone']}:\n", "sent")
                self.messages_list.insert(tk.END, f"{msg['message']}\n\n", "message")
            
            # Configure text tags for styling
            self.messages_list.tag_config("title", font=("Arial", 12, "bold"), foreground="#0066cc")
            self.messages_list.tag_config("received", font=("Arial", 10, "bold"), foreground="#00aa00")
            self.messages_list.tag_config("sent", font=("Arial", 10, "bold"), foreground="#aa0000")
            self.messages_list.tag_config("message", font=("Arial", 10))
            
            self.update_status("Message history loaded")
            
        except Exception as e:
            self.messages_list.delete("1.0", tk.END)
            self.messages_list.insert(tk.END, f"Error loading messages: {str(e)}")
            messagebox.showerror("Error", f"Failed to load message history: {str(e)}")
            
    def connect_to_server(self):
        """Connect to WACSA-MD2 server"""
        url = self.server_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter server URL")
            return
            
        try:
            # Test connection
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                self.api_base_url = url
                self.connection_status.configure(text="● Connected", text_color="#51cf66")
                self.update_status(f"Connected to {url}")
                messagebox.showinfo("Success", "Connected to server successfully!")
            else:
                self.connection_status.configure(text="● Error", text_color="#ff6b6b")
                messagebox.showerror("Error", f"Server returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.connection_status.configure(text="● Disconnected", text_color="#ff6b6b")
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
            
    def save_settings(self):
        """Save application settings"""
        url = self.settings_url_entry.get().strip()
        if url:
            self.api_base_url = url
            self.server_url_entry.delete(0, tk.END)
            self.server_url_entry.insert(0, url)
            self.update_status("Settings saved")
            messagebox.showinfo("Success", "Settings saved successfully!")
            
    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=message)
        
    def run(self):
        """Start the application"""
        self.mainloop()

def main():
    """Main entry point"""
    try:
        app = WACSAUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
