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

# Global list that never gets cleared - keeps ALL images forever
_ALL_IMAGES = []

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
        
        # Initialize document storage
        self._document_bytes = None
        self._document_filename = None
        self._document_mimetype = None
        
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
        
        # Check if message is a document file
        document_info = self._extract_document_info()
        
        if image_data and PIL_AVAILABLE:
            # Extract caption from message_data fields (caption is separate from image base64)
            caption = self._extract_caption_from_message()
            
            # Create a container for image + caption
            image_container = ctk.CTkFrame(inner_content, fg_color="transparent")
            image_container.pack(padx=4, pady=(2, 0), anchor="w", fill="x")
            
            # Render image in the container
            self._render_image_file(image_container, image_data, text_color)
            
            # If there's caption, show it below image
            if caption:
                print(f"DEBUG: Displaying caption: '{caption}'")
                caption_label = ctk.CTkLabel(
                    image_container,
                    text=caption,
                    font=ctk.CTkFont(size=14),
                    text_color=text_color,
                    wraplength=400,
                    justify="left",
                    anchor="w"
                )
                caption_label.pack(padx=4, pady=(4, 0), anchor="w")
        elif document_info:
            # Render document file
            self._render_document_file(inner_content, document_info, text_color)
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
        """Extract caption text from message (text before image data)"""
        if not text or not isinstance(text, str):
            return None
        
        # Check if message starts with base64 image pattern
        image_patterns = ['/9j/', 'iVBORw0KGgo', 'R0lGOD', 'UklGR']
        text_stripped = text.strip()
        
        # Debug
        print(f"DEBUG: Extracting caption from: {text_stripped[:50]}...")
        
        # If text starts with image pattern, no caption before image
        for pattern in image_patterns:
            if text_stripped.startswith(pattern):
                print(f"DEBUG: Text starts with image pattern, no caption")
                return None
        
        # Check if text contains image pattern somewhere
        # If yes, extract text before the image
        for pattern in image_patterns:
            idx = text_stripped.find(pattern)
            if idx > 0:
                caption = text_stripped[:idx].strip()
                print(f"DEBUG: Found caption before image: '{caption}'")
                if caption:
                    return caption
        
        # Check for embedded base64 via regex (text before base64 block)
        import re
        base64_pattern = r'([A-Za-z0-9+/]{50,}={0,2})'
        match = re.search(base64_pattern, text_stripped)
        if match:
            caption = text_stripped[:match.start()].strip()
            print(f"DEBUG: Found caption via regex: '{caption}'")
            if caption:
                return caption
        
        print(f"DEBUG: No caption found")
        return None

    def _extract_caption_from_message(self):
        """Extract caption from message_data fields (separate from image data)"""
        # Check various fields where caption might be stored
        caption = None
        
        # Try direct caption field
        caption = self.message_data.get('caption')
        if caption:
            print(f"DEBUG: Found caption in 'caption' field: '{caption}'")
            return caption
        
        # Try _raw -> _data -> caption
        raw = self.message_data.get('_raw', {})
        if isinstance(raw, dict):
            data = raw.get('_data', {})
            caption = data.get('caption')
            if caption:
                print(f"DEBUG: Found caption in _raw._data.caption: '{caption}'")
                return caption
        
        # Check if there's a separate body/text that is not base64 image
        body = self.message_data.get('body') or self.message_data.get('text')
        if body and isinstance(body, str):
            # Check if body is NOT base64 image
            if not body.startswith('/9j/') and not body.startswith('iVBOR'):
                print(f"DEBUG: Found caption in body/text field: '{body}'")
                return body
        
        print(f"DEBUG: No caption found in message_data")
        return None

    def _extract_document_info(self):
        """Extract document file info from message data (PDF, XLS, DOC, etc.)"""
        # Check if message has media but is not an image
        has_media = self.message_data.get('hasMedia') or self.message_data.get('_hasMedia')
        mimetype = self.message_data.get('mimetype', '')
        filename = self.message_data.get('filename', '')
        
        # Also check in _raw data
        raw = self.message_data.get('_raw', {})
        if isinstance(raw, dict):
            data = raw.get('_data', {})
            if not has_media:
                has_media = data.get('hasMedia') or data.get('_hasMedia')
            if not mimetype:
                mimetype = data.get('mimetype', '')
            if not filename:
                filename = data.get('filename', '')
        
        if not has_media:
            return None
        
        # Check if it's a document type (not image or video)
        document_mimetypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain',
            'text/csv',
            'application/rtf',
            'application/vnd.oasis.opendocument.text',
            'application/vnd.oasis.opendocument.spreadsheet',
            'application/vnd.oasis.opendocument.presentation',
            'application/zip',
            'application/vnd.rar',
        ]
        
        is_document = any(mimetype.startswith(doc_type) for doc_type in document_mimetypes)
        
        if not is_document:
            return None
        
        # Get base64 data
        base64_data = self.message_data.get('base64', '')
        if not base64_data and isinstance(raw, dict):
            base64_data = data.get('base64', '')
        
        if not base64_data or base64_data == '-' or base64_data == 'disabled':
            return None
        
        # Decode base64
        try:
            import base64
            document_bytes = base64.b64decode(base64_data)
            
            # If no filename, generate from mimetype
            if not filename:
                ext = mimetype.split('/')[-1] if '/' in mimetype else 'bin'
                filename = f"document.{ext}"
            
            return {
                'filename': filename,
                'mimetype': mimetype,
                'bytes': document_bytes,
                'size': len(document_bytes)
            }
        except Exception as e:
            print(f"DEBUG: Failed to decode document base64: {e}")
            return None
    
    def _get_document_icon(self, mimetype):
        """Get icon emoji for document type"""
        if 'pdf' in mimetype:
            return "📄"
        elif 'word' in mimetype or 'document' in mimetype:
            return "📝"
        elif 'excel' in mimetype or 'spreadsheet' in mimetype or 'csv' in mimetype:
            return "📊"
        elif 'powerpoint' in mimetype or 'presentation' in mimetype:
            return "📽"
        elif 'text' in mimetype:
            return "📃"
        elif 'zip' in mimetype or 'rar' in mimetype or '7z' in mimetype:
            return "🗜"
        else:
            return "📎"
    
    def _format_file_size(self, size_bytes):
        """Format file size to human readable"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _render_document_file(self, parent, document_info, text_color):
        """Render document file with icon and download button"""
        try:
            # Store document info
            self._document_bytes = document_info['bytes']
            self._document_filename = document_info['filename']
            self._document_mimetype = document_info['mimetype']
            
            filename = document_info['filename']
            mimetype = document_info['mimetype']
            size = document_info['size']
            
            # Get icon for document type
            icon = self._get_document_icon(mimetype)
            
            # Create document container
            doc_container = ctk.CTkFrame(parent, fg_color="transparent")
            doc_container.pack(padx=4, pady=(2, 0), anchor="w", fill="x")
            
            # Document icon + name frame
            doc_frame = ctk.CTkFrame(doc_container, fg_color="#F0F0F0", corner_radius=8)
            doc_frame.pack(padx=4, pady=2, anchor="w")
            
            # Icon label
            icon_label = ctk.CTkLabel(
                doc_frame,
                text=icon,
                font=ctk.CTkFont(size=24)
            )
            icon_label.pack(side="left", padx=(8, 4), pady=8)
            
            # Info frame (filename + size)
            info_frame = ctk.CTkFrame(doc_frame, fg_color="transparent")
            info_frame.pack(side="left", padx=(4, 8), pady=8, fill="both", expand=True)
            
            # Filename label
            name_label = ctk.CTkLabel(
                info_frame,
                text=filename,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=text_color,
                wraplength=300,
                justify="left",
                anchor="w"
            )
            name_label.pack(anchor="w")
            
            # Size label
            size_label = ctk.CTkLabel(
                info_frame,
                text=self._format_file_size(size),
                font=ctk.CTkFont(size=11),
                text_color="#667781"
            )
            size_label.pack(anchor="w", pady=(2, 0))
            
            # Make the whole frame clickable
            doc_frame.configure(cursor="hand2")
            
            def on_document_click(event):
                if not self._downloading:
                    self._download_document()
            
            doc_frame.bind("<Button-1>", on_document_click)
            icon_label.bind("<Button-1>", on_document_click)
            name_label.bind("<Button-1>", on_document_click)
            size_label.bind("<Button-1>", on_document_click)
            
            # Add download hint
            hint = ctk.CTkLabel(
                doc_container,
                text="👆 Click to download",
                font=ctk.CTkFont(size=10),
                text_color="#667781"
            )
            hint.pack(padx=4, pady=(0, 2), anchor="w")
            
            print(f"DEBUG: Document rendered: {filename} ({self._format_file_size(size)})")
            
        except Exception as e:
            print(f"DEBUG: Failed to render document: {e}")
            import traceback
            traceback.print_exc()
            # Fallback
            fallback = ctk.CTkLabel(
                parent,
                text="📎 Document attached (click to download)",
                font=ctk.CTkFont(size=14),
                text_color="#667781"
            )
            fallback.pack(padx=4, pady=(2, 0), anchor="w")
            fallback.configure(cursor="hand2")
            
            def on_fallback_click(event):
                if not self._downloading:
                    self._download_document()
            
            fallback.bind("<Button-1>", on_fallback_click)
    
    def _download_document(self):
        """Download document file when user clicks"""
        try:
            if not self._document_bytes:
                print("DEBUG: No document bytes to download")
                return
            
            from tkinter import filedialog
            import os
            
            # Get original extension from filename
            original_ext = os.path.splitext(self._document_filename)[1]
            
            # Ask user where to save
            filetypes = [("All files", "*.*")]
            
            # Add specific filetype based on mimetype
            if 'pdf' in self._document_mimetype:
                filetypes.insert(0, ("PDF files", "*.pdf"))
            elif 'word' in self._document_mimetype or 'document' in self._document_mimetype:
                filetypes.insert(0, ("Word files", "*.docx *.doc"))
            elif 'excel' in self._document_mimetype or 'spreadsheet' in self._document_mimetype:
                filetypes.insert(0, ("Excel files", "*.xlsx *.xls"))
            elif 'powerpoint' in self._document_mimetype or 'presentation' in self._document_mimetype:
                filetypes.insert(0, ("PowerPoint files", "*.pptx *.ppt"))
            elif 'text' in self._document_mimetype:
                filetypes.insert(0, ("Text files", "*.txt"))
            elif 'csv' in self._document_mimetype:
                filetypes.insert(0, ("CSV files", "*.csv"))
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=original_ext,
                filetypes=filetypes,
                title="Save Document",
                initialfile=self._document_filename
            )
            
            if file_path:
                # Save document
                with open(file_path, 'wb') as f:
                    f.write(self._document_bytes)
                print(f"DEBUG: Document saved by user to: {file_path}")
                
        except Exception as e:
            print(f"DEBUG: Failed to save document: {e}")
            import traceback
            traceback.print_exc()

    def _render_image_file(self, parent, image_bytes, text_color):
        """Render actual image and allow user to download on click"""
        try:
            import os
            import tempfile
            from PIL import Image
            import tkinter as tk
            
            # Store bytes immediately
            self._image_bytes = image_bytes
            
            # Load image from bytes
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Calculate display dimensions - larger like WhatsApp
            max_width = 480
            max_height = 480
            min_width = 200  # Minimum width for small images
            min_height = 100  # Minimum height for small images
            orig_width, orig_height = pil_image.size
            
            # Store original dimensions
            self._image_width = orig_width
            self._image_height = orig_height
            
            # Start with original size
            width, height = orig_width, orig_height
            
            # Scale up small images to minimum size
            if width < min_width:
                ratio = min_width / width
                width = min_width
                height = int(height * ratio)
            if height < min_height:
                ratio = min_height / height
                height = min_height
                width = int(width * ratio)
            
            # Then apply max limits
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
            
            # Save to temp file - PhotoImage from file is more stable
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"wacsa_img_{id(self)}.png")
            display_image.save(temp_path, "PNG")
            
            # Get the root window for PhotoImage master
            try:
                root = parent.winfo_toplevel()
            except:
                root = None
            
            # Create PhotoImage from file with explicit master
            if root:
                self._photo = tk.PhotoImage(master=root, file=temp_path)
            else:
                self._photo = tk.PhotoImage(file=temp_path)
            
            # CRITICAL: Add to global list that NEVER gets cleared
            global _ALL_IMAGES
            _ALL_IMAGES.append(self._photo)
            
            print(f"DEBUG: PhotoImage created, total global images: {len(_ALL_IMAGES)}")
            
            # Create frame to hold image
            bg_color = "#D6E9FF" if self.is_sent else "#FFFFFF"
            img_frame = tk.Frame(parent, bg=bg_color, bd=0, highlightthickness=0)
            img_frame.pack(padx=4, pady=(2, 0), anchor="w")
            
            # Create tkinter Label with image - no image param in constructor
            img_label = tk.Label(
                img_frame,
                bg=bg_color,
                bd=0,
                highlightthickness=0
            )
            # Set image AFTER creation
            img_label.config(image=self._photo)
            img_label.pack()
            
            # Store reference
            img_label._photo = self._photo
            self._img_label = img_label
            
            print(f"DEBUG: Image rendered successfully: {orig_width}x{orig_height} -> {width}x{height}")
            
            # Add click handler to show preview
            def on_image_click(event):
                if not self._downloading:
                    self._show_image_preview()
            
            # Bind click to label only (no container reference needed)
            img_label.bind("<Button-1>", on_image_click)
            img_label.configure(cursor="hand2")
            
            # Add preview hint
            hint = ctk.CTkLabel(
                parent,
                text="� Click to preview",
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

    def _show_image_preview(self):
        """Show image preview window with zoom controls"""
        try:
            if not hasattr(self, '_image_bytes') or not self._image_bytes:
                print("DEBUG: No image bytes to preview")
                return
            
            from PIL import Image
            import io
            import tkinter as tk
            
            # Create preview window
            preview_window = ctk.CTkToplevel(self)
            preview_window.title("Image Preview")
            preview_window.geometry("800x600")
            preview_window.minsize(400, 300)
            
            # Make window modal and stay on top
            preview_window.transient(self.winfo_toplevel())
            preview_window.grab_set()
            preview_window.lift()
            preview_window.focus_force()
            
            # Load image
            pil_image = Image.open(io.BytesIO(self._image_bytes))
            orig_width, orig_height = pil_image.size
            
            # Store current scale
            self._preview_scale = 1.0
            self._preview_image = pil_image
            self._preview_photos = []  # Store all PhotoImages to prevent GC
            
            # Main container
            main_frame = ctk.CTkFrame(preview_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Image info label
            info_label = ctk.CTkLabel(
                main_frame,
                text=f"Original size: {orig_width}x{orig_height}px | Current: 100%",
                font=ctk.CTkFont(size=12)
            )
            info_label.pack(pady=(0, 10))
            
            # Canvas for image display with scrollbars
            canvas_frame = ctk.CTkFrame(main_frame)
            canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            canvas = tk.Canvas(canvas_frame, bg="#2B2B2B", highlightthickness=0)
            h_scroll = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
            v_scroll = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            
            canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
            
            v_scroll.pack(side="right", fill="y")
            h_scroll.pack(side="bottom", fill="x")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Function to update image display
            def update_display():
                # Calculate new size
                new_width = int(orig_width * self._preview_scale)
                new_height = int(orig_height * self._preview_scale)
                
                # Resize image
                resized = self._preview_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save to temp file and use PhotoImage from file (more stable)
                import tempfile
                import os
                temp_path = os.path.join(tempfile.gettempdir(), f"wacsa_preview_{id(self)}_{self._preview_scale}.png")
                resized.save(temp_path, "PNG")
                
                # Create PhotoImage from file with explicit master
                preview_photo = tk.PhotoImage(master=preview_window, file=temp_path)
                
                # Store reference in multiple places to prevent GC
                self._preview_photos.append(preview_photo)
                canvas._current_image = preview_photo
                preview_window._current_image = preview_photo
                
                # Clear canvas and display new image
                canvas.delete("all")
                canvas.create_image(0, 0, anchor="nw", image=preview_photo)
                canvas.config(scrollregion=(0, 0, new_width, new_height))
                
                # Update info label
                info_label.configure(
                    text=f"Original size: {orig_width}x{orig_height}px | Current: {int(self._preview_scale * 100)}% ({new_width}x{new_height})"
                )
            
            # Initial display
            update_display()
            
            # Zoom controls frame
            controls_frame = ctk.CTkFrame(main_frame)
            controls_frame.pack(fill="x", pady=(10, 0))
            
            # Zoom out button
            def zoom_out():
                if self._preview_scale > 0.25:
                    self._preview_scale *= 0.8
                    update_display()
            
            zoom_out_btn = ctk.CTkButton(
                controls_frame,
                text="🔍- Zoom Out",
                command=zoom_out,
                width=100
            )
            zoom_out_btn.pack(side="left", padx=5)
            
            # Zoom in button
            def zoom_in():
                if self._preview_scale < 5.0:
                    self._preview_scale *= 1.25
                    update_display()
            
            zoom_in_btn = ctk.CTkButton(
                controls_frame,
                text="🔍+ Zoom In",
                command=zoom_in,
                width=100
            )
            zoom_in_btn.pack(side="left", padx=5)
            
            # Reset zoom button
            def reset_zoom():
                self._preview_scale = 1.0
                update_display()
            
            reset_btn = ctk.CTkButton(
                controls_frame,
                text="↺ Reset",
                command=reset_zoom,
                width=80
            )
            reset_btn.pack(side="left", padx=5)
            
            # Spacer
            ctk.CTkFrame(controls_frame, fg_color="transparent").pack(side="left", expand=True)
            
            # Download button
            def download_from_preview():
                self._downloading = True
                self._download_image()
                self._downloading = False
            
            download_btn = ctk.CTkButton(
                controls_frame,
                text="💾 Download",
                command=download_from_preview,
                width=100,
                fg_color="#007AFF",
                hover_color="#0051D5"
            )
            download_btn.pack(side="right", padx=5)
            
            # Close button
            close_btn = ctk.CTkButton(
                controls_frame,
                text="✕ Close",
                command=preview_window.destroy,
                width=80,
                fg_color="#666666",
                hover_color="#555555"
            )
            close_btn.pack(side="right", padx=5)
            
            # Keyboard shortcuts
            def on_key(event):
                if event.keysym == "plus" or event.keysym == "equal":
                    zoom_in()
                elif event.keysym == "minus":
                    zoom_out()
                elif event.keysym == "Escape":
                    preview_window.destroy()
            
            preview_window.bind("<Key>", on_key)
            preview_window.focus_set()
            
            print(f"DEBUG: Image preview window opened for {orig_width}x{orig_height}px image")
            
        except Exception as e:
            print(f"DEBUG: Failed to show image preview: {e}")
            import traceback
            traceback.print_exc()

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
