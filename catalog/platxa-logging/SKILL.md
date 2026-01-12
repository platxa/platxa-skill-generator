---
name: platxa-logging
description: Structured logging and correlation ID patterns for Platxa services. Covers Python logging, Go slog, TypeScript console patterns, and request tracing across microservices.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - guide
    - logging
    - correlation-ids
    - observability
---

# Platxa Logging

Guide for structured logging and correlation ID patterns across Platxa services.

## Overview

| Language | Logger | Correlation | Output Format |
|----------|--------|-------------|---------------|
| **Python** | logging module | ContextVar | JSON (audit) |
| **TypeScript** | Console | Session ID | Text/JSON |
| **Go** | log/slog | context.Context | JSON |

## Core Principles

1. **Structured Over Unstructured**: JSON format for machine parsing and log aggregation
2. **Correlation Required**: Every request gets a unique ID, propagated across all services
3. **Context Propagation**: Thread/goroutine-safe context passing
4. **Consistent Field Keys**: Standardized keys across all languages
5. **Log Levels by Impact**: ERROR=failed, WARN=degraded, INFO=normal, DEBUG=diagnostic

## Standard Field Keys

| Key | Type | Description |
|-----|------|-------------|
| `timestamp` | ISO8601 | When event occurred |
| `level` | string | error/warn/info/debug |
| `message` | string | Human-readable description |
| `request_id` | string | Correlation ID (UUID) |
| `namespace` | string | K8s namespace (instance-xxx) |
| `service` | string | Service name |
| `duration_ms` | int | Operation duration in milliseconds |
| `error` | string | Error message (if any) |
| `user_id` | int | User identifier (if authenticated) |

## Correlation ID Patterns

### HTTP Header Propagation

```
Client → Service A → Service B → Service C
         │            │            │
         └─ X-Request-ID: abc123 ─┘
```

**Header Name**: `X-Request-ID` (primary) or `X-Correlation-ID`

### Generation Rules

1. **At Service Boundary**: Generate if header missing
2. **Format**: UUID v4 (`550e8400-e29b-41d4-a716-446655440000`)
3. **Propagate**: Include in all downstream requests
4. **Log**: Include in every log entry

### Python Implementation

```python
import uuid
from contextvars import ContextVar

# Thread-safe storage
request_id: ContextVar[str] = ContextVar('request_id', default='')

def get_request_id() -> str:
    """Get current request ID or generate new one."""
    rid = request_id.get()
    return rid if rid else str(uuid.uuid4())

def set_request_id(rid: str) -> None:
    """Set request ID for current context."""
    request_id.set(rid)

# Flask/Werkzeug middleware
@app.before_request
def extract_request_id():
    rid = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    set_request_id(rid)
    g.request_id = rid

@app.after_request
def add_request_id_header(response):
    response.headers['X-Request-ID'] = get_request_id()
    return response
```

### Go Implementation

```go
type contextKey string

const RequestIDKey contextKey = "request_id"

func RequestIDMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        reqID := r.Header.Get("X-Request-ID")
        if reqID == "" {
            reqID = uuid.New().String()
        }
        ctx := context.WithValue(r.Context(), RequestIDKey, reqID)
        w.Header().Set("X-Request-ID", reqID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

func GetRequestID(ctx context.Context) string {
    if reqID, ok := ctx.Value(RequestIDKey).(string); ok {
        return reqID
    }
    return ""
}
```

### TypeScript Implementation

```typescript
import { v4 as uuidv4 } from 'uuid';

interface RequestContext {
  requestId: string;
  sessionId: string;
  userId?: string;
}

// Express middleware
function requestIdMiddleware(req: Request, res: Response, next: NextFunction) {
  const requestId = req.headers['x-request-id'] as string || uuidv4();
  req.context = { requestId, sessionId: req.sessionID };
  res.setHeader('X-Request-ID', requestId);
  next();
}

// Fetch wrapper for downstream calls
async function fetchWithCorrelation(url: string, ctx: RequestContext, options = {}) {
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'X-Request-ID': ctx.requestId,
    },
  });
}
```

