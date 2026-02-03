---
name: platxa-error-handling
description: Guide for structured error handling across Platxa stack. Covers error types, retry patterns with exponential backoff, logging, and HTTP response mapping for Python, TypeScript, and Go.
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - guide
    - error-handling
    - retry
    - logging
---

# Platxa Error Handling

Guide for structured error handling patterns across the Platxa platform.

## Overview

| Language | Error Type | Retry Pattern | Logging |
|----------|------------|---------------|---------|
| **Python** | Exceptions (ValueError, PermissionError) | Polling with timeout | logging + audit |
| **TypeScript** | NormalizedError, ConnectionError | Exponential backoff + jitter | Console, events |
| **Go** | WakeError struct, sentinel errors | Retryable map + context timeout | slog JSON |

## Core Principles

1. **Dual Messages**: User-friendly message + technical detail
2. **Error Classification**: Severity, source, retryability
3. **Never Log Secrets**: Only log key names, not values
4. **Fail Fast**: Validate inputs before operations
5. **Preserve Error Chain**: Wrap errors with context

## Structured Error Types

### Python Exceptions

```python
# Semantic exception types
raise ValueError(f"Invalid domain format: {domain}")
raise PermissionError("You don't have permission to provision this instance")

# Kubernetes API exceptions
from kubernetes.client.rest import ApiException

try:
    core_v1.read_namespace(namespace)
except ApiException as e:
    if e.status == 404:  # Expected - create new
        core_v1.create_namespace(body)
    elif e.status == 409:  # Conflict - already exists
        _logger.info(f"Resource already exists")
    else:
        raise  # Unexpected - re-raise
```

### TypeScript Error Types

```typescript
// Normalized error format
interface NormalizedError {
  id: string;
  type: string;                    // Error class name
  message: string;                 // Human-readable
  severity: 'error' | 'warning' | 'info' | 'hint';
  source: 'exception' | 'static' | 'runtime' | 'build' | 'test';
  code?: string;                   // Error code (TS2322, E1001)
  location?: SourceLocation;
  raw: string;                     // Original error text
  timestamp: Date;
}

// Connection error classification
type ConnectionErrorType =
  | 'NETWORK_ERROR'
  | 'AUTH_ERROR'
  | 'TIMEOUT'
  | 'SERVER_ERROR'
  | 'RATE_LIMITED';
```

### Go Custom Errors

```go
// WakeError with dual messages
type WakeError struct {
    Code            ErrorCode
    UserMessage     string    // Safe for users
    TechnicalDetail string    // For logs/support
    RetryAllowed    bool
    SupportRef      string
    Timestamp       time.Time
}

// Error codes as typed constants
type ErrorCode string

const (
    CodeImagePullFailed ErrorCode = "IMAGE_PULL_FAILED"
    CodeCrashLoop       ErrorCode = "CRASH_LOOP"
    CodeOOMKilled       ErrorCode = "OUT_OF_MEMORY"
    CodeStartupTimeout  ErrorCode = "STARTUP_TIMEOUT"
)

// Sentinel errors
var ErrBodyTooLarge = fmt.Errorf("request body too large")
```

## Error Classification

### Severity Levels

| Level | Python | TypeScript | Go | Usage |
|-------|--------|------------|-----|-------|
| Error | Exception raised | severity: 'error' | slog.Error | Operation failed |
| Warning | _logger.warning | severity: 'warning' | slog.Warn | Degraded but working |
| Info | _logger.info | severity: 'info' | slog.Info | Normal operation |

### Retryability

```typescript
// TypeScript: Retryable classification
const retryableErrors = ['NETWORK_ERROR', 'TIMEOUT', 'SERVER_ERROR'];
const nonRetryableErrors = ['AUTH_ERROR', 'RATE_LIMITED'];
```

```go
// Go: Retryable map
var retryableErrors = map[ErrorCode]bool{
    CodeEvicted:         true,
    CodeStartupTimeout:  true,
    CodeScaleUpFailed:   true,
    CodeImagePullFailed: false,  // Non-retryable
    CodeCrashLoop:       false,
}

func IsRetryable(code ErrorCode) bool {
    return retryableErrors[code]
}
```

## Retry Patterns

