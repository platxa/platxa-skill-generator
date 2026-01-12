---
name: platxa-jwt-auth
description: Generate RS256 JWT authentication with JWKS endpoint for Platxa services. Creates secure token infrastructure with key rotation support.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - builder
    - authentication
    - jwt
    - security
    - rs256
---

# Platxa JWT Authentication

Builder skill for generating RS256 JWT authentication infrastructure with JWKS endpoints.

## Overview

This skill generates production-ready JWT authentication components:

| Component | What Gets Generated |
|-----------|-------------------|
| **Key Infrastructure** | RSA key pair, Fernet encryption, secure storage |
| **Token Service** | Create/verify tokens for access, editor, service |
| **JWKS Endpoint** | Public key endpoint at `/.well-known/jwks.json` |
| **Key Rotation** | Rotation commands with 24-hour grace period |

## Workflow

### Step 1: Analyze Requirements

Determine which token types are needed:

| Token Type | Purpose | Default Expiry |
|------------|---------|----------------|
| **Access** | User authentication | 1 hour |
| **Editor** | Sidecar communication | 8 hours |
| **Service** | Service-to-service | 5 minutes |

### Step 2: Generate Key Infrastructure

Create RSA key pair with secure storage:

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.fernet import Fernet
import base64
import os

def generate_key_pair():
    """Generate RSA key pair for JWT signing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize public key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem

def encrypt_private_key(private_pem: bytes) -> str:
    """Encrypt private key with Fernet."""
    key = os.environ.get('JWT_ENCRYPTION_KEY')
    if not key:
        key = Fernet.generate_key().decode()
        print(f"Generated encryption key: {key}")
        print("Set JWT_ENCRYPTION_KEY environment variable!")

    fernet = Fernet(key.encode() if isinstance(key, str) else key)
    encrypted = fernet.encrypt(private_pem)
    return base64.b64encode(encrypted).decode()
```

### Step 3: Create Token Service

Implement token creation and verification:

```python
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

class TokenService:
    def __init__(self, private_key: bytes, public_key: bytes, issuer: str):
        self.private_key = private_key
        self.public_key = public_key
        self.issuer = issuer
        self.algorithm = "RS256"

    def create_access_token(
        self,
        user_id: int,
        partner_id: int,
        instance_ids: list[int],
        roles: list[str],
        expires_delta: timedelta = timedelta(hours=1)
    ) -> str:
        """Create access token for user authentication."""
        now = datetime.utcnow()
        payload = {
            "iss": self.issuer,
            "sub": str(user_id),
            "aud": "platxa-api",
            "exp": now + expires_delta,
            "nbf": now,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "type": "access",
            "user_id": user_id,
            "partner_id": partner_id,
            "instance_ids": instance_ids,
            "roles": roles,
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def create_editor_token(
        self,
        instance_name: str,
        user_id: int,
        permissions: list[str],
        expires_delta: timedelta = timedelta(hours=8)
    ) -> str:
        """Create editor token for Sidecar communication."""
        now = datetime.utcnow()
        payload = {
            "iss": self.issuer,
            "sub": f"editor:{instance_name}",
            "aud": f"sidecar-{instance_name}",
            "exp": now + expires_delta,
            "nbf": now,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "type": "editor",
            "instance_name": instance_name,
            "user_id": user_id,
            "permissions": permissions,
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def create_service_token(
        self,
        service_name: str,
        allowed_endpoints: list[str],
        expires_delta: timedelta = timedelta(minutes=5)
    ) -> str:
        """Create service token for service-to-service auth."""
        now = datetime.utcnow()
        payload = {
            "iss": self.issuer,
            "sub": f"service:{service_name}",
            "aud": "platxa-internal",
            "exp": now + expires_delta,
            "nbf": now,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "type": "service",
            "service_name": service_name,
            "allowed_endpoints": allowed_endpoints,
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def verify_token(
        self,
        token: str,
        expected_type: Optional[str] = None,
        expected_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                audience=expected_audience,
                issuer=self.issuer,
            )

            if expected_type and payload.get("type") != expected_type:
                raise jwt.InvalidTokenError(
                    f"Expected {expected_type} token, got {payload.get('type')}"
                )

            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")
```

### Step 4: Implement JWKS Endpoint

Create the public key endpoint:

```python
from fastapi import FastAPI
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import base64

app = FastAPI()

def get_jwk(public_key: RSAPublicKey, kid: str) -> dict:
    """Convert RSA public key to JWK format."""
    public_numbers = public_key.public_numbers()

    def int_to_base64url(n: int, length: int) -> str:
        data = n.to_bytes(length, byteorder='big')
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

    return {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": kid,
        "n": int_to_base64url(public_numbers.n, 256),
        "e": int_to_base64url(public_numbers.e, 3),
    }

@app.get("/.well-known/jwks.json")
async def jwks():
    """Return JSON Web Key Set with all active public keys."""
    keys = []
    for key_record in get_active_keys():  # From database
        keys.append(get_jwk(key_record.public_key, key_record.kid))

    return {
        "keys": keys
    }
```

### Step 5: Add Key Rotation

Implement rotation with grace period:

```python
from datetime import datetime, timedelta
import hashlib

def rotate_keys(db_session):
    """Rotate JWT signing keys with 24-hour grace period."""
    # Generate new key pair
    private_pem, public_pem = generate_key_pair()

    # Generate key ID from public key hash
    kid = hashlib.sha256(public_pem).hexdigest()[:16]

    # Encrypt and store
    encrypted_private = encrypt_private_key(private_pem)

    new_key = JWTKey(
        kid=kid,
        encrypted_private_key=encrypted_private,
        public_key=public_pem.decode(),
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
        is_active=True,
    )
    db_session.add(new_key)

    # Mark old keys for expiry (24-hour grace period)
    grace_period = datetime.utcnow() + timedelta(hours=24)
    db_session.query(JWTKey).filter(
        JWTKey.kid != kid,
        JWTKey.is_active == True
    ).update({
        "expires_at": grace_period
    })

    db_session.commit()
    return kid
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_ENCRYPTION_KEY` | Yes | Fernet key for private key encryption |
| `JWT_ISSUER` | Yes | Token issuer (e.g., `https://platxa.com`) |
| `JWT_DEFAULT_AUDIENCE` | No | Default audience claim |

### Database Schema

```sql
CREATE TABLE jwt_keys (
    id SERIAL PRIMARY KEY,
    kid VARCHAR(32) UNIQUE NOT NULL,
    encrypted_private_key TEXT NOT NULL,
    public_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_jwt_keys_active ON jwt_keys(is_active, expires_at);
```

## Examples

### Example 1: Basic Single-Instance Setup

**User**: "Set up JWT auth for a single Platxa instance"

**Generated Code**:

```python
# config.py
JWT_CONFIG = {
    "issuer": "https://myinstance.platxa.com",
    "access_token_expire": 3600,      # 1 hour
    "editor_token_expire": 28800,     # 8 hours
    "algorithm": "RS256",
}

# Initialize on startup
from token_service import TokenService

token_service = TokenService(
    private_key=load_private_key(),
    public_key=load_public_key(),
    issuer=JWT_CONFIG["issuer"]
)
```

### Example 2: Multi-Tenant Token Generation

**User**: "Generate tokens for multi-tenant setup with instance isolation"

**Generated Code**:

```python
def generate_user_tokens(user, instance):
    """Generate access and editor tokens for a user's instance."""
    access_token = token_service.create_access_token(
        user_id=user.id,
        partner_id=user.partner_id,
        instance_ids=[instance.id],
        roles=user.get_roles_for_instance(instance.id)
    )

    editor_token = token_service.create_editor_token(
        instance_name=instance.name,
        user_id=user.id,
        permissions=["read", "write", "deploy"]
    )

    return {
        "access_token": access_token,
        "editor_token": editor_token,
        "token_type": "bearer",
        "expires_in": 3600,
    }
