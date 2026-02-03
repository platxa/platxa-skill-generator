# Kubernetes Secrets Reference

Patterns for managing Kubernetes secrets in Platxa.

## Secret Types

| Type | Usage | Fields |
|------|-------|--------|
| `Opaque` | Generic secrets | Any key-value |
| `kubernetes.io/tls` | TLS certificates | `tls.crt`, `tls.key` |
| `kubernetes.io/dockerconfigjson` | Registry auth | `.dockerconfigjson` |

## Python Client Setup

```python
from kubernetes import client, config

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

core_v1 = client.CoreV1Api()
```

## Creating Secrets

### Using stringData (Recommended)

```python
def create_secret(namespace: str, name: str, data: dict) -> None:
    """Create secret with auto base64 encoding."""
    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(
            name=name, namespace=namespace,
            labels={'app.kubernetes.io/managed-by': 'platxa'}
        ),
        string_data=data,
        type='Opaque'
    )
    core_v1.create_namespaced_secret(namespace, secret)
```

### TLS Secret

```python
def create_tls_secret(namespace: str, name: str, cert: str, key: str) -> None:
    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        type='kubernetes.io/tls',
        string_data={'tls.crt': cert, 'tls.key': key}
    )
    core_v1.create_namespaced_secret(namespace, secret)
```

## Reading Secrets

```python
import base64

def read_secret(namespace: str, name: str) -> dict:
    """Read and decode secret data."""
    secret = core_v1.read_namespaced_secret(name, namespace)
    if not secret.data:
        return {}
    return {k: base64.b64decode(v).decode() for k, v in secret.data.items()}

def read_secret_key(namespace: str, name: str, key: str) -> str | None:
    """Read single key from secret."""
    try:
        secret = core_v1.read_namespaced_secret(name, namespace)
        if secret.data and key in secret.data:
            return base64.b64decode(secret.data[key]).decode()
    except client.ApiException as e:
        if e.status == 404:
            return None
        raise
    return None
```

## Updating Secrets

### Create or Update (Upsert)

```python
def create_or_update_secret(namespace: str, name: str, data: dict) -> None:
    """Create secret or update if exists."""
    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        string_data=data,
        type='Opaque'
    )
    try:
        core_v1.create_namespaced_secret(namespace, secret)
    except client.ApiException as e:
        if e.status == 409:
            existing = core_v1.read_namespaced_secret(name, namespace)
            secret.metadata.resource_version = existing.metadata.resource_version
            core_v1.replace_namespaced_secret(name, namespace, secret)
        else:
            raise
```

## Deleting Secrets

```python
def delete_secret(namespace: str, name: str) -> bool:
    try:
        core_v1.delete_namespaced_secret(name, namespace)
        return True
    except client.ApiException as e:
        if e.status == 404:
            return False
        raise
```

## Using Secrets in Pods

### Environment Variable

```yaml
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secrets
      key: password
```

### Mount as Volume

```yaml
volumes:
- name: secrets
  secret:
    secretName: db-secrets
volumeMounts:
- name: secrets
  mountPath: /etc/secrets
  readOnly: true
```

## RBAC for Secrets

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secret-reader
subjects:
- kind: ServiceAccount
  name: my-service
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

## Security Best Practices

1. **Namespace isolation** - Secrets are namespace-scoped
2. **RBAC** - Limit who can read/write secrets
3. **Enable encryption at rest** - Configure etcd encryption
4. **Avoid `get secrets *`** - Use specific names in RBAC
5. **Don't log secret data** - Only log metadata/key names
6. **Rotate secrets regularly** - Implement rotation strategy