## Structured Logging

### JSON Output Format

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "info",
  "message": "request completed",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "namespace": "instance-abc123xy",
  "service": "waking-service",
  "duration_ms": 45,
  "method": "GET",
  "path": "/api/status",
  "status": 200
}
```

### Python Structured Logger

```python
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """JSON formatter with correlation ID."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname.lower(),
            'message': record.getMessage(),
            'logger': record.name,
            'request_id': get_request_id(),
        }

        # Add extra fields
        if hasattr(record, 'namespace'):
            log_entry['namespace'] = record.namespace
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

# Setup
handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logging.root.addHandler(handler)
```

### Go slog Setup

```go
import (
    "log/slog"
    "os"
)

// Field key constants
const (
    KeyRequestID  = "request_id"
    KeyNamespace  = "namespace"
    KeyDurationMS = "duration_ms"
    KeyError      = "error"
    KeyService    = "service"
)

func SetupLogger(level string, jsonFormat bool) {
    opts := &slog.HandlerOptions{Level: parseLevel(level)}

    var handler slog.Handler
    if jsonFormat {
        handler = slog.NewJSONHandler(os.Stdout, opts)
    } else {
        handler = slog.NewTextHandler(os.Stdout, opts)
    }

    slog.SetDefault(slog.New(handler))
}

// Usage with context
func LogWithContext(ctx context.Context, msg string, args ...any) {
    allArgs := append([]any{KeyRequestID, GetRequestID(ctx)}, args...)
    slog.Info(msg, allArgs...)
}
```

### TypeScript Logger

```typescript
interface LogEntry {
  timestamp: string;
  level: 'error' | 'warn' | 'info' | 'debug';
  message: string;
  requestId?: string;
  [key: string]: unknown;
}

class StructuredLogger {
  constructor(private service: string, private context?: RequestContext) {}

  private log(level: LogEntry['level'], message: string, data?: Record<string, unknown>) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      service: this.service,
      requestId: this.context?.requestId,
      ...data,
    };

    if (level === 'error') {
      console.error(JSON.stringify(entry));
    } else {
      console.log(JSON.stringify(entry));
    }
  }

  info(message: string, data?: Record<string, unknown>) { this.log('info', message, data); }
  warn(message: string, data?: Record<string, unknown>) { this.log('warn', message, data); }
  error(message: string, data?: Record<string, unknown>) { this.log('error', message, data); }
  debug(message: string, data?: Record<string, unknown>) { this.log('debug', message, data); }
}
```

## Log Level Guidelines

| Level | When to Use | Example |
|-------|-------------|---------|
| ERROR | Operation failed, requires attention | `"database connection failed"` |
| WARN | Degraded but working, potential issue | `"rate limit at 80%"` |
| INFO | Normal operation, significant events | `"instance started"` |
| DEBUG | Diagnostic detail, development | `"parsing config file"` |

### Dynamic Log Levels (Go)

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        wrapped := &responseWriter{ResponseWriter: w}

        next.ServeHTTP(wrapped, r)

        // Dynamic level based on status
        level := slog.LevelInfo
        if wrapped.statusCode >= 500 {
            level = slog.LevelError
        } else if wrapped.statusCode >= 400 {
            level = slog.LevelWarn
        }

        slog.Log(r.Context(), level, "http request",
            KeyRequestID, GetRequestID(r.Context()),
            "method", r.Method,
            "path", r.URL.Path,
            "status", wrapped.statusCode,
            KeyDurationMS, time.Since(start).Milliseconds(),
        )
    })
}
```

## Workflow

### Step 1: Add Correlation ID Middleware

| Language | Implementation |
|----------|----------------|
| Python | Flask `@app.before_request` with ContextVar |
| Go | `RequestIDMiddleware` with context.Context |
| TypeScript | Express middleware with request augmentation |

### Step 2: Configure Structured Logger

1. Create JSON formatter
2. Add request ID to all log entries
3. Define standard field keys
4. Set appropriate log levels

### Step 3: Propagate to Downstream Services

```python
# Python - httpx/requests
response = requests.post(url, headers={'X-Request-ID': get_request_id()})

# Go - http.Client
req.Header.Set("X-Request-ID", GetRequestID(ctx))

# TypeScript - fetch
fetch(url, { headers: { 'X-Request-ID': context.requestId } })
```

### Step 4: Query Logs by Correlation ID

```bash
# Loki query
{namespace="instance-abc123"} |= "request_id=550e8400"

# grep
grep "550e8400" /var/log/service/*.log
```

## Examples

### Example 1: Python API with Correlation

```python
import logging
from flask import Flask, request, g

app = Flask(__name__)
_logger = logging.getLogger(__name__)

@app.before_request
def setup_correlation():
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    set_request_id(g.request_id)

@app.route('/api/provision', methods=['POST'])
def provision():
    _logger.info("Provisioning instance", extra={
        'namespace': request.json.get('namespace'),
        'action': 'provision'
    })

    # Call downstream service
    response = requests.post(
        f"{VALIDATOR_URL}/validate",
        headers={'X-Request-ID': g.request_id},
        json=request.json
    )

    return jsonify({'status': 'ok'})
```

### Example 2: Go Service Handler

```go
func (h *Handler) HandleWake(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    namespace := chi.URLParam(r, "namespace")

    slog.Info("wake request received",
        KeyRequestID, GetRequestID(ctx),
        KeyNamespace, namespace,
    )

    start := time.Now()
    err := h.scaler.WakeInstance(ctx, namespace)

    if err != nil {
        slog.Error("wake failed",
            KeyRequestID, GetRequestID(ctx),
            KeyNamespace, namespace,
            KeyError, err,
            KeyDurationMS, time.Since(start).Milliseconds(),
        )
        http.Error(w, "Failed to wake instance", http.StatusServiceUnavailable)
        return
    }

    slog.Info("wake completed",
        KeyRequestID, GetRequestID(ctx),
        KeyNamespace, namespace,
        KeyDurationMS, time.Since(start).Milliseconds(),
    )

    w.WriteHeader(http.StatusOK)
}
```

### Example 3: Audit Logging (Python)

```python
_audit_logger = logging.getLogger('instance_manager.audit')

def _audit_log(self, action: str, resource_type: str, resource_name: str,
               result: str = 'success', details: dict = None):
    """Create structured audit log entry."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'request_id': get_request_id(),
        'action': action,
        'resource_type': resource_type,
        'resource_name': resource_name,
        'result': result,
        'user_id': self.env.user.id,
        'user_name': self.env.user.name,
        'details': details,  # Never include secrets!
    }
    _audit_logger.info(json.dumps(log_entry))
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Missing request ID | Middleware not installed | Add correlation middleware first |
| ID not propagating | Forgot header in downstream call | Add X-Request-ID to all requests |
| Duplicate IDs | Generating instead of reusing | Check header before generating |
| Lost context (Python) | Thread boundary | Use ContextVar, not threading.local |
| Lost context (Go) | Not passing ctx | Always pass context.Context |
| JSON parse errors | Non-JSON in logs | Ensure all loggers use JSON formatter |
| Missing fields | Not using extra/attrs | Add fields via extra (Python) or args (Go) |

## Output Checklist

After implementing logging:

- [ ] Correlation ID middleware installed
- [ ] All log entries include request_id
- [ ] JSON format for production logs
- [ ] Standard field keys used consistently
- [ ] Downstream calls propagate X-Request-ID
- [ ] Log levels match severity guidelines
- [ ] Audit logs include user context
- [ ] No secrets in log output
- [ ] Logs queryable by correlation ID

## Related Resources

- **Correlation IDs**: See `references/correlation-ids.md`
- **Structured Logging**: See `references/structured-logging.md`
- **Language Patterns**: See `references/language-patterns.md`
