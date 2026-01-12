# Token Patterns Reference

Secure token generation and verification patterns for Platxa.

## Token Types

| Type | Use Case | Format | Length |
|------|----------|--------|--------|
| Password | User/DB credentials | Alphanumeric | 16-32 chars |
| API Token | Service auth | Hex | 32-64 chars |
| Webhook Token | HTTP auth | Hex | 32 chars |
| Session ID | User sessions | URL-safe base64 | 32 chars |
| DNS Verification | Domain ownership | Hex | 16-32 chars |

## Secure Random Generation

### Python `secrets` Module

Always use `secrets` for cryptographic randomness, never `random`:

```python
import secrets
import string

# CORRECT: cryptographically secure
password = secrets.token_hex(16)

# WRONG: predictable, NOT secure
import random
password = ''.join(random.choices(string.ascii_letters, k=16))  # DON'T USE
```

### Password Generation

```python
import secrets
import string

def generate_password(length: int = 32, include_special: bool = False) -> str:
    """Generate secure password."""
    alphabet = string.ascii_letters + string.digits
    if include_special:
        alphabet += string.punctuation

    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Usage
db_password = generate_password(32)
admin_password = generate_password(24)
user_password = generate_password(16, include_special=True)
```

### Hex Token

```python
import secrets

def generate_hex_token(nbytes: int = 32) -> str:
    """Generate hex token (2 chars per byte)."""
    return secrets.token_hex(nbytes)

# Usage
api_token = generate_hex_token(32)   # 64 chars
webhook_token = generate_hex_token(16)  # 32 chars
```

### URL-Safe Token

```python
import secrets

def generate_urlsafe_token(nbytes: int = 32) -> str:
    """Generate URL-safe base64 token."""
    return secrets.token_urlsafe(nbytes)

# Usage (shorter than hex for same entropy)
session_id = generate_urlsafe_token(24)  # ~32 chars
```

### Instance Name Generation

```python
import secrets
import string

def generate_instance_name(length: int = 8) -> str:
    """Generate lowercase alphanumeric identifier."""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Usage
instance_name = generate_instance_name()  # e.g., "abc12xyz"
```

## Token Verification

### CRITICAL: Constant-Time Comparison

**Always** use `hmac.compare_digest()` to prevent timing attacks:

```python
import hmac

# CORRECT: constant-time comparison
def verify_token(provided: str, expected: str) -> bool:
    """Verify token using constant-time comparison."""
    return hmac.compare_digest(provided, expected)

# WRONG: timing attack vulnerable
def verify_token_insecure(provided: str, expected: str) -> bool:
    return provided == expected  # DON'T USE - timing attack!
```

### Timing Attack Explanation

```python
# Standard == comparison exits early on first mismatch
"secret123" == "wrongXXXX"  # Returns False after 1 char comparison
"secret123" == "secreXXXX"  # Returns False after 6 char comparisons

# Attacker measures response time to guess characters
# hmac.compare_digest always takes same time regardless of match position
```

### Bearer Token Verification

```python
import hmac
from flask import request, jsonify

def verify_bearer_token() -> bool:
    """Verify Authorization: Bearer <token> header."""
    auth_header = request.headers.get('Authorization', '')

    # Check format
    if not auth_header.startswith('Bearer '):
        return False

    # Extract token
    provided_token = auth_header[7:]  # Remove "Bearer "

    # Get expected token from secure storage
    expected_token = get_config('webhook_token')

    # Secure by default - reject if not configured
    if not expected_token:
        _logger.warning("No token configured - rejecting request")
        return False

    # Constant-time comparison
    return hmac.compare_digest(provided_token, expected_token)
```

### Complete Webhook Handler

```python
import hmac
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
_logger = logging.getLogger(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Secure webhook endpoint."""
    # 1. Verify authentication
    if not verify_bearer_token():
        _logger.warning(
            "Unauthorized webhook attempt",
            extra={'ip': request.remote_addr}
        )
        return jsonify({'error': 'Unauthorized'}), 401

    # 2. Validate content type
    if request.content_type != 'application/json':
        return jsonify({'error': 'Invalid content type'}), 415

    # 3. Parse and process
    try:
        data = request.get_json()
        process_webhook(data)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        _logger.error(f"Webhook processing failed: {e}")
        return jsonify({'error': 'Processing failed'}), 500
```

## Token Storage

### Environment Variable

```python
import os

def get_token_from_env(name: str) -> str | None:
    """Get token from environment."""
    token = os.environ.get(name)
    if not token:
        _logger.warning(f"Token {name} not set in environment")
    return token

# Usage
webhook_token = get_token_from_env('ALERTMANAGER_WEBHOOK_TOKEN')
```

