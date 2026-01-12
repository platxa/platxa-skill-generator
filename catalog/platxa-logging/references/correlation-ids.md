# Correlation ID Patterns Reference

Request tracing across Platxa services.

## Header Conventions

| Header | Usage |
|--------|-------|
| `X-Request-ID` | Primary (Platxa default) |
| `X-Correlation-ID` | Alternative |
| `traceparent` | W3C Trace Context |

**Rules**: Check incoming header first → Generate UUID v4 if missing → Propagate to all downstream calls.

## Python Implementation

### ContextVar (Thread-Safe)

```python
import uuid
from contextvars import ContextVar

_request_id: ContextVar[str] = ContextVar('request_id', default='')

def get_request_id() -> str:
    rid = _request_id.get()
    if not rid:
        rid = str(uuid.uuid4())
        _request_id.set(rid)
    return rid

def set_request_id(rid: str) -> None:
    _request_id.set(rid)
```

### Flask Middleware

```python
from flask import Flask, request, g, Response

@app.before_request
def extract_request_id():
    rid = request.headers.get('X-Request-ID') or str(uuid.uuid4())
    g.request_id = rid
    set_request_id(rid)

@app.after_request
def add_request_id_header(response: Response) -> Response:
    response.headers['X-Request-ID'] = g.request_id
    return response
```

### FastAPI Middleware

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        set_request_id(request_id)
        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response
```

### Propagate to Downstream

```python
import httpx

async def call_downstream(url: str, data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data,
            headers={'X-Request-ID': get_request_id()})
        return response.json()
```

## Go Implementation

### Context-Based Storage

```go
type contextKey string
const RequestIDKey contextKey = "request_id"

func GetRequestID(ctx context.Context) string {
    if reqID, ok := ctx.Value(RequestIDKey).(string); ok {
        return reqID
    }
    return ""
}

func WithRequestID(ctx context.Context, reqID string) context.Context {
    return context.WithValue(ctx, RequestIDKey, reqID)
}
```

### HTTP Middleware

```go
func RequestIDMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        reqID := r.Header.Get("X-Request-ID")
        if reqID == "" {
            reqID = uuid.New().String()
        }
        ctx := WithRequestID(r.Context(), reqID)
        w.Header().Set("X-Request-ID", reqID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## TypeScript Implementation

### Express Middleware

```typescript
import { v4 as uuidv4 } from 'uuid';

export function requestIdMiddleware(req: Request, res: Response, next: NextFunction) {
  const requestId = (req.headers['x-request-id'] as string) || uuidv4();
  req.context = { requestId, startTime: new Date() };
  res.setHeader('X-Request-ID', requestId);
  next();
}
```

### Fetch Wrapper

```typescript
export async function fetchWithCorrelation<T>(
  url: string, requestId: string, options: RequestInit = {}
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: { ...options.headers, 'X-Request-ID': requestId },
  });
  return response.json();
}
```

## Best Practices

**Do:**
- Generate ID at service boundary if missing
- Include in ALL log entries
- Propagate to ALL downstream calls
- Use UUID v4 for uniqueness

**Don't:**
- Generate new ID if header exists
- Log without correlation ID
- Use sequential IDs (security risk)

## Debugging

```bash
# Loki query
{namespace="instance-abc123"} |= "request_id=550e8400"

# kubectl logs
kubectl logs -l app=waking-service | grep "550e8400"
```
