r"""
Backup Log Reader
Reads deleted log files from C:\wacsa\backup directory
"""

import os
import json
import glob
from typing import List, Dict, Any
from loguru import logger


class BackupLogReader:
    """Read backup log files from local directory"""
    
    def __init__(self, backup_path: str = r"C:\wacsa\backup"):
        self.backup_path = backup_path
        
    def _read_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Read and parse a single JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                if not content:
                    return []
                
                # Handle case where file contains array of objects
                if content.startswith('['):
                    return json.loads(content)
                else:
                    # Handle case where file contains comma-separated objects
                    # Remove trailing comma and wrap in array brackets
                    if content.endswith(','):
                        content = content[:-1]
                    content = '[' + content + ']'
                    return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []
    
    def get_received_messages(self) -> Dict[str, Any]:
        """Get all received messages from backup files"""
        try:
            pattern = os.path.join(self.backup_path, "deleted_wacsa-received-*.json")
            files = glob.glob(pattern)
            
            if not files:
                logger.info("No backup received message files found")
                return {"status": True, "response": [], "message": "No backup files found"}
            
            # Sort files by timestamp (newest first)
            files.sort(reverse=True)
            
            all_messages = []
            for file_path in files:
                messages = self._read_json_file(file_path)
                all_messages.extend(messages)
            
            logger.info(f"Loaded {len(all_messages)} messages from {len(files)} backup files")
            return {"status": True, "response": all_messages}
            
        except Exception as e:
            logger.error(f"Error reading backup received messages: {e}")
            return {"status": False, "response": [], "message": str(e)}
    
    def get_sent_messages(self) -> Dict[str, Any]:
        """Get all sent messages from backup files"""
        try:
            pattern = os.path.join(self.backup_path, "deleted_wacsa-sent-*.json")
            files = glob.glob(pattern)
            
            if not files:
                logger.info("No backup sent message files found")
                return {"status": True, "response": [], "message": "No backup files found"}
            
            # Sort files by timestamp (newest first)
            files.sort(reverse=True)
            
            all_messages = []
            for file_path in files:
                messages = self._read_json_file(file_path)
                all_messages.extend(messages)
            
            logger.info(f"Loaded {len(all_messages)} messages from {len(files)} backup files")
            return {"status": True, "response": all_messages}
            
        except Exception as e:
            logger.error(f"Error reading backup sent messages: {e}")
            return {"status": False, "response": [], "message": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get all statistics from backup files"""
        try:
            pattern = os.path.join(self.backup_path, "deleted_wacsa-stats-*.json")
            files = glob.glob(pattern)
            
            if not files:
                logger.info("No backup statistics files found")
                return {"status": True, "response": [], "message": "No backup files found"}
            
            # Sort files by timestamp (newest first)
            files.sort(reverse=True)
            
            all_stats = []
            for file_path in files:
                stats = self._read_json_file(file_path)
                all_stats.extend(stats)
            
            logger.info(f"Loaded {len(all_stats)} stats from {len(files)} backup files")
            return {"status": True, "response": all_stats}
            
        except Exception as e:
            logger.error(f"Error reading backup statistics: {e}")
            return {"status": False, "response": [], "message": str(e)}
    
    def get_file_list(self) -> Dict[str, List[str]]:
        """Get list of all backup files"""
        try:
            received_files = glob.glob(os.path.join(self.backup_path, "deleted_wacsa-received-*.json"))
            sent_files = glob.glob(os.path.join(self.backup_path, "deleted_wacsa-sent-*.json"))
            stats_files = glob.glob(os.path.join(self.backup_path, "deleted_wacsa-stats-*.json"))
            
            return {
                "received": [os.path.basename(f) for f in sorted(received_files, reverse=True)],
                "sent": [os.path.basename(f) for f in sorted(sent_files, reverse=True)],
                "stats": [os.path.basename(f) for f in sorted(stats_files, reverse=True)]
            }
        except Exception as e:
            logger.error(f"Error getting file list: {e}")
            return {"received": [], "sent": [], "stats": []}
