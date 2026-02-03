# WebSocket Server Patterns

## Basic Server Setup

```typescript
import WebSocket, { Server } from 'ws';
import { createServer } from 'http';

const httpServer = createServer();
const wss = new Server({ server: httpServer });

wss.on('connection', (ws, req) => {
  const clientId = generateId();

  ws.on('message', (data) => handleMessage(ws, data));
  ws.on('close', () => handleClose(clientId));
  ws.on('error', (error) => handleError(clientId, error));
});

httpServer.listen(3001);
```

## Connection Management

### Client Tracking

```typescript
interface ClientState {
  id: string;
  userId: string;
  document: string;
  cursor?: { line: number; column: number };
  lastPing: number;
}

const clients = new Map<WebSocket, ClientState>();

function addClient(ws: WebSocket, userId: string, document: string) {
  clients.set(ws, {
    id: generateId(),
    userId,
    document,
    lastPing: Date.now(),
  });
}

function removeClient(ws: WebSocket) {
  clients.delete(ws);
}

function getClientsInDocument(docName: string): ClientState[] {
  return Array.from(clients.values())
    .filter((c) => c.document === docName);
}
```

### Heartbeat (Ping/Pong)

```typescript
const HEARTBEAT_INTERVAL = 30000;  // 30s
const HEARTBEAT_TIMEOUT = 60000;   // 60s

setInterval(() => {
  const now = Date.now();

  for (const [ws, client] of clients) {
    if (now - client.lastPing > HEARTBEAT_TIMEOUT) {
      // Client is dead
      ws.terminate();
      clients.delete(ws);
    } else {
      // Send ping
      ws.ping();
    }
  }
}, HEARTBEAT_INTERVAL);

// Update lastPing when pong received
ws.on('pong', () => {
  const client = clients.get(ws);
  if (client) client.lastPing = Date.now();
});
```

## Message Protocol

### Message Format

```typescript
interface Message {
  type: 'sync' | 'update' | 'presence' | 'ack' | 'error';
  docName?: string;
  payload: any;
  messageId?: string;  // For deduplication
}

function sendMessage(ws: WebSocket, msg: Message) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
  }
}

function handleMessage(ws: WebSocket, data: WebSocket.Data) {
  try {
    const msg: Message = JSON.parse(data.toString());

    switch (msg.type) {
      case 'sync':
        handleSync(ws, msg);
        break;
      case 'update':
        handleUpdate(ws, msg);
        break;
      case 'presence':
        handlePresence(ws, msg);
        break;
    }

    // Acknowledge receipt
    if (msg.messageId) {
      sendMessage(ws, { type: 'ack', payload: { messageId: msg.messageId } });
    }
  } catch (error) {
    sendMessage(ws, { type: 'error', payload: { message: 'Invalid message' } });
  }
}
```

### Broadcasting

```typescript
function broadcast(message: Message, exclude?: WebSocket) {
  const data = JSON.stringify(message);

  for (const [ws, client] of clients) {
    if (ws !== exclude && ws.readyState === WebSocket.OPEN) {
      // Only broadcast to clients in same document
      if (!message.docName || client.document === message.docName) {
        ws.send(data);
      }
    }
  }
}

// Broadcast file change to all clients
function notifyFileChange(path: string) {
  broadcast({
    type: 'update',
    docName: path,
    payload: { event: 'file-changed', path },
  });
}
```

## Yjs Integration

### Sync Protocol

```typescript
import * as Y from 'yjs';
import * as syncProtocol from 'y-protocols/sync';
import * as encoding from 'lib0/encoding';
import * as decoding from 'lib0/decoding';

const documents = new Map<string, Y.Doc>();

function getDoc(name: string): Y.Doc {
  if (!documents.has(name)) {
    documents.set(name, new Y.Doc());
  }
  return documents.get(name)!;
}

function handleYjsMessage(ws: WebSocket, data: Uint8Array) {
  const decoder = decoding.createDecoder(data);
  const messageType = decoding.readVarUint(decoder);

  if (messageType === 0) {  // Sync message
    const encoder = encoding.createEncoder();
    const doc = getDoc('current-doc');

    syncProtocol.readSyncMessage(decoder, encoder, doc, null);

    if (encoding.length(encoder) > 0) {
      ws.send(encoding.toUint8Array(encoder));
    }
  }
}
```

### Awareness (Cursor Sync)

```typescript
import * as awarenessProtocol from 'y-protocols/awareness';

const awareness = new awarenessProtocol.Awareness(doc);

// Set local cursor position
awareness.setLocalState({
  user: { id: userId, name: userName, color: '#ff0000' },
  cursor: { line: 10, column: 5 },
});

// Broadcast awareness to other clients
awareness.on('update', ({ added, updated, removed }) => {
  const encoder = encoding.createEncoder();
  encoding.writeVarUint(encoder, 1);  // Awareness message type
  encoding.writeVarUint8Array(
    encoder,
    awarenessProtocol.encodeAwarenessUpdate(awareness, [...added, ...updated])
  );
  broadcast({ type: 'awareness', payload: encoding.toUint8Array(encoder) });
});
```

## Scalability Patterns

### Redis Pub/Sub for Multi-Node

```typescript
import { createClient } from 'redis';

const publisher = createClient();
const subscriber = createClient();

await publisher.connect();
await subscriber.connect();

// Subscribe to updates from other nodes
await subscriber.subscribe('document-updates', (message) => {
  const update = JSON.parse(message);
  // Broadcast to local clients
  broadcast(update);
});

// Publish updates to other nodes
function publishUpdate(message: Message) {
  publisher.publish('document-updates', JSON.stringify(message));
}
```

### Connection Limits

| Metric | Recommended Limit |
|--------|------------------|
| Max connections per server | 10,000 |
| Max message size | 1 MB |
| Rate limit per client | 100 msg/sec |
| Max documents per server | 1,000 |

```typescript
const MAX_CONNECTIONS = 10000;
const MAX_MESSAGE_SIZE = 1024 * 1024;  // 1MB

wss.on('connection', (ws, req) => {
  if (clients.size >= MAX_CONNECTIONS) {
    ws.close(4003, 'Server at capacity');
    return;
  }
  // ... handle connection
});

ws.on('message', (data) => {
  if (data.length > MAX_MESSAGE_SIZE) {
    sendMessage(ws, { type: 'error', payload: { message: 'Message too large' } });
    return;
  }
  // ... handle message
});
```
