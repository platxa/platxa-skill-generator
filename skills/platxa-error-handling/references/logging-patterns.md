# Logging Patterns Reference

Structured logging implementations across Platxa languages.

## Python Logging

### Module Setup

```python
import logging
import json
from datetime import datetime

_logger = logging.getLogger(__name__)
_audit_logger = logging.getLogger('instance_manager.audit')
```

### Log Levels

```python
_logger.debug(f"Connected to API: {api_server}")
_logger.info(f"Namespace {namespace} created")
_logger.warning(f"Template not found, using default")
_logger.error(f"Failed to create user: {output}")
_logger.error(f"Failed: {e}", exc_info=True)  # With stack trace
```

### Structured Audit Logging

```python
def _audit_log(self, action, resource_type, resource_name,
               namespace=None, result='success', details=None):
    """Create structured audit log entry."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'resource_type': resource_type,
        'resource_name': resource_name,
        'namespace': namespace,
        'result': result,
        'user_id': self.env.user.id,
        'details': details,
    }
    _audit_logger.info(json.dumps(log_entry))
```

### Security: Never Log Secrets

```python
# WRONG
_logger.info(f"Created secret with data: {secret_data}")

# CORRECT - log only key names
self._audit_log('create_secret', details={'keys': list(secret_data.keys())})
```

## Go slog

### Logger Setup

```go
func Setup(level string, jsonFormat bool) {
    opts := &slog.HandlerOptions{Level: parseLevel(level)}
    var handler slog.Handler
    if jsonFormat {
        handler = slog.NewJSONHandler(os.Stdout, opts)
    } else {
        handler = slog.NewTextHandler(os.Stdout, opts)
    }
    slog.SetDefault(slog.New(handler))
}
```

### Consistent Field Keys

```go
const (
    KeyError      = "error"
    KeyDurationMS = "duration_ms"
    KeyNamespace  = "namespace"
    KeyStatus     = "status"
)
```

### Log Levels

```go
slog.Debug("checking pod", "namespace", namespace)
slog.Info("instance woke", KeyNamespace, namespace, KeyDurationMS, ms)
slog.Warn("rate limit approaching", "remaining", remaining)
slog.Error("scale-up failed", KeyNamespace, namespace, KeyError, err)
```

## TypeScript Logging

### Console Logging

```typescript
console.error('Monaco Error:', error);
console.warn('Connection retry:', attempt);
console.info('Connected to WebSocket');
console.debug('Message:', JSON.stringify(message));
```

### Structured Error Logging

```typescript
function logError(error: NormalizedError): void {
  const entry = {
    timestamp: error.timestamp.toISOString(),
    type: error.type,
    message: error.message,
    severity: error.severity,
    location: error.location,
  };
  console.error(JSON.stringify(entry));
}
```

## Log Level Guidelines

| Level | When to Use | Example |
|-------|-------------|---------|
| DEBUG | Diagnostic info | Connection params |
| INFO | Normal operations | "Instance started" |
| WARN | Recoverable issues | "Retry in progress" |
| ERROR | Operation failures | "Failed to connect" |

## What to Log

### Always Include

```python
log_entry = {
    'timestamp': datetime.now().isoformat(),
    'request_id': request_id,
    'user_id': user_id,
    'action': action,
    'result': result,
}
```

### Never Include

- Passwords, API keys/tokens
- Session secrets, PII
- Credit card numbers, Private keys

## JSON Format (Production)

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "ERROR",
  "message": "Permission denied",
  "context": {
    "user_id": 123,
    "action": "delete"
  }
}
```

## Correlation with Metrics

```go
slog.Info("request completed",
    "namespace", namespace,
    "duration_ms", durationMs,
    "status", status,
)
// Correlates with: http_request_duration_seconds{namespace="..."}
```
