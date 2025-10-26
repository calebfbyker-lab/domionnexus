"""
HMAC Keyring for Codex v98 Orthos
Secure key rotation and management for HMAC signatures
"""
import os
import json
import hmac
import hashlib
import time
from pathlib import Path

KEYRING_FILE = "config/keyring.json"
ROTATION_INTERVAL = 86400 * 30  # 30 days in seconds


class HMACKeyring:
    """Manages HMAC keys with rotation support"""
    
    def __init__(self, keyring_path=KEYRING_FILE):
        self.keyring_path = keyring_path
        self.keys = {}
        self.current_key_id = None
        self._load_keyring()
    
    def _load_keyring(self):
        """Load keyring from disk"""
        if not os.path.exists(self.keyring_path):
            # Initialize with default key from environment
            default_key = os.getenv('CODEX_HMAC_KEY', 'dev-hmac')
            self._initialize_keyring(default_key)
            return
        
        try:
            with open(self.keyring_path, 'r') as f:
                data = json.load(f)
            self.keys = data.get('keys', {})
            self.current_key_id = data.get('current_key_id')
        except (json.JSONDecodeError, FileNotFoundError):
            default_key = os.getenv('CODEX_HMAC_KEY', 'dev-hmac')
            self._initialize_keyring(default_key)
    
    def _initialize_keyring(self, initial_key):
        """Initialize keyring with first key"""
        key_id = f"key-{int(time.time())}"
        self.keys = {
            key_id: {
                "value": initial_key,
                "created_at": int(time.time()),
                "status": "active"
            }
        }
        self.current_key_id = key_id
        self._save_keyring()
    
    def _save_keyring(self):
        """Save keyring to disk"""
        os.makedirs(os.path.dirname(self.keyring_path), exist_ok=True)
        data = {
            "keys": self.keys,
            "current_key_id": self.current_key_id,
            "updated_at": int(time.time())
        }
        with open(self.keyring_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_current_key(self):
        """Get the current active key"""
        if not self.current_key_id or self.current_key_id not in self.keys:
            return None
        return self.keys[self.current_key_id]["value"]
    
    def sign(self, message):
        """Sign a message with current key"""
        key = self.get_current_key()
        if not key:
            raise ValueError("No active key available")
        
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        return hmac.new(key.encode('utf-8'), message, hashlib.sha256).hexdigest()
    
    def verify(self, message, signature, key_id=None):
        """
        Verify a signature against message
        
        Args:
            message: The message to verify
            signature: The signature to check
            key_id: Optional specific key to use. If None, tries current then all keys.
        
        Returns:
            bool: True if signature is valid
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Try specific key if provided
        if key_id:
            if key_id not in self.keys:
                return False
            key = self.keys[key_id]["value"]
            expected = hmac.new(key.encode('utf-8'), message, hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected, signature)
        
        # Try current key first
        current_key = self.get_current_key()
        if current_key:
            expected = hmac.new(current_key.encode('utf-8'), message, hashlib.sha256).hexdigest()
            if hmac.compare_digest(expected, signature):
                return True
        
        # Try all other keys (for graceful rotation)
        for kid, key_data in self.keys.items():
            if kid == self.current_key_id:
                continue
            key = key_data["value"]
            expected = hmac.new(key.encode('utf-8'), message, hashlib.sha256).hexdigest()
            if hmac.compare_digest(expected, signature):
                return True
        
        return False
    
    def rotate_key(self, new_key=None):
        """
        Rotate to a new key
        
        Args:
            new_key: New key value. If None, generates a random key.
        
        Returns:
            str: New key ID
        """
        if new_key is None:
            # Generate random 32-byte key
            new_key = hashlib.sha256(os.urandom(32)).hexdigest()
        
        # Mark current key as rotated
        if self.current_key_id and self.current_key_id in self.keys:
            self.keys[self.current_key_id]["status"] = "rotated"
            self.keys[self.current_key_id]["rotated_at"] = int(time.time())
        
        # Add new key
        new_key_id = f"key-{int(time.time())}"
        self.keys[new_key_id] = {
            "value": new_key,
            "created_at": int(time.time()),
            "status": "active"
        }
        self.current_key_id = new_key_id
        
        self._save_keyring()
        return new_key_id
    
    def should_rotate(self):
        """Check if key should be rotated based on age"""
        if not self.current_key_id or self.current_key_id not in self.keys:
            return True
        
        created_at = self.keys[self.current_key_id].get("created_at", 0)
        age = int(time.time()) - created_at
        return age > ROTATION_INTERVAL
    
    def list_keys(self):
        """List all keys with metadata"""
        return {
            "current_key_id": self.current_key_id,
            "keys": [
                {
                    "key_id": kid,
                    "created_at": kdata.get("created_at"),
                    "status": kdata.get("status"),
                    "rotated_at": kdata.get("rotated_at")
                }
                for kid, kdata in self.keys.items()
            ]
        }


# Global keyring instance
_keyring = None

def get_keyring():
    """Get or create global keyring instance"""
    global _keyring
    if _keyring is None:
        _keyring = HMACKeyring()
    return _keyring
