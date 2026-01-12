# Fernet Encryption Reference

Detailed Fernet encryption patterns for Platxa services.

## What is Fernet?

Fernet is a symmetric encryption scheme from the `cryptography` library that provides:
- **AES-128-CBC** encryption
- **HMAC-SHA256** authentication
- **Timestamp** for optional TTL enforcement
- **URL-safe base64** encoding

## Key Format

```
Fernet key = 32 bytes = 256 bits
Encoded = 44 characters (url-safe base64)

Example: b'ZmRlZmVyZW50a2V5MTIzNDU2Nzg5MDEyMzQ1Njc4OTA='
```

## Installation

```bash
pip install cryptography
```

## Basic Usage

### Key Generation

```python
from cryptography.fernet import Fernet

# Generate new key
key = Fernet.generate_key()
# b'...' (44 characters, base64)

# NEVER hardcode - store securely
```

### Encrypt/Decrypt

```python
from cryptography.fernet import Fernet

key = b'your-32-byte-key-base64-encoded=='
f = Fernet(key)

# Encrypt (bytes in, bytes out)
plaintext = b"sensitive data"
ciphertext = f.encrypt(plaintext)

# Decrypt
decrypted = f.decrypt(ciphertext)
assert decrypted == plaintext
```

### String Handling

```python
def encrypt_string(value: str, key: bytes) -> str:
    """Encrypt string, return string for database storage."""
    f = Fernet(key)
    encrypted_bytes = f.encrypt(value.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')  # Base64 string

def decrypt_string(encrypted: str, key: bytes) -> str:
    """Decrypt string from database."""
    f = Fernet(key)
    decrypted_bytes = f.decrypt(encrypted.encode('utf-8'))
    return decrypted_bytes.decode('utf-8')
```

## Key Management

### From Environment

```python
import os
from cryptography.fernet import Fernet

def get_fernet_key() -> bytes:
    """Get Fernet key from environment."""
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        raise ValueError("ENCRYPTION_KEY environment variable not set")
    return key.encode()

# Usage
key = get_fernet_key()
f = Fernet(key)
```

### From Config File

```python
from odoo.tools import config

def get_fernet_key() -> bytes:
    """Get Fernet key from Odoo config."""
    key = config.get('instance_manager_encryption_key')
    if not key:
        raise ValueError("Encryption key not configured")
    return key.encode()
```

### From Database Parameter

```python
def get_fernet_key(self) -> bytes:
    """Get Fernet key from system parameter."""
    key = self.env['ir.config_parameter'].sudo().get_param(
        'instance_manager.encryption_key'
    )
    if not key:
        raise ValueError("Encryption key not set in system parameters")
    return key.encode()
```

### Development Fallback (Insecure)

```python
import logging
import base64

_logger = logging.getLogger(__name__)

def get_fernet_key_with_fallback() -> bytes:
    """Get key with development fallback."""
    key = os.environ.get('ENCRYPTION_KEY')

    if not key:
        _logger.warning(
            "ENCRYPTION_KEY not set. Using insecure default. "
            "DO NOT USE IN PRODUCTION!"
        )
        # 32 bytes -> base64 = 44 chars
        key = base64.urlsafe_b64encode(b'developmentonlykey32bytes!!').decode()

    return key.encode()
```

## Converting Custom Keys

### 32-Character String to Fernet Key

```python
import base64

def string_to_fernet_key(s: str) -> bytes:
    """Convert 32-char string to Fernet key format."""
    if len(s) != 32:
        raise ValueError("Key must be exactly 32 characters")

    # Fernet requires url-safe base64 of 32 bytes
    return base64.urlsafe_b64encode(s.encode())

# Usage
custom_key = "MySecretKey12345MySecretKey12345"  # 32 chars
fernet_key = string_to_fernet_key(custom_key)
f = Fernet(fernet_key)
```

### Validate Key Format

