# Language-Specific Logging Patterns

Detailed patterns for Python, TypeScript, and Go logging in Platxa.

## Python Patterns

### Module Logger Setup

```python
import logging

# Standard module-level logger
_logger = logging.getLogger(__name__)

# Separate audit logger
_audit_logger = logging.getLogger('instance_manager.audit')
```

### Timing Decorator

```python
import time
import functools
import logging
from contextlib import contextmanager

_logger = logging.getLogger(__name__)

def timed(func):
    """Decorator to log function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            _logger.info(
                f"{func.__name__} completed",
                extra={'duration_ms': int(duration_ms)}
            )
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            _logger.error(
                f"{func.__name__} failed: {e}",
                extra={'duration_ms': int(duration_ms)},
                exc_info=True
            )
            raise
    return wrapper

@contextmanager
def log_duration(operation: str):
    """Context manager for timing operations."""
    start = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        _logger.info(f"{operation}", extra={'duration_ms': int(duration_ms)})

# Usage
@timed
def provision_instance(name: str):
    ...

with log_duration("database query"):
    result = db.execute(query)
```

### Exception Logging

```python
try:
    result = risky_operation()
except ValueError as e:
    # Log with stack trace
    _logger.error("Validation failed: %s", e, exc_info=True)
    raise
except Exception as e:
    # Log and wrap
    _logger.exception("Unexpected error")  # Always includes stack trace
    raise RuntimeError(f"Operation failed: {e}") from e
```

### Flask Integration

```python
from flask import Flask, g, request
import uuid
import logging

app = Flask(__name__)
_logger = logging.getLogger(__name__)

@app.before_request
def setup_request_logging():
    """Set up logging context for request."""
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    g.start_time = time.perf_counter()
    _logger.info("Request started",
                 extra={'method': request.method, 'path': request.path})

@app.after_request
def log_response(response):
    """Log request completion."""
    duration_ms = (time.perf_counter() - g.start_time) * 1000
    _logger.info("Request completed",
                 extra={
                     'method': request.method,
                     'path': request.path,
                     'status': response.status_code,
                     'duration_ms': int(duration_ms)
                 })
    return response
```

### Odoo-Specific Patterns

```python
import logging

_logger = logging.getLogger(__name__)

class InstanceManager(models.Model):
    _name = 'instance.manager'

    def provision(self, vals):
        """Provision instance with audit logging."""
        _logger.info(
            "Provisioning instance %s for user %s",
            vals.get('name'),
            self.env.user.name
        )

        try:
            instance = self._do_provision(vals)
            self._audit_log('provision', 'instance', instance.name, result='success')
            return instance
        except Exception as e:
            self._audit_log('provision', 'instance', vals.get('name'),
                          result='failure', details={'error': str(e)})
            _logger.error("Provision failed: %s", e, exc_info=True)
            raise

    def _audit_log(self, action, resource_type, resource_name,
                   result='success', details=None):
        """Create audit log entry."""
        import json
        log_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'action': action,
            'resource_type': resource_type,
            'resource_name': resource_name,
            'result': result,
            'user_id': self.env.user.id,
            'user_name': self.env.user.name,
            'details': details,
        }
        logging.getLogger('audit').info(json.dumps(log_entry))
```

## Go Patterns

### Package Structure

```go
// internal/logging/logger.go
package logging

import (
    "log/slog"
    "os"
)

var defaultLogger *slog.Logger

func Init(service string, level string, json bool) {
    opts := &slog.HandlerOptions{Level: parseLevel(level)}

    var handler slog.Handler
    if json {
        handler = slog.NewJSONHandler(os.Stdout, opts)
    } else {
        handler = slog.NewTextHandler(os.Stdout, opts)
    }

    defaultLogger = slog.New(handler).With("service", service)
    slog.SetDefault(defaultLogger)
}
```

### Field Constants

