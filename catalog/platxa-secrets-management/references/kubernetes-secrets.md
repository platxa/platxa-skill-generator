# Kubernetes Secrets Reference

Detailed patterns for managing Kubernetes secrets in Platxa.

## Secret Types

| Type | Usage | Fields |
|------|-------|--------|
| `Opaque` | Generic secrets | Any key-value pairs |
| `kubernetes.io/tls` | TLS certificates | `tls.crt`, `tls.key` |
| `kubernetes.io/dockerconfigjson` | Docker registry auth | `.dockerconfigjson` |
| `kubernetes.io/basic-auth` | Basic authentication | `username`, `password` |
| `kubernetes.io/service-account-token` | Service account | Auto-managed by K8s |

## Python Client Setup

```python
from kubernetes import client, config

# In-cluster (pod running in K8s)
try:
    config.load_incluster_config()
except config.ConfigException:
    # Local development
    config.load_kube_config()

core_v1 = client.CoreV1Api()
```

## Creating Secrets

### Using stringData (Recommended)

```python
def create_secret(namespace: str, name: str, data: dict) -> None:
    """Create secret with auto base64 encoding."""
    core_v1 = client.CoreV1Api()

    secret = client.V1Secret(
        api_version='v1',
        kind='Secret',
        metadata=client.V1ObjectMeta(
            name=name,
            namespace=namespace,
            labels={
                'app.kubernetes.io/managed-by': 'platxa',
                'app.kubernetes.io/component': 'secrets'
            }
        ),
        string_data=data,  # Plain text - K8s encodes to base64
        type='Opaque'
    )

    core_v1.create_namespaced_secret(namespace, secret)
```

### Using data (Manual Base64)

```python
import base64

def create_secret_manual(namespace: str, name: str, data: dict) -> None:
    """Create secret with manual base64 encoding."""
    core_v1 = client.CoreV1Api()

    encoded_data = {
        key: base64.b64encode(value.encode()).decode()
        for key, value in data.items()
    }

    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        data=encoded_data,  # Pre-encoded base64
        type='Opaque'
    )

    core_v1.create_namespaced_secret(namespace, secret)
```

### TLS Secret

```python
def create_tls_secret(
    namespace: str,
    name: str,
    certificate: str,
    private_key: str
) -> None:
    """Create TLS secret for certificates."""
    core_v1 = client.CoreV1Api()

    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        type='kubernetes.io/tls',
        string_data={
            'tls.crt': certificate,
            'tls.key': private_key,
        }
    )

    core_v1.create_namespaced_secret(namespace, secret)
```

### Docker Registry Secret

```python
import json
import base64

def create_docker_registry_secret(
    namespace: str,
    name: str,
    server: str,
    username: str,
    password: str,
    email: str = ''
) -> None:
    """Create Docker registry pull secret."""
    core_v1 = client.CoreV1Api()

    # Docker config format
    docker_config = {
        'auths': {
            server: {
                'username': username,
                'password': password,
                'email': email,
                'auth': base64.b64encode(
                    f'{username}:{password}'.encode()
                ).decode()
            }
        }
    }

    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        type='kubernetes.io/dockerconfigjson',
        data={
            '.dockerconfigjson': base64.b64encode(
                json.dumps(docker_config).encode()
            ).decode()
        }
    )

    core_v1.create_namespaced_secret(namespace, secret)
```

## Reading Secrets

### Read and Decode

```python
import base64

def read_secret(namespace: str, name: str) -> dict:
    """Read and decode secret data."""
    core_v1 = client.CoreV1Api()

    secret = core_v1.read_namespaced_secret(name, namespace)

    if not secret.data:
        return {}

    return {
        key: base64.b64decode(value).decode()
        for key, value in secret.data.items()
    }
```

### Read Single Key

```python
def read_secret_key(namespace: str, name: str, key: str) -> str | None:
    """Read single key from secret."""
    core_v1 = client.CoreV1Api()

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

### Patch (Partial Update)

```python
def patch_secret(namespace: str, name: str, updates: dict) -> None:
    """Patch specific keys in secret."""
    core_v1 = client.CoreV1Api()

    encoded_updates = {
        key: base64.b64encode(value.encode()).decode()
        for key, value in updates.items()
    }

    core_v1.patch_namespaced_secret(
        name=name,
        namespace=namespace,
        body={'data': encoded_updates}
    )
