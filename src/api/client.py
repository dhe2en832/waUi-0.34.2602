"""
WACSA-MD2 API Client
Handles communication with WACSA-MD2 WhatsApp server and log endpoints
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger

@dataclass
class APIConfig:
    """API Configuration"""
    base_url: str
    timeout: int = 30
    verify_ssl: bool = True

class WACSAAPIClient:
    """WACSA-MD2 WhatsApp API Client"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout
        self.auth_token = None
        
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login to WACSA-MD2 and get token"""
        url = f"{self.config.base_url.rstrip('/')}/auth/login"
        data = {"email": email, "password": password}
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get('status'):
                # Extract token from login response
                # Note: WACSA might return token differently, adjust accordingly
                return result
            else:
                raise Exception(result.get('message', 'Login failed'))
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Login failed: {e}")
            raise
            
    def set_token(self, token: str):
        """Set authentication token"""
        self.auth_token = token
        self.session.headers.update({'x-access-token': token})
        
    def _make_request(self, method, endpoint, data=None, params=None, json=None, files=None):
        """Make HTTP request to WACSA-MD2 API"""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add token if available
        if self.auth_token:
            headers['x-access-token'] = self.auth_token
            
        try:
            response = self.session.request(method, url, headers=headers, data=data, json=json, params=params)
            
            # Handle authentication errors
            if response.status_code == 403:
                logger.error("Authentication failed: Token tidak tercantum")
                raise Exception("Authentication failed: Please login first")
            elif response.status_code == 401:
                logger.error("Authentication failed: Token salah")
                raise Exception("Authentication failed: Invalid token")
            elif response.status_code == 404:
                # 404 for log endpoints means log file is empty, not endpoint missing
                if 'log/' in endpoint:
                    logger.info(f"Log file empty for endpoint: {endpoint}")
                    return {"status": False, "response": [], "message": "Log file is empty"}
                else:
                    logger.error(f"Endpoint not found: {endpoint}")
                    raise Exception(f"Endpoint not found: {endpoint}")
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
            
    def health_check(self) -> Dict[str, Any]:
        """Check server health - use statistic endpoint as health check"""
        try:
            return self.get_statistics()
        except:
            # If statistic fails, try received message
            try:
                return self.get_received_messages()
            except:
                return {"status": "offline", "message": "Server not accessible"}
        
    def get_whatsapp_status(self) -> Dict[str, Any]:
        """Get WhatsApp connection status - use statistic as status check"""
        try:
            stats = self.get_statistics()
            return {"status": "connected", "data": stats}
        except Exception as e:
            return {"status": "disconnected", "error": str(e)}
        
    def send_text_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp text message using /message/send-text"""
        data = {
            "number": phone,  # Server expects 'number' not 'phone'
            "message": message
        }
        return self._make_request("POST", "message/send-text", json=data)
        
    # WACSA Log Endpoints (Based on actual WACSA-MD2 implementation)
    def get_received_messages(self) -> Dict[str, Any]:
        """
        Get received messages from WACSA log
        NOTE: This uses "Read-and-Clear" pattern - logs will be deleted after reading
        Endpoint: GET /log/received-message
        """
        return self._make_request("GET", "log/received-message")
        
    def get_sent_messages(self) -> Dict[str, Any]:
        """
        Get sent messages from WACSA log
        NOTE: This uses "Read-and-Clear" pattern - logs will be deleted after reading
        Endpoint: GET /log/sent-message
        """
        return self._make_request("GET", "log/sent-message")
        
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get WhatsApp statistics from WACSA log
        NOTE: This uses "Read-and-Clear" pattern - logs will be deleted after reading
        Endpoint: GET /log/statistic
        """
        return self._make_request("GET", "log/statistic")
    
    # Backup Log Endpoints - Read from server backup folder
    def get_backup_received_messages(self) -> Dict[str, Any]:
        """
        Get received messages from server backup files
        Endpoint: GET /log/backup/received-message
        """
        return self._make_request("GET", "log/backup/received-message")
    
    def get_backup_sent_messages(self) -> Dict[str, Any]:
        """
        Get sent messages from server backup files
        Endpoint: GET /log/backup/sent-message
        """
        return self._make_request("GET", "log/backup/sent-message")
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """
        Get statistics from server backup files
        Endpoint: GET /log/backup/statistic
        """
        return self._make_request("GET", "log/backup/statistic")
        
    def send_media_message(self, phone: str, media_file: str, caption: str = "") -> Dict[str, Any]:
        """Send WhatsApp media message using /message/send-media with file upload"""
        url = f"{self.config.base_url.rstrip('/')}/message/send-media"
        
        # Prepare form data
        data = {"number": phone, "message": caption}
        
        # Prepare file
        with open(media_file, 'rb') as f:
            files = {'file': (os.path.basename(media_file), f, self._get_mime_type(media_file))}
            headers = {'x-access-token': self.auth_token} if self.auth_token else {}
            
            try:
                response = self.session.post(url, data=data, files=files, headers=headers)
                
                if response.status_code == 403:
                    raise Exception("Authentication failed: Please login first")
                elif response.status_code == 401:
                    raise Exception("Authentication failed: Invalid token")
                    
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Media send failed: {e}")
                raise
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            # Images
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
            '.svg': 'image/svg+xml',
            # Videos
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.webm': 'video/webm',
            '.flv': 'video/x-flv',
            # Documents
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.rtf': 'application/rtf',
            '.odt': 'application/vnd.oasis.opendocument.text',
            '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
            '.odp': 'application/vnd.oasis.opendocument.presentation',
            # Archives
            '.zip': 'application/zip',
            '.rar': 'application/vnd.rar',
            '.7z': 'application/x-7z-compressed',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            # Audio
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac',
            '.m4a': 'audio/mp4',
        }
        return mime_types.get(ext, 'application/octet-stream')
        
    def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message (legacy - uses send_text_message)"""
        return self.send_text_message(phone, message)
        
    def send_bulk_messages(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send bulk WhatsApp messages"""
        data = {"messages": messages}
        return self._make_request("POST", "whatsapp/send-bulk", json=data)
        
    def upload_media(self, file_path: str, media_type: str = "image") -> Dict[str, Any]:
        """Upload media file"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'type': media_type}
            return self._make_request("POST", "whatsapp/upload", files=files, data=data)
        
        
    def get_chats(self, limit: int = 50) -> Dict[str, Any]:
        """Get WhatsApp chats"""
        params = {"limit": limit}
        return self._make_request("GET", "whatsapp/chats", params=params)
        
    def get_chat_messages(self, chat_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get messages from specific chat"""
        params = {"limit": limit}
        return self._make_request("GET", f"whatsapp/chats/{chat_id}/messages", params=params)
        
    def get_webhook_url(self) -> Dict[str, Any]:
        """Get current webhook URL"""
        return self._make_request("GET", "whatsapp/webhook")
        
    def set_webhook_url(self, webhook_url: str) -> Dict[str, Any]:
        """Set webhook URL for receiving messages"""
        data = {"url": webhook_url}
        return self._make_request("POST", "whatsapp/webhook", json=data)
        
    def export_messages(self, format: str = "csv", date_from: Optional[str] = None, date_to: Optional[str] = None) -> bytes:
        """Export message history"""
        params = {"format": format}
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        
        url = f"{self.config.base_url.rstrip('/')}/whatsapp/export"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content
