# Key Rotation Reference

Secure key management and rotation patterns for JWT signing keys.

## Key Generation

Using cryptography library for RSA keys:

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import hashlib

def generate_rsa_keypair():
    """Generate 2048-bit RSA key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # PEM format for storage
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Key ID from public key hash
    kid = hashlib.sha256(public_pem).hexdigest()[:16]

    return private_pem, public_pem, kid
```

## Fernet Encryption

Encrypt private keys for database storage:

```python
from cryptography.fernet import Fernet
import base64
import os

def get_fernet():
    """Get Fernet instance from environment key."""
    key = os.environ["JWT_ENCRYPTION_KEY"]
    return Fernet(key.encode())

def encrypt_private_key(private_pem: bytes) -> str:
    """Encrypt private key with Fernet."""
    fernet = get_fernet()
    encrypted = fernet.encrypt(private_pem)
    return base64.b64encode(encrypted).decode()

def decrypt_private_key(encrypted: str) -> bytes:
    """Decrypt private key from storage."""
    fernet = get_fernet()
    encrypted_bytes = base64.b64decode(encrypted.encode())
    return fernet.decrypt(encrypted_bytes)
```

## Database Schema

```sql
CREATE TABLE jwt_keys (
    id SERIAL PRIMARY KEY,
    kid VARCHAR(32) UNIQUE NOT NULL,
    encrypted_private_key TEXT NOT NULL,
    public_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    rotation_id INTEGER  -- Links old/new keys
);

CREATE INDEX idx_jwt_keys_lookup ON jwt_keys(is_active, expires_at);
```

## Rotation Workflow

24-hour grace period for zero-downtime rotation:

```python
from datetime import datetime, timedelta

def rotate_keys(session):
    """Perform key rotation with grace period."""
    # 1. Generate new key
    private_pem, public_pem, kid = generate_rsa_keypair()

    # 2. Store encrypted
    new_key = JWTKey(
        kid=kid,
        encrypted_private_key=encrypt_private_key(private_pem),
        public_key=public_pem.decode(),
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
        is_active=True,
    )
    session.add(new_key)

    # 3. Schedule old keys for expiry (24h grace)
    grace_deadline = datetime.utcnow() + timedelta(hours=24)
    session.query(JWTKey).filter(
        JWTKey.kid != kid,
        JWTKey.is_active == True
    ).update({"expires_at": grace_deadline})

    session.commit()
    return kid

def cleanup_expired_keys(session):
    """Remove keys past their expiry."""
    count = session.query(JWTKey).filter(
        JWTKey.expires_at < datetime.utcnow()
    ).delete()
    session.commit()
    return count
```

## Signing Key Selection

Always use newest active key for signing:

```python
def get_signing_key(session) -> tuple[bytes, str]:
    """Get current signing key (newest active)."""
    key = session.query(JWTKey).filter(
        JWTKey.is_active == True,
        JWTKey.expires_at > datetime.utcnow()
    ).order_by(JWTKey.created_at.desc()).first()

    if not key:
        raise RuntimeError("No active signing key")

    private_pem = decrypt_private_key(key.encrypted_private_key)
    return private_pem, key.kid
```

## Verification Key Set

Return all active keys for verification:

```python
def get_verification_keys(session) -> list[dict]:
    """Get all active public keys for JWKS."""
    keys = session.query(JWTKey).filter(
        JWTKey.is_active == True,
        JWTKey.expires_at > datetime.utcnow()
    ).all()

    return [
        {
            "kid": k.kid,
            "public_key": k.public_key,
            "expires_at": k.expires_at.isoformat()
        }
        for k in keys
    ]
```

## Rotation Schedule

| Scenario | Rotation Frequency |
|----------|-------------------|
| Development | Manual only |
| Production | Monthly (cron) |
| Security incident | Immediate |

Cron example (monthly):
```bash
0 0 1 * * /app/manage.py rotate_jwt_keys
```

## Environment Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `JWT_ENCRYPTION_KEY` | `ABCdef123...` | 32-byte Fernet key |
| `JWT_KEY_ROTATION_DAYS` | `30` | Days until rotation |
| `JWT_GRACE_PERIOD_HOURS` | `24` | Overlap period |

Generate Fernet key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```
