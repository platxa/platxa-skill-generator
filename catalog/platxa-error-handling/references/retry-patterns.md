# Retry Patterns Reference

Retry implementations with exponential backoff across Platxa languages.

## Exponential Backoff Formula

```
delay = min(baseDelay * 2^attempt + jitter, maxDelay)

Where:
- baseDelay: Initial delay (e.g., 1000ms)
- attempt: Current retry attempt (0-indexed)
- jitter: Random variation to prevent thundering herd
- maxDelay: Maximum delay cap (e.g., 30000ms)
```

## TypeScript Implementation

### Full Retry Hook

```typescript
export interface UseConnectionRetryOptions {
  maxRetries?: number;      // Default: 5
  baseDelay?: number;       // Default: 1000ms
  maxDelay?: number;        // Default: 30000ms
  onError?: (error: ConnectionError) => void;
  onRetry?: (attempt: number, delay: number) => void;
  onMaxRetriesReached?: (error: ConnectionError) => void;
}

export function useConnectionRetry(
  connect: () => void,
  options: UseConnectionRetryOptions = {}
): UseConnectionRetryResult {
  const {
    maxRetries = 5,
    baseDelay = 1000,
    maxDelay = 30000,
    onError,
    onRetry,
    onMaxRetriesReached,
  } = options;

  const [attempt, setAttempt] = useState(0);
  const [error, setError] = useState<ConnectionError | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);

  const calculateDelay = useCallback((currentAttempt: number): number => {
    // Exponential: baseDelay * 2^attempt
    const delay = baseDelay * Math.pow(2, currentAttempt);

    // Jitter: ±25% to prevent thundering herd
    const jitter = delay * 0.25 * (Math.random() * 2 - 1);

    // Cap at maxDelay
    return Math.min(delay + jitter, maxDelay);
  }, [baseDelay, maxDelay]);

  const attemptConnection = useCallback(async () => {
    try {
      await connect();
      setError(null);
      setAttempt(0);
    } catch (err) {
      const connectionError = classifyError(err);
      setError(connectionError);
      onError?.(connectionError);

      if (connectionError.retryable && attempt < maxRetries) {
        const delay = calculateDelay(attempt);
        onRetry?.(attempt, delay);
        setIsRetrying(true);

        setTimeout(() => {
          setAttempt(prev => prev + 1);
          setIsRetrying(false);
          attemptConnection();
        }, delay);
      } else {
        onMaxRetriesReached?.(connectionError);
      }
    }
  }, [connect, attempt, maxRetries, calculateDelay, onError, onRetry, onMaxRetriesReached]);

  return {
    retry: attemptConnection,
    reset: () => { setAttempt(0); setError(null); },
    attempt,
    error,
    isRetrying,
    isMaxRetriesReached: attempt >= maxRetries,
  };
}
```

### Error Classification

```typescript
function classifyError(err: unknown): ConnectionError {
  if (err instanceof Error) {
    const message = err.message.toLowerCase();

    if (message.includes('network') || message.includes('fetch')) {
      return { type: 'NETWORK_ERROR', message: err.message, retryable: true, timestamp: new Date() };
    }
    if (message.includes('timeout') || message.includes('timed out')) {
      return { type: 'TIMEOUT', message: err.message, retryable: true, timestamp: new Date() };
    }
    if (message.includes('401') || message.includes('unauthorized')) {
      return { type: 'AUTH_ERROR', message: err.message, retryable: false, timestamp: new Date() };
    }
    if (message.includes('429') || message.includes('rate limit')) {
      return { type: 'RATE_LIMITED', message: err.message, retryable: false, timestamp: new Date() };
    }
    if (message.includes('5')) {  // 5xx errors
      return { type: 'SERVER_ERROR', message: err.message, retryable: true, timestamp: new Date() };
    }
  }

  return { type: 'UNKNOWN', message: String(err), retryable: false, timestamp: new Date() };
}
```

## Go Implementation

### Retryable Classification Map

```go
// internal/errors/codes.go
var retryableErrors = map[ErrorCode]bool{
    CodeEvicted:               true,
    CodePreempted:             true,
    CodeStartupTimeout:        true,
    CodeScaleUpFailed:         true,
    CodeInsufficientResources: true,

    // Non-retryable
    CodeImagePullFailed:  false,
    CodeCrashLoop:        false,
    CodeOOMKilled:        false,
    CodeCreateContainer:  false,
}

func IsRetryable(code ErrorCode) bool {
    return retryableErrors[code]
}

func IsRetryableReason(reason string) bool {
    return IsRetryable(MapK8sReason(reason))
}
```

### Context Timeout with Retry

