# Scale-to-Zero Flow Reference

Detailed request flow and state transitions for Platxa's scale-to-zero implementation.

## Request Classification

Waking-service classifies incoming requests to determine behavior:

| Type | Detection | Wakes | Activity |
|------|-----------|-------|----------|
| PageLoad | Accept: text/html | Yes | Yes |
| XHR | X-Requested-With or Accept: application/json | Yes | Yes |
| Longpoll | Path contains /longpolling | No | No |
| WebSocket | Upgrade: websocket | No | No |
| Static | Path matches *.js, *.css, etc. | No | No |
| Health | Path = /health or /ready | No | No |

## State Transitions

```
                    ┌─────────────┐
                    │   SLEEPING  │ ←── Idle timeout reached
                    │ (replicas=0)│
                    └──────┬──────┘
                           │ Wake request
                           ↓
                    ┌─────────────┐
         Timeout ──→│   WAKING    │←── Pod starting
         (Error)    │ (replicas>0)│
                    └──────┬──────┘
                           │ Pod ready
                           ↓
                    ┌─────────────┐
                    │   RUNNING   │ ←── Serving traffic
                    │ (pod ready) │
                    └──────┬──────┘
                           │ Idle > timeout
                           ↓
                    (Scale to 0) → SLEEPING
```

## Idle Detection Algorithm

```go
// Runs every IDLE_CHECK_INTERVAL (60s)
func checkIdleInstances() {
    for each instance in cache:
        if instance.replicas > 0 &&
           (now - instance.lastActivity) > IDLE_TIMEOUT:

            // Skip if wake in progress
            if instance.waking:
                continue

            // Scale down
            k8s.SetReplicas(instance.namespace, 0)
            instance.state = Sleeping
}
```

## Wake Operation Flow

```
1. Request arrives for sleeping instance
2. Check if wake already in progress
   - If yes: Return existing readiness channel
   - If no: Create new wake operation

3. Background wake goroutine:
   a. Set replicas = 1
   b. Poll for pod readiness (every 500ms)
   c. On ready: Close readiness channel
   d. On error: Set instance.error

4. Request handler:
   - PageLoad: Serve waking HTML page
   - XHR: Hold connection, wait for ready
   - On ready: Proxy to pod
```

## XHR Request Holding

```go
func handleXHR(w, r, instance) {
    readyChan := scaler.EnsureScaleUp(instance)

    select {
    case <-readyChan:
        // Pod ready, proxy request
        proxy.Forward(w, r, instance.podIP)

    case <-time.After(XHR_HOLD_TIMEOUT):
        // Timeout (2 min default)
        w.WriteHeader(504)
        w.Write("Gateway Timeout")

    case <-r.Context().Done():
        // Client cancelled
        return
    }
}
```

## Activity Update Logic

Only certain request types update LastActivity:

```go
func (c *RequestClassifier) UpdatesActivity() bool {
    switch c.Type {
    case PageLoad, XHR, FileOperation:
        return true
    case Longpoll, WebSocket, Static, Health:
        return false
    }
}
```

## Rate Limiting

Prevents abuse of wake functionality:

| Limit | Value | Scope |
|-------|-------|-------|
| Per-instance | 10/hour | Wake attempts |
| Per-IP | 100/hour | All requests |
| Global | 1000/min | All wakes |

## Error Detection

During pod startup, waking-service detects specific errors:

| Error | Detection | Retry |
|-------|-----------|-------|
| ImagePullFailed | Pod event | No |
| CrashLoopBackOff | Container status | No |
| OOMKilled | Termination reason | No |
| InsufficientResources | Pod condition | Yes |
| StartupTimeout | 5 min elapsed | Yes |
