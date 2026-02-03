---
name: platxa-secrets-management
description: Fernet encryption, Kubernetes secrets, and secure token patterns for Platxa services. Covers Python cryptography, K8s Secret objects, key rotation, and constant-time token verification.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - guide
    - security
    - encryption
    - kubernetes
    - secrets
---

# Platxa Secrets Management

Guide for secrets management patterns across Platxa services.

## Overview

| Component | Encryption | Storage | Pattern |
|-----------|------------|---------|---------|
| **Credentials** | Fernet (AES-128-CBC) | Odoo DB (encrypted) | Encrypt before store |
| **K8s Secrets** | Base64 + etcd encryption | K8s API | stringData/data fields |
| **Tokens** | N/A | Memory/Header | HMAC verification |
| **JWT Keys** | Fernet (RSA private) | DB | Rotate with grace period |

## Core Principles

1. **Defense in Depth**: Encrypt at rest, in transit, and minimize plaintext in memory
2. **Least Privilege**: Namespace-scoped secrets, RBAC for access control
3. **Key Rotation**: Regular rotation with grace periods for validation
4. **Audit Trail**: Log secret operations (never log values, only key names)
5. **No Plaintext Storage**: Never store secrets unencrypted in code, configs, or logs

## Fernet Encryption

### Key Generation

```python
from cryptography.fernet import Fernet

# Generate a new key (32 bytes, url-safe base64)
key = Fernet.generate_key()  # b'...' (44 chars base64)

# Store key securely (environment, config parameter, vault)
# NEVER hardcode in source code
```

### Encryption/Decryption

```python
from cryptography.fernet import Fernet

def encrypt_value(value: str, key: bytes) -> str:
    """Encrypt a string value."""
    f = Fernet(key)
    encrypted = f.encrypt(value.encode())
    return encrypted.decode()  # Store as string

def decrypt_value(encrypted: str, key: bytes) -> str:
    """Decrypt a string value."""
    f = Fernet(key)
    decrypted = f.decrypt(encrypted.encode())
    return decrypted.decode()
```

### Key Retrieval Pattern

```python
import base64
from odoo.tools import config

def _get_encryption_key(self) -> bytes:
    """Get encryption key from config with fallback."""
    # Priority 1: Odoo config file
    key = config.get('instance_manager_encryption_key')

    # Priority 2: System parameter (database)
    if not key:
        key = self.env['ir.config_parameter'].sudo().get_param(
            'instance_manager.encryption_key', ''
        )

    # Priority 3: Development fallback (WARNING: insecure)
    if not key:
        _logger.warning("No encryption key configured. Using default (INSECURE!)")
        key = 'developmentonlykey32byteslong!!'

    # Ensure proper Fernet format
    if not key.endswith('='):  # Not base64 encoded
        key = base64.urlsafe_b64encode(key[:32].ljust(32).encode()).decode()

    return key.encode()
```

## Kubernetes Secrets

### Create Secret with stringData

```python
from kubernetes import client

def create_secret(namespace: str, name: str, data: dict) -> None:
    """Create K8s secret using stringData (auto base64)."""
    core_v1 = client.CoreV1Api()

    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(
            name=name,
            namespace=namespace,
            labels={'app.kubernetes.io/managed-by': 'platxa'}
        ),
        string_data=data,  # Plain text, K8s encodes automatically
        type='Opaque'
    )

    core_v1.create_namespaced_secret(namespace, secret)
```

### Create Secret with Manual Base64

```python
import base64

def create_secret_manual(namespace: str, name: str, data: dict) -> None:
    """Create K8s secret with manual base64 encoding."""
    core_v1 = client.CoreV1Api()

    # Manually encode each value
    encoded_data = {
        k: base64.b64encode(v.encode()).decode()
        for k, v in data.items()
    }

    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        data=encoded_data,  # Pre-encoded base64
        type='Opaque'
    )

    core_v1.create_namespaced_secret(namespace, secret)
```

### Read Secret

```python
def read_secret(namespace: str, name: str) -> dict:
    """Read and decode K8s secret."""
    core_v1 = client.CoreV1Api()

    secret = core_v1.read_namespaced_secret(name, namespace)

    # Decode base64 values
    return {
        k: base64.b64decode(v).decode()
        for k, v in secret.data.items()
    }
```

### TLS Secret (Certificate)

```python
def create_tls_secret(namespace: str, name: str, cert: str, key: str) -> None:
    """Create TLS secret for certificates."""
    core_v1 = client.CoreV1Api()

    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        type='kubernetes.io/tls',
        string_data={
            'tls.crt': cert,
            'tls.key': key,
        }
    )

    core_v1.create_namespaced_secret(namespace, secret)
```

## Secure Token Generation

### Password Generation

```python
import secrets
import string

def generate_password(length: int = 32) -> str:
    """Generate cryptographically secure password."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Usage
db_password = generate_password(32)
admin_password = generate_password(24)
```

### API Token Generation

```python
import secrets

def generate_token(nbytes: int = 32) -> str:
    """Generate hex token for API authentication."""
    return secrets.token_hex(nbytes)  # 64 char hex string

def generate_urlsafe_token(nbytes: int = 32) -> str:
    """Generate URL-safe token."""
    return secrets.token_urlsafe(nbytes)  # ~43 char base64
```

### DNS Verification Token

```python
def generate_dns_token() -> str:
    """Generate token for DNS verification."""
    return secrets.token_hex(16)  # 32 char hex
```

## Token Verification

### Constant-Time Comparison

```python
import hmac

def verify_token(provided: str, expected: str) -> bool:
    """Verify token using constant-time comparison.

    IMPORTANT: Never use == for token comparison (timing attack).
    """
    return hmac.compare_digest(provided, expected)
```

