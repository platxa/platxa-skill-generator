# Structured Logging Reference

JSON-based logging patterns for Platxa services.

## Why Structured Logging?

| Aspect | Unstructured | Structured |
|--------|--------------|------------|
| Format | `"Error: failed to connect"` | `{"level":"error","message":"failed to connect"}` |
| Parsing | Regex, brittle | JSON, reliable |
| Querying | Text search | Field queries |
| Aggregation | Difficult | Native support |
| Alerting | Pattern matching | Field-based rules |

## Standard JSON Schema

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "info",
  "message": "request completed",
  "service": "waking-service",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "namespace": "instance-abc123xy",
  "duration_ms": 45,
  "method": "GET",
  "path": "/api/status",
  "status": 200
}
```

## Field Standards

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO8601 with timezone | `"2024-01-15T10:30:45.123Z"` |
| `level` | string | Log level | `"info"`, `"error"` |
| `message` | string | Human-readable | `"request completed"` |

### Recommended Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `service` | string | Service name | `"waking-service"` |
| `request_id` | string | Correlation ID | `"550e8400..."` |
| `namespace` | string | K8s namespace | `"instance-abc123xy"` |
| `duration_ms` | int | Operation time | `45` |
| `error` | string | Error message | `"connection refused"` |
| `user_id` | int | Authenticated user | `123` |

### HTTP Request Fields

| Field | Type | Description |
|-------|------|-------------|
| `method` | string | HTTP method |
| `path` | string | Request path |
| `status` | int | Response status code |
| `client_ip` | string | Client IP address |
| `user_agent` | string | User-Agent header |

## Python Implementation

### Custom JSON Formatter

```python
import logging
import json
from datetime import datetime, timezone
from typing import Any

