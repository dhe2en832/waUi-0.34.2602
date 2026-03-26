"""
Configuration Management
Handle app settings and credentials
"""

import json
import os
from pathlib import Path


class Config:
    """Application configuration manager"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        self.credentials_file = self.config_dir / "credentials.json"
        self.settings_file = self.config_dir / "settings.json"
    
    def save_credentials(self, server_url, email, password, remember=True):
        """Save user credentials"""
        credentials = {
            "server_url": server_url,
            "email": email,
            "password": password,  # TODO: Encrypt in production
            "remember": remember
        }
        
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f, indent=2)
    
    def load_credentials(self):
        """Load saved credentials"""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def clear_credentials(self):
        """Clear saved credentials"""
        if self.credentials_file.exists():
            os.remove(self.credentials_file)
    
    def save_settings(self, settings):
        """Save app settings"""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def load_settings(self):
        """Load app settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
