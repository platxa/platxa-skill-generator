# Yjs WebSocket API Reference

Protocol and message format for y-websocket synchronization.

## Connection Endpoints

| Endpoint | Purpose |
|----------|---------|
| `ws://host:port/{room}` | Standard y-websocket |
| `ws://host:port/ws/doc/{path}` | Per-file documents (Platxa) |

## Authentication

Use `Sec-WebSocket-Protocol` header (not query params):

```typescript
// Client
const ws = new WebSocket(url, [authToken]);

// Server
const token = req.headers['sec-websocket-protocol'];
jwt.verify(token, secret);
```

## Sync Protocol Flow

```
Client                          Server
  │                               │
  ├── Connect ───────────────────▶│
  │                               │
  │◀── Sync Step 0 (state vector)─┤
  │                               │
  ├── Sync Step 1 (diff) ────────▶│
  │                               │
  │◀── Sync Step 2 (diff) ───────┤
  │                               │
  │◀─── Updates (continuous) ────▶│
  │                               │
```

## Message Types

| Type | Code | Direction | Purpose |
|------|------|-----------|---------|
| Sync Step 0 | 0 | Server → Client | Initial state vector |
| Sync Step 1 | 1 | Client → Server | Client diff |
| Sync Step 2 | 2 | Server → Client | Server diff |
| Update | 3 | Bidirectional | Incremental changes |
| Awareness | 1 | Bidirectional | Presence data |

## Message Format

Binary messages with type prefix:

```typescript
// Encoding
const encoder = encoding.createEncoder();
encoding.writeVarUint(encoder, messageType);
syncProtocol.writeSyncStep1(encoder, doc);
const message = encoding.toUint8Array(encoder);

// Decoding
const decoder = decoding.createDecoder(message);
const messageType = decoding.readVarUint(decoder);
```

## Reconnection Logic

Exponential backoff with jitter:

```typescript
function reconnect(attempt: number) {
  const base = 1000;
  const max = 30000;
  const delay = Math.min(base * Math.pow(2, attempt), max);
  const jitter = delay * 0.25 * (Math.random() * 2 - 1);

  setTimeout(() => connect(), delay + jitter);
}
```

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 4000 | Bad Request | Check room/path |
| 4001 | Unauthorized | Refresh token |
| 4003 | Forbidden | Document locked |
| 4008 | Timeout | Reconnect |
| 1006 | Abnormal Close | Reconnect |

## Server Implementation

Custom server without y-websocket utils:

```typescript
import { syncProtocol, awarenessProtocol } from 'y-protocols';
import * as encoding from 'lib0/encoding';
import * as decoding from 'lib0/decoding';

ws.on('message', (data) => {
  const decoder = decoding.createDecoder(new Uint8Array(data));
  const messageType = decoding.readVarUint(decoder);

  switch (messageType) {
    case 0: // Sync
      const syncType = decoding.readVarUint(decoder);
      // Handle sync step 0, 1, 2
      break;
    case 1: // Awareness
      awarenessProtocol.applyAwarenessUpdate(awareness, data, ws);
      break;
  }
});
```

## Connection State

Track connection health:

```typescript
provider.on('status', ({ status }) => {
  // 'disconnected' | 'connecting' | 'connected'
});

provider.on('sync', (synced: boolean) => {
  // true when initial sync complete
});
```