### Exponential Backoff with Jitter

```typescript
function calculateDelay(attempt: number, baseDelay = 1000, maxDelay = 30000): number {
  const delay = baseDelay * Math.pow(2, attempt);           // Exponential
  const jitter = delay * 0.25 * (Math.random() * 2 - 1);    // ±25% jitter
  return Math.min(delay + jitter, maxDelay);                // Cap at max
}
```

### Python Polling with Timeout

```python
import time

def wake_instance(self, instance):
    """Wake instance with timeout."""
    start_time = time.time()
    timeout = 30  # seconds

    while time.time() - start_time < timeout:
        status, _ = self.get_pod_status(instance)
        if status == 'running':
            return True, int((time.time() - start_time) * 1000)
        time.sleep(1)

    return False, None  # Timeout
```

### Go Context Timeout

```go
func (s *Scaler) waitForReady(ctx context.Context, namespace string) error {
    ctx, cancel := context.WithTimeout(ctx, s.config.WakeTimeout)
    defer cancel()

    for {
        select {
        case <-ctx.Done():
            if ctx.Err() == context.DeadlineExceeded {
                return fmt.Errorf("timeout waiting for pod ready")
            }
            return ctx.Err()
        default:
            if s.isPodReady(namespace) {
                return nil
            }
            time.Sleep(time.Second)
        }
    }
}
```

## Error Logging

### Python Structured Logging

```python
import logging
import json

_logger = logging.getLogger(__name__)
_audit_logger = logging.getLogger('instance_manager.audit')

def _audit_log(self, action, resource_type, resource_name, result='success', details=None):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'resource_type': resource_type,
        'resource_name': resource_name,
        'result': result,
        'user_id': self.env.user.id,
        'details': details,  # Never include secrets!
    }
    _audit_logger.info(json.dumps(log_entry))

# Security: Log key names, not values
security._audit_log(
    action='create_secret',
    details={'keys': list(secret_data.keys())}  # Only key names
)
```

### Go Structured Logging (slog)

```go
import "log/slog"

// Setup with JSON output
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

// Consistent field keys
const (
    KeyError      = "error"
    KeyErrorCode  = "error_code"
    KeyDurationMS = "duration_ms"
)

// Usage
slog.Error("scale-up failed",
    "namespace", namespace,
    "error", err,
)
```

## HTTP Error Responses

### Status Code Mapping

| Error Type | HTTP Status | When to Use |
|------------|-------------|-------------|
| Validation error | 400 Bad Request | Invalid input |
| Authentication error | 401 Unauthorized | Missing/invalid token |
| Authorization error | 403 Forbidden | Insufficient permissions |
| Resource not found | 404 Not Found | Missing resource |
| Rate limit | 429 Too Many Requests | Throttled |
| Server error | 500 Internal Server Error | Unexpected error |
| Service unavailable | 503 Service Unavailable | Temporary unavailable |
| Timeout | 504 Gateway Timeout | Upstream timeout |

### Python (FastAPI/Werkzeug)

```python
from werkzeug.exceptions import Unauthorized, BadRequest

# Validation error
if not valid_input(data):
    raise BadRequest("Invalid JSON payload")

# Auth error
if not verify_token(request):
    raise Unauthorized("Invalid or missing Bearer token")

# JSON response wrapper
def _json_response(self, data, status=200):
    return Response(
        json.dumps(data),
        status=status,
        mimetype='application/json'
    )
```

### Go HTTP Responses

```go
// Map errors to status codes
func errorHandler(w http.ResponseWriter, r *http.Request, err error) {
    if r.Context().Err() != nil {
        return  // Client disconnected
    }

    if isConnectionRefused(err) {
        http.Error(w, "Instance is not ready", http.StatusBadGateway)
        return
    }

    if isTimeout(err) {
        http.Error(w, "Request timed out", http.StatusGatewayTimeout)
        return
    }

    http.Error(w, "An error occurred", http.StatusBadGateway)
}

// Rate limiting response
if !rateLimiter.Allow(key) {
    w.Header().Set("Retry-After", "60")
    http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
}
```

## Workflow

### Step 1: Define Error Strategy