```go
// internal/logging/fields.go
package logging

// Standard field keys
const (
    KeyService    = "service"
    KeyRequestID  = "request_id"
    KeyNamespace  = "namespace"
    KeyInstance   = "instance"
    KeyDurationMS = "duration_ms"
    KeyError      = "error"
    KeyErrorCode  = "error_code"
    KeySupportRef = "support_ref"
    KeyMethod     = "method"
    KeyPath       = "path"
    KeyStatus     = "status"
    KeyHost       = "host"
    KeyUserID     = "user_id"
)
```

### HTTP Handler Logging

```go
func (h *Handler) Wake(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    namespace := chi.URLParam(r, "namespace")
    start := time.Now()

    slog.InfoContext(ctx, "wake request",
        KeyRequestID, correlation.GetRequestID(ctx),
        KeyNamespace, namespace,
    )

    err := h.scaler.Wake(ctx, namespace)
    duration := time.Since(start)

    if err != nil {
        slog.ErrorContext(ctx, "wake failed",
            KeyRequestID, correlation.GetRequestID(ctx),
            KeyNamespace, namespace,
            KeyError, err.Error(),
            KeyDurationMS, duration.Milliseconds(),
        )
        http.Error(w, "Wake failed", http.StatusServiceUnavailable)
        return
    }

    slog.InfoContext(ctx, "wake completed",
        KeyRequestID, correlation.GetRequestID(ctx),
        KeyNamespace, namespace,
        KeyDurationMS, duration.Milliseconds(),
    )

    w.WriteHeader(http.StatusOK)
}
```

### Error Wrapping with Context

```go
import "fmt"

func (s *Scaler) Wake(ctx context.Context, namespace string) error {
    deployment, err := s.getDeployment(ctx, namespace)
    if err != nil {
        return fmt.Errorf("get deployment %s: %w", namespace, err)
    }

    if err := s.scale(ctx, deployment, 1); err != nil {
        return fmt.Errorf("scale deployment %s to 1: %w", namespace, err)
    }

    return nil
}
```

### Middleware Chain

```go
func SetupMiddleware(r *chi.Mux) {
    // Order matters!
    r.Use(middleware.RequestID)      // 1. Generate/extract request ID
    r.Use(middleware.RealIP)         // 2. Extract client IP
    r.Use(middleware.Recoverer)      // 3. Panic recovery
    r.Use(middleware.Logging)        // 4. Request logging
}
```

### Health Check Skip Pattern

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Skip logging for health endpoints
        if r.URL.Path == "/health" || r.URL.Path == "/ready" || r.URL.Path == "/metrics" {
            next.ServeHTTP(w, r)
            return
        }

        // ... logging logic
    })
}
```

## TypeScript Patterns

### Console Logger Wrapper

```typescript
type LogLevel = 'error' | 'warn' | 'info' | 'debug';

interface LoggerConfig {
  service: string;
  level: LogLevel;
  json: boolean;
}

class Logger {
  private config: LoggerConfig;
  private levels: Record<LogLevel, number> = {
    error: 0,
    warn: 1,
    info: 2,
    debug: 3,
  };

  constructor(config: LoggerConfig) {
    this.config = config;
  }

  private shouldLog(level: LogLevel): boolean {
    return this.levels[level] <= this.levels[this.config.level];
  }

  private format(level: LogLevel, message: string, data?: Record<string, unknown>): string {
    if (this.config.json) {
      return JSON.stringify({
        timestamp: new Date().toISOString(),
        level,
        service: this.config.service,
        message,
        ...data,
      });
    }
    const dataStr = data ? ` ${JSON.stringify(data)}` : '';
    return `[${new Date().toISOString()}] ${level.toUpperCase()} ${this.config.service}: ${message}${dataStr}`;
  }

  error(message: string, data?: Record<string, unknown>): void {
    if (this.shouldLog('error')) {
      console.error(this.format('error', message, data));
    }
  }

  warn(message: string, data?: Record<string, unknown>): void {
    if (this.shouldLog('warn')) {
      console.warn(this.format('warn', message, data));
    }
  }