### Bearer Token Middleware

```python
import hmac
from flask import request

def verify_bearer_auth() -> bool:
    """Verify Bearer token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return False

    token = auth_header[7:]  # Remove 'Bearer ' prefix
    expected = get_expected_token()  # From secure storage

    if not expected:
        return False  # Secure by default

    return hmac.compare_digest(token, expected)
```

## Key Rotation

### Rotation Strategy

| Phase | Duration | Old Key | New Key |
|-------|----------|---------|---------|
| Generate | Immediate | Active | Created (inactive) |
| Grace Period | 24 hours | Active | Available for decrypt |
| Activate | After grace | Inactive | Active |
| Cleanup | 7 days | Deleted | Active |

### Implementation Pattern

```python
def rotate_encryption_key():
    """Rotate encryption key with grace period."""
    # 1. Generate new key
    new_key = Fernet.generate_key()
    new_key_id = generate_key_id()

    # 2. Store new key (inactive)
    store_key(new_key_id, new_key, is_active=False)

    # 3. Schedule activation (after grace period)
    schedule_key_activation(new_key_id, delay=timedelta(hours=24))

    # 4. Re-encrypt existing data (background job)
    schedule_reencryption(new_key_id)

    return new_key_id
```

## Go Environment Secrets

### Config from Environment

```go
func getEnvString(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}

// Usage - never log default values
apiKey := getEnvString("API_KEY", "")
if apiKey == "" {
    log.Fatal("API_KEY environment variable required")
}
```

### In-Cluster Authentication

```go
// K8s automatically mounts service account token
// at /var/run/secrets/kubernetes.io/serviceaccount/token
config, err := rest.InClusterConfig()
if err != nil {
    // Fallback to kubeconfig for local dev
    config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
}
```

## Workflow

### Step 1: Generate Encryption Key

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(f"Add to config: {key.decode()}")
# Store in environment or config file, NOT in code
```

### Step 2: Configure Key Storage

```python
# Option A: Environment variable
export ENCRYPTION_KEY="your-32-byte-key-here..."

# Option B: Odoo config parameter
self.env['ir.config_parameter'].sudo().set_param(
    'instance_manager.encryption_key', key.decode()
)
```

### Step 3: Encrypt Sensitive Data

```python
def create_credentials(self, vals):
    """Encrypt credentials before storage."""
    vals['db_password_encrypted'] = self._encrypt(vals.pop('db_password'))
    vals['admin_password_encrypted'] = self._encrypt(vals.pop('admin_password'))
    return super().create(vals)
```

### Step 4: Create K8s Secret

```python
def deploy_secrets(namespace: str, credentials: dict):
    """Deploy credentials as K8s secret."""
    create_secret(namespace, 'app-secrets', {
        'DB_HOST': credentials['db_host'],
        'DB_NAME': credentials['db_name'],
        'DB_PASSWORD': credentials['db_password'],
    })
```

## Examples

### Example 1: Encrypt Database Credentials

```python
class InstanceCredential(models.Model):
    _name = 'instance.credential'

    db_password_encrypted = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            password = self._generate_password()
            vals['db_password_encrypted'] = self._encrypt(password)
        return super().create(vals_list)

    def get_db_password(self):
        """Decrypt password for use."""
        return self._decrypt(self.db_password_encrypted)
```

### Example 2: Create Instance Secret in K8s

```python
def _create_instance_secrets(self, instance, namespace):
    """Create K8s secret for instance."""
    creds = instance.credential_id.get_credentials_dict()

    secret_data = {
        'DB_HOST': self.db_host,
        'DB_NAME': creds['db_name'],
        'DB_USER': creds['db_user'],
        'DB_PASSWORD': creds['db_password'],
        'ADMIN_PASSWORD': creds['admin_password'],
    }

    create_secret(namespace, 'odoo-secrets', secret_data)

    # Audit log (no values!)
    self._audit_log('create_secret', 'secret', 'odoo-secrets',
                   details={'keys': list(secret_data.keys())})
```

### Example 3: Webhook Token Verification

```python
from flask import request, jsonify
import hmac

@app.route('/webhook/alerts', methods=['POST'])
def handle_alerts():
    # Verify bearer token
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({'error': 'Missing token'}), 401

    token = auth[7:]
    expected = get_config('alertmanager_webhook_token')

    if not expected or not hmac.compare_digest(token, expected):
        _logger.warning("Invalid webhook token")
        return jsonify({'error': 'Invalid token'}), 401

    # Process alerts
    return process_alerts(request.json)
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Decryption failed | Wrong key | Verify key matches encryption key |
| Key format error | Not base64 | Ensure 32-byte key is base64 encoded |
| K8s 403 Forbidden | RBAC | Grant secrets access to service account |
| Timing attack | Using == | Use `hmac.compare_digest()` |
| Secret not found | Wrong namespace | Verify namespace matches |
| Base64 decode error | Double encoding | Check if using data vs stringData |
| Token rejected | Whitespace | Strip token before comparison |

## Output Checklist

After implementing secrets management:

- [ ] Encryption key stored outside code (env/config/vault)
- [ ] Development fallback logs warning
- [ ] Fernet used for symmetric encryption
- [ ] K8s secrets use stringData or proper base64
- [ ] Token comparison uses `hmac.compare_digest()`
- [ ] Passwords generated with `secrets` module
- [ ] Audit logs include key names, not values
- [ ] Key rotation strategy documented
- [ ] RBAC configured for secret access
- [ ] TLS secrets use `kubernetes.io/tls` type

## Related Resources

- **Fernet Encryption**: See `references/fernet-encryption.md`
- **Kubernetes Secrets**: See `references/kubernetes-secrets.md`
- **Token Patterns**: See `references/token-patterns.md`
