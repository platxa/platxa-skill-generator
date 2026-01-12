# Correlation ID Patterns Reference

Detailed implementations for request tracing across Platxa services.

## What Are Correlation IDs?

A correlation ID (also called request ID, trace ID) is a unique identifier that follows a request through all services it touches. This enables:

- **Distributed Tracing**: Follow a request across microservices
- **Log Aggregation**: Query all logs for a single request
- **Debugging**: Trace errors back to their source
- **Performance Analysis**: Measure end-to-end latency

## Header Conventions

### Standard Headers

| Header | Usage | Notes |
|--------|-------|-------|
| `X-Request-ID` | Primary correlation ID | Most common, Platxa default |
| `X-Correlation-ID` | Alternative name | Same purpose |
| `X-Trace-ID` | OpenTelemetry/Jaeger | Part of distributed tracing |
| `traceparent` | W3C Trace Context | Standard format for tracing |

### Generation Rules

1. **Check incoming header first** - Reuse if present
2. **Generate at boundary** - Create if missing
3. **Use UUID v4** - Globally unique, no coordination needed
4. **Propagate always** - Include in all downstream requests

## Python Implementation

### Using ContextVar (Thread-Safe)

```python
import uuid
from contextvars import ContextVar
from typing import Optional

# Thread-safe storage - works with async and sync code
_request_id: ContextVar[str] = ContextVar('request_id', default='')

def get_request_id() -> str:
    """Get current request ID or generate new one."""
    rid = _request_id.get()
    if not rid:
        rid = str(uuid.uuid4())
        _request_id.set(rid)
    return rid

def set_request_id(rid: str) -> None:
    """Set request ID for current context."""
    _request_id.set(rid)

def clear_request_id() -> None:
    """Clear request ID (use at request end)."""
    _request_id.set('')
```

### Flask Middleware

```python
from flask import Flask, request, g, Response
import uuid

app = Flask(__name__)

@app.before_request
def extract_request_id():
    """Extract or generate request ID."""
    rid = request.headers.get('X-Request-ID')
    if not rid:
        rid = str(uuid.uuid4())
    g.request_id = rid
    set_request_id(rid)

@app.after_request
def add_request_id_header(response: Response) -> Response:
    """Add request ID to response headers."""
    response.headers['X-Request-ID'] = g.request_id
    return response

@app.teardown_request
def cleanup_request_id(exception=None):
    """Clean up request context."""
    clear_request_id()
```

### FastAPI Middleware

```python
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        set_request_id(request_id)

        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id

        clear_request_id()
        return response

app = FastAPI()
app.add_middleware(RequestIDMiddleware)
```

### Propagating to Downstream Services

```python
import httpx

async def call_downstream_service(url: str, data: dict) -> dict:
    """Call another service with correlation ID."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=data,
            headers={'X-Request-ID': get_request_id()}
        )
        return response.json()
```

## Go Implementation

### Context-Based Storage

```go
package correlation

import (
    "context"
    "github.com/google/uuid"
)

type contextKey string

const RequestIDKey contextKey = "request_id"

// GetRequestID retrieves request ID from context
func GetRequestID(ctx context.Context) string {
    if reqID, ok := ctx.Value(RequestIDKey).(string); ok {
        return reqID
    }
    return ""
}

// WithRequestID adds request ID to context
func WithRequestID(ctx context.Context, reqID string) context.Context {
    return context.WithValue(ctx, RequestIDKey, reqID)
}

// NewRequestID generates a new UUID
func NewRequestID() string {
    return uuid.New().String()
}
```

### HTTP Middleware

```go
package middleware

import (
    "net/http"
    "your-project/internal/correlation"
)

func RequestIDMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Check for existing header
        reqID := r.Header.Get("X-Request-ID")
        if reqID == "" {
            reqID = correlation.NewRequestID()
        }

        // Add to context
        ctx := correlation.WithRequestID(r.Context(), reqID)

        // Add to response header
        w.Header().Set("X-Request-ID", reqID)

        // Continue with enriched context
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

### Chi Router Example

```go
import "github.com/go-chi/chi/v5"

func SetupRouter() *chi.Mux {
    r := chi.NewRouter()

    // Add middleware early in chain
    r.Use(RequestIDMiddleware)
    r.Use(LoggingMiddleware)

    r.Get("/api/health", healthHandler)
    r.Post("/api/wake/{namespace}", wakeHandler)

    return r
}
```

### HTTP Client Propagation

```go
func (c *Client) DoWithContext(ctx context.Context, req *http.Request) (*http.Response, error) {
    // Propagate request ID to downstream service
    if reqID := correlation.GetRequestID(ctx); reqID != "" {
        req.Header.Set("X-Request-ID", reqID)
    }
    return c.httpClient.Do(req)
}
```

## TypeScript Implementation

### Request Context Type

```typescript
export interface RequestContext {
  requestId: string;
  sessionId?: string;
  userId?: string;
  startTime: Date;
}

export function createRequestContext(requestId?: string): RequestContext {
  return {
    requestId: requestId || crypto.randomUUID(),
    startTime: new Date(),
  };
}
```

### Express Middleware

```typescript
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

declare global {
  namespace Express {
    interface Request {
      context: RequestContext;
    }
  }
}

export function requestIdMiddleware(req: Request, res: Response, next: NextFunction) {
  const requestId = (req.headers['x-request-id'] as string) || uuidv4();

  req.context = {
    requestId,
    sessionId: req.sessionID,
    startTime: new Date(),
  };

  res.setHeader('X-Request-ID', requestId);
  next();
}

// Usage
app.use(requestIdMiddleware);
```

### Fetch Wrapper

```typescript
export async function fetchWithCorrelation<T>(
  url: string,
  context: RequestContext,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'X-Request-ID': context.requestId,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }

  return response.json();
}
```

### WebSocket Session Tracking

```typescript
class WebSocketSession {
  private sessionId: string;

  constructor() {
    this.sessionId = crypto.randomUUID();
  }

  get requestId(): string {
    return this.sessionId;
  }

  sendWithCorrelation(ws: WebSocket, data: unknown) {
    ws.send(JSON.stringify({
      ...data,
      _meta: {
        requestId: this.sessionId,
        timestamp: new Date().toISOString(),
      },
    }));
  }
}
```

## Best Practices

### Do

- Generate ID at service boundary if missing
- Include in ALL log entries
- Propagate to ALL downstream calls
- Store in response header for debugging
- Use UUID v4 for uniqueness

### Don't

- Generate new ID if header exists (breaks chain)
- Log without correlation ID
- Forget header in async callbacks
- Use sequential IDs (security risk)
- Store sensitive data in correlation ID

## Debugging with Correlation IDs

### Query Logs by ID

```bash
# Loki
{namespace="instance-abc123"} |= "request_id=550e8400-e29b-41d4-a716-446655440000"

# Grep across services
grep -r "550e8400-e29b-41d4-a716-446655440000" /var/log/platxa/

# kubectl logs
kubectl logs -l app=waking-service | grep "550e8400"
```

### Trace Request Flow

```
1. Frontend generates: 550e8400-e29b-41d4-a716-446655440000
2. AI Engine receives header, logs with ID
3. AI Engine calls Validator with same header
4. Validator logs with ID
5. AI Engine calls Sidecar with same header
6. Sidecar logs with ID
7. All logs queryable by single ID
```
