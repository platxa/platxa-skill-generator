# Logging Patterns Reference

Structured logging implementations across Platxa languages.

## Python Logging

### Module Setup

```python
import logging
import json
from datetime import datetime

# Module-level loggers
_logger = logging.getLogger(__name__)
_audit_logger = logging.getLogger('instance_manager.audit')

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log Levels

```python
# DEBUG - Detailed diagnostic information
_logger.debug(f"Connected to Kubernetes API: {api_server}")

# INFO - Normal operation confirmation
_logger.info(f"Namespace {namespace} created successfully")

# WARNING - Recoverable issue
_logger.warning(f"Template {template_name} not found, using default")

# ERROR - Operation failed but service continues
_logger.error(f"Failed to create user: {output}")

# ERROR with stack trace
_logger.error(f"Failed to process alert: {e}", exc_info=True)
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
        'user_name': self.env.user.name,
        'details': details,
    }

    # Log as JSON for structured parsing
    _audit_logger.info(json.dumps(log_entry))

    # Also persist to database
    self.env['instance.audit.log'].sudo().create({
        'action': action,
        'resource_type': resource_type,
        'resource_name': resource_name,
        'namespace': namespace,
        'result': result,
        'details': json.dumps(details) if details else None,
    })
```

### Audit Results

```python
# Success
self._audit_log(
    action='provision',
    resource_type='instance',
    resource_name=instance.name,
    result='success'
)

# Failure
self._audit_log(
    action='provision',
    result='failure',
    details={'error': str(e)}
)

# Denied
self._audit_log(
    action='delete',
    result='denied',
    details={'reason': 'Insufficient permissions'}
)
```

### Security: Never Log Secrets

```python
# WRONG - logs actual secret values
_logger.info(f"Created secret with data: {secret_data}")

# CORRECT - log only key names
self._audit_log(
    action='create_secret',
    details={'keys': list(secret_data.keys())}
)

# Example output: {"action": "create_secret", "details": {"keys": ["password", "token"]}}
```

## Go Structured Logging (slog)

### Logger Setup

```go
import (
    "log/slog"
    "os"
)

func Setup(level string, jsonFormat bool) {
    logLevel := parseLevel(level)
    opts := &slog.HandlerOptions{Level: logLevel}

    var handler slog.Handler
    if jsonFormat {
        handler = slog.NewJSONHandler(os.Stdout, opts)
    } else {
        handler = slog.NewTextHandler(os.Stdout, opts)
    }

    logger := slog.New(handler)
    slog.SetDefault(logger)
}

func parseLevel(level string) slog.Level {
    switch strings.ToLower(level) {
    case "debug":
        return slog.LevelDebug
    case "warn", "warning":
        return slog.LevelWarn
    case "error":
        return slog.LevelError
    default:
        return slog.LevelInfo
    }
}
```

### Consistent Field Keys

```go
// internal/logging/fields.go
const (
    KeyError      = "error"
    KeyErrorCode  = "error_code"
    KeySupportRef = "support_ref"
    KeyDurationMS = "duration_ms"
    KeyNamespace  = "namespace"
    KeyPath       = "path"
    KeyHost       = "host"
    KeyStatus     = "status"
)
```

### Log Levels

```go
// Debug - Detailed diagnostic
slog.Debug("checking pod status",
    "namespace", namespace,
    "pod", podName,
)

// Info - Normal operations
slog.Info("instance woke up",
    "namespace", namespace,
    KeyDurationMS, durationMs,
)

// Warn - Recoverable issues
slog.Warn("rate limit approaching",
    "namespace", namespace,
    "remaining", remaining,
)

// Error - Operation failed
slog.Error("scale-up failed",
    "namespace", namespace,
    KeyError, err,
)
```

### Error Logging with Context

```go
// Proxy error with request context
slog.Error("proxy error",
    KeyError, err,
    KeyPath, r.URL.Path,
    KeyHost, r.Host,
)

// K8s operation error
slog.Error("failed to get deployment",
    "namespace", namespace,
    "deployment", name,
    KeyError, err,
)

