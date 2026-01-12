# Structured Logging Reference

JSON-based logging patterns for Platxa services.

## Standard JSON Schema

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "info",
  "message": "request completed",
  "service": "waking-service",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "namespace": "instance-abc123xy",
  "duration_ms": 45
}
```

## Field Standards

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO8601 with timezone |
| `level` | string | error/warn/info/debug |
| `message` | string | Human-readable |

### Recommended Fields

| Field | Type | Description |
|-------|------|-------------|
| `service` | string | Service name |
| `request_id` | string | Correlation ID |
| `namespace` | string | K8s namespace |
| `duration_ms` | int | Operation time |
| `error` | string | Error message |

## Python Implementation

```python
import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def __init__(self, service_name: str = "unknown"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname.lower(),
            'message': record.getMessage(),
            'service': self.service_name,
        }
        if hasattr(record, 'request_id'):
            entry['request_id'] = record.request_id
        for key in ['namespace', 'duration_ms', 'user_id']:
            if hasattr(record, key):
                entry[key] = getattr(record, key)
        if record.exc_info:
            entry['exception'] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)

def setup_logging(service_name: str, level: str = 'INFO'):
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter(service_name))
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    root.handlers = [handler]
```

## Go slog Implementation

```go
const (
    KeyRequestID  = "request_id"
    KeyNamespace  = "namespace"
    KeyDurationMS = "duration_ms"
    KeyError      = "error"
)

func Setup(service, level string, jsonFormat bool) {
    opts := &slog.HandlerOptions{Level: parseLevel(level)}
    var handler slog.Handler
    if jsonFormat {
        handler = slog.NewJSONHandler(os.Stdout, opts)
    } else {
        handler = slog.NewTextHandler(os.Stdout, opts)
    }
    slog.SetDefault(slog.New(handler).With("service", service))
}

func InfoCtx(ctx context.Context, msg string, args ...any) {
    args = append([]any{KeyRequestID, GetRequestID(ctx)}, args...)
    slog.Info(msg, args...)
}
```

### HTTP Middleware

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.URL.Path == "/health" {
            next.ServeHTTP(w, r)
            return
        }
        start := time.Now()
        wrapped := &responseWriter{ResponseWriter: w, statusCode: 200}
        next.ServeHTTP(wrapped, r)

        level := slog.LevelInfo
        if wrapped.statusCode >= 500 {
            level = slog.LevelError
        } else if wrapped.statusCode >= 400 {
            level = slog.LevelWarn
        }
        slog.Log(r.Context(), level, "http request",
            KeyRequestID, GetRequestID(r.Context()),
            "method", r.Method,
            "status", wrapped.statusCode,
            KeyDurationMS, time.Since(start).Milliseconds(),
        )
    })
}
```

## TypeScript Implementation

```typescript
type LogLevel = 'error' | 'warn' | 'info' | 'debug';

class StructuredLogger {
  constructor(private service: string, private getRequestId?: () => string) {}

  private formatEntry(level: LogLevel, message: string, data?: Record<string, unknown>): string {
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      level,
      message,
      service: this.service,
      request_id: this.getRequestId?.(),
      ...data,
    });
  }

  error(message: string, data?: Record<string, unknown>): void {
    console.error(this.formatEntry('error', message, data));
  }
  info(message: string, data?: Record<string, unknown>): void {
    console.log(this.formatEntry('info', message, data));
  }
}
```

## Audit Logging

```python
def audit_log(action: str, resource_type: str, resource_name: str,
              user_id: int, result: str = 'success', details: dict = None):
    """IMPORTANT: Never include secrets in details!"""
    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'type': 'audit',
        'action': action,
        'resource_type': resource_type,
        'resource_name': resource_name,
        'user_id': user_id,
        'result': result,
    }
    if details:
        safe = {k: v for k, v in details.items()
                if k not in ['password', 'token', 'secret']}
        entry['details'] = safe
    _audit_logger.info(json.dumps(entry))
```

## Log Levels

| Level | Condition | Example |
|-------|-----------|---------|
| ERROR | Operation failed | Database connection failed |
| WARN | Degraded but functional | Rate limit at 80% |
| INFO | Normal milestone | Instance started |
| DEBUG | Diagnostic detail | Parsing config |