```

### Example 3: Service-to-Service Authentication

**User**: "Set up AI Engine to Sidecar authentication"

**Generated Code**:

```python
# ai_engine/auth.py
class ServiceAuth:
    def __init__(self, token_service: TokenService):
        self.token_service = token_service

    def get_sidecar_token(self, instance_name: str) -> str:
        """Get short-lived token for Sidecar API calls."""
        return self.token_service.create_service_token(
            service_name="ai-engine",
            allowed_endpoints=[
                f"/instances/{instance_name}/files/*",
                f"/instances/{instance_name}/deploy",
            ],
            expires_delta=timedelta(minutes=5)
        )

# Usage in AI Engine
async def deploy_to_instance(instance_name: str, files: dict):
    token = service_auth.get_sidecar_token(instance_name)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://edit-{instance_name}.platxa.com/deploy",
            headers={"Authorization": f"Bearer {token}"},
            json={"files": files}
        )
```

### Example 4: Complete Key Rotation

**User**: "Implement key rotation with zero downtime"

**Generated Code**:

```python
# management/commands/rotate_jwt_keys.py
from datetime import datetime, timedelta

def rotate_jwt_keys():
    """Rotate JWT keys with 24-hour grace period."""
    with db.session() as session:
        # Generate new key
        new_kid = rotate_keys(session)
        print(f"Generated new key: {new_kid}")

        # List all active keys
        active_keys = session.query(JWTKey).filter(
            JWTKey.is_active == True,
            JWTKey.expires_at > datetime.utcnow()
        ).all()

        print(f"Active keys: {len(active_keys)}")
        for key in active_keys:
            remaining = key.expires_at - datetime.utcnow()
            print(f"  - {key.kid}: expires in {remaining}")

        # Clean up expired keys
        expired = session.query(JWTKey).filter(
            JWTKey.expires_at < datetime.utcnow()
        ).delete()
        print(f"Removed {expired} expired keys")

