# Language-Specific Logging Patterns

Patterns for Python, TypeScript, and Go logging in Platxa.

## Python Patterns

### Module Logger Setup

```python
import logging

_logger = logging.getLogger(__name__)
_audit_logger = logging.getLogger('instance_manager.audit')
```

### Timing Decorator

```python
import time
import functools

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            _logger.info(f"{func.__name__} completed",
                extra={'duration_ms': int((time.perf_counter() - start) * 1000)})
            return result
        except Exception as e:
            _logger.error(f"{func.__name__} failed: {e}", exc_info=True)
            raise
    return wrapper
```

### Exception Logging

```python
try:
    result = risky_operation()
except ValueError as e:
    _logger.error("Validation failed: %s", e, exc_info=True)
    raise
except Exception as e:
    _logger.exception("Unexpected error")
    raise RuntimeError(f"Operation failed: {e}") from e
```

### Flask Integration

```python
@app.before_request
def setup_request_logging():
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    g.start_time = time.perf_counter()

@app.after_request
def log_response(response):
    duration_ms = (time.perf_counter() - g.start_time) * 1000
    _logger.info("Request completed", extra={
        'method': request.method, 'path': request.path,
        'status': response.status_code, 'duration_ms': int(duration_ms)
    })
    return response
```

## Go Patterns

### Package Structure

```go
package logging

import "log/slog"

func Init(service, level string, json bool) {
    opts := &slog.HandlerOptions{Level: parseLevel(level)}
    var handler slog.Handler
    if json {
        handler = slog.NewJSONHandler(os.Stdout, opts)
    } else {
        handler = slog.NewTextHandler(os.Stdout, opts)
    }
    slog.SetDefault(slog.New(handler).With("service", service))
}
```

### Field Constants

```go
const (
    KeyRequestID  = "request_id"
    KeyNamespace  = "namespace"
    KeyDurationMS = "duration_ms"
    KeyError      = "error"
)
```

### HTTP Handler Logging

```go
func (h *Handler) Wake(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    namespace := chi.URLParam(r, "namespace")
    start := time.Now()

    err := h.scaler.Wake(ctx, namespace)

    if err != nil {
        slog.ErrorContext(ctx, "wake failed",
            KeyRequestID, GetRequestID(ctx),
            KeyNamespace, namespace,
            KeyError, err.Error(),
            KeyDurationMS, time.Since(start).Milliseconds())
        http.Error(w, "Wake failed", http.StatusServiceUnavailable)
        return
    }

    slog.InfoContext(ctx, "wake completed",
        KeyRequestID, GetRequestID(ctx),
        KeyDurationMS, time.Since(start).Milliseconds())
    w.WriteHeader(http.StatusOK)
}
```

### Health Check Skip

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.URL.Path == "/health" || r.URL.Path == "/ready" {
            next.ServeHTTP(w, r)
            return
        }
        // ... logging logic
    })
}
```

## TypeScript Patterns

### Logger Class

```typescript
type LogLevel = 'error' | 'warn' | 'info' | 'debug';

class Logger {
  constructor(private service: string, private json: boolean = true) {}

  private format(level: LogLevel, message: string, data?: Record<string, unknown>) {
    if (this.json) {
      return JSON.stringify({
        timestamp: new Date().toISOString(), level, service: this.service, message, ...data
      });
    }
    return `[${new Date().toISOString()}] ${level.toUpperCase()} ${this.service}: ${message}`;
  }

  error(message: string, data?: Record<string, unknown>) {
    console.error(this.format('error', message, data));
  }
  info(message: string, data?: Record<string, unknown>) {
    console.log(this.format('info', message, data));
  }
}
```

### Async Operation Logging

```typescript
async function withLogging<T>(
  logger: Logger, operation: string, fn: () => Promise<T>
): Promise<T> {
  const start = Date.now();
  try {
    const result = await fn();
    logger.info(`${operation} completed`, { duration_ms: Date.now() - start });
    return result;
  } catch (error) {
    logger.error(`${operation} failed`, {
      duration_ms: Date.now() - start,
      error: error instanceof Error ? error.message : String(error)
    });
    throw error;
  }
}
```

## Cross-Language Standards

### Consistent Field Names

| Field | All Languages |
|-------|---------------|
| Request ID | `request_id` |
| Namespace | `namespace` |
| Duration | `duration_ms` |
| Error | `error` |
| Service | `service` |

### Log Level Mapping

| Severity | Python | Go | TypeScript |
|----------|--------|-----|------------|
| Error | `logging.ERROR` | `slog.LevelError` | `'error'` |
| Warning | `logging.WARNING` | `slog.LevelWarn` | `'warn'` |
| Info | `logging.INFO` | `slog.LevelInfo` | `'info'` |
| Debug | `logging.DEBUG` | `slog.LevelDebug` | `'debug'` |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `LOG_LEVEL` | `debug`, `info`, `warn`, `error` |
| `LOG_FORMAT` | `json`, `text` |
| `SERVICE_NAME` | Service identifier |