| Question | Consideration |
|----------|---------------|
| What can fail? | Network, validation, auth, resources |
| Who sees the error? | User vs developer vs ops |
| Should it retry? | Transient vs permanent failures |
| What to log? | Context without secrets |

### Step 2: Create Error Types

1. Define severity levels
2. Create typed error codes
3. Separate user message from technical detail
4. Mark retryable conditions

### Step 3: Implement Retry Logic

1. Classify which errors are retryable
2. Configure backoff: base delay, max delay, max retries
3. Add jitter to prevent thundering herd
4. Set timeout boundaries

### Step 4: Add Structured Logging

1. Use structured format (JSON)
2. Include correlation context
3. Never log sensitive data
4. Use appropriate log levels

### Step 5: Map to HTTP Responses

1. Convert internal errors to status codes
2. Craft safe user messages
3. Include Retry-After for rate limits

## Examples

### Example 1: Python API Error Handling

**Scenario**: Validate user input and handle K8s errors

```python
@api.model
def provision_instance(self, instance):
    # 1. Validate input
    if not self.validate_domain(instance.domain):
        raise ValueError(f"Invalid domain: {instance.domain}")

    # 2. Check permissions
    if not self.check_permission(instance, 'write'):
        self._audit_log(action='provision', result='denied')
        raise PermissionError("Permission denied")

    # 3. K8s operation with error handling
    try:
        result = k8s.create_namespace(instance.namespace)
        self._audit_log(action='provision', result='success')
        return result
    except ApiException as e:
        self._audit_log(action='provision', result='failure',
                       details={'error': str(e)})
        raise
```

### Example 2: TypeScript Retry with Backoff

**Scenario**: Reconnect WebSocket with exponential backoff

```typescript
const { retry, isConnected, error } = useConnectionRetry(
  () => websocket.connect(),
  {
    maxRetries: 5,
    baseDelay: 1000,
    maxDelay: 30000,
    onRetry: (attempt, delay) => {
      console.log(`Retry ${attempt} in ${delay}ms`);
    },
    onMaxRetriesReached: (error) => {
      showNotification('Connection failed. Please refresh.');
    },
  }
);
```

### Example 3: Go Service Error Handling

**Scenario**: Handle wake-up with timeout and proper responses

```go
func handleWake(w http.ResponseWriter, r *http.Request, namespace string) {
    ctx, cancel := context.WithTimeout(r.Context(), 30*time.Second)
    defer cancel()

    err := scaler.WakeInstance(ctx, namespace)
    if err != nil {
        if ctx.Err() == context.DeadlineExceeded {
            http.Error(w, "Instance took too long to start",
                      http.StatusGatewayTimeout)
            return
        }
        slog.Error("wake failed", "namespace", namespace, "error", err)
        http.Error(w, "Failed to start instance",
                  http.StatusServiceUnavailable)
        return
    }

    w.WriteHeader(http.StatusOK)
}
```

### Example 4: Error Boundary (React)

**Scenario**: Catch Monaco Editor rendering errors

```typescript
class EditorErrorBoundary extends Component {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Monaco Editor Error:', error);
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <FallbackUI onRetry={this.handleRetry} />;
    }
    return this.props.children;
  }
}
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Retry storm | No jitter | Add ±25% jitter to delays |
| Infinite retry | No max retries | Set maxRetries limit |
| Secrets leaked | Logging values | Only log key names |
| Lost error context | Not wrapping | Use `fmt.Errorf %w` or chain |
| Wrong status code | Poor mapping | Review error-to-status table |
| Client hangs | No timeout | Add context.WithTimeout |

## Output Checklist

After implementing error handling:

- [ ] Error types defined with severity and codes
- [ ] User messages separated from technical details
- [ ] Retry logic includes backoff and jitter
- [ ] Retryable vs non-retryable classified
- [ ] Structured logging with context (no secrets)
- [ ] HTTP status codes properly mapped
- [ ] Timeout boundaries set
- [ ] Error boundaries for UI components
- [ ] Audit logging for sensitive operations

## Related Resources

- **Error Types**: See `references/error-types.md`
- **Retry Patterns**: See `references/retry-patterns.md`
- **Logging Patterns**: See `references/logging-patterns.md`
