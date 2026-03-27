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
        self.header = ctk.CTkFrame(self, height=60, fg_color="white")
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
            text_color="#667781"
        )
        self.contact_status_label.pack(anchor="w")
        
        # Messages area (scrollable)
        self.messages_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#F5F6F6"
        )
        self.messages_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        input_container = ctk.CTkFrame(self, height=70, fg_color="white")
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
            fg_color="#F0F2F5",
            text_color="#111B21",
            hover_color="#E9EDEF",
            command=self.attach_media
        )
        attach_btn.pack(side="left", padx=(0, 10))
        
        # Message input
        self.message_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message...",
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#E9EDEF",
            fg_color="#F8F9FA"
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
        
    def _normalize_message(self, msg):
        if isinstance(msg, dict) and isinstance(msg.get("_data"), dict):
            normalized = dict(msg["_data"])
            normalized["_raw"] = msg
            return normalized
        if isinstance(msg, dict):
            return msg
        return {}

    def set_contact(self, contact_data):
        """Set current contact and load messages"""
        self.current_contact = contact_data
        
        # Update header with name and number on same line
        contact_name = contact_data.get('name', 'Unknown')
        contact_number = contact_data.get('number', '')
        
        # Display both name and number on same line
        if contact_number and contact_number != contact_name:
            header_text = f"{contact_name} • {contact_number}"
        else:
            header_text = contact_name
            
        self.contact_name_label.configure(text=header_text)
        self.contact_status_label.configure(text="Online")
        
        # Clear and load messages
        self.clear_messages()
        messages = contact_data.get('messages', [])
        normalized_messages = [self._normalize_message(m) for m in messages if m]
        self.load_messages(normalized_messages)
        
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
                try:
                    is_sent = bool(msg.get("fromMe") or (isinstance(msg.get("id"), dict) and msg["id"].get("fromMe")))
                    bubble = MessageBubble(self.messages_frame, msg, is_sent=is_sent)
                    bubble.pack(fill="x")
                except Exception as e:
                    print(f"DEBUG: Error rendering message bubble: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        # Scroll to bottom
        try:
            self.messages_frame._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass
        
    def group_by_date(self, messages):
        """Group messages by date with WhatsApp-like order"""
        from datetime import datetime
        
        grouped = {}
        
        for msg in messages:
            # Get timestamp
            timestamp = msg.get('timestamp', msg.get('t', 0))
            
            try:
                if isinstance(timestamp, str) and timestamp.isdigit():
                    timestamp = int(timestamp)
                if isinstance(timestamp, int) and timestamp > 0:
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
        
        # Sort messages within each date group (oldest first, like WhatsApp)
        for date_key in grouped:
            def _msg_sort_key(m):
                t = m.get("timestamp", m.get("t", 0))
                if isinstance(t, str) and t.isdigit():
                    return int(t)
                if isinstance(t, int):
                    return t
                raw = m.get('_raw', {})
                if isinstance(raw, dict):
                    data = raw.get('_data', {})
                    tt = data.get('timestamp', data.get('t', 0))
                    try:
                        return int(tt)
                    except Exception:
                        return 0
                return 0
            grouped[date_key].sort(key=_msg_sort_key)
        
        # Sort dates in WhatsApp-like order: Yesterday → Today (oldest first, newest at bottom)
        def get_date_sort_key(date_key):
            if date_key == "Yesterday":
                return 0  # Yesterday first (top)
            elif date_key == "Today":
                return 1  # Today second (bottom)
            elif date_key == "Unknown":
                return 999  # Unknown last
            else:
                # For other dates, parse and sort by date (older first)
                try:
                    dt = datetime.strptime(date_key, "%B %d, %Y")
                    return 2 + (datetime.now().date() - dt.date()).days
                except:
                    return 998
        
        # Sort and return ordered dict
        sorted_keys = sorted(grouped.keys(), key=get_date_sort_key)
        return {key: grouped[key] for key in sorted_keys}
        
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
