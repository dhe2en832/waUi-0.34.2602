"""
Main Application Window
WhatsApp-like interface with chat list and conversation view
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.api.client import WACSAAPIClient, APIConfig
from src.api.backup_reader import BackupLogReader
from src.ui.components.chat_list import ChatList
from src.ui.components.chat_view import ChatView


class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self, server_url, auth_token, user_email, on_logout=None):
        super().__init__()
        
        # Store session data
        self.server_url = server_url
        self.auth_token = auth_token
        self.user_email = user_email
        self.on_logout = on_logout  # Callback for logout
        
        # API Client
        config = APIConfig(base_url=server_url)
        self.api_client = WACSAAPIClient(config)
        self.api_client.set_token(auth_token)
        
        # Backup Reader
        self.backup_reader = BackupLogReader()
        self.data_source_mode = "current"  # Options: "current", "server_backup", "local_backup"
        
        # ID to phone number mapping cache for consistent contact matching
        self.id_to_phone_map = {}
        
        # Real-time polling thread
        self.polling_thread = None
        self.stop_polling = threading.Event()
        self.last_message_count = 0
        
        # Window configuration
        self.title("WACSA-MD2")
        
        # Get screen dimensions and set window size to fit
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set window size (max 85% of screen width, 80% of height for margin)
        win_width = min(1200, int(screen_width * 0.85))
        win_height = min(750, int(screen_height * 0.8))
        
        # Calculate center position with top margin
        x = (screen_width - win_width) // 2
        y = max(30, (screen_height - win_height) // 2 - 20)  # Add 30px top margin, shift up by 20px
        
        self.geometry(f"{win_width}x{win_height}+{x}+{y}")
        self.minsize(900, 600)
        
        # Current page
        self.current_page = "messages"
        
        # Navigation buttons reference
        self.nav_buttons = {}
        
        self.setup_ui()
        self.load_initial_data()
        self.start_realtime_polling()
        
    def setup_ui(self):
        """Setup main UI"""
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.sidebar_visible = True
        self.sidebar_width = 200
        self.create_sidebar(main_container)
        
        self.toggle_btn = ctk.CTkButton(
            self,
            text="⟨",
            width=30,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1F2937",
            text_color="#D1D5DB",
            hover_color="#24324A",
            corner_radius=10,
            command=self.toggle_sidebar
        )
        self._position_toggle_button()
        self.bind("<Configure>", lambda e: self._position_toggle_button())
        
        # Content area
        self.content_frame = ctk.CTkFrame(main_container)
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        # Status bar (create before pages)
        self.create_status_bar()
        
        # Create pages
        self.pages = {}
        self.create_messages_page()
        self.create_dashboard_page()
        self.create_settings_page()
        
        # Show messages page by default
        self.switch_page("messages")
        
    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        self.sidebar = ctk.CTkFrame(parent, width=self.sidebar_width, fg_color="#111827")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(pady=(30, 20))
        
        ctk.CTkLabel(
            title_frame,
            text="WACSA-MD2",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#007AFF"
        ).pack()
        
        # User info
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="#1F2937", corner_radius=12)
        user_frame.pack(fill="x", padx=15, pady=(0, 25))
        
        # Avatar
        avatar = ctk.CTkFrame(user_frame, width=44, height=44, corner_radius=22, fg_color="#007AFF")
        avatar.pack(pady=(15, 8))
        avatar.pack_propagate(False)
        
        initial = self.user_email[0].upper() if self.user_email else "U"
        ctk.CTkLabel(
            avatar,
            text=initial,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Email
        ctk.CTkLabel(
            user_frame,
            text=self.user_email[:22] + ".." if len(self.user_email) > 22 else self.user_email,
            font=ctk.CTkFont(size=12),
            text_color="#D1D5DB"
        ).pack(pady=(0, 15))
        
        # Navigation buttons
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("💬 Messages", "messages"),
            ("⚙️ Settings", "settings")
        ]
        
        self.nav_buttons = {}
        for text, page in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda p=page: self.switch_page(p),
                height=45,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color="#D1D5DB",
                hover_color="#24324A",
                anchor="w",
                corner_radius=8
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[page] = btn
        
        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            command=self.handle_logout,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#F15C6D",
            hover_color="#D94E5E",
            corner_radius=8
        )
        logout_btn.pack(fill="x", padx=15, pady=20)
        
    def create_messages_page(self):
        """Create WhatsApp-like messages page"""
        page = ctk.CTkFrame(self.content_frame)
        self.pages["messages"] = page
        
        # Create resizable splitter between chat list and chat view
        self.create_chat_splitter(page)
        
        # Initial load
        self.load_initial_data()
    
    def create_chat_splitter(self, parent):
        """Create resizable chat list and chat view with splitter"""
        # Container for both chat list and chat view
        self.chat_container = ctk.CTkFrame(parent, fg_color="#F5F6F6")
        self.chat_container.pack(fill="both", expand=True)
        
        # Chat list (left side)
        self.chat_list_frame = ctk.CTkFrame(self.chat_container, width=280, fg_color="white")
        self.chat_list_frame.pack(side="left", fill="both", expand=False)
        self.chat_list_frame.pack_propagate(False)
        
        self.chat_list = ChatList(self.chat_list_frame, on_chat_select=self.handle_chat_select)
        self.chat_list.pack(fill="both", expand=True)
        
        # Resize handle between chat list and chat view
        self.resize_handle = ctk.CTkFrame(self.chat_container, width=6, fg_color="#E5E7EB", cursor="sb_h_double_arrow")
        self.resize_handle.place(x=280, y=0, relheight=1.0)
        # Drag zone overlay (lebih lebar, menyatu dengan area scrollbar)
        self.drag_zone_width = 4
        self.drag_zone = ctk.CTkFrame(self.chat_list_frame, width=self.drag_zone_width, fg_color="#D1D5DB", cursor="sb_h_double_arrow")
        self.drag_zone.place(relx=1.0, rely=0.0, anchor="ne", relheight=1.0)
        self.drag_zone.lift()
        
        # Chat view (right side)
        self.chat_view = ChatView(self.chat_container, on_send_message=self.handle_send_message, on_send_media=self.handle_send_media)
        self.chat_view.pack(side="left", fill="both", expand=True)
        
        # Make chat list resizable
        self.make_chat_list_resizable()
        self.chat_container.bind("<Configure>", lambda e: self._update_splitter_position())
    
    def make_chat_list_resizable(self):
        """Make chat list resizable"""
        self.chat_list_width = 280
        self.resizing = False
        
        def on_drag_start(event):
            self.resizing = True
            self.drag_start_x_root = event.x_root
            self.drag_start_width = self.chat_list_width
        
        def on_drag_motion(event):
            if self.resizing:
                # Calculate new width
                delta_x = event.x_root - self.drag_start_x_root
                new_width = self.drag_start_width + delta_x
                
                # Set minimum and maximum width
                new_width = max(240, min(520, new_width))
                
                # Update widths
                self.chat_list_width = new_width
                self.chat_list_frame.configure(width=new_width)
                self._update_splitter_position()
        
        def on_drag_end(event):
            self.resizing = False
        
        # Bind mouse events to resize handle
        self.resize_handle.bind("<Button-1>", on_drag_start)
        self.resize_handle.bind("<B1-Motion>", on_drag_motion)
        self.resize_handle.bind("<ButtonRelease-1>", on_drag_end)
        # Bind events juga ke drag_zone
        self.drag_zone.bind("<Button-1>", on_drag_start)
        self.drag_zone.bind("<B1-Motion>", on_drag_motion)
        self.drag_zone.bind("<ButtonRelease-1>", on_drag_end)
        # Double click untuk reset ke lebar default
        def on_double_click(event):
            self.chat_list_width = 280
            self.chat_list_frame.configure(width=self.chat_list_width)
            self._update_splitter_position()
        self.resize_handle.bind("<Double-Button-1>", on_double_click)
        self.drag_zone.bind("<Double-Button-1>", on_double_click)

    def _update_splitter_position(self):
        try:
            self.resize_handle.place(x=self.chat_list_width, y=0, relheight=1.0)
            self.drag_zone.place(relx=1.0, rely=0.0, anchor="ne", relheight=1.0)
            self.drag_zone.lift()
        except Exception:
            pass
    
    def add_chat_list_toggle(self):
        """Add toggle button for chat list hide/unhide"""
        # Chat list toggle button
        self.chat_list_toggle = ctk.CTkButton(
            self.chat_list_frame,
            text="◀",
            width=25,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color="#007AFF",
            hover_color="#0051D5",
            command=self.toggle_chat_list
        )
        self.chat_list_toggle.place(x=5, y=35)  # Position below sidebar toggle
        
        self.chat_list_visible = True
    
    def toggle_chat_list(self):
        """Toggle chat list visibility"""
        if self.chat_list_visible:
            # Hide chat list
            self.chat_list_frame.pack_forget()
            self.chat_list_visible = False
            self.chat_list_toggle.configure(text="▶")
            # Move toggle to main window
            self.chat_list_toggle.place_forget()
            self.chat_list_toggle = ctk.CTkButton(
                self.chat_container,
                text="▶",
                width=25,
                height=25,
                font=ctk.CTkFont(size=12),
                fg_color="#007AFF",
                hover_color="#0051D5",
                command=self.toggle_chat_list
            )
            self.chat_list_toggle.place(x=5, y=5)
        else:
            # Show chat list
            self.chat_list_frame.pack(side="left", fill="both", expand=False, before=self.chat_view)
            self.chat_list_visible = True
            self.chat_list_toggle.configure(text="◀")
            # Move toggle back to chat list frame
            self.chat_list_toggle.place_forget()
            self.chat_list_toggle = ctk.CTkButton(
                self.chat_list_frame,
                text="◀",
                width=25,
                height=25,
                font=ctk.CTkFont(size=12),
                fg_color="#007AFF",
                hover_color="#0051D5",
                command=self.toggle_chat_list
            )
            self.chat_list_toggle.place(x=5, y=35)
    
        
    def add_settings_content(self, parent):
        """Add settings content"""
        # Server info
        server_frame = ctk.CTkFrame(parent)
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
            text_color="#007AFF",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=5)
        
        # Data source selection
        source_frame = ctk.CTkFrame(server_frame)
        source_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            source_frame,
            text="📊 Data Source: Unified (All Sources)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.data_source_var = ctk.StringVar(value="current")
        
        ctk.CTkRadioButton(
            source_frame,
            text="Current Logs (Server API - Real-time)",
            variable=self.data_source_var,
            value="current",
            command=self.on_data_source_change
        ).pack(anchor="w", padx=40, pady=5)
        
        ctk.CTkRadioButton(
            source_frame,
            text="Server Backup (via API - Historical)",
            variable=self.data_source_var,
            value="server_backup",
            command=self.on_data_source_change
        ).pack(anchor="w", padx=40, pady=5)
        
        ctk.CTkRadioButton(
            source_frame,
            text="Local Backup (C:\\wacsa\\backup - Direct Access)",
            variable=self.data_source_var,
            value="local_backup",
            command=self.on_data_source_change
        ).pack(anchor="w", padx=40, pady=(5, 15))
        
        # Refresh button
        ctk.CTkButton(
            server_frame,
            text="🔄 Refresh Messages",
            command=self.refresh_messages,
            height=40
        ).pack(pady=20, padx=20)
    
    def create_dashboard_page(self):
        """Create dashboard page"""
        page = ctk.CTkFrame(self.content_frame, fg_color="#F0F2F5")
        self.pages["dashboard"] = page
        
        # Header
        header_frame = ctk.CTkFrame(page, fg_color="white", corner_radius=12)
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="WACSA Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#111B21"
        ).pack(pady=20, padx=20, anchor="w")
        
        # Stats grid
        stats_container = ctk.CTkFrame(page, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=10)
        
        # Grid configuration for 4 columns
        stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        stats_data = [
            ("Sent Messages", "0", "#007AFF"),
            ("Received Messages", "0", "#5AC8FA"),
            ("Active Contacts", "0", "#FFD700"),
            ("System Status", "Connected", "#007AFF")
        ]
        
        self.stats_labels = {}
        for i, (label, val, color) in enumerate(stats_data):
            card = ctk.CTkFrame(stats_container, fg_color="white", corner_radius=12, height=120)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)
            
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#667781"
            ).pack(pady=(15, 5), padx=15, anchor="w")
            
            val_label = ctk.CTkLabel(
                card,
                text=val,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            )
            val_label.pack(pady=(5, 15), padx=15, anchor="w")
            self.stats_labels[label] = val_label
            
        # Recent Activity section (scrollable)
        activity_frame = ctk.CTkFrame(page, fg_color="white", corner_radius=12)
        activity_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        ctk.CTkLabel(
            activity_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#111B21"
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        # Scrollable activity list
        self.activity_list = ctk.CTkScrollableFrame(activity_frame, fg_color="transparent")
        self.activity_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            self.activity_list,
            text="Loading recent activities...",
            font=ctk.CTkFont(size=13),
            text_color="#667781"
        ).pack(pady=40)
    
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
            text_color="#007AFF",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=5)
        
        # Data source selection
        source_frame = ctk.CTkFrame(server_frame)
        source_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            source_frame,
            text="📊 Data Source: Unified (All Sources)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.data_source_var = ctk.StringVar(value="current")
        
        ctk.CTkRadioButton(
            source_frame,
            text="Current Logs (Server API - Real-time)",
            variable=self.data_source_var,
            value="current",
            command=self.on_data_source_change
        ).pack(anchor="w", padx=40, pady=5)
        
        ctk.CTkRadioButton(
            source_frame,
            text="Server Backup (via API - Historical)",
            variable=self.data_source_var,
            value="server_backup",
            command=self.on_data_source_change
        ).pack(anchor="w", padx=40, pady=5)
        
        ctk.CTkRadioButton(
            source_frame,
            text="Local Backup (C:\\wacsa\\backup - Direct Access)",
            variable=self.data_source_var,
            value="local_backup",
            command=self.on_data_source_change
        ).pack(anchor="w", padx=40, pady=(5, 15))
        
        # Refresh button
        ctk.CTkButton(
            server_frame,
            text="🔄 Refresh Messages",
            command=self.refresh_messages,
            height=40
        ).pack(pady=20, padx=20)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ctk.CTkFrame(self, height=30, fg_color="#F5F6F6")
        self.status_bar.pack(side="bottom", fill="x")
        self.status_bar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color="#667781"
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
                    btn.configure(fg_color="#24324A", text_color="white")
                else:
                    btn.configure(fg_color="transparent", text_color="#D1D5DB")
    
    def load_initial_data(self):
        """Load initial data from server"""
        try:
            self.update_status("Loading messages from local backup (C:\\wacsa\\backup)...")
            self.refresh_messages()
        except Exception as e:
            self.update_status(f"✗ Error: {str(e)}")
    
    def on_data_source_change(self):
        """Handle data source selection change"""
        self.data_source_mode = self.data_source_var.get()
        
        source_names = {
            "current": "Current Logs (Server API)",
            "server_backup": "Server Backup (via API)",
            "local_backup": "Local Backup (Direct Access)"
        }
        
        source_name = source_names.get(self.data_source_mode, "Unknown")
        
        self.update_status(f"Data source: {source_name}")
        self.refresh_messages()
    
    def refresh_messages(self):
        """Refresh messages from all unified data sources"""
        try:
            self.update_status("Loading messages from all sources...")
            
            # Load from all sources and merge
            all_received = []
            all_sent = []
            
            # 1. Try current logs (API real-time)
            try:
                received_data = self.api_client.get_received_messages()
                sent_data = self.api_client.get_sent_messages()
                
                received_count = self._count_messages(received_data)
                sent_count = self._count_messages(sent_data)
                
                if received_count > 0 or sent_count > 0:
                    all_received.extend(self._extract_messages(received_data))
                    all_sent.extend(self._extract_messages(sent_data))
                    print(f"DEBUG: Loaded {received_count} received, {sent_count} sent from current logs")
            except Exception as e:
                print(f"DEBUG: Current logs failed: {e}")
            
            # 2. Try server backup (API historical)
            try:
                received_data = self.api_client.get_backup_received_messages()
                sent_data = self.api_client.get_backup_sent_messages()
                
                received_count = self._count_messages(received_data)
                sent_count = self._count_messages(sent_data)
                
                if received_count > 0 or sent_count > 0:
                    all_received.extend(self._extract_messages(received_data))
                    all_sent.extend(self._extract_messages(sent_data))
                    print(f"DEBUG: Loaded {received_count} received, {sent_count} sent from server backup")
            except Exception as e:
                print(f"DEBUG: Server backup failed: {e}")
            
            # 3. Try local backup (file)
            try:
                received_data = self.backup_reader.get_received_messages()
                sent_data = self.backup_reader.get_sent_messages()
                
                received_count = self._count_messages(received_data)
                sent_count = self._count_messages(sent_data)
                
                if received_count > 0 or sent_count > 0:
                    all_received.extend(self._extract_messages(received_data))
                    all_sent.extend(self._extract_messages(sent_data))
                    print(f"DEBUG: Loaded {received_count} received, {sent_count} sent from local backup")
            except Exception as e:
                print(f"DEBUG: Local backup failed: {e}")
            
            # Remove duplicates based on message ID
            all_received = self._deduplicate_messages(all_received)
            all_sent = self._deduplicate_messages(all_sent)
            
            # Create unified data structure
            received_data = {'status': True, 'response': all_received}
            sent_data = {'status': True, 'response': all_sent}
            
            print(f"DEBUG: Total after dedup: {len(all_received)} received, {len(all_sent)} sent")
            
            # Parse messages and create contacts
            contacts = self.parse_messages_to_contacts(received_data, sent_data)
            print(f"DEBUG: parsed {len(contacts)} contacts")
            
            # Update dashboard stats
            self._update_dashboard_stats(len(all_sent), len(all_received), len(contacts))
            
            # Update Recent Activity
            self._update_recent_activity(received_data, sent_data)
            
            # Load into chat list
            self.chat_list.load_contacts(contacts)
            
            total_msgs = len(all_received) + len(all_sent)
            self.update_status(f"✓ Loaded {len(contacts)} conversations ({total_msgs} messages) from all sources")
            
        except Exception as e:
            self.update_status(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh messages:\n\n{str(e)}")
    
    def _extract_messages(self, data):
        """Extract message list from API response"""
        try:
            if isinstance(data, dict):
                if data.get('status') and data.get('response'):
                    return data['response']
                elif 'response' in data:
                    return data['response']
            elif isinstance(data, list):
                return data
        except:
            pass
        return []
    
    def _deduplicate_messages(self, messages):
        """Remove duplicate messages based on ID or timestamp+body hash"""
        seen = set()
        unique = []
        
        for msg in messages:
            # Try to get unique identifier
            msg_id = None
            msg_data = msg.get('_data', msg) if isinstance(msg, dict) else msg
            
            if isinstance(msg_data, dict):
                # Try message ID
                if 'id' in msg_data:
                    if isinstance(msg_data['id'], dict):
                        msg_id = str(msg_data['id'].get('_serialized', msg_data['id']))
                    else:
                        msg_id = str(msg_data['id'])
                
                # Fallback: use timestamp + body hash
                if not msg_id:
                    timestamp = msg_data.get('t', msg_data.get('timestamp', 0))
                    body = msg_data.get('body', '')
                    from_field = str(msg_data.get('from', ''))
                    msg_id = f"{timestamp}_{hash(body + from_field)}"
            
            if msg_id and msg_id not in seen:
                seen.add(msg_id)
                unique.append(msg)
            elif not msg_id:
                # If no ID, include anyway
                unique.append(msg)
        
        return unique
    
    def _count_messages(self, data):
        """Count total messages from API response"""
        try:
            if isinstance(data, dict):
                if data.get('status') and data.get('response'):
                    return len(data['response'])
                elif 'response' in data:
                    return len(data['response'])
            elif isinstance(data, list):
                return len(data)
        except:
            pass
        return 0
    
    def _update_dashboard_stats(self, sent_count, received_count, contacts_count):
        """Update dashboard statistics labels"""
        try:
            # Check if stats_labels exists (dashboard may not be created yet)
            if not hasattr(self, 'stats_labels') or self.stats_labels is None:
                print("DEBUG: stats_labels not available yet, skipping dashboard stats update")
                return
            
            if 'Sent Messages' in self.stats_labels:
                self.stats_labels['Sent Messages'].configure(text=str(sent_count))
            if 'Received Messages' in self.stats_labels:
                self.stats_labels['Received Messages'].configure(text=str(received_count))
            if 'Active Contacts' in self.stats_labels:
                self.stats_labels['Active Contacts'].configure(text=str(contacts_count))
        except Exception as e:
            print(f"Error updating dashboard stats: {e}")
    
    def _update_recent_activity(self, received_data, sent_data):
        """Update Recent Activity section with actual data"""
        try:
            # Check if activity_list exists (dashboard may not be created yet)
            if not hasattr(self, 'activity_list') or self.activity_list is None:
                print("DEBUG: activity_list not available yet, skipping recent activity update")
                return
            
            # Clear existing content
            for widget in self.activity_list.winfo_children():
                widget.destroy()
            
            # Get recent messages (last 10)
            recent_messages = []
            
            # Process received messages
            received_messages = []
            if isinstance(received_data, dict):
                if received_data.get('status') and received_data.get('response'):
                    received_messages = received_data['response']
                elif 'response' in received_data:
                    received_messages = received_data['response']
            elif isinstance(received_data, list):
                received_messages = received_data
            
            # Process sent messages
            sent_messages = []
            if isinstance(sent_data, dict):
                if sent_data.get('status') and sent_data.get('response'):
                    sent_messages = sent_data['response']
                elif 'response' in sent_data:
                    sent_messages = sent_data['response']
            elif isinstance(sent_data, list):
                sent_messages = sent_data
            
            # Combine and sort by timestamp (most recent first)
            all_messages = []
            
            for msg in received_messages[-5:]:  # Last 5 received
                msg_data = msg.get('_data', msg) if isinstance(msg, dict) else msg
                all_messages.append({
                    'type': 'received',
                    'from': msg_data.get('from', 'Unknown'),
                    'body': msg_data.get('body', 'Media')[:50],
                    'time': msg_data.get('t', msg_data.get('timestamp', 0))
                })
            
            for msg in sent_messages[-5:]:  # Last 5 sent
                msg_data = msg.get('_data', msg) if isinstance(msg, dict) else msg
                all_messages.append({
                    'type': 'sent',
                    'to': msg_data.get('to', 'Unknown'),
                    'body': msg_data.get('body', 'Media')[:50],
                    'time': msg_data.get('t', msg_data.get('timestamp', 0))
                })
            
            # Sort by time (descending)
            all_messages.sort(key=lambda x: int(str(x['time'])) if str(x['time']).isdigit() else 0, reverse=True)
            
            # Display top 10 recent activities
            if all_messages:
                for i, msg in enumerate(all_messages[:10]):
                    # Create activity item
                    activity_item = ctk.CTkFrame(self.activity_list, fg_color="white", corner_radius=8)
                    activity_item.pack(fill="x", pady=2)
                    
                    # Icon based on type
                    icon = "📥" if msg['type'] == 'received' else "📤"
                    color = "#007AFF" if msg['type'] == 'received' else "#34C759"
                    
                    # Format contact info
                    contact = msg.get('from', msg.get('to', 'Unknown'))
                    if isinstance(contact, dict):
                        contact = contact.get('user', str(contact))
                    if '@' in str(contact):
                        contact = contact.split('@')[0]
                    
                    # Truncate if too long
                    contact_str = str(contact)[:20] + "..." if len(str(contact)) > 20 else str(contact)
                    
                    # Activity text
                    activity_text = f"{icon} {contact_str}: {msg['body'][:30]}..."
                    
                    ctk.CTkLabel(
                        activity_item,
                        text=activity_text,
                        font=ctk.CTkFont(size=12),
                        text_color=color,
                        anchor="w"
                    ).pack(fill="x", padx=15, pady=8)
            else:
                # No activity
                ctk.CTkLabel(
                    self.activity_list,
                    text="No recent activity",
                    font=ctk.CTkFont(size=13),
                    text_color="#667781"
                ).pack(pady=40)
                
        except Exception as e:
            print(f"Error updating recent activity: {e}")
            # Show error in UI
            for widget in self.activity_list.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                self.activity_list,
                text=f"Error loading activity: {str(e)[:50]}",
                font=ctk.CTkFont(size=13),
                text_color="#F15C6D"
            ).pack(pady=40)
    
    def convert_whatsapp_id_to_phone(self, whatsapp_id):
        """Convert WhatsApp ID to actual phone number format"""
        try:
            # Remove any non-digit characters
            clean_id = ''.join(filter(str.isdigit, whatsapp_id))
            
            # Custom mapping for specific cases
            custom_mappings = {
                '84869224869994': '6281239761063',  # bataasku
                '80397543153761': '6285861732864',   # budyanto (from "to" field in messages)
                # Add more mappings as needed
            }
            
            # Check custom mapping first
            if clean_id in custom_mappings:
                mapped_number = custom_mappings[clean_id]
                return self.format_indonesian_number(mapped_number)
            
            # Handle different country codes
            if clean_id.startswith('0'):
                # Local format (08123456789) -> +62 812-3456-789
                if len(clean_id) >= 10:  # Indonesian number format
                    return self.format_indonesian_number(clean_id)
                else:
                    return clean_id
            elif clean_id.startswith('62'):
                # International format (628123456789) -> +62 812-3456-789
                if len(clean_id) >= 11:  # Indonesian number with country code
                    return self.format_indonesian_number(clean_id)
                else:
                    return f"+{clean_id}"
            elif len(clean_id) >= 10 and clean_id.startswith('1'):
                # US format (1234567890) -> +1 (123) 456-7890
                formatted = f"+1 ({clean_id[:3]}) {clean_id[3:6]}-{clean_id[6:]}"
                return formatted
            else:
                # Default: just add + if it looks like a country code
                if len(clean_id) >= 10:
                    return f"+{clean_id}"
                else:
                    return clean_id
        except Exception:
            return whatsapp_id
    
    def format_indonesian_number(self, number):
        """Format Indonesian phone number"""
        try:
            # Remove any non-digit characters
            clean_number = ''.join(filter(str.isdigit, number))
            
            # Ensure it starts with 62
            if clean_number.startswith('0'):
                clean_number = '62' + clean_number[1:]
            elif not clean_number.startswith('62'):
                clean_number = '62' + clean_number
            
            # Format: +62 8123-9761-063
            if len(clean_number) >= 11:
                country_code = clean_number[:2]  # 62
                rest = clean_number[2:]  # 81239761063
                
                if len(rest) >= 8:
                    formatted = f"+{country_code} {rest[:4]}-{rest[4:8]}-{rest[8:]}"
                else:
                    formatted = f"+{country_code} {rest}"
                
                return formatted
            else:
                return f"+{clean_number}"
        except Exception:
            return number
    
    def get_conversation_partner(self, msg_data, phone_number):
        """Get the actual conversation partner (not the server number)"""
        try:
            # Check if this is a sent message (fromMe: true) - read from id.fromMe
            from_me = False
            if 'id' in msg_data:
                from_me = msg_data['id'].get('fromMe', False)
            
            if from_me:
                # This is a message we sent - the partner is in 'to' field
                to_field = msg_data.get('to', {})
                
                if isinstance(to_field, dict) and 'user' in to_field:
                    partner_id = to_field['user']
                elif isinstance(to_field, str):
                    partner_id = to_field.split('@')[0] if '@' in to_field else to_field
                else:
                    partner_id = str(to_field)
                
                # Convert partner ID to phone number
                if partner_id and partner_id.isdigit():
                    result = self.format_indonesian_number(partner_id)
                else:
                    result = self.convert_whatsapp_id_to_phone(partner_id)
                
                return result
            else:
                # This is a received message - the partner is in 'from' field
                from_field = msg_data.get('from', '')
                
                if isinstance(from_field, str) and '@lid' in from_field:
                    partner_id = from_field.split('@')[0]
                    # Convert partner ID to phone number using mapping
                    result = self.convert_whatsapp_id_to_phone(partner_id)
                elif isinstance(from_field, str) and '@c.us' in from_field:
                    # This is already a phone number
                    partner_id = from_field.split('@')[0]
                    result = self.format_indonesian_number(partner_id)
                else:
                    result = phone_number
                
                return result
        except Exception as e:
            return phone_number
    
    def _normalize_phone_for_matching(self, phone_number):
        """Normalize phone number for consistent matching across different formats"""
        if not phone_number or phone_number == "Unknown":
            return None
        
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, str(phone_number)))
        
        # Ensure it starts with 62 (Indonesia)
        if digits.startswith('0'):
            digits = '62' + digits[1:]
        elif not digits.startswith('62'):
            digits = '62' + digits
        
        return digits
    
    def _get_contact_key(self, phone_number):
        """Get normalized key for contact dictionary lookup"""
        normalized = self._normalize_phone_for_matching(phone_number)
        if normalized:
            return normalized
        return str(phone_number) if phone_number else "Unknown"
    
    def parse_messages_to_contacts(self, received_data, sent_data):
        """Parse API messages into contact list"""
        contacts_dict = {}
        
        try:
            # Process received messages
            received_messages = []
            if received_data.get('status') and received_data.get('response'):
                received_messages = received_data['response']
            elif isinstance(received_data, list):
                received_messages = received_data
            elif isinstance(received_data, dict) and 'response' in received_data:
                received_messages = received_data['response']
            
            for msg in received_messages:
                try:
                    msg_data = msg.get('_data', msg)
                    
                    # Extract phone number from id.remote or from field
                    sender = None
                    phone_number = None
                    
                    # Try to get actual phone number from message fields first
                    actual_phone = None
                    
                    # Check 'from' field for actual phone number (not ID)
                    from_field = msg_data.get('from', '')
                    print(f"DEBUG received: from_field={from_field}, type={type(from_field)}")
                    if isinstance(from_field, str) and '@c.us' in from_field:
                        # This looks like an actual phone number
                        actual_phone = from_field.split('@')[0]
                    elif isinstance(from_field, str) and '@lid' in from_field:
                        # WhatsApp Limited Identifier - use as-is but mark for ID-based lookup
                        actual_phone = from_field.split('@')[0]
                        print(f"DEBUG received: found @lid ID: {actual_phone}")
                    elif isinstance(from_field, str) and from_field.isdigit() and len(from_field) >= 10:
                        actual_phone = from_field
                    
                    # Check 'to' field for actual phone number
                    to_field = msg_data.get('to', '')
                    if isinstance(to_field, str) and '@c.us' in to_field:
                        # This looks like an actual phone number
                        actual_phone = to_field.split('@')[0]
                    elif isinstance(to_field, str) and '@lid' in to_field:
                        # WhatsApp Limited Identifier - use as-is
                        actual_phone = to_field.split('@')[0]
                    elif isinstance(to_field, str) and to_field.isdigit() and len(to_field) >= 10:
                        actual_phone = to_field
                    
                    # If we found actual phone number, use it
                    if actual_phone:
                        # First check if it's a WhatsApp ID that needs mapping
                        phone_number = self.convert_whatsapp_id_to_phone(actual_phone)
                        print(f"DEBUG received: actual_phone={actual_phone}, converted_phone={phone_number}")
                        # Get actual conversation partner (not server number)
                        conversation_partner = self.get_conversation_partner(msg_data, phone_number)
                        print(f"DEBUG received: conversation_partner={conversation_partner}")
                        if conversation_partner != phone_number:
                            phone_number = conversation_partner
                        sender = phone_number
                    else:
                        # Fallback to ID-based conversion
                        if 'id' in msg_data and 'remote' in msg_data['id']:
                            remote = msg_data['id']['remote']
                            if '@' in remote:
                                raw_number = remote.split('@')[0]
                                temp_phone = self.convert_whatsapp_id_to_phone(raw_number)
                                # Get actual conversation partner
                                conversation_partner = self.get_conversation_partner(msg_data, temp_phone)
                                phone_number = conversation_partner if conversation_partner != temp_phone else temp_phone
                        
                        # Final fallback to from field
                        if not phone_number:
                            sender = msg_data.get('from', 'Unknown')
                            if isinstance(sender, dict):
                                sender = str(sender)
                            if '@' in sender:
                                raw_number = sender.split('@')[0]
                                temp_phone = self.convert_whatsapp_id_to_phone(raw_number)
                                conversation_partner = self.get_conversation_partner(msg_data, temp_phone)
                                phone_number = conversation_partner if conversation_partner != temp_phone else temp_phone
                            else:
                                phone_number = self.convert_whatsapp_id_to_phone(sender)
                        else:
                            sender = phone_number
                    
                    # Ensure we have a valid phone number
                    if not phone_number:
                        phone_number = "Unknown"
                        sender = "Unknown"
                    
                    # Cache the ID-to-phone mapping for consistent lookup
                    # This helps match sent and received messages for the same contact
                    if actual_phone and actual_phone != phone_number:
                        self.id_to_phone_map[actual_phone] = phone_number
                        print(f"DEBUG: Cached ID mapping {actual_phone} -> {phone_number}")
                    
                    # Normalize phone number for consistent matching
                    phone_key = self._get_contact_key(phone_number)
                    
                    if phone_key not in contacts_dict:
                        # Get display name from notifyName or use phone number
                        notify_name = msg_data.get('notifyName', '')
                        if notify_name and notify_name != phone_number:
                            display_name = notify_name
                        else:
                            # Use phone number as display name
                            display_name = phone_number
                        
                        contacts_dict[phone_key] = {
                            'number': phone_number,
                            'name': display_name,
                            'messages': [],
                            'last_message': '',
                            'last_message_time': '',
                            'unread_count': 0
                        }
                    else:
                        # Update display name if we find a better one (prefer actual names over phone numbers)
                        current_name = contacts_dict[phone_key]['name']
                        notify_name = msg_data.get('notifyName', '')
                        if notify_name and notify_name != phone_number:
                            # If current name is just a phone number and we found a real name, update it
                            if current_name.replace('+', '').replace(' ', '').replace('-', '').isdigit():
                                contacts_dict[phone_key]['name'] = notify_name
                    
                    contacts_dict[phone_key]['messages'].append(msg)
                    body = msg_data.get('body', 'Media')
                    if body and len(body) > 50:
                        body = body[:50] + '...'
                    contacts_dict[phone_key]['last_message'] = body
                    
                    # Update last message time only if this message is newer
                    msg_time = msg_data.get('t', msg_data.get('timestamp', ''))
                    if msg_time:
                        current_time = contacts_dict[phone_key].get('last_message_time', '0')
                        try:
                            if int(str(msg_time)) > int(str(current_time)):
                                contacts_dict[phone_key]['last_message_time'] = str(msg_time)
                        except:
                            contacts_dict[phone_key]['last_message_time'] = str(msg_time)
                    
                except Exception as e:
                    print(f"Error parsing received message: {e}")
                    continue
            
            # Process sent messages
            sent_messages = []
            if sent_data.get('status') and sent_data.get('response'):
                sent_messages = sent_data['response']
            elif isinstance(sent_data, list):
                sent_messages = sent_data
            elif isinstance(sent_data, dict) and 'response' in sent_data:
                sent_messages = sent_data['response']
            
                        
            for msg in sent_messages:
                try:
                    msg_data = msg.get('_data', msg)
                    
                    # Get fromMe from correct location (id.fromMe, not fromMe)
                    from_me = False
                    if 'id' in msg_data:
                        from_me = msg_data['id'].get('fromMe', False)
                    
                    # Extract phone number from id.remote or to field
                    recipient = None
                    phone_number = None
                    
                    # Try to get actual phone number from message fields first
                    actual_phone = None
                    
                    # Check 'to' field for actual phone number (not ID)
                    to_field = msg_data.get('to', '')
                    if isinstance(to_field, dict) and 'user' in to_field:
                        # Check if it's an actual phone number
                        user = to_field['user']
                        print(f"DEBUG sent: to_field is dict, user={user}")
                        if user.isdigit() and len(user) >= 10:
                            actual_phone = user
                    elif isinstance(to_field, str) and '@c.us' in to_field:
                        # This looks like an actual phone number
                        actual_phone = to_field.split('@')[0]
                    elif isinstance(to_field, str) and '@lid' in to_field:
                        # WhatsApp Limited Identifier - use as-is
                        actual_phone = to_field.split('@')[0]
                    elif isinstance(to_field, str) and to_field.isdigit() and len(to_field) >= 10:
                        actual_phone = to_field
                    
                    # Check 'from' field for actual phone number
                    from_field = msg_data.get('from', '')
                    if isinstance(from_field, str) and '@c.us' in from_field:
                        # This looks like an actual phone number
                        actual_phone = from_field.split('@')[0]
                    elif isinstance(from_field, str) and '@lid' in from_field:
                        # WhatsApp Limited Identifier - use as-is
                        actual_phone = from_field.split('@')[0]
                    elif isinstance(from_field, str) and from_field.isdigit() and len(from_field) >= 10:
                        actual_phone = from_field
                    
                    # If we found actual phone number, use it
                    if actual_phone:
                        # For LID-based numbers, use direct conversion without partner lookup
                        if len(actual_phone) >= 14 and not actual_phone.startswith('0') and not actual_phone.startswith('62'):
                            # This looks like a WhatsApp LID, convert directly
                            phone_number = self.convert_whatsapp_id_to_phone(actual_phone)
                            print(f"DEBUG sent: LID direct conversion: {actual_phone} -> {phone_number}")
                        else:
                            # Regular phone number processing
                            temp_phone = self.convert_whatsapp_id_to_phone(actual_phone)
                            print(f"DEBUG sent: actual_phone={actual_phone}, converted_phone={temp_phone}")
                            # Get actual conversation partner (not server number)
                            conversation_partner = self.get_conversation_partner(msg_data, temp_phone)
                            print(f"DEBUG sent: conversation_partner={conversation_partner}")
                            phone_number = conversation_partner if conversation_partner != temp_phone else temp_phone
                        recipient = phone_number
                    else:
                        # Fallback to ID-based conversion
                        if 'id' in msg_data and 'remote' in msg_data['id']:
                            remote = msg_data['id']['remote']
                            if '@' in remote:
                                raw_number = remote.split('@')[0]
                                temp_phone = self.convert_whatsapp_id_to_phone(raw_number)
                                # Get actual conversation partner
                                conversation_partner = self.get_conversation_partner(msg_data, temp_phone)
                                phone_number = conversation_partner if conversation_partner != temp_phone else temp_phone
                        
                        # Final fallback to to field
                        if not phone_number:
                            recipient = msg_data.get('to', 'Unknown')
                            if isinstance(recipient, dict):
                                recipient = str(recipient)
                            if '@' in recipient:
                                raw_number = recipient.split('@')[0]
                                temp_phone = self.convert_whatsapp_id_to_phone(raw_number)
                                conversation_partner = self.get_conversation_partner(msg_data, temp_phone)
                                phone_number = conversation_partner if conversation_partner != temp_phone else temp_phone
                            else:
                                phone_number = self.convert_whatsapp_id_to_phone(recipient)
                        else:
                            recipient = phone_number
                    
                    # Ensure we have a valid phone number
                    if not phone_number:
                        phone_number = "Unknown"
                        recipient = "Unknown"
                    
                    # Check if we have a cached mapping for this ID
                    # This ensures sent messages match with received messages from same contact
                    if actual_phone and actual_phone in self.id_to_phone_map:
                        cached_phone = self.id_to_phone_map[actual_phone]
                        if cached_phone != phone_number:
                            print(f"DEBUG: Using cached mapping for sent: {actual_phone} -> {cached_phone}")
                            phone_number = cached_phone
                    
                    # Also cache this mapping for future use
                    if actual_phone and phone_number not in ["Unknown", actual_phone]:
                        self.id_to_phone_map[actual_phone] = phone_number
                    
                    # Normalize phone number for consistent matching
                    phone_key = self._get_contact_key(phone_number)
                    
                    if phone_key not in contacts_dict:
                        # Get display name from notifyName or use phone number
                        display_name = msg_data.get('notifyName', phone_number)
                        if display_name == phone_number and '@' in phone_number:
                            display_name = phone_number.split('@')[0]
                        
                        contacts_dict[phone_key] = {
                            'number': phone_number,
                            'name': display_name,
                            'messages': [],
                            'last_message': '',
                            'last_message_time': '',
                            'unread_count': 0
                        }
                    
                    # Update display name for sent messages too
                    current_name = contacts_dict[phone_key]['name']
                    notify_name = msg_data.get('notifyName', '')
                    if notify_name and notify_name != phone_number:
                        # If current name is just a phone number and we found a real name, update it
                        if current_name.replace('+', '').replace(' ', '').replace('-', '').isdigit():
                            contacts_dict[phone_key]['name'] = notify_name
                    
                    contacts_dict[phone_key]['messages'].append(msg)
                    body = msg_data.get('body', 'Media')
                    if body and len(body) > 50:
                        body = body[:50] + '...'
                    contacts_dict[phone_key]['last_message'] = body
                    
                    # Update last message time only if this message is newer
                    msg_time = msg_data.get('t', msg_data.get('timestamp', ''))
                    if msg_time:
                        current_time = contacts_dict[phone_key].get('last_message_time', '0')
                        try:
                            if int(str(msg_time)) > int(str(current_time)):
                                contacts_dict[phone_key]['last_message_time'] = str(msg_time)
                        except:
                            contacts_dict[phone_key]['last_message_time'] = str(msg_time)
                    
                except Exception as e:
                    print(f"Error parsing sent message: {e}")
                    continue
        
        except Exception as e:
            print(f"Error parsing messages: {e}")
        
        # Convert to list and sort by last message time (like WhatsApp)
        contacts = list(contacts_dict.values())
        
        # Sort by last message time (most recent first), like WhatsApp
        def get_sort_key(contact):
            try:
                time_str = contact.get('last_message_time', '0')
                if time_str and time_str.isdigit():
                    return int(time_str)
                return 0
            except:
                return 0
        
        contacts.sort(key=get_sort_key, reverse=True)
        
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
                self.update_status("✓ Message sent successfully")
                # Refresh messages to show the sent message
                self.refresh_messages()
            else:
                error_msg = result.get('response', 'Unknown error')
                self.update_status("✗ Failed to send message")
                messagebox.showerror("Send Error", f"Failed to send message:\n\n{error_msg}")
                
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"✗ Error: {error_msg}")
            messagebox.showerror("Send Error", f"Failed to send message:\n\n{error_msg}")
    
    def handle_send_media(self, phone, file_path, caption=""):
        """Handle sending media message"""
        try:
            self.update_status(f"Sending media to {phone}...")
            
            # Send via API with caption
            result = self.api_client.send_media_message(phone, file_path, caption)
            
            if result.get('status'):
                self.update_status("✓ Media sent successfully")
                # Refresh messages to show the sent message
                self.refresh_messages()
            else:
                error_msg = result.get('response', 'Unknown error')
                self.update_status("✗ Failed to send media")
                messagebox.showerror("Send Error", f"Failed to send media:\n\n{error_msg}")
                
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"✗ Error: {error_msg}")
            messagebox.showerror("Send Error", f"Failed to send media:\n\n{error_msg}")
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
            self.toggle_btn.configure(text="⟩")
            self._position_toggle_button()
            self.toggle_btn.lift()
        else:
            self.sidebar.pack(side="left", fill="y", before=self.content_frame)
            self.sidebar_visible = True
            self.toggle_btn.configure(text="⟨")
            self._position_toggle_button()
            self.toggle_btn.lift()

    def _position_toggle_button(self):
        try:
            y = max(12, (self.winfo_height() // 2) - 20)
            if self.sidebar_visible:
                x = self.sidebar_width - 12  # menyatu di tepi kanan sidebar
            else:
                x = 8  # tepi kiri window saat sidebar hide
            self.toggle_btn.place(x=x, y=y)
        except Exception:
            pass
    
    def make_sidebar_draggable(self):
        """Make sidebar draggable to resize"""
        self.sidebar = self.sidebar  # Store reference
        
        def on_drag_start(event):
            self.drag_start_x = event.x
            self.drag_start_width = self.sidebar_width
        
        def on_drag_motion(event):
            if hasattr(self, 'drag_start_x'):
                # Calculate new width
                delta_x = event.x - self.drag_start_x
                new_width = self.drag_start_width + delta_x
                
                # Set minimum and maximum width
                new_width = max(150, min(400, new_width))
                
                # Update sidebar width
                self.sidebar_width = new_width
                self.sidebar.configure(width=new_width)
                
                # Update toggle button position
                if self.sidebar_visible:
                    self.toggle_btn.place(x=new_width - 25, y=5)
        
        def on_drag_end(event):
            if hasattr(self, 'drag_start_x'):
                delattr(self, 'drag_start_x')
                delattr(self, 'drag_start_width')
        
        # Bind mouse events for dragging
        self.sidebar.bind("<Button-1>", on_drag_start)
        self.sidebar.bind("<B1-Motion>", on_drag_motion)
        self.sidebar.bind("<ButtonRelease-1>", on_drag_end)
        
        # Change cursor when hovering over sidebar edge
        def on_enter(event):
            self.sidebar.configure(cursor="sb_h_double_arrow")
        
        def on_leave(event):
            self.sidebar.configure(cursor="")
        
        self.sidebar.bind("<Enter>", on_enter)
        self.sidebar.bind("<Leave>", on_leave)
    
    def handle_logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Note: We keep credentials file unchanged so remember checkbox stays as user set it
            # Call logout callback to return to login window
            if self.on_logout:
                self.on_logout()
            else:
                # Fallback: destroy and exit
                self.destroy()
                sys.exit(0)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=message)
    
    def start_realtime_polling(self):
        """Start background thread for real-time message polling"""
        if self.polling_thread and self.polling_thread.is_alive():
            return
        
        self.stop_polling.clear()
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        print("DEBUG: Real-time polling started")
    
    def stop_realtime_polling(self):
        """Stop the polling thread"""
        self.stop_polling.set()
        if self.polling_thread:
            self.polling_thread.join(timeout=1)
    
    def _polling_loop(self):
        """Background thread that polls for new messages every 3 seconds"""
        while not self.stop_polling.is_set():
            try:
                time.sleep(3)  # Poll every 3 seconds
                
                if self.stop_polling.is_set():
                    break
                
                # Use after() to safely update UI from background thread
                self.after(0, self._check_for_new_messages)
                
            except Exception as e:
                print(f"DEBUG: Polling error: {e}")
    
    def _check_for_new_messages(self):
        """Check for new messages and refresh if needed (called in main thread)"""
        try:
            # Quick check for new messages from current API only
            received_data = self.api_client.get_received_messages()
            sent_data = self.api_client.get_sent_messages()
            
            current_count = self._count_messages(received_data) + self._count_messages(sent_data)
            
            # If message count changed, do full refresh
            if current_count != self.last_message_count:
                if self.last_message_count > 0:
                    print(f"DEBUG: New messages detected ({self.last_message_count} -> {current_count}), refreshing...")
                    self.update_status(f"📩 {current_count - self.last_message_count} new message(s) received")
                    self.refresh_messages()
                self.last_message_count = current_count
            
        except Exception as e:
            # Silently fail - don't show errors during polling
            print(f"DEBUG: Check messages error: {e}")
