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
        self.container = ctk.CTkFrame(self, fg_color="transparent", height=70)
        self.container.pack(fill="x", padx=5, pady=2)
        self.container.pack_propagate(False)
        
        # Avatar
        avatar_frame = ctk.CTkFrame(
            self.container,
            width=50,
            height=50,
            corner_radius=25,
            fg_color="#007AFF"
        )
        avatar_frame.pack(side="left", padx=10, pady=10)
        avatar_frame.pack_propagate(False)
        
        # Get first letter of name
        name = self.contact_data.get('name', self.contact_data.get('number', '?'))
        initial = name[0].upper() if name else '?'
        
        ctk.CTkLabel(
            avatar_frame,
            text=initial,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Info container
        info_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # Top row: Name and time
        top_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        top_row.pack(fill="x")
        
        # Name
        name_label = ctk.CTkLabel(
            top_row,
            text=name[:25] + "..." if len(name) > 25 else name,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Time
        time_text = self.contact_data.get('last_message_time', '')
        if time_text:
            time_label = ctk.CTkLabel(
                top_row,
                text=time_text,
                font=ctk.CTkFont(size=11),
                text_color="#8E8E93"
            )
            time_label.pack(side="right")
        
        # Bottom row: Last message and unread count
        bottom_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        bottom_row.pack(fill="x")
        
        # Last message preview
        last_msg = self.contact_data.get('last_message', 'No messages yet')
        msg_label = ctk.CTkLabel(
            bottom_row,
            text=last_msg[:35] + "..." if len(last_msg) > 35 else last_msg,
            font=ctk.CTkFont(size=12),
            text_color="#8E8E93",
            anchor="w"
        )
        msg_label.pack(side="left", fill="x", expand=True)
        
        # Unread count badge
        unread_count = self.contact_data.get('unread_count', 0)
        if unread_count > 0:
            badge = ctk.CTkFrame(
                bottom_row,
                fg_color="#34C759",
                corner_radius=10,
                width=20,
                height=20
            )
            badge.pack(side="right")
            badge.pack_propagate(False)
            
            ctk.CTkLabel(
                badge,
                text=str(unread_count),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Bind click to all children
        for widget in self.container.winfo_children():
            widget.bind("<Button-1>", self.handle_click)
            for child in widget.winfo_children():
                child.bind("<Button-1>", self.handle_click)
    
    def handle_click(self, event=None):
        """Handle item click"""
        if self.on_click:
            self.on_click(self.contact_data)
        self.set_selected(True)
    
    def set_selected(self, selected):
        """Set selection state"""
        self.is_selected = selected
        if selected:
            self.container.configure(fg_color="#E5E5EA")
        else:
            self.container.configure(fg_color="transparent")


class ChatList(ctk.CTkFrame):
    """Chat list component with search"""
    
    def __init__(self, parent, on_chat_select=None):
        super().__init__(parent, fg_color="#F2F2F7")
        
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
            font=ctk.CTkFont(size=13)
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
