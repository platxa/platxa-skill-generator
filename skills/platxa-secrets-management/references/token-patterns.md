# Token Patterns Reference

Secure token generation and verification patterns for Platxa.

## Token Types

| Type | Use Case | Format | Length |
|------|----------|--------|--------|
| Password | Credentials | Alphanumeric | 16-32 |
| API Token | Service auth | Hex | 32-64 |
| Webhook | HTTP auth | Hex | 32 |
| Session ID | User sessions | URL-safe base64 | 32 |

## Secure Random Generation

### Python `secrets` Module

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
def generate_password(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
```

### Token Generation

```python
def generate_hex_token(nbytes: int = 32) -> str:
    return secrets.token_hex(nbytes)  # 64 chars

def generate_urlsafe_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)  # ~43 chars
```

## Token Verification

### CRITICAL: Constant-Time Comparison

```python
import hmac

# CORRECT: constant-time comparison
def verify_token(provided: str, expected: str) -> bool:
    return hmac.compare_digest(provided, expected)

# WRONG: timing attack vulnerable
def verify_insecure(provided: str, expected: str) -> bool:
    return provided == expected  # DON'T USE
```

### Bearer Token Verification

```python
from flask import request

def verify_bearer_token() -> bool:
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return False
    token = auth[7:]
    expected = get_config('webhook_token')
    if not expected:
        return False
    return hmac.compare_digest(token, expected)
```

## Token Storage

### Environment Variable

```python
def get_token_from_env(name: str) -> str | None:
    token = os.environ.get(name)
    if not token:
        _logger.warning(f"Token {name} not set")
    return token
```

### K8s Secret

```python
def get_token_from_k8s(namespace: str, secret_name: str, key: str) -> str | None:
    try:
        secret = core_v1.read_namespaced_secret(secret_name, namespace)
        if secret.data and key in secret.data:
            return base64.b64decode(secret.data[key]).decode()
    except client.ApiException:
        pass
    return None
```

## Token Rotation

```python
def rotate_webhook_token(self) -> str:
    new_token = secrets.token_hex(32)
    self.env['ir.config_parameter'].sudo().set_param(
        'instance_manager.webhook_token', new_token
    )
    _logger.info("Webhook token rotated")  # Don't log token!
    return new_token
```

## Go Token Patterns

```go
import (
    "crypto/rand"
    "crypto/subtle"
    "encoding/hex"
)

func GenerateToken(nbytes int) (string, error) {
    bytes := make([]byte, nbytes)
    if _, err := rand.Read(bytes); err != nil {
        return "", err
    }
    return hex.EncodeToString(bytes), nil
}

func VerifyToken(provided, expected string) bool {
    return subtle.ConstantTimeCompare(
        []byte(provided), []byte(expected),
    ) == 1
}
```

## TypeScript Token Patterns

```typescript
import crypto from 'crypto';

function generateToken(bytes: number = 32): string {
  return crypto.randomBytes(bytes).toString('hex');
}

function verifyToken(provided: string, expected: string): boolean {
  const providedBuf = Buffer.from(provided);
  const expectedBuf = Buffer.from(expected);
  if (providedBuf.length !== expectedBuf.length) return false;
  return crypto.timingSafeEqual(providedBuf, expectedBuf);
}
```

## Security Checklist

- [ ] Use `secrets` module (not `random`)
- [ ] Use `hmac.compare_digest()` for verification
- [ ] Never log token values
- [ ] Store tokens in secure storage
- [ ] Implement token rotation
- [ ] Set appropriate token length (32+ bytes)
- [ ] Reject requests if token not configured
