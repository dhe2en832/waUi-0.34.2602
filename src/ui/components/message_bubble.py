"""
Message Bubble Component
WhatsApp-like message bubbles for sent and received messages
"""

import customtkinter as ctk
from datetime import datetime


class MessageBubble(ctk.CTkFrame):
    """Individual message bubble component"""
    
    def __init__(self, parent, message_data, is_sent=False):
        """
        Initialize message bubble
        
        Args:
            parent: Parent widget
            message_data: Dict with message info (text, timestamp, status, etc)
            is_sent: True if sent message, False if received
        """
        super().__init__(parent, fg_color="transparent")
        
        self.message_data = message_data
        self.is_sent = is_sent
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup message bubble UI"""
        # Container for alignment
        container = ctk.CTkFrame(self, fg_color="transparent")
        
        if self.is_sent:
            # Sent messages: right-aligned
            container.pack(fill="x", padx=10, pady=4, anchor="e")
            bubble_color = "#007AFF"  # Blue
            text_color = "white"
            align = "e"
        else:
            # Received messages: left-aligned
            container.pack(fill="x", padx=10, pady=4, anchor="w")
            bubble_color = "#E5E5EA"  # Gray
            text_color = "black"
            align = "w"
        
        # Message bubble
        bubble_frame = ctk.CTkFrame(
            container,
            fg_color=bubble_color,
            corner_radius=15
        )
        bubble_frame.pack(side=align, padx=(0 if self.is_sent else 50, 50 if self.is_sent else 0))
        
        # Message text
        message_text = self.message_data.get('text', self.message_data.get('body', 'No message'))
        
        text_label = ctk.CTkLabel(
            bubble_frame,
            text=message_text,
            font=ctk.CTkFont(size=14),
            text_color=text_color,
            wraplength=400,
            justify="left",
            anchor="w"
        )
        text_label.pack(padx=12, pady=(8, 4), anchor="w")
        
        # Bottom info (time + status)
        info_frame = ctk.CTkFrame(bubble_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        # Timestamp
        timestamp = self.format_timestamp(self.message_data.get('timestamp', self.message_data.get('t', '')))
        time_label = ctk.CTkLabel(
            info_frame,
            text=timestamp,
            font=ctk.CTkFont(size=11),
            text_color=text_color if self.is_sent else "#8E8E93"
        )
        time_label.pack(side="left")
        
        # Status for sent messages
        if self.is_sent:
            status = self.get_status_icon(self.message_data.get('ack', 0))
            status_label = ctk.CTkLabel(
                info_frame,
                text=status,
                font=ctk.CTkFont(size=11),
                text_color=text_color
            )
            status_label.pack(side="left", padx=(5, 0))
        
        # Media indicator
        if self.message_data.get('hasMedia') or self.message_data.get('type') == 'image':
            media_label = ctk.CTkLabel(
                bubble_frame,
                text="📎 Media",
                font=ctk.CTkFont(size=12),
                text_color=text_color
            )
            media_label.pack(padx=12, pady=(0, 4), anchor="w")
    
    def format_timestamp(self, timestamp):
        """Format timestamp to readable format"""
        try:
            if isinstance(timestamp, int):
                # Unix timestamp
                dt = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                # Try parsing string
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                return "Unknown"
            
            # Format as HH:MM
            return dt.strftime("%H:%M")
        except:
            return str(timestamp)[:5] if timestamp else ""
    
    def get_status_icon(self, ack):
        """Get status icon based on ack value"""
        status_map = {
            0: "○",      # Pending
            1: "✓",      # Sent
            2: "✓✓",     # Delivered
            3: "✓✓",     # Read (blue in real WhatsApp)
        }
        return status_map.get(ack, "○")


class DateSeparator(ctk.CTkFrame):
    """Date separator for grouping messages"""
    
    def __init__(self, parent, date_text):
        super().__init__(parent, fg_color="transparent")
        
        # Container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", pady=10)
        
        # Date label
        date_label = ctk.CTkFrame(container, fg_color="#E5E5EA", corner_radius=10)
        date_label.pack()
        
        ctk.CTkLabel(
            date_label,
            text=date_text,
            font=ctk.CTkFont(size=12),
            text_color="#8E8E93"
        ).pack(padx=12, pady=4)
