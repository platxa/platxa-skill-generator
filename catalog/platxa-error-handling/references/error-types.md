# Error Types Reference

Detailed error type definitions for each language in Platxa.

## Python Error Types

### Built-in Exceptions

```python
# ValueError - Invalid input data
raise ValueError(f"Invalid domain format: {domain}")
raise ValueError("Label value cannot be empty")

# PermissionError - Authorization failures
raise PermissionError("You don't have permission to provision this instance")
raise PermissionError("Only managers can delete instances")

# RuntimeError - Unexpected runtime conditions
raise RuntimeError("No PostgreSQL pod found in postgres-system namespace")

# Exception - Generic fallback
raise Exception("kubernetes package not installed. Run: pip install kubernetes")
```

### Kubernetes ApiException

```python
from kubernetes.client.rest import ApiException

# Handle by status code
try:
    core_v1.read_namespace(namespace)
except ApiException as e:
    if e.status == 404:      # Not found - expected
        core_v1.create_namespace(body)
    elif e.status == 409:    # Conflict - already exists
        _logger.info(f"Namespace {namespace} already exists")
    elif e.status == 403:    # Forbidden
        raise PermissionError(f"Cannot access namespace: {namespace}")
    else:
        raise
```

### Werkzeug HTTP Exceptions

```python
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound

# 401 Unauthorized
raise Unauthorized("Invalid or missing Bearer token")

# 400 Bad Request
raise BadRequest("Invalid JSON payload")

# 404 Not Found
raise NotFound("Instance not found")
```

### Odoo Exceptions

```python
from odoo.exceptions import UserError, ValidationError, AccessError

# User-facing errors
raise UserError("Cannot delete instance with active subscriptions")

# Validation errors
raise ValidationError("Domain already in use")

# Access control errors
raise AccessError("Insufficient permissions")
```

## TypeScript Error Types

### NormalizedError Interface

```typescript
export interface NormalizedError {
  id: string;                          // Unique identifier
  type: string;                        // Error class (TypeError, SyntaxError)
  message: string;                     // Human-readable message
  severity: ErrorSeverity;
  source: ErrorSource;
  language: Language;
  location?: SourceLocation;
  stackTrace?: StackFrame[];
  code?: string;                       // Error code (TS2322, E1001)
  context?: Record<string, unknown>;
  raw: string;                         // Original error text
  timestamp: Date;
  relatedErrors?: string[];
}

export type ErrorSeverity = 'error' | 'warning' | 'info' | 'hint';

export type ErrorSource =
  | 'exception'    // Runtime exception/traceback
  | 'static'       // Static analysis (linter, type checker)
  | 'runtime'      // Runtime error (not exception)
  | 'build'        // Build/compilation error
  | 'test'         // Test failure
  | 'log'          // Log file entry
  | 'console'      // Console output
  | 'unknown';
```

### ConnectionError Interface

```typescript
export type ConnectionErrorType =
  | 'NETWORK_ERROR'    // Network unreachable
  | 'AUTH_ERROR'       // Authentication failed
  | 'TIMEOUT'          // Connection/request timeout
  | 'SERVER_ERROR'     // 5xx response
  | 'RATE_LIMITED'     // 429 response
  | 'UNKNOWN';

export interface ConnectionError {
  type: ConnectionErrorType;
  message: string;
  code?: number;           // HTTP status code
  retryable: boolean;
  timestamp: Date;
}

// Classification
const retryableTypes = new Set([
  'NETWORK_ERROR',
  'TIMEOUT',
  'SERVER_ERROR'
]);

function isRetryable(error: ConnectionError): boolean {
  return retryableTypes.has(error.type);
}
```

### SourceLocation Interface

```typescript
export interface SourceLocation {
  file: string;
  line: number;
  column?: number;
  endLine?: number;
  endColumn?: number;
}

export interface StackFrame {
  function?: string;
  file: string;
  line: number;
  column?: number;
  isUserCode: boolean;   // vs library code
  raw: string;
}
```

## Go Error Types

### WakeError Struct