```

### Replace (Full Update)

```python
def replace_secret(namespace: str, name: str, data: dict) -> None:
    """Replace entire secret data."""
    core_v1 = client.CoreV1Api()

    # Read existing to get resourceVersion
    existing = core_v1.read_namespaced_secret(name, namespace)

    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(
            name=name,
            namespace=namespace,
            resource_version=existing.metadata.resource_version
        ),
        string_data=data,
        type='Opaque'
    )

    core_v1.replace_namespaced_secret(name, namespace, secret)
```

### Create or Update (Upsert)

```python
def create_or_update_secret(namespace: str, name: str, data: dict) -> None:
    """Create secret or update if exists."""
    core_v1 = client.CoreV1Api()

    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=name, namespace=namespace),
        string_data=data,
        type='Opaque'
    )

    try:
        core_v1.create_namespaced_secret(namespace, secret)
    except client.ApiException as e:
        if e.status == 409:  # Already exists
            # Get resourceVersion for replace
            existing = core_v1.read_namespaced_secret(name, namespace)
            secret.metadata.resource_version = existing.metadata.resource_version
            core_v1.replace_namespaced_secret(name, namespace, secret)
        else:
            raise
```

## Copying Secrets

### Copy Between Namespaces

```python
def copy_secret(
    source_namespace: str,
    source_name: str,
    target_namespace: str,
    target_name: str = None
) -> None:
    """Copy secret from one namespace to another."""
    core_v1 = client.CoreV1Api()

    # Read source
    source = core_v1.read_namespaced_secret(source_name, source_namespace)

    # Create target
    target = client.V1Secret(
        metadata=client.V1ObjectMeta(
            name=target_name or source_name,
            namespace=target_namespace,
            labels=source.metadata.labels,
            annotations={
                'platxa.io/copied-from': f'{source_namespace}/{source_name}',
                **(source.metadata.annotations or {})
            }
        ),
        type=source.type,
        data=source.data  # Already base64
    )

    try:
        core_v1.create_namespaced_secret(target_namespace, target)
    except client.ApiException as e:
        if e.status == 409:
            # Replace if exists
            existing = core_v1.read_namespaced_secret(
                target_name or source_name, target_namespace
            )
            target.metadata.resource_version = existing.metadata.resource_version
            core_v1.replace_namespaced_secret(
                target_name or source_name, target_namespace, target
            )
        else:
            raise
```

## Deleting Secrets

```python
def delete_secret(namespace: str, name: str) -> bool:
    """Delete secret if exists."""
    core_v1 = client.CoreV1Api()

    try:
        core_v1.delete_namespaced_secret(name, namespace)
        return True
    except client.ApiException as e:
        if e.status == 404:
            return False
        raise
```

## Using Secrets in Pods

### Environment Variables from Secret

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secrets
          key: password
```

### All Keys as Environment

```yaml
spec:
  containers:
  - name: app
    envFrom:
    - secretRef:
        name: db-secrets
```

### Mount as Volume

```yaml
spec:
  containers:
  - name: app
    volumeMounts:
    - name: secrets
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secrets
    secret:
      secretName: db-secrets
```

## RBAC for Secrets

### Service Account with Secret Access

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: secret-reader
  namespace: my-namespace
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
  namespace: my-namespace
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secret-reader
  namespace: my-namespace
subjects:
- kind: ServiceAccount
  name: secret-reader
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

## Security Best Practices

1. **Namespace isolation** - Secrets are namespace-scoped
2. **RBAC** - Limit who can read/write secrets
3. **Enable encryption at rest** - Configure etcd encryption
4. **Avoid `get secrets *`** - Use specific secret names in RBAC
5. **Don't log secret data** - Only log metadata/key names
6. **Use External Secrets Operator** - For production (Vault, AWS SM)
7. **Rotate secrets regularly** - Implement rotation strategy
