"""
Chat List Component
Contact/conversation list with search functionality
"""

import customtkinter as ctk


class ChatListItem(ctk.CTkFrame):
    """Individual chat list item"""
    
    def __init__(self, parent, contact_data, on_click=None):
        super().__init__(parent, fg_color="transparent", cursor="hand2")
        
        self.contact_data = contact_data
        self.on_click = on_click
        self.is_selected = False
        
        self.setup_ui()
        self.bind("<Button-1>", self.handle_click)
        
    def setup_ui(self):
        """Setup chat list item UI"""
        # Container
        self.container = ctk.CTkFrame(
            self, 
            fg_color="transparent", 
            height=72,
            corner_radius=0
        )
        self.container.pack(fill="x", padx=0, pady=0)
        self.container.pack_propagate(False)
        
        # Hover effect container (inner)
        self.inner_container = ctk.CTkFrame(
            self.container,
            fg_color="transparent",
            corner_radius=8
        )
        self.inner_container.pack(fill="both", expand=True, padx=8, pady=4)
        
        # Avatar
        avatar_frame = ctk.CTkFrame(
            self.inner_container,
            width=48,
            height=48,
            corner_radius=24,
            fg_color="#007AFF"
        )
        avatar_frame.pack(side="left", padx=(12, 12), pady=8)
        avatar_frame.pack_propagate(False)
        
        # Get first letter of name
        name = self.contact_data.get('name', self.contact_data.get('number', '?'))
        if not name or name == 'None':
            name = self.contact_data.get('number', '?')
            
        initial = name[0].upper() if name and name != '?' else '?'
        
        ctk.CTkLabel(
            avatar_frame,
            text=initial,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Info container
        info_frame = ctk.CTkFrame(self.inner_container, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=10)
        
        # Top row: Name and time
        top_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        top_row.pack(fill="x")
        
        # Name
        display_name = name[:25] + "..." if len(name) > 25 else name
        
        self.name_label = ctk.CTkLabel(
            top_row,
            text=display_name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#111B21",
            anchor="w"
        )
        self.name_label.pack(side="left", fill="x", expand=True)
        
        # Time
        time_text = self.contact_data.get('last_message_time', '')
        if time_text:
            formatted_time = self.format_time_display(time_text)
            self.time_label = ctk.CTkLabel(
                top_row,
                text=formatted_time,
                font=ctk.CTkFont(size=11),
                text_color="#667781"
            )
            self.time_label.pack(side="right", padx=(5, 0))
        
        # Bottom row: Last message and unread count
        bottom_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(2, 0))
        
        # Last message preview
        last_msg = self.contact_data.get('last_message', '')
        if not last_msg or last_msg == 'None':
            last_msg = 'No messages'
            
        self.msg_label = ctk.CTkLabel(
            bottom_row,
            text=last_msg[:35] + "..." if len(last_msg) > 35 else last_msg,
            font=ctk.CTkFont(size=13),
            text_color="#667781",
            anchor="w"
        )
        self.msg_label.pack(side="left", fill="x", expand=True)
        
        # Unread count badge
        unread_count = self.contact_data.get('unread_count', 0)
        if unread_count and int(unread_count) > 0:
            self.badge = ctk.CTkFrame(
                bottom_row,
                fg_color="#007AFF",
                corner_radius=10,
                width=20,
                height=20
            )
            self.badge.pack(side="right")
            self.badge.pack_propagate(False)
            
            ctk.CTkLabel(
                self.badge,
                text=str(unread_count),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="white"
            ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Bind events for hover and click
        self.bind_events(self.container)
        self.bind_events(self.inner_container)
        for widget in self.inner_container.winfo_children():
            self.bind_events(widget)
            for child in widget.winfo_children():
                self.bind_events(child)

    def bind_events(self, widget):
        """Bind hover and click events"""
        widget.bind("<Enter>", self.on_enter)
        widget.bind("<Leave>", self.on_leave)
        widget.bind("<Button-1>", self.handle_click)

    def on_enter(self, event=None):
        """Handle mouse enter"""
        if not self.is_selected:
            self.inner_container.configure(fg_color="#F0F2F5")

    def on_leave(self, event=None):
        """Handle mouse leave"""
        if not self.is_selected:
            self.inner_container.configure(fg_color="transparent")
    
    def handle_click(self, event=None):
        """Handle item click"""
        if self.on_click:
            self.on_click(self.contact_data)
        self.set_selected(True)
    
    def format_time_display(self, time_str):
        """Format time like WhatsApp (e.g., '10:30', 'Yesterday', 'dd/mm')"""
        try:
            if not time_str or time_str == '0':
                return ''
            
            # Convert timestamp to datetime
            import datetime
            try:
                timestamp = int(time_str)
                msg_time = datetime.datetime.fromtimestamp(timestamp)
            except:
                return time_str
            
            now = datetime.datetime.now()
            today = now.date()
            msg_date = msg_time.date()
            
            # Calculate days difference
            days_diff = (today - msg_date).days
            
            if days_diff == 0:
                # Today - show time only
                return msg_time.strftime('%H:%M')
            elif days_diff == 1:
                # Yesterday
                return 'Yesterday'
            elif days_diff < 7:
                # This week - show day name
                return msg_time.strftime('%A')
            else:
                # Older - show date
                return msg_time.strftime('%d/%m')
                
        except Exception:
            return time_str
    
    def set_selected(self, selected):
        """Set selection state"""
        self.is_selected = selected
        try:
            if selected:
                self.inner_container.configure(fg_color="#E6F0FF")
                self.name_label.configure(text_color="#000000")
            else:
                self.inner_container.configure(fg_color="transparent")
                self.name_label.configure(text_color="#111B21")
        except Exception:
            pass


class ChatList(ctk.CTkFrame):
    """Chat list component with search"""
    
    def __init__(self, parent, on_chat_select=None):
        super().__init__(parent, fg_color="#F5F6F6")
        
        self.on_chat_select = on_chat_select
        self.chat_items = []
        self.selected_item = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup chat list UI"""
        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search contacts...",
            height=35,
            font=ctk.CTkFont(size=13),
            corner_radius=10,
            border_color="#E9EDEF",
            fg_color="white"
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_chats)
        
        # Chat list (scrollable)
        self.chat_list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white"
        )
        self.chat_list_frame.pack(fill="both", expand=True)
        
    def load_contacts(self, contacts):
        """Load contacts into list"""
        # Clear existing
        for item in self.chat_items:
            item.destroy()
        self.chat_items.clear()
        
        # Add contacts
        for contact in contacts:
            item = ChatListItem(
                self.chat_list_frame,
                contact,
                on_click=self.handle_chat_select
            )
            item.pack(fill="x")
            self.chat_items.append(item)
    
    def handle_chat_select(self, contact_data):
        """Handle chat selection"""
        # Deselect previous
        if self.selected_item:
            self.selected_item.set_selected(False)
        
        # Find and select new item
        for item in self.chat_items:
            if item.contact_data == contact_data:
                item.set_selected(True)
                self.selected_item = item
                break
        
        # Callback
        if self.on_chat_select:
            self.on_chat_select(contact_data)
    
    def filter_chats(self, event=None):
        """Filter chats based on search"""
        search_text = self.search_entry.get().lower()
        
        for item in self.chat_items:
            name = item.contact_data.get('name', '').lower()
            number = item.contact_data.get('number', '').lower()
            
            if search_text in name or search_text in number:
                item.pack(fill="x")
            else:
                item.pack_forget()
    
    def add_contact(self, contact_data):
        """Add a new contact to the list"""
        item = ChatListItem(
            self.chat_list_frame,
            contact_data,
            on_click=self.handle_chat_select
        )
        item.pack(fill="x")
        self.chat_items.insert(0, item)
