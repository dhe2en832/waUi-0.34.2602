"""
Main Application Window
WhatsApp-like interface with chat list and conversation view
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.api.client import WACSAAPIClient, APIConfig
from src.ui.components.chat_list import ChatList
from src.ui.components.chat_view import ChatView


class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self, server_url, auth_token, user_email):
        super().__init__()
        
        # Store session data
        self.server_url = server_url
        self.auth_token = auth_token
        self.user_email = user_email
        
        # API Client
        config = APIConfig(base_url=server_url)
        self.api_client = WACSAAPIClient(config)
        self.api_client.set_token(auth_token)
        
        # Window configuration
        self.title("WACSA-MD2")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Current page
        self.current_page = "messages"
        
        self.setup_ui()
        self.load_initial_data()
        
    def setup_ui(self):
        """Setup main UI"""
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.create_sidebar(main_container)
        
        # Content area
        self.content_frame = ctk.CTkFrame(main_container)
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        # Create pages
        self.pages = {}
        self.create_messages_page()
        self.create_dashboard_page()
        self.create_settings_page()
        
        # Show messages page by default
        self.switch_page("messages")
        
        # Status bar
        self.create_status_bar()
        
    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar = ctk.CTkFrame(parent, width=200, fg_color="#2B2B2B")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.pack(pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="WACSA-MD2",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#007AFF"
        ).pack()
        
        # User info
        user_frame = ctk.CTkFrame(sidebar, fg_color="#1E1E1E", corner_radius=10)
        user_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        # Avatar
        avatar = ctk.CTkFrame(user_frame, width=40, height=40, corner_radius=20, fg_color="#007AFF")
        avatar.pack(pady=(10, 5))
        avatar.pack_propagate(False)
        
        initial = self.user_email[0].upper() if self.user_email else "U"
        ctk.CTkLabel(
            avatar,
            text=initial,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Email
        ctk.CTkLabel(
            user_frame,
            text=self.user_email[:20] + "..." if len(self.user_email) > 20 else self.user_email,
            font=ctk.CTkFont(size=11),
            text_color="#8E8E93"
        ).pack(pady=(0, 10))
        
        # Navigation buttons
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("💬 Messages", "messages"),
            ("⚙️ Settings", "settings")
        ]
        
        self.nav_buttons = {}
        for text, page in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=lambda p=page: self.switch_page(p),
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color="#3A3A3A",
                anchor="w"
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[page] = btn
        
        # Spacer
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="both", expand=True)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            sidebar,
            text="🚪 Logout",
            command=self.handle_logout,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#FF3B30",
            hover_color="#D32F2F"
        )
        logout_btn.pack(fill="x", padx=10, pady=10)
        
    def create_messages_page(self):
        """Create WhatsApp-like messages page"""
        page = ctk.CTkFrame(self.content_frame)
        self.pages["messages"] = page
        
        # Split view: Chat list (left) + Chat view (right)
        # Chat list
        self.chat_list = ChatList(page, on_chat_select=self.handle_chat_select)
        self.chat_list.pack(side="left", fill="both", expand=False, ipadx=250)
        
        # Chat view
        self.chat_view = ChatView(page, on_send_message=self.handle_send_message)
        self.chat_view.pack(side="left", fill="both", expand=True)
        
    def create_dashboard_page(self):
        """Create dashboard page"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        self.pages["dashboard"] = page
        
        # Header
        ctk.CTkLabel(
            page,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)
        
        # Stats cards
        stats_frame = ctk.CTkFrame(page, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats = [
            ("Messages Sent", "0", "#007AFF"),
            ("Messages Received", "0", "#34C759"),
            ("Active Chats", "0", "#FF9500")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color=color, corner_radius=15)
            card.grid(row=0, column=i, padx=10, sticky="ew")
            stats_frame.columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=36, weight="bold"),
                text_color="white"
            ).pack(pady=(20, 5))
            
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=14),
                text_color="white"
            ).pack(pady=(0, 20))
        
    def create_settings_page(self):
        """Create settings page"""
        page = ctk.CTkScrollableFrame(self.content_frame)
        self.pages["settings"] = page
        
        # Header
        ctk.CTkLabel(
            page,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)
        
        # Server info
        server_frame = ctk.CTkFrame(page)
        server_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            server_frame,
            text="🌐 Server Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10, anchor="w", padx=20)
        
        # Server URL (read-only)
        url_frame = ctk.CTkFrame(server_frame, fg_color="transparent")
        url_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(url_frame, text="Server URL:", anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(
            url_frame,
            text=self.server_url,
            font=ctk.CTkFont(size=12),
            text_color="#007AFF"
        ).pack(side="left", padx=5)
        
        # Status
        status_frame = ctk.CTkFrame(server_frame, fg_color="transparent")
        status_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(status_frame, text="Status:", anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(
            status_frame,
            text="● Connected",
            text_color="#34C759",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=5)
        
        # Refresh button
        ctk.CTkButton(
            server_frame,
            text="🔄 Refresh Messages",
            command=self.refresh_messages,
            height=40
        ).pack(pady=20, padx=20)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ctk.CTkFrame(self, height=30, fg_color="#2B2B2B")
        self.status_bar.pack(side="bottom", fill="x")
        self.status_bar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color="#8E8E93"
        )
        self.status_label.pack(side="left", padx=10)
        
    def switch_page(self, page_name):
        """Switch between pages"""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show selected page
        if page_name in self.pages:
            self.pages[page_name].pack(fill="both", expand=True)
            self.current_page = page_name
            
            # Update nav button colors
            for name, btn in self.nav_buttons.items():
                if name == page_name:
                    btn.configure(fg_color="#3A3A3A")
                else:
                    btn.configure(fg_color="transparent")
    
    def load_initial_data(self):
        """Load initial data from server"""
        self.update_status("Loading messages...")
        
        try:
            # Load messages from server
            self.refresh_messages()
        except Exception as e:
            self.update_status(f"Error loading data: {str(e)}")
    
    def refresh_messages(self):
        """Refresh messages from server"""
        try:
            # Get received and sent messages
            received_data = self.api_client.get_received_messages()
            sent_data = self.api_client.get_sent_messages()
            
            # Parse messages and create contacts
            contacts = self.parse_messages_to_contacts(received_data, sent_data)
            
            # Load into chat list
            self.chat_list.load_contacts(contacts)
            
            self.update_status(f"Loaded {len(contacts)} conversations")
            
        except Exception as e:
            self.update_status(f"Error refreshing messages: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh messages: {str(e)}")
    
    def parse_messages_to_contacts(self, received_data, sent_data):
        """Parse API messages into contact list"""
        contacts_dict = {}
        
        # Process received messages
        if received_data.get('status') and received_data.get('response'):
            for msg in received_data['response']:
                msg_data = msg.get('_data', msg)
                sender = msg_data.get('from', 'Unknown')
                
                if sender not in contacts_dict:
                    contacts_dict[sender] = {
                        'number': sender,
                        'name': msg_data.get('notifyName', sender.split('@')[0]),
                        'messages': [],
                        'last_message': '',
                        'last_message_time': '',
                        'unread_count': 0
                    }
                
                contacts_dict[sender]['messages'].append(msg)
                contacts_dict[sender]['last_message'] = msg_data.get('body', 'Media')[:50]
        
        # Process sent messages
        if sent_data.get('status') and sent_data.get('response'):
            for msg in sent_data['response']:
                msg_data = msg.get('_data', msg)
                recipient = msg_data.get('to', 'Unknown')
                
                if recipient not in contacts_dict:
                    contacts_dict[recipient] = {
                        'number': recipient,
                        'name': recipient.split('@')[0],
                        'messages': [],
                        'last_message': '',
                        'last_message_time': '',
                        'unread_count': 0
                    }
                
                contacts_dict[recipient]['messages'].append(msg)
        
        # Convert to list and sort by last message time
        contacts = list(contacts_dict.values())
        
        return contacts
    
    def handle_chat_select(self, contact_data):
        """Handle chat selection"""
        self.chat_view.set_contact(contact_data)
        self.update_status(f"Viewing chat with {contact_data.get('name', 'Unknown')}")
    
    def handle_send_message(self, phone, message):
        """Handle sending message"""
        try:
            self.update_status(f"Sending message to {phone}...")
            
            # Send via API
            result = self.api_client.send_text_message(phone, message)
            
            if result.get('status'):
                self.update_status("Message sent successfully")
            else:
                self.update_status("Failed to send message")
                messagebox.showerror("Error", "Failed to send message")
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")
    
    def handle_logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Clear credentials
            try:
                import json
                config_file = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "config",
                    "credentials.json"
                )
                if os.path.exists(config_file):
                    os.remove(config_file)
            except:
                pass
            
            # Close and restart
            self.destroy()
            sys.exit(0)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=message)