```go
func (s *Scaler) EnsureScaleUp(ctx context.Context, namespace string) (<-chan struct{}, error) {
    // Check if already retrying
    snapshot := s.cache.Get(namespace)
    if snapshot.Error != nil && !snapshot.Error.RetryAllowed {
        return nil, fmt.Errorf("instance in error state: %s", snapshot.Error.Code)
    }

    // Create context with timeout
    ctx, cancel := context.WithTimeout(ctx, s.config.WakeTimeout)

    readyCh := make(chan struct{})

    go func() {
        defer cancel()
        defer close(readyCh)

        for {
            select {
            case <-ctx.Done():
                if ctx.Err() == context.DeadlineExceeded {
                    wakeErr := errors.NewWakeErrorWithCode(
                        errors.CodeStartupTimeout,
                        fmt.Sprintf("Timeout after %v", s.config.WakeTimeout),
                    )
                    s.cache.MarkError(namespace, wakeErr)
                }
                return

            default:
                if s.isPodReady(namespace) {
                    return  // Success - channel closes
                }
                time.Sleep(time.Second)
            }
        }
    }()

    return readyCh, nil
}
```

### Retry in Main Handler

```go
// Check if error state allows retry
if snapshot.Error != nil && snapshot.Error.RetryAllowed && reqType.ShouldWake() {
    readyCh, err := instanceScaler.EnsureScaleUp(r.Context(), namespace)
    if err == nil {
        slog.Info("retrying wake-up from error state", "namespace", namespace)
        // Handle like new wake request
    }
}
```

## Python Implementation

### Polling with Timeout

```python
import time

def wake_instance(self, instance):
    """Wake instance with timeout and polling."""
    # Scale up
    apps_v1.patch_namespaced_deployment_scale(
        name=f"odoo-{instance.name}",
        namespace=f"instance-{instance.name}",
        body={'spec': {'replicas': 1}}
    )

    # Wait with timeout
    start_time = time.time()
    params = self.env['ir.config_parameter'].sudo()
    timeout = int(params.get_param('instance_manager.wake_timeout_seconds', '30'))

    while time.time() - start_time < timeout:
        status, _ = self.get_pod_status(instance)
        if status == 'running':
            duration_ms = int((time.time() - start_time) * 1000)
            return True, duration_ms
        time.sleep(1)

    return False, None  # Timeout
```

### Rate Limiting Check

```python
def check_rate_limit(self, key, max_requests=10, window_seconds=60):
    """Check if operation is within rate limit."""
    now = time.time()
    window_start = now - window_seconds

    # Get request history for this key
    history = self._rate_limit_history.get(key, [])

    # Remove old entries
    history = [t for t in history if t > window_start]

    if len(history) >= max_requests:
        return False  # Rate limited

    # Add current request
    history.append(now)
    self._rate_limit_history[key] = history
    return True
```

### Idempotent K8s Operations

```python
def create_namespace_if_not_exists(self, namespace):
    """Create namespace idempotently."""
    try:
        core_v1.read_namespace(namespace)
        _logger.info(f"Namespace {namespace} already exists")
        return True
    except ApiException as e:
        if e.status == 404:
            core_v1.create_namespace(V1Namespace(
                metadata=V1ObjectMeta(name=namespace)
            ))
            return True
        raise

def create_or_update_secret(self, namespace, name, data):
    """Create or update secret idempotently."""
    secret = V1Secret(
        metadata=V1ObjectMeta(name=name),
        string_data=data
    )

    try:
        core_v1.create_namespaced_secret(namespace, secret)
    except ApiException as e:
        if e.status == 409:  # Already exists
            core_v1.replace_namespaced_secret(name, namespace, secret)
        else:
            raise
```

## Retry Configuration Best Practices

| Parameter | Recommended | Why |
|-----------|-------------|-----|
| baseDelay | 1000ms | Enough time for transient issues |
| maxDelay | 30000ms | Don't wait forever |
| maxRetries | 5 | Total wait ~60s with exponential |
| jitter | ±25% | Prevent thundering herd |
| timeout | 30-60s | Context boundary |

## Delays by Attempt

With baseDelay=1000ms, maxDelay=30000ms:

| Attempt | Base Delay | With Jitter (±25%) |
|---------|------------|-------------------|
| 0 | 1000ms | 750-1250ms |
| 1 | 2000ms | 1500-2500ms |
| 2 | 4000ms | 3000-5000ms |
| 3 | 8000ms | 6000-10000ms |
| 4 | 16000ms | 12000-20000ms |
| 5 | 30000ms (capped) | 22500-30000ms |

**Total max wait**: ~60-90 seconds

## When NOT to Retry

| Error Type | Reason |
|------------|--------|
| AUTH_ERROR | Credentials won't fix themselves |
| RATE_LIMITED | Wait for Retry-After header |
| Validation errors | Input is wrong |
| CrashLoopBackOff | Application bug |
| OOMKilled | Need resource adjustment |
| ImagePullFailed | Wrong image reference |
