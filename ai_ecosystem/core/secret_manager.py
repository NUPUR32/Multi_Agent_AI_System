"""
Secret Manager - Enterprise Security
=====================================
Encrypted secrets storage, rotation, and access control
"""

import base64
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


@dataclass
class SecretEntry:
    """Stored secret with metadata"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    key: str = ""
    value: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    version: int = 1
    access_count: int = 0
    last_accessed: Optional[str] = None
    rotation_required: bool = False


class SecretManager:
    """
    Enterprise secret manager with encryption, rotation, and audit
    """
    
    def __init__(self, master_key: Optional[str] = None):
        self._secrets: Dict[str, SecretEntry] = {}
        self._cipher = self._init_cipher(master_key)
        self._audit_log: List[Dict[str, Any]] = []
        self._lock = False
        logger.info("SecretManager initialized")
    
    def _init_cipher(self, master_key: Optional[str] = None) -> Fernet:
        """Initialize encryption cipher"""
        if master_key:
            key = base64.urlsafe_b64encode(
                hashlib.sha256(master_key.encode()).digest()
            )
        else:
            # Use environment variable or generate key
            env_key = os.getenv("NUPUR32_MASTER_KEY")
            if env_key:
                key = base64.urlsafe_b64encode(
                    hashlib.sha256(env_key.encode()).digest()
                )
            else:
                key = Fernet.generate_key()
                logger.warning("No master key set - using generated key")
        
        return Fernet(key)
    
    def set(self, key: str, value: str, description: str = "",
            tags: Optional[List[str]] = None,
            expires_in_days: Optional[int] = None,
            rotation_required: bool = False) -> str:
        """Store an encrypted secret"""
        encrypted = self._cipher.encrypt(value.encode()).decode()
        
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()
        
        entry = SecretEntry(
            key=key,
            value=encrypted,
            description=description,
            tags=tags or [],
            expires_at=expires_at,
            rotation_required=rotation_required,
        )
        
        self._secrets[key] = entry
        self._audit("SET", key)
        logger.info(f"Secret stored: {key}")
        return entry.id
    
    def get(self, key: str) -> Optional[str]:
        """Retrieve and decrypt a secret"""
        entry = self._secrets.get(key)
        if not entry:
            logger.warning(f"Secret not found: {key}")
            return None
        
        # Check expiration
        if entry.expires_at:
            expires = datetime.fromisoformat(entry.expires_at)
            if datetime.utcnow() > expires:
                logger.warning(f"Secret expired: {key}")
                return None
        
        try:
            decrypted = self._cipher.decrypt(entry.value.encode()).decode()
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow().isoformat()
            self._audit("GET", key)
            return decrypted
        except Exception as e:
            logger.error(f"Failed to decrypt secret {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a secret"""
        if key in self._secrets:
            del self._secrets[key]
            self._audit("DELETE", key)
            logger.info(f"Secret deleted: {key}")
            return True
        return False
    
    def rotate(self, key: str) -> bool:
        """Rotate a secret (re-encrypt with new key)"""
        value = self.get(key)
        if value is None:
            return False
        
        # Re-encrypt with new cipher
        new_cipher = self._init_cipher()
        encrypted = new_cipher.encrypt(value.encode()).decode()
        
        entry = self._secrets[key]
        entry.value = encrypted
        entry.version += 1
        entry.rotation_required = False
        
        self._cipher = new_cipher
        self._audit("ROTATE", key)
        logger.info(f"Secret rotated: {key} (v{entry.version})")
        return True
    
    def list_keys(self, tag: Optional[str] = None) -> List[str]:
        """List all secret keys, optionally filtered by tag"""
        if tag:
            return [k for k, v in self._secrets.items() if tag in v.tags]
        return list(self._secrets.keys())
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get secret metadata without decrypting"""
        entry = self._secrets.get(key)
        if not entry:
            return None
        return {
            "id": entry.id,
            "key": entry.key,
            "description": entry.description,
            "tags": entry.tags,
            "created_at": entry.created_at,
            "expires_at": entry.expires_at,
            "version": entry.version,
            "access_count": entry.access_count,
            "last_accessed": entry.last_accessed,
            "rotation_required": entry.rotation_required,
        }
    
    def get_expired_secrets(self) -> List[str]:
        """Get list of expired secrets"""
        expired = []
        now = datetime.utcnow()
        for key, entry in self._secrets.items():
            if entry.expires_at:
                expires = datetime.fromisoformat(entry.expires_at)
                if now > expires:
                    expired.append(key)
        return expired
    
    def get_secrets_needing_rotation(self) -> List[str]:
        """Get secrets that need rotation"""
        return [k for k, v in self._secrets.items() if v.rotation_required]
    
    def _audit(self, action: str, key: str):
        """Log an audit entry"""
        self._audit_log.append({
            "action": action,
            "key": key,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._audit_log[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_secrets": len(self._secrets),
            "expired": len(self.get_expired_secrets()),
            "needs_rotation": len(self.get_secrets_needing_rotation()),
            "total_accesses": sum(v.access_count for v in self._secrets.values()),
        }


# Global singleton
global_secret_manager = SecretManager()