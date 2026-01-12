# Retry Patterns Reference

Retry implementations with exponential backoff across Platxa languages.

## Exponential Backoff Formula

```
delay = min(baseDelay * 2^attempt + jitter, maxDelay)
```

| Parameter | Recommended | Why |
|-----------|-------------|-----|
| baseDelay | 1000ms | Time for transient issues |
| maxDelay | 30000ms | Don't wait forever |
| maxRetries | 5 | Total wait ~60s |
| jitter | ±25% | Prevent thundering herd |

## TypeScript Implementation

```typescript
export function useConnectionRetry(
  connect: () => void,
  options: { maxRetries?: number; baseDelay?: number; maxDelay?: number } = {}
) {
  const { maxRetries = 5, baseDelay = 1000, maxDelay = 30000 } = options;
  const [attempt, setAttempt] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);

  const calculateDelay = (currentAttempt: number): number => {
    const delay = baseDelay * Math.pow(2, currentAttempt);
    const jitter = delay * 0.25 * (Math.random() * 2 - 1);
    return Math.min(delay + jitter, maxDelay);
  };

  const attemptConnection = async () => {
    try {
      await connect();
      setAttempt(0);
    } catch (err) {
      const error = classifyError(err);
      if (error.retryable && attempt < maxRetries) {
        setIsRetrying(true);
        setTimeout(() => {
          setAttempt(prev => prev + 1);
          attemptConnection();
        }, calculateDelay(attempt));
      }
    }
  };

  return { retry: attemptConnection, attempt, isRetrying };
}
```

### Error Classification

```typescript
function classifyError(err: unknown): ConnectionError {
  if (err instanceof Error) {
    const msg = err.message.toLowerCase();
    if (msg.includes('network')) return { type: 'NETWORK', retryable: true };
    if (msg.includes('timeout')) return { type: 'TIMEOUT', retryable: true };
    if (msg.includes('401')) return { type: 'AUTH', retryable: false };
    if (msg.includes('429')) return { type: 'RATE_LIMITED', retryable: false };
    if (msg.includes('5')) return { type: 'SERVER', retryable: true };
  }
  return { type: 'UNKNOWN', retryable: false };
}
```

## Go Implementation

### Retryable Classification

```go
var retryableErrors = map[ErrorCode]bool{
    CodeEvicted:        true,
    CodePreempted:      true,
    CodeStartupTimeout: true,
    CodeScaleUpFailed:  true,
    CodeImagePullFailed: false,
    CodeCrashLoop:       false,
    CodeOOMKilled:       false,
}

func IsRetryable(code ErrorCode) bool {
    return retryableErrors[code]
}
```

### Context Timeout with Retry

```go
func (s *Scaler) EnsureScaleUp(ctx context.Context, namespace string) error {
    ctx, cancel := context.WithTimeout(ctx, s.config.WakeTimeout)
    defer cancel()

    for {
        select {
        case <-ctx.Done():
            return errors.NewWakeError(errors.CodeStartupTimeout, "timeout")
        default:
            if s.isPodReady(namespace) {
                return nil
            }
            time.Sleep(time.Second)
        }
    }
}
```

## Python Implementation

### Polling with Timeout

```python
def wake_instance(self, instance):
    """Wake instance with timeout and polling."""
    apps_v1.patch_namespaced_deployment_scale(
        name=f"odoo-{instance.name}",
        namespace=f"instance-{instance.name}",
        body={'spec': {'replicas': 1}}
    )

    start_time = time.time()
    timeout = 30

    while time.time() - start_time < timeout:
        status, _ = self.get_pod_status(instance)
        if status == 'running':
            return True, int((time.time() - start_time) * 1000)
        time.sleep(1)
    return False, None
```

### Idempotent K8s Operations

```python
def create_or_update_secret(self, namespace, name, data):
    """Create or update secret idempotently."""
    secret = V1Secret(metadata=V1ObjectMeta(name=name), string_data=data)
    try:
        core_v1.create_namespaced_secret(namespace, secret)
    except ApiException as e:
        if e.status == 409:
            core_v1.replace_namespaced_secret(name, namespace, secret)
        else:
            raise
```

## Delays by Attempt

| Attempt | Base Delay | With Jitter |
|---------|------------|-------------|
| 0 | 1000ms | 750-1250ms |
| 1 | 2000ms | 1500-2500ms |
| 2 | 4000ms | 3000-5000ms |
| 3 | 8000ms | 6000-10000ms |
| 4 | 16000ms | 12000-20000ms |

## When NOT to Retry

| Error Type | Reason |
|------------|--------|
| AUTH_ERROR | Credentials won't fix themselves |
| RATE_LIMITED | Wait for Retry-After header |
| Validation | Input is wrong |
| CrashLoop | Application bug |
| OOMKilled | Need resource adjustment |