// Startup failure
slog.Error("failed to initialize components",
    KeyError, err,
)
```

### JSON Output Example

```json
{
  "time": "2024-01-15T10:30:45.123Z",
  "level": "ERROR",
  "msg": "scale-up failed",
  "namespace": "instance-abc123xy",
  "error": "timeout waiting for pod ready"
}
```

## TypeScript Logging

### Console Logging

```typescript
// Error with component stack
console.error('Monaco Editor Error:', error);
console.error('Component Stack:', errorInfo.componentStack);

// Warning for degraded operation
console.warn('Connection retry:', attempt, 'delay:', delay);

// Info for normal operations
console.info('Connected to WebSocket');

// Debug for development
console.debug('Received message:', JSON.stringify(message));
```

### Event-Based Logging

```typescript
export interface DebugEvent {
  type: EventType;
  timestamp: Date;
  sessionId: string;
  data: unknown;
}

type EventType =
  | 'session_started'
  | 'error_parsed'
  | 'fix_suggested'
  | 'error';

class Orchestrator {
  private eventListeners = new Set<EventListener>();

  on(listener: EventListener): () => void {
    this.eventListeners.add(listener);
    return () => this.eventListeners.delete(listener);
  }

  private emit(event: DebugEvent): void {
    for (const listener of this.eventListeners) {
      try {
        listener(event);
      } catch (error) {
        // Fail-safe: don't let listener errors break others
        console.error('Event listener error:', error);
      }
    }
  }

  private log(message: string, data?: unknown): void {
    console.log(`[Orchestrator] ${message}`, data ?? '');
  }
}
```

### Structured Error Logging

```typescript
function logError(error: NormalizedError): void {
  const entry = {
    timestamp: error.timestamp.toISOString(),
    type: error.type,
    message: error.message,
    severity: error.severity,
    source: error.source,
    location: error.location ? {
      file: error.location.file,
      line: error.location.line,
      column: error.location.column,
    } : undefined,
    code: error.code,
  };

  console.error(JSON.stringify(entry));
}
```

## Log Level Guidelines

| Level | When to Use | Example |
|-------|-------------|---------|
| DEBUG | Detailed diagnostic info | Connection params, state changes |
| INFO | Normal operation confirmations | "Instance started", "Request completed" |
| WARN | Recoverable issues | "Retry in progress", "Rate limit near" |
| ERROR | Operation failures | "Failed to connect", "Validation failed" |

## What to Log

### Always Include

```python
# Correlation context
log_entry = {
    'timestamp': datetime.now().isoformat(),
    'request_id': request_id,
    'user_id': user_id,
    'action': action,
    'resource': resource,
    'result': result,
}
```

### Never Include

```python
# NEVER log these:
# - Passwords
# - API keys/tokens
# - Session secrets
# - PII (personally identifiable information)
# - Credit card numbers
# - Private keys

# BAD
_logger.info(f"Auth with token: {token}")

# GOOD
_logger.info(f"Auth attempt for user: {user_id}")
```

## Log Format Standards

### JSON (Production)

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "ERROR",
  "logger": "instance_manager.security",
  "message": "Permission denied",
  "context": {
    "user_id": 123,
    "action": "delete",
    "resource": "instance-abc123xy"
  }
}
```

### Text (Development)

```
2024-01-15 10:30:45,123 - instance_manager.security - ERROR - Permission denied user_id=123 action=delete resource=instance-abc123xy
```

## Integration with Observability

### Loki Labels (for log querying)

```yaml
# Kubernetes metadata added by Fluent Bit
namespace: instance-abc123xy
container: odoo
pod: odoo-abc123xy-7f8b9c
app: odoo
```

### Correlation with Metrics

```go
// Log with same labels as Prometheus metrics
slog.Info("request completed",
    "namespace", namespace,
    "duration_ms", durationMs,
    "status", status,
)

// Can correlate with:
// http_request_duration_seconds{namespace="instance-abc123xy", status="200"}
```