  info(message: string, data?: Record<string, unknown>): void {
    if (this.shouldLog('info')) {
      console.log(this.format('info', message, data));
    }
  }

  debug(message: string, data?: Record<string, unknown>): void {
    if (this.shouldLog('debug')) {
      console.debug(this.format('debug', message, data));
    }
  }

  child(data: Record<string, unknown>): ChildLogger {
    return new ChildLogger(this, data);
  }
}

class ChildLogger {
  constructor(
    private parent: Logger,
    private context: Record<string, unknown>
  ) {}

  error(message: string, data?: Record<string, unknown>): void {
    this.parent.error(message, { ...this.context, ...data });
  }
  // ... other methods
}
```

### React Error Boundary Logging

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  logger: Logger;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.props.logger.error('React error boundary caught error', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong</div>;
    }
    return this.props.children;
  }
}
```

### WebSocket Event Logging

```typescript
class WebSocketLogger {
  private logger: Logger;
  private sessionId: string;

  constructor(sessionId: string) {
    this.sessionId = sessionId;
    this.logger = new Logger({
      service: 'websocket',
      level: 'info',
      json: true,
    });
  }

  onConnect(clientId: string): void {
    this.logger.info('client connected', {
      session_id: this.sessionId,
      client_id: clientId,
    });
  }

  onDisconnect(clientId: string, reason: string): void {
    this.logger.info('client disconnected', {
      session_id: this.sessionId,
      client_id: clientId,
      reason,
    });
  }

  onMessage(clientId: string, messageType: string, size: number): void {
    this.logger.debug('message received', {
      session_id: this.sessionId,
      client_id: clientId,
      message_type: messageType,
      size_bytes: size,
    });
  }

  onError(clientId: string, error: Error): void {
    this.logger.error('websocket error', {
      session_id: this.sessionId,
      client_id: clientId,
      error: error.message,
      stack: error.stack,
    });
  }
}
```

### Async Operation Logging

```typescript
async function withLogging<T>(
  logger: Logger,
  operation: string,
  fn: () => Promise<T>,
  context?: Record<string, unknown>
): Promise<T> {
  const start = Date.now();
  logger.debug(`${operation} started`, context);

  try {
    const result = await fn();
    const duration = Date.now() - start;
    logger.info(`${operation} completed`, {
      ...context,
      duration_ms: duration,
    });
    return result;
  } catch (error) {
    const duration = Date.now() - start;
    logger.error(`${operation} failed`, {
      ...context,
      duration_ms: duration,
      error: error instanceof Error ? error.message : String(error),
    });
    throw error;
  }
}

// Usage
const result = await withLogging(
  logger,
  'fetch user data',
  () => api.getUser(userId),
  { user_id: userId }
);
```

## Cross-Language Patterns

### Consistent Field Names

All languages should use these exact field names:

| Field | Python | Go | TypeScript |
|-------|--------|-----|------------|
| Request ID | `request_id` | `request_id` | `request_id` |
| Namespace | `namespace` | `namespace` | `namespace` |
| Duration | `duration_ms` | `duration_ms` | `duration_ms` |
| Error | `error` | `error` | `error` |
| User ID | `user_id` | `user_id` | `user_id` |
| Service | `service` | `service` | `service` |

### Log Level Mapping

| Severity | Python | Go | TypeScript |
|----------|--------|-----|------------|
| Error | `logging.ERROR` | `slog.LevelError` | `'error'` |
| Warning | `logging.WARNING` | `slog.LevelWarn` | `'warn'` |
| Info | `logging.INFO` | `slog.LevelInfo` | `'info'` |
| Debug | `logging.DEBUG` | `slog.LevelDebug` | `'debug'` |

### Environment Configuration

| Variable | Purpose | Values |
|----------|---------|--------|
| `LOG_LEVEL` | Minimum log level | `debug`, `info`, `warn`, `error` |
| `LOG_FORMAT` | Output format | `json`, `text` |
| `SERVICE_NAME` | Service identifier | e.g., `waking-service` |
