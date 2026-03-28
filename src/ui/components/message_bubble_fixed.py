"""
Message Bubble Component
WhatsApp-like message bubbles for sent and received messages
"""

import customtkinter as ctk
from datetime import datetime
import base64
import io
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Global image storage - module level to persist across all instances
_IMAGE_STORAGE = {
    'counter': 0,
    'photos': [],  # List to store PhotoImage references
}

def _store_photo(photo):
    """Store PhotoImage in global cache to prevent garbage collection"""
    _IMAGE_STORAGE['photos'].append(photo)
    _IMAGE_STORAGE['counter'] += 1
    return _IMAGE_STORAGE['counter'] - 1


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
        
        # Initialize image storage
        self._image_bytes = None
        self._ctk_image = None
        self._img_label = None
        self._downloading = False
        
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
        
        # Store container reference for image rendering
        self._bubble_container = container
        
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

        # Check if message contains base64 image data
        image_data = self._extract_image_data(message_text)
        
        if image_data and PIL_AVAILABLE:
            # Render image immediately with proper references
            self._render_image_file(inner_content, image_data, text_color)
            # If there's remaining text after removing image data, show it as caption
            caption = self._extract_caption(message_text)
            if caption:
                caption_label = ctk.CTkLabel(
                    inner_content,
                    text=caption,
                    font=ctk.CTkFont(size=14),
                    text_color=text_color,
                    wraplength=400,
                    justify="left",
                    anchor="w"
                )
                caption_label.pack(padx=4, pady=(4, 0), anchor="w")
        else:
            # Render as text
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

    def _extract_image_data(self, text):
        """Extract base64 image data from message text"""
        if not text or not isinstance(text, str):
            return None
        
        text_stripped = text.strip()
        
        # Debug: print first 100 chars to see what we're dealing with
        print(f"DEBUG: Checking message, first 100 chars: {text_stripped[:100]}")
        
        # Check for base64 image patterns (JPEG, PNG, GIF, WebP)
        image_patterns = [
            ('/9j/', 'JPEG'),  # JPEG
            ('iVBORw0KGgo', 'PNG'),  # PNG
            ('R0lGOD', 'GIF'),  # GIF
            ('UklGR', 'WebP'),  # WebP
        ]
        
        for pattern, img_type in image_patterns:
            if text_stripped.startswith(pattern):
                print(f"DEBUG: Found {img_type} pattern")
                # Found base64 image data
                try:
                    # Decode base64 - add padding if needed
                    padded_text = text_stripped
                    # Add padding if necessary
                    padding_needed = 4 - len(padded_text) % 4
                    if padding_needed != 4:
                        padded_text += '=' * padding_needed
                    
                    image_bytes = base64.b64decode(padded_text)
                    print(f"DEBUG: Successfully decoded {len(image_bytes)} bytes")
                    return image_bytes
                except Exception as e:
                    print(f"DEBUG: Failed to decode base64: {e}")
                    return None
        
        # Check if text might contain base64 data within it (not at start)
        # This handles cases where there might be some prefix
        import re
        # Look for base64 patterns anywhere in the text
        base64_pattern = r'([A-Za-z0-9+/]{100,}={0,2})'
        matches = re.findall(base64_pattern, text_stripped)
        if matches:
            for match in matches:
                # Check if this match starts with image signatures
                for pattern, img_type in image_patterns:
                    if match.startswith(pattern):
                        print(f"DEBUG: Found embedded {img_type} pattern")
                        try:
                            padding_needed = 4 - len(match) % 4
                            if padding_needed != 4:
                                match += '=' * padding_needed
                            image_bytes = base64.b64decode(match)
                            print(f"DEBUG: Successfully decoded embedded image: {len(image_bytes)} bytes")
                            return image_bytes
                        except Exception as e:
                            print(f"DEBUG: Failed to decode embedded base64: {e}")
                            continue
        
        return None
    
    def _extract_caption(self, text):
        """Extract caption text from message (if any after image data)"""
        # For now, return None - caption extraction can be enhanced later
        # if the server separates caption from image data
        return None

    def _render_image_file(self, parent, image_bytes, text_color):
        """Render actual image and allow user to download on click"""
        try:
            import os
            from PIL import Image
            import tkinter as tk
            
            # Store bytes immediately
            self._image_bytes = image_bytes
            
            # Load image from bytes
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Calculate display dimensions
            max_width = 300
            max_height = 300
            orig_width, orig_height = pil_image.size
            
            # Store original dimensions
            self._image_width = orig_width
            self._image_height = orig_height
            
            width, height = orig_width, orig_height
            if width > max_width:
                ratio = max_width / width
                width = max_width
                height = int(height * ratio)
            if height > max_height:
                ratio = max_height / height
                height = max_height
                width = int(width * ratio)
            
            # Resize for display
            display_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Create CTkImage (CustomTkinter's native image type)
            ctk_image = ctk.CTkImage(
                light_image=display_image,
                dark_image=display_image,
                size=(width, height)
            )
            
            # IMPORTANT: Store strong reference to prevent garbage collection
            self._ctk_image = ctk_image  # Instance variable
            photo_id = _store_photo(ctk_image)  # Global storage
            print(f"DEBUG: CTkImage created and stored with ID {photo_id}")
            
            # Create CTkLabel with the image
            img_label = ctk.CTkLabel(
                parent,
                image=ctk_image,
                text="",
                fg_color="transparent",
                width=width,
                height=height
            )
            img_label.pack(padx=4, pady=(2, 0), anchor="w")
            
            # Keep strong reference in both places
            img_label._ctk_image = ctk_image
            self._img_label = img_label
            
            print(f"DEBUG: CTkLabel with image created and packed")
            
            # Add click handler to download image
            def on_image_click(event):
                if not self._downloading:
                    self._downloading = True
                    self._download_image()
                    # Reset flag after delay
                    self.after(500, lambda: setattr(self, '_downloading', False))
            
            # Bind click to label only (no container reference needed)
            img_label.bind("<Button-1>", on_image_click)
            img_label.configure(cursor="hand2")
            
            # Add download hint
            hint = ctk.CTkLabel(
                parent,
                text="📥 Click to download",
                font=ctk.CTkFont(size=10),
                text_color="#667781"
            )
            hint.pack(padx=4, pady=(0, 2), anchor="w")
            hint.bind("<Button-1>", on_image_click)
            hint.configure(cursor="hand2")
            
            print(f"DEBUG: Image rendered successfully: {orig_width}x{orig_height} -> {width}x{height}")
            
        except Exception as e:
            print(f"DEBUG: Failed to render image: {e}")
            import traceback
            traceback.print_exc()
            # Fallback
            fallback = ctk.CTkLabel(
                parent,
                text="📷 Image attached (click to download)",
                font=ctk.CTkFont(size=14),
                text_color="#667781"
            )
            fallback.pack(padx=4, pady=(2, 0), anchor="w")
            
            # Store bytes for download
            self._image_bytes = image_bytes
            
            def on_fallback_click(event):
                if not self._downloading:
                    self._downloading = True
                    self._download_image()
                    self.after(500, lambda: setattr(self, '_downloading', False))
            
            fallback.bind("<Button-1>", on_fallback_click)
            fallback.configure(cursor="hand2")

    def _download_image(self):
        """Download image when user clicks"""
        try:
            if not hasattr(self, '_image_bytes') or not self._image_bytes:
                print("DEBUG: No image bytes to download")
                return
            
            from tkinter import filedialog
            from PIL import Image
            import io
            
            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")],
                title="Save Image"
            )
            
            if file_path:
                # Save image
                pil_image = Image.open(io.BytesIO(self._image_bytes))
                pil_image.save(file_path, quality=95)
                print(f"DEBUG: Image saved by user to: {file_path}")
        except Exception as e:
            print(f"DEBUG: Failed to save image: {e}")

    def get_status_icon(self, ack):
        """Get status icon based on ack value"""
        if ack == 0: return "⏱"  # Pending
        if ack == 1: return "✓"   # Sent
        if ack == 2: return "✓✓"  # Delivered
        if ack >= 3: return "✓✓"  # Read (blue in original, but we use same for simplicity)
        return "?"

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
