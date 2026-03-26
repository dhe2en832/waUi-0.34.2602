"""
Chat View Component
WhatsApp-like conversation view with message bubbles
"""

import customtkinter as ctk
from tkinter import filedialog
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.ui.components.message_bubble import MessageBubble, DateSeparator


class ChatView(ctk.CTkFrame):
    """Chat conversation view component"""
    
    def __init__(self, parent, on_send_message=None):
        super().__init__(parent)
        
        self.on_send_message = on_send_message
        self.current_contact = None
        self.messages = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup chat view UI"""
        # Header
        self.header = ctk.CTkFrame(self, height=60, fg_color="#F2F2F7")
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        # Contact info
        contact_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        contact_frame.pack(side="left", padx=20, pady=10)
        
        self.contact_name_label = ctk.CTkLabel(
            contact_frame,
            text="Select a contact",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.contact_name_label.pack(anchor="w")
        
        self.contact_status_label = ctk.CTkLabel(
            contact_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#8E8E93"
        )
        self.contact_status_label.pack(anchor="w")
        
        # Messages area (scrollable)
        self.messages_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white"
        )
        self.messages_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Input area
        input_container = ctk.CTkFrame(self, height=70, fg_color="#F2F2F7")
        input_container.pack(fill="x", side="bottom")
        input_container.pack_propagate(False)
        
        input_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        input_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Attach button
        attach_btn = ctk.CTkButton(
            input_frame,
            text="📎",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            fg_color="#E5E5EA",
            text_color="black",
            hover_color="#D1D1D6",
            command=self.attach_media
        )
        attach_btn.pack(side="left", padx=(0, 10))
        
        # Message input
        self.message_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.message_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.message_input.bind("<Return>", lambda e: self.send_message())
        
        # Send button
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="▶",
            width=40,
            height=40,
            font=ctk.CTkFont(size=16),
            fg_color="#007AFF",
            hover_color="#0051D5",
            command=self.send_message
        )
        self.send_btn.pack(side="left")
        
    def set_contact(self, contact_data):
        """Set current contact and load messages"""
        self.current_contact = contact_data
        
        # Update header
        contact_name = contact_data.get('name', contact_data.get('number', 'Unknown'))
        self.contact_name_label.configure(text=contact_name)
        self.contact_status_label.configure(text="Online")
        
        # Clear and load messages
        self.clear_messages()
        self.load_messages(contact_data.get('messages', []))
        
    def load_messages(self, messages):
        """Load messages into chat view"""
        self.messages = messages
        
        # Group messages by date
        grouped_messages = self.group_by_date(messages)
        
        for date_text, date_messages in grouped_messages.items():
            # Add date separator
            DateSeparator(self.messages_frame, date_text).pack(fill="x")
            
            # Add messages
            for msg in date_messages:
                is_sent = msg.get('fromMe', False) or msg.get('_data', {}).get('id', {}).get('fromMe', False)
                bubble = MessageBubble(self.messages_frame, msg, is_sent=is_sent)
                bubble.pack(fill="x")
        
        # Scroll to bottom
        self.messages_frame._parent_canvas.yview_moveto(1.0)
        
    def group_by_date(self, messages):
        """Group messages by date"""
        from datetime import datetime
        from collections import OrderedDict
        
        grouped = OrderedDict()
        
        for msg in messages:
            # Get timestamp
            timestamp = msg.get('timestamp', msg.get('t', 0))
            
            try:
                if isinstance(timestamp, int):
                    dt = datetime.fromtimestamp(timestamp)
                else:
                    dt = datetime.now()
                
                # Format date
                today = datetime.now().date()
                msg_date = dt.date()
                
                if msg_date == today:
                    date_key = "Today"
                elif (today - msg_date).days == 1:
                    date_key = "Yesterday"
                else:
                    date_key = dt.strftime("%B %d, %Y")
                
                if date_key not in grouped:
                    grouped[date_key] = []
                grouped[date_key].append(msg)
                
            except:
                if "Unknown" not in grouped:
                    grouped["Unknown"] = []
                grouped["Unknown"].append(msg)
        
        return grouped
        
    def clear_messages(self):
        """Clear all messages from view"""
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
    def send_message(self):
        """Send message"""
        message_text = self.message_input.get().strip()
        
        if not message_text:
            return
        
        if not self.current_contact:
            return
        
        # Get phone number
        phone = self.current_contact.get('number', self.current_contact.get('phone', ''))
        
        if self.on_send_message:
            self.on_send_message(phone, message_text)
        
        # Clear input
        self.message_input.delete(0, 'end')
        
        # Add message to view (optimistic update)
        from datetime import datetime
        new_message = {
            'text': message_text,
            'timestamp': int(datetime.now().timestamp()),
            'fromMe': True,
            'ack': 0
        }
        
        bubble = MessageBubble(self.messages_frame, new_message, is_sent=True)
        bubble.pack(fill="x")
        
        # Scroll to bottom
        self.messages_frame._parent_canvas.yview_moveto(1.0)
        
    def attach_media(self):
        """Attach media file"""
        file_path = filedialog.askopenfilename(
            title="Select Media File",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif"),
                ("Videos", "*.mp4 *.avi *.mov"),
                ("Documents", "*.pdf *.doc *.docx"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            # TODO: Handle media upload
            print(f"Selected file: {file_path}")