### Database Parameter (Odoo)

```python
def get_token_from_param(self, param_name: str) -> str | None:
    """Get token from Odoo system parameter."""
    return self.env['ir.config_parameter'].sudo().get_param(param_name)

def set_token_param(self, param_name: str, token: str) -> None:
    """Set token in Odoo system parameter."""
    self.env['ir.config_parameter'].sudo().set_param(param_name, token)

# Usage
token = self.get_token_from_param('instance_manager.webhook_token')
```

### K8s Secret

```python
import base64
from kubernetes import client

def get_token_from_k8s(namespace: str, secret_name: str, key: str) -> str | None:
    """Get token from Kubernetes secret."""
    core_v1 = client.CoreV1Api()

    try:
        secret = core_v1.read_namespaced_secret(secret_name, namespace)
        if secret.data and key in secret.data:
            return base64.b64decode(secret.data[key]).decode()
    except client.ApiException:
        pass

    return None
```

## Token Rotation

### Generate and Store New Token

```python
import secrets

def rotate_webhook_token(self) -> str:
    """Generate new webhook token and store."""
    # 1. Generate new token
    new_token = secrets.token_hex(32)

    # 2. Store in config
    self.env['ir.config_parameter'].sudo().set_param(
        'instance_manager.webhook_token',
        new_token
    )

    # 3. Update dependent services
    self._update_alertmanager_webhook_secret(new_token)

    # 4. Log rotation (not the token value!)
    _logger.info("Webhook token rotated")

    return new_token
```

### Grace Period Pattern

```python
from datetime import datetime, timedelta

class TokenRotation:
    """Token rotation with grace period."""

    def __init__(self):
        self.current_token = None
        self.previous_token = None
        self.rotation_time = None
        self.grace_period = timedelta(hours=1)

    def rotate(self) -> str:
        """Rotate token with grace period."""
        # Keep old token for grace period
        self.previous_token = self.current_token
        self.rotation_time = datetime.utcnow()

        # Generate new token
        self.current_token = secrets.token_hex(32)

        return self.current_token

    def verify(self, token: str) -> bool:
        """Verify token (accepts old token during grace period)."""
        # Check current token
        if self.current_token and hmac.compare_digest(token, self.current_token):
            return True

        # Check previous token during grace period
        if self.previous_token and self.rotation_time:
            if datetime.utcnow() < self.rotation_time + self.grace_period:
                if hmac.compare_digest(token, self.previous_token):
                    return True

        return False
```

## Go Token Patterns

### Generate Token

```go
import (
    "crypto/rand"
    "encoding/hex"
)

func GenerateToken(nbytes int) (string, error) {
    bytes := make([]byte, nbytes)
    if _, err := rand.Read(bytes); err != nil {
        return "", err
    }
    return hex.EncodeToString(bytes), nil
}

// Usage
token, err := GenerateToken(32)  // 64 char hex
```

### Constant-Time Comparison

```go
import "crypto/subtle"

func VerifyToken(provided, expected string) bool {
    // crypto/subtle.ConstantTimeCompare for constant-time
    return subtle.ConstantTimeCompare(
        []byte(provided),
        []byte(expected),
    ) == 1
}
```

## TypeScript Token Patterns

### Generate Token (Node.js)

```typescript
import crypto from 'crypto';

function generateToken(bytes: number = 32): string {
  return crypto.randomBytes(bytes).toString('hex');
}

function generateUrlSafeToken(bytes: number = 32): string {
  return crypto.randomBytes(bytes).toString('base64url');
}
```

### Constant-Time Comparison

```typescript
import crypto from 'crypto';

function verifyToken(provided: string, expected: string): boolean {
  // Convert to buffers of equal length for timingSafeEqual
  const providedBuf = Buffer.from(provided);
  const expectedBuf = Buffer.from(expected);

  // Must be same length for timingSafeEqual
  if (providedBuf.length !== expectedBuf.length) {
    return false;
  }

  return crypto.timingSafeEqual(providedBuf, expectedBuf);
}
```

## Security Checklist

- [ ] Use `secrets` module (not `random`)
- [ ] Use `hmac.compare_digest()` for verification
- [ ] Never log token values
- [ ] Store tokens in secure storage (env/config/vault)
- [ ] Implement token rotation
- [ ] Set appropriate token length (32+ bytes)
- [ ] Reject requests if token not configured
- [ ] Log failed verification attempts (for monitoring)