# Cron job: 0 0 1 * * (monthly rotation)
```

## Security Best Practices

| Area | Practice | Implementation |
|------|----------|---------------|
| Keys | Encryption | Fernet (AES-128-CBC), never in code |
| Keys | Isolation | Separate keys per environment |
| Tokens | Short expiry | Access: 1h, Service: 5m |
| Tokens | Validation | Always verify `aud` and `type` claims |
| Tokens | Revocation | Include `jti` for blacklisting |
| JWKS | Caching | `max-age=3600`, include `kid` in tokens |

## Troubleshooting

| Error/Issue | Cause | Fix |
|-------------|-------|-----|
| `ExpiredSignatureError` | Token expired | Refresh token |
| `InvalidAudienceError` | Wrong audience | Check `aud` claim |
| `InvalidSignatureError` | Key mismatch | Check JWKS endpoint |
| Tokens invalid after rotation | Grace period too short | Extend to 24+ hours |
| Decryption failure | Wrong encryption key | Check JWT_ENCRYPTION_KEY |

## Output Checklist

After generating JWT authentication:

- [ ] RSA key pair generated (2048-bit minimum)
- [ ] Private key encrypted with Fernet
- [ ] JWT_ENCRYPTION_KEY documented
- [ ] TokenService implements all token types
- [ ] JWKS endpoint at `/.well-known/jwks.json`
- [ ] Key rotation script created
- [ ] Database migration for jwt_keys table
- [ ] Environment variables documented
- [ ] Token verification includes type checking
- [ ] Tests cover creation and verification

## Related Resources

- **Token Claims**: See `references/token-claims.md`
- **JWKS Format**: See `references/jwks-format.md`
- **Key Rotation**: See `references/key-rotation.md`
- **Odoo Integration**: Use `platxa-k8s-ops` for deployment