```go
// WakeError is the canonical error type
type WakeError struct {
    Code            ErrorCode     // Standardized error code
    UserMessage     string        // User-friendly message
    TechnicalDetail string        // Technical debugging info
    RetryAllowed    bool          // Whether operation can be retried
    SupportRef      string        // Support reference ID
    Timestamp       time.Time     // When error occurred
}

func (e *WakeError) Error() string {
    return e.UserMessage
}

// Constructor with code lookup
func NewWakeErrorWithCode(code ErrorCode, detail string) *WakeError {
    return &WakeError{
        Code:            code,
        UserMessage:     codeToUserMessage[code],
        TechnicalDetail: detail,
        RetryAllowed:    retryableErrors[code],
        Timestamp:       time.Now(),
    }
}
```

### Error Codes

```go
type ErrorCode string

const (
    // Image errors
    CodeImagePullFailed ErrorCode = "IMAGE_PULL_FAILED"
    CodeImageNotFound   ErrorCode = "IMAGE_NOT_FOUND"

    // Container errors
    CodeCrashLoop        ErrorCode = "CRASH_LOOP"
    CodeOOMKilled        ErrorCode = "OUT_OF_MEMORY"
    CodeCreateContainer  ErrorCode = "CREATE_CONTAINER_ERROR"

    // Resource errors
    CodeInsufficientResources ErrorCode = "INSUFFICIENT_RESOURCES"
    CodeEvicted              ErrorCode = "EVICTED"
    CodePreempted            ErrorCode = "PREEMPTED"
    CodeVolumeMountFailed    ErrorCode = "VOLUME_MOUNT_FAILED"

    // Timeout errors
    CodeStartupTimeout ErrorCode = "STARTUP_TIMEOUT"

    // Database errors
    CodeDBConnectionFailed ErrorCode = "DATABASE_CONNECTION_FAILED"

    // Scale errors
    CodeScaleUpFailed ErrorCode = "SCALE_UP_FAILED"

    // Unknown
    CodeUnknown ErrorCode = "UNKNOWN"
)
```

### Kubernetes Reason Mapping

```go
// Map K8s reasons to domain error codes
var k8sReasonToCode = map[string]ErrorCode{
    "ErrImagePull":         CodeImagePullFailed,
    "ImagePullBackOff":     CodeImagePullFailed,
    "InvalidImageName":     CodeImageNotFound,
    "CrashLoopBackOff":     CodeCrashLoop,
    "OOMKilled":            CodeOOMKilled,
    "CreateContainerError": CodeCreateContainer,
    "Evicted":              CodeEvicted,
    "Preempted":            CodePreempted,
}

func MapK8sReason(reason string) ErrorCode {
    if code, ok := k8sReasonToCode[reason]; ok {
        return code
    }
    return CodeUnknown
}
```

### Sentinel Errors

```go
// Package-level sentinel errors
var (
    ErrBodyTooLarge    = fmt.Errorf("request body too large")
    ErrInstanceNotFound = fmt.Errorf("instance not found")
    ErrRateLimited     = fmt.Errorf("rate limit exceeded")
)

// Usage with identity check
if err == ErrBodyTooLarge {
    http.Error(w, "Request body too large", http.StatusRequestEntityTooLarge)
}

// Usage with errors.Is (for wrapped errors)
if errors.Is(err, ErrInstanceNotFound) {
    http.Error(w, "Instance not found", http.StatusNotFound)
}
```

### Error Wrapping

```go
// Always wrap with context using %w
if err != nil {
    return nil, fmt.Errorf("failed to get kubernetes config: %w", err)
}

if err != nil {
    return fmt.Errorf("scale deployment %s/%s to %d: %w",
        namespace, name, replicas, err)
}

// Unwrap with errors.Is and errors.As
if errors.Is(err, context.DeadlineExceeded) {
    // Handle timeout
}

var apiErr *ApiError
if errors.As(err, &apiErr) {
    // Handle API-specific error
}
```

## Error Type Selection Guide

| Scenario | Python | TypeScript | Go |
|----------|--------|------------|-----|
| Invalid input | ValueError | NormalizedError (source: static) | fmt.Errorf |
| Auth failure | PermissionError | ConnectionError (AUTH_ERROR) | WakeError |
| Not found | KeyError / NotFound | NormalizedError (source: runtime) | ErrNotFound |
| Timeout | TimeoutError | ConnectionError (TIMEOUT) | context.DeadlineExceeded |
| API error | ApiException | ConnectionError (SERVER_ERROR) | WakeError |
| Rate limit | - | ConnectionError (RATE_LIMITED) | ErrRateLimited |
