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
            # Sent messages: right-aligned with WhatsApp-style colors
            container.pack(fill="x", padx=(60, 12), pady=4, anchor="e")
            bubble_color = "#D6E9FF"
            text_color = "#111B21"
            align = "right"
        else:
            # Received messages: left-aligned
            container.pack(fill="x", padx=(12, 60), pady=4, anchor="w")
            bubble_color = "#FFFFFF"
            text_color = "#111B21"
            align = "left"
        
        # Message bubble with rounded corners
        bubble_frame = ctk.CTkFrame(
            container,
            fg_color=bubble_color,
            corner_radius=12,
            border_width=0
        )
        bubble_frame.pack(side=align, fill="x", expand=False)
        
        # Inner layout to handle text and info row
        inner_content = ctk.CTkFrame(bubble_frame, fg_color="transparent")
        inner_content.pack(padx=8, pady=4)

        # Message text (robust extraction)
        message_text = self.message_data.get('text') or self.message_data.get('body') or ""
        if not message_text:
            raw = self.message_data.get('_raw', {})
            if isinstance(raw, dict):
                data = raw.get('_data', {})
                message_text = data.get('body') or data.get('text') or data.get('caption') or ""
        if not message_text or message_text == 'None':
            message_text = 'Empty message'

        text_label = ctk.CTkLabel(
            inner_content,
            text=message_text,
            font=ctk.CTkFont(size=14),
            text_color=text_color,
            wraplength=400,
            justify="left",
            anchor="w"
        )
        text_label.pack(padx=4, pady=(2, 0), anchor="w")
        
        # Bottom info (time + status)
        info_frame = ctk.CTkFrame(inner_content, fg_color="transparent")
        info_frame.pack(side="right", anchor="e", pady=(2, 0))
        
        # Timestamp (robust extraction)
        ts = self.message_data.get('timestamp', self.message_data.get('t'))
        if ts is None:
            raw = self.message_data.get('_raw', {})
            if isinstance(raw, dict):
                data = raw.get('_data', {})
                ts = data.get('timestamp', data.get('t'))
        timestamp = self.format_timestamp(ts)
        time_label = ctk.CTkLabel(
            info_frame,
            text=timestamp,
            font=ctk.CTkFont(size=10),
            text_color="#667781"
        )
        time_label.pack(side="left")
        
        # Status for sent messages
        if self.is_sent:
            ack = self.message_data.get('ack', 0)
            status_color = "#007AFF" if ack >= 3 else "#667781"
            status_icon = self.get_status_icon(ack)
            
            status_label = ctk.CTkLabel(
                info_frame,
                text=status_icon,
                font=ctk.CTkFont(size=12),
                text_color=status_color
            )
            status_label.pack(side="left", padx=(4, 0))

    def get_status_icon(self, ack):
        """Get status icon based on ack value"""
        if ack == 0: return "🕐" # Pending
        if ack == 1: return "✓"  # Sent
        if ack == 2: return "✓✓" # Delivered
        if ack >= 3: return "✓✓" # Read
        return "✓"

    def format_timestamp(self, ts):
        """Format timestamp to HH:MM"""
        try:
            if ts is None:
                return ""
            if isinstance(ts, str) and ts.isdigit():
                ts = int(ts)
            if isinstance(ts, int) and ts > 0:
                dt = datetime.fromtimestamp(ts)
                return dt.strftime("%H:%M")
            return ""
        except:
            return ""


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