class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter."""

    def __init__(self, service_name: str = "unknown"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname.lower(),
            'message': record.getMessage(),
            'service': self.service_name,
            'logger': record.name,
        }

        # Add correlation ID if available
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        else:
            from correlation import get_request_id
            rid = get_request_id()
            if rid:
                log_entry['request_id'] = rid

        # Add extra fields from record
        for key in ['namespace', 'duration_ms', 'user_id', 'action']:
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        # Add exception info
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info),
            }

        return json.dumps(log_entry, default=str)

# Setup
def setup_logging(service_name: str, level: str = 'INFO'):
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter(service_name))

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    root.handlers = [handler]
```

### Logger with Context

```python
class ContextLogger:
    """Logger that automatically includes context."""

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def _log(self, level: int, message: str, **kwargs):
        extra = kwargs.copy()
        extra['request_id'] = get_request_id()
        self._logger.log(level, message, extra=extra)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)

# Usage
logger = ContextLogger(__name__)
logger.info("Instance provisioned", namespace="instance-abc123", duration_ms=1500)
```

## Go slog Implementation

### Logger Setup

```go
package logging

import (
    "log/slog"
    "os"
    "strings"
)

// Field key constants for consistency
const (
    KeyTimestamp  = "timestamp"
    KeyLevel      = "level"
    KeyMessage    = "msg"
    KeyService    = "service"
    KeyRequestID  = "request_id"
    KeyNamespace  = "namespace"
    KeyDurationMS = "duration_ms"
    KeyError      = "error"
    KeyErrorCode  = "error_code"
    KeyUserID     = "user_id"
    KeyMethod     = "method"
    KeyPath       = "path"
    KeyStatus     = "status"
)

func Setup(service, level string, jsonFormat bool) {
    logLevel := parseLevel(level)
    opts := &slog.HandlerOptions{Level: logLevel}

    var handler slog.Handler
    if jsonFormat {
        handler = slog.NewJSONHandler(os.Stdout, opts)
    } else {
        handler = slog.NewTextHandler(os.Stdout, opts)
    }

    // Add service name to all logs
    logger := slog.New(handler).With(KeyService, service)
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

### Context-Aware Logging

```go
package logging

import (
    "context"
    "log/slog"
    "your-project/internal/correlation"
)

// InfoCtx logs at INFO level with context
func InfoCtx(ctx context.Context, msg string, args ...any) {
    args = prependRequestID(ctx, args)
    slog.Info(msg, args...)
}

// ErrorCtx logs at ERROR level with context
func ErrorCtx(ctx context.Context, msg string, args ...any) {
    args = prependRequestID(ctx, args)
    slog.Error(msg, args...)
}

// WarnCtx logs at WARN level with context
func WarnCtx(ctx context.Context, msg string, args ...any) {
    args = prependRequestID(ctx, args)
    slog.Warn(msg, args...)
}

func prependRequestID(ctx context.Context, args []any) []any {
    reqID := correlation.GetRequestID(ctx)
    if reqID != "" {
        return append([]any{KeyRequestID, reqID}, args...)
    }
    return args
}

// Usage
func HandleRequest(ctx context.Context) {
    logging.InfoCtx(ctx, "processing request",
        KeyNamespace, "instance-abc123",
        KeyMethod, "POST",
    )
}
```

### HTTP Middleware Logging

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Skip health checks
        if r.URL.Path == "/health" || r.URL.Path == "/ready" {
            next.ServeHTTP(w, r)
            return
        }

        start := time.Now()
        wrapped := &responseWriter{ResponseWriter: w, statusCode: 200}

        next.ServeHTTP(wrapped, r)

        duration := time.Since(start)

        // Dynamic log level based on status
        level := slog.LevelInfo
        if wrapped.statusCode >= 500 {
            level = slog.LevelError
        } else if wrapped.statusCode >= 400 {
            level = slog.LevelWarn
        }

        slog.Log(r.Context(), level, "http request",
            KeyRequestID, correlation.GetRequestID(r.Context()),
            KeyMethod, r.Method,
            KeyPath, r.URL.Path,
            KeyStatus, wrapped.statusCode,
            KeyDurationMS, duration.Milliseconds(),
        )
    })
}
```

## TypeScript Implementation

### Logger Class

```typescript
type LogLevel = 'error' | 'warn' | 'info' | 'debug';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  service: string;
  request_id?: string;
  [key: string]: unknown;
}

class StructuredLogger {
  constructor(
    private service: string,
    private getRequestId?: () => string | undefined
  ) {}

  private formatEntry(level: LogLevel, message: string, data?: Record<string, unknown>): string {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      service: this.service,
      request_id: this.getRequestId?.(),
      ...data,
    };

    // Remove undefined values
    Object.keys(entry).forEach(key => {
      if (entry[key] === undefined) {
        delete entry[key];
      }
    });

    return JSON.stringify(entry);
  }

  error(message: string, data?: Record<string, unknown>): void {
    console.error(this.formatEntry('error', message, data));
  }

  warn(message: string, data?: Record<string, unknown>): void {
    console.warn(this.formatEntry('warn', message, data));
  }

  info(message: string, data?: Record<string, unknown>): void {
    console.log(this.formatEntry('info', message, data));
  }

  debug(message: string, data?: Record<string, unknown>): void {
    if (process.env.LOG_LEVEL === 'debug') {
      console.debug(this.formatEntry('debug', message, data));
    }
  }
}

// Usage
const logger = new StructuredLogger('editor-sync', () => getCurrentRequestId());
logger.info('file saved', { path: '/src/main.py', size: 1024 });
```

### Express Request Logger

```typescript
import { Request, Response, NextFunction } from 'express';

export function requestLogger(logger: StructuredLogger) {
  return (req: Request, res: Response, next: NextFunction) => {
    const start = Date.now();

    res.on('finish', () => {
      const duration = Date.now() - start;
      const level = res.statusCode >= 500 ? 'error' :
                   res.statusCode >= 400 ? 'warn' : 'info';

      logger[level]('http request', {
        method: req.method,
        path: req.path,
        status: res.statusCode,
        duration_ms: duration,
        user_agent: req.headers['user-agent'],
      });
    });

    next();
  };
}
```

## Audit Logging

### Python Audit Logger

```python
import json
import logging
from datetime import datetime

_audit_logger = logging.getLogger('audit')

def audit_log(
    action: str,
    resource_type: str,
    resource_name: str,
    user_id: int,
    user_name: str,
    result: str = 'success',
    details: dict = None
):
    """Create structured audit log entry.

    IMPORTANT: Never include secrets in details!
    """
    log_entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'type': 'audit',
        'request_id': get_request_id(),
        'action': action,
        'resource_type': resource_type,
        'resource_name': resource_name,
        'user_id': user_id,
        'user_name': user_name,
        'result': result,
    }

    if details:
        # Sanitize - only include safe fields
        safe_details = {k: v for k, v in details.items()
                       if k not in ['password', 'token', 'secret', 'key']}
        log_entry['details'] = safe_details

    _audit_logger.info(json.dumps(log_entry))

# Usage
audit_log(
    action='provision',
    resource_type='instance',
    resource_name='my-instance',
    user_id=123,
    user_name='john@example.com',
    result='success',
    details={'template': 'odoo-17', 'region': 'eu-west-1'}
)
```

## Log Levels

### When to Use Each Level

| Level | Condition | Example |
|-------|-----------|---------|
| ERROR | Operation failed | Database connection failed |
| WARN | Degraded but functional | Rate limit at 80% |
| INFO | Normal operation milestone | Instance started |
| DEBUG | Diagnostic detail | Parsing config file |

### Level Configuration

```python
# Python
import os
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.root.setLevel(getattr(logging, log_level))
```

```go
// Go
level := os.Getenv("LOG_LEVEL")
if level == "" {
    level = "info"
}
logging.Setup("my-service", level, true)
```

```typescript
// TypeScript
const LOG_LEVEL = process.env.LOG_LEVEL || 'info';
```

## Performance Considerations

1. **Avoid string concatenation in logs**
   ```python
   # Bad - always creates string
   logger.debug(f"Processing {expensive_computation()}")

   # Good - only evaluates if debug enabled
   logger.debug("Processing %s", expensive_computation)
   ```

2. **Skip health check logging**
   ```go
   if r.URL.Path == "/health" {
       next.ServeHTTP(w, r)
       return
   }
   ```

3. **Buffer writes for high-volume**
   ```python
   handler = logging.handlers.MemoryHandler(
       capacity=1000,
       flushLevel=logging.ERROR
   )
   ```
