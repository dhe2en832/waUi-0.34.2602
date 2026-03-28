"""
Chat View Component
WhatsApp-like conversation view with message bubbles
"""

import customtkinter as ctk
from tkinter import filedialog
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.ui.components.message_bubble import MessageBubble, DateSeparator


class ChatView(ctk.CTkFrame):
    """Chat conversation view component"""
    
    def __init__(self, parent, on_send_message=None, on_send_media=None):
        super().__init__(parent)
        
        self.on_send_message = on_send_message
        self.on_send_media = on_send_media
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
        
        # Scroll to bottom after UI is fully rendered
        self.after(100, self._scroll_to_bottom)
        
    def _scroll_to_bottom(self):
        """Scroll messages to bottom"""
        try:
            self.messages_frame._parent_canvas.yview_moveto(1.0)
        except Exception as e:
            print(f"DEBUG: Error scrolling to bottom: {e}")
        
    def group_by_date(self, messages):
        """Group messages by date with WhatsApp-like order"""
        from datetime import datetime, timedelta
        
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
        
        # Sort dates in WhatsApp-like order: oldest first (top), newest at bottom
        # Messages should flow chronologically: older messages at top, newer at bottom
        def get_date_sort_key(date_key):
            today = datetime.now().date()
            
            if date_key == "Unknown":
                return 99999  # Unknown last
            elif date_key == "Today":
                # Today should be at the bottom (newest)
                return today.toordinal()
            elif date_key == "Yesterday":
                # Yesterday should be just before Today
                return (today - timedelta(days=1)).toordinal()
            else:
                # For other dates, parse and return the actual date ordinal
                try:
                    dt = datetime.strptime(date_key, "%B %d, %Y")
                    return dt.date().toordinal()
                except:
                    return 99998
        
        # Sort and return ordered dict (oldest dates first)
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
        
        # Scroll to bottom after UI update
        self.after(100, self._scroll_to_bottom)
        
    def attach_media(self):
        """Attach media file - show preview dialog like WhatsApp"""
        file_path = filedialog.askopenfilename(
            title="Select Media File",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("Videos", "*.mp4 *.avi *.mov *.mkv"),
                ("Documents", "*.pdf *.doc *.docx *.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path and self.current_contact:
            self.show_media_preview(file_path)
    
    def show_media_preview(self, file_path):
        """Show media preview dialog with caption input - WhatsApp style"""
        # Create overlay frame (dark gray semi-transparent look)
        self.preview_overlay = ctk.CTkFrame(self, fg_color="#1a1a2e")
        self.preview_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.preview_overlay.lift()
        
        # Preview container - larger size like WhatsApp
        preview_container = ctk.CTkFrame(self.preview_overlay, fg_color="#111B21", corner_radius=20, width=500, height=450)
        preview_container.place(relx=0.5, rely=0.45, anchor="center")
        preview_container.pack_propagate(False)
        
        # Header
        header = ctk.CTkFrame(preview_container, fg_color="#202C33", height=55, corner_radius=20)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="Send to " + self.current_contact.get('name', 'Unknown'),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=20, pady=15)
        
        # Close button
        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=35,
            height=35,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color="#374151",
            command=self.close_media_preview
        )
        close_btn.pack(side="right", padx=15, pady=10)
        
        # Media preview area - larger
        media_frame = ctk.CTkFrame(preview_container, fg_color="#0B141A", corner_radius=15)
        media_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Try to show image preview
        try:
            ext = os.path.splitext(file_path)[1].lower()
            image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
            
            if ext in image_exts:
                try:
                    # Use PyQt5 for image display
                    from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit
                    from PyQt5.QtGui import QPixmap
                    from PyQt5.QtCore import Qt
                    import sys
                    
                    # Create QApplication if not exists
                    qt_app = QApplication.instance()
                    if qt_app is None:
                        qt_app = QApplication(sys.argv)
                    
                    # Create preview dialog
                    dialog = QDialog()
                    dialog.setWindowTitle(f"Send to {self.current_contact.get('name', 'Unknown')}")
                    dialog.setMinimumSize(500, 450)
                    dialog.setStyleSheet("""
                        QDialog {
                            background-color: #111B21;
                        }
                        QPushButton {
                            background-color: #00A884;
                            color: white;
                            border: none;
                            border-radius: 20px;
                            padding: 10px 20px;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #008F72;
                        }
                        QLineEdit {
                            background-color: #202C33;
                            color: white;
                            border: 1px solid #374151;
                            border-radius: 8px;
                            padding: 10px;
                            font-size: 14px;
                        }
                        QLabel {
                            color: white;
                        }
                    """)
                    
                    layout = QVBoxLayout(dialog)
                    layout.setSpacing(15)
                    layout.setContentsMargins(20, 20, 20, 20)
                    
                    # Image label
                    img_label = QLabel()
                    pixmap = QPixmap(file_path)
                    
                    # Scale to fit
                    max_width = 450
                    max_height = 300
                    scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    img_label.setPixmap(scaled_pixmap)
                    img_label.setAlignment(Qt.AlignCenter)
                    layout.addWidget(img_label)
                    
                    # Caption input
                    caption_input = QLineEdit()
                    caption_input.setPlaceholderText("Add a caption...")
                    layout.addWidget(caption_input)
                    
                    # Buttons
                    btn_layout = QHBoxLayout()
                    
                    close_btn = QPushButton("Cancel")
                    close_btn.setStyleSheet("background-color: #374151;")
                    close_btn.clicked.connect(dialog.reject)
                    btn_layout.addWidget(close_btn)
                    
                    send_btn = QPushButton("Send")
                    send_btn.clicked.connect(dialog.accept)
                    btn_layout.addWidget(send_btn)
                    
                    layout.addLayout(btn_layout)
                    
                    # Show dialog
                    result = dialog.exec_()
                    
                    if result == QDialog.Accepted:
                        # Get caption and send
                        caption = caption_input.text().strip()
                        if self.current_contact and self.on_send_media:
                            phone = self.current_contact.get('number', self.current_contact.get('phone', ''))
                            self.on_send_media(phone, file_path, caption)
                    
                    # Don't show the customtkinter preview since we used PyQt5
                    self.preview_overlay.destroy()
                    delattr(self, 'preview_overlay')
                    return
                    
                except Exception as qt_err:
                    print(f"DEBUG: PyQt5 failed: {qt_err}")
                    import traceback
                    traceback.print_exc()
                    # Continue to show fallback icon preview
            else:
                # Show file icon/name for non-images - centered and larger
                file_name = os.path.basename(file_path)
                file_frame = ctk.CTkFrame(media_frame, fg_color="transparent")
                file_frame.pack(expand=True)
                
                file_icon = ctk.CTkLabel(
                    file_frame,
                    text="📄",
                    font=ctk.CTkFont(size=64),
                    text_color="#667781"
                )
                file_icon.pack(pady=(20, 10))
                
                file_label = ctk.CTkLabel(
                    file_frame,
                    text=file_name,
                    font=ctk.CTkFont(size=14),
                    text_color="white",
                    wraplength=350
                )
                file_label.pack(pady=(0, 20))
        except Exception as e:
            # Fallback to filename - centered
            file_name = os.path.basename(file_path)
            file_frame = ctk.CTkFrame(media_frame, fg_color="transparent")
            file_frame.pack(expand=True)
            
            file_icon = ctk.CTkLabel(
                file_frame,
                text="📎",
                font=ctk.CTkFont(size=64),
                text_color="#667781"
            )
            file_icon.pack(pady=(20, 10))
            
            file_label = ctk.CTkLabel(
                file_frame,
                text=file_name,
                font=ctk.CTkFont(size=14),
                text_color="white",
                wraplength=350
            )
            file_label.pack(pady=(0, 20))
        
        # Caption input area - at bottom like WhatsApp
        caption_frame = ctk.CTkFrame(preview_container, fg_color="#202C33", height=70, corner_radius=15)
        caption_frame.pack(fill="x", padx=20, pady=(0, 20))
        caption_frame.pack_propagate(False)
        
        self.caption_input = ctk.CTkEntry(
            caption_frame,
            placeholder_text="Add a caption...",
            font=ctk.CTkFont(size=14),
            fg_color="#202C33",
            border_color="#374151",
            text_color="white",
            height=45
        )
        self.caption_input.pack(side="left", fill="x", expand=True, padx=15, pady=12)
        self.caption_input.bind("<Return>", lambda e: self.send_media_with_caption(file_path))
        
        # Send button (green circle like WhatsApp)
        send_btn = ctk.CTkButton(
            caption_frame,
            text="▶",
            width=45,
            height=45,
            font=ctk.CTkFont(size=18),
            fg_color="#00A884",  # WhatsApp green
            hover_color="#008F72",
            corner_radius=23,
            command=lambda: self.send_media_with_caption(file_path)
        )
        send_btn.pack(side="right", padx=15, pady=12)
        
        # Store file path for sending
        self.pending_media_file = file_path
        
        # Focus caption input
        self.caption_input.focus()
    
    def close_media_preview(self):
        """Close media preview dialog"""
        if hasattr(self, 'preview_overlay'):
            self.preview_overlay.destroy()
            delattr(self, 'preview_overlay')
        if hasattr(self, 'pending_media_file'):
            delattr(self, 'pending_media_file')
    
    def send_media_with_caption(self, file_path):
        """Send media with caption"""
        caption = self.caption_input.get().strip() if hasattr(self, 'caption_input') else ""
        
        if self.current_contact and self.on_send_media:
            phone = self.current_contact.get('number', self.current_contact.get('phone', ''))
            # Send with caption
            self.on_send_media(phone, file_path, caption)
        
        # Close preview
        self.close_media_preview()