```python
from cryptography.fernet import Fernet, InvalidToken
import base64

def is_valid_fernet_key(key: bytes) -> bool:
    """Check if key is valid Fernet format."""
    try:
        # Fernet constructor validates key
        Fernet(key)
        return True
    except (ValueError, TypeError):
        return False

def normalize_key(key: str) -> bytes:
    """Normalize key to Fernet format."""
    # Already base64?
    if key.endswith('='):
        return key.encode()

    # Raw 32-byte string
    if len(key) == 32:
        return base64.urlsafe_b64encode(key.encode())

    raise ValueError(f"Invalid key length: {len(key)} (expected 32 or base64)")
```

## Error Handling

### InvalidToken

```python
from cryptography.fernet import Fernet, InvalidToken

def safe_decrypt(encrypted: str, key: bytes) -> str | None:
    """Decrypt with error handling."""
    try:
        f = Fernet(key)
        return f.decrypt(encrypted.encode()).decode()
    except InvalidToken:
        _logger.error("Decryption failed: invalid token (wrong key or corrupted data)")
        return None
    except Exception as e:
        _logger.error(f"Decryption error: {type(e).__name__}: {e}")
        return None
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `InvalidToken` | Wrong key or corrupted data | Verify correct key |
| `ValueError: Fernet key must be 32 url-safe base64-encoded bytes` | Invalid key format | Use `Fernet.generate_key()` or encode properly |
| `TypeError` | Key not bytes | Encode string with `.encode()` |

## TTL (Time-To-Live)

```python
from cryptography.fernet import Fernet, InvalidToken

f = Fernet(key)

# Encrypt with embedded timestamp
token = f.encrypt(b"data")

# Decrypt with TTL check (seconds)
try:
    data = f.decrypt(token, ttl=3600)  # 1 hour max age
except InvalidToken:
    print("Token expired or invalid")
```

## Multiple Keys (Rotation)

```python
from cryptography.fernet import Fernet, MultiFernet

# Old key (for decrypting old data)
old_key = Fernet(b'old-key...')

# New key (for encrypting new data)
new_key = Fernet(b'new-key...')

# MultiFernet tries keys in order
mf = MultiFernet([new_key, old_key])

# Encrypt uses first key
encrypted = mf.encrypt(b"new data")

# Decrypt tries all keys
decrypted = mf.decrypt(old_encrypted_data)  # Uses old_key
decrypted = mf.decrypt(encrypted)            # Uses new_key

# Re-encrypt old data with new key
rotated = mf.rotate(old_encrypted_data)
```

## Odoo Model Integration

```python
from odoo import models, fields, api

class SecureCredential(models.Model):
    _name = 'secure.credential'

    name = fields.Char(required=True)
    password_encrypted = fields.Text()

    def _get_fernet(self):
        """Get Fernet instance with configured key."""
        key = self.env['ir.config_parameter'].sudo().get_param(
            'encryption_key'
        )
        if not key:
            raise ValueError("Encryption key not configured")
        return Fernet(key.encode())

    def set_password(self, password: str):
        """Encrypt and store password."""
        f = self._get_fernet()
        self.password_encrypted = f.encrypt(password.encode()).decode()

    def get_password(self) -> str:
        """Decrypt and return password."""
        if not self.password_encrypted:
            return ''
        f = self._get_fernet()
        return f.decrypt(self.password_encrypted.encode()).decode()

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-encrypt passwords on create."""
        for vals in vals_list:
            if 'password' in vals:
                # Encrypt before storage
                record = self.new({})
                f = record._get_fernet()
                vals['password_encrypted'] = f.encrypt(
                    vals.pop('password').encode()
                ).decode()
        return super().create(vals_list)
```

## Security Best Practices

1. **Never hardcode keys** - Use environment variables or secure config
2. **Generate keys properly** - Always use `Fernet.generate_key()`
3. **Log key operations, not values** - Audit key creation/rotation
4. **Use MultiFernet for rotation** - Allows gradual key migration
5. **Handle errors gracefully** - Don't expose decryption failures to users
6. **Consider TTL** - For time-sensitive tokens
7. **Backup keys securely** - Lost key = lost data
