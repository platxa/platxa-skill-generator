---
name: platxa-yjs-server
description: Yjs WebSocket server implementation guide for real-time collaboration. Configure y-websocket, awareness cursors, and persistence with production-ready patterns.
allowed-tools:
  - Read
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - guide
    - yjs
    - websocket
    - collaboration
    - crdt
---

# Platxa Yjs Server

Guide for implementing Yjs WebSocket servers for real-time collaborative editing in the Platxa platform.

## Overview

This skill covers the server-side implementation of Yjs CRDT synchronization:

| Component | What You Can Configure |
|-----------|----------------------|
| **y-websocket Server** | WebSocket setup, room management, connection handling |
| **Awareness Protocol** | User presence, cursor positions, selection highlighting |
| **Persistence** | LevelDB, IndexedDB, file system, git integration |
| **Authentication** | JWT validation, session management, single-user enforcement |
| **Error Handling** | Reconnection, conflict resolution, graceful degradation |

## Workflow

When implementing a Yjs server, follow this workflow:

### Step 1: Choose Architecture

Determine your requirements:
- **Single-document**: One Y.Doc shared by all clients (simple chat, whiteboard)
- **Multi-document**: Separate Y.Doc per file/room (code editor, multi-file IDE)
- **Auth model**: Anonymous, JWT, session-based

### Step 2: Setup Server

Choose implementation approach:
- **y-websocket utils**: Use built-in `setupWSConnection` for quick start
- **Custom server**: Build on raw WebSocket for full control

### Step 3: Configure Awareness

Add user presence features:
- Set local state (user id, name, color)
- Handle awareness updates from other clients
- Render cursor decorations in editor

### Step 4: Add Persistence

Select storage backend based on needs:
- **Development**: In-memory (default, no persistence)
- **Production**: y-leveldb for Node.js server persistence
- **Client-side**: y-indexeddb for offline support
- **Audit trail**: Git commits on file save

## Quick Start

### Basic Server (Node.js)

```typescript
import { WebSocketServer } from 'ws';
import { setupWSConnection } from 'y-websocket/bin/utils';

const wss = new WebSocketServer({ port: 1234 });

wss.on('connection', (ws, req) => {
  setupWSConnection(ws, req);
});

console.log('Yjs server running on ws://localhost:1234');
```

### Basic Client

```typescript
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

const doc = new Y.Doc();
const provider = new WebsocketProvider(
  'ws://localhost:1234',
  'my-room',
  doc
);

// Access shared types
const yText = doc.getText('content');

// Listen for sync
provider.on('sync', (synced: boolean) => {
  console.log('Synced:', synced);
});
```

## Server Configuration Presets

### Basic (Development)

Minimal setup for local development:

```typescript
import { WebSocketServer } from 'ws';
import { setupWSConnection } from 'y-websocket/bin/utils';

const wss = new WebSocketServer({ port: 1234 });
wss.on('connection', setupWSConnection);
```

### Authenticated

JWT validation before allowing connection:

```typescript
import { WebSocketServer } from 'ws';
import { setupWSConnection } from 'y-websocket/bin/utils';
import jwt from 'jsonwebtoken';

const wss = new WebSocketServer({ port: 1234 });

wss.on('connection', (ws, req) => {
  // Get token from Sec-WebSocket-Protocol header
  const token = req.headers['sec-websocket-protocol'];

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    // Store user info for awareness
    (ws as any).user = payload;
    setupWSConnection(ws, req);
  } catch (err) {
    ws.close(4001, 'Unauthorized');
  }
});
```

### Persistent (LevelDB)

Documents survive server restarts:

```typescript
import { WebSocketServer } from 'ws';
import { setupWSConnection, setPersistence } from 'y-websocket/bin/utils';
import { LeveldbPersistence } from 'y-leveldb';

const ldb = new LeveldbPersistence('./yjs-data');

setPersistence({
  bindState: async (docName, ydoc) => {
    const persistedYdoc = await ldb.getYDoc(docName);
    const state = Y.encodeStateAsUpdate(persistedYdoc);
    Y.applyUpdate(ydoc, state);
    ydoc.on('update', (update) => {
      ldb.storeUpdate(docName, update);
    });
  },
  writeState: async (docName, ydoc) => {
    // Called on document close
  }
});

const wss = new WebSocketServer({ port: 1234 });
wss.on('connection', setupWSConnection);
```

### Platxa Production

Full setup with authentication, single-user, and file persistence:

```typescript
import { WebSocketServer } from 'ws';
import * as Y from 'yjs';
import { encoding, decoding, syncProtocol, awarenessProtocol } from 'y-protocols';
import fs from 'fs/promises';

const docs = new Map<string, Y.Doc>();
const sessions = new Map<string, { userId: string; expiry: number }>();

async function handleConnection(ws, req, user) {
  const docPath = req.url.replace('/ws/doc/', '');

  // Single-user check (bypass for AI)
  if (user.client_type !== 'ai') {
    const existing = sessions.get(docPath);
    if (existing && existing.userId !== user.id && existing.expiry > Date.now()) {
      ws.close(4003, 'Document locked by another user');
      return;
    }
    sessions.set(docPath, { userId: user.id, expiry: Date.now() + 30000 });
  }

  // Get or create Y.Doc
  let doc = docs.get(docPath);
  if (!doc) {
    doc = new Y.Doc();
    // Initialize from file system
    try {
      const content = await fs.readFile(`/mnt/addons/${docPath}`, 'utf-8');
      doc.getText('content').insert(0, content);
    } catch (e) {
      // New file
    }
    docs.set(docPath, doc);
  }

  // Setup sync protocol
  // ... (see references/websocket-api.md for full protocol)
}
```

## Awareness Protocol

### Setting User Presence

```typescript
// Client-side
provider.awareness.setLocalState({
  id: user.id,
  name: user.name,
  color: generateColor(user.id),
  colorLight: generateColor(user.id, 0.9),
  cursor: null  // Updated by Monaco binding
});

function generateColor(id: string, lightness = 0.45) {
  const hue = hashString(id) % 360;
  return `hsl(${hue}, 70%, ${lightness * 100}%)`;
}
```

### Reading Connected Users

```typescript
function getConnectedUsers(provider: WebsocketProvider) {
  const users: UserPresence[] = [];
  provider.awareness.getStates().forEach((state, clientId) => {
    if (state && clientId !== provider.awareness.clientID) {
      users.push(state as UserPresence);
    }
  });
  return users;
}

// Listen for changes
provider.awareness.on('change', () => {
  const users = getConnectedUsers(provider);
  updateUserList(users);
});
```

### Cursor Decorations (Monaco)

```typescript
import { MonacoBinding } from 'y-monaco';

const binding = new MonacoBinding(
  yText,
  editor.getModel(),
  new Set([editor]),
  provider.awareness  // Pass awareness for cursor sync
);
```

## Examples

### Example 1: Collaborative Text Editor

**User**: "Set up a simple Yjs server for collaborative text editing"

**Response**:

Server (server.ts):
```typescript
import { WebSocketServer } from 'ws';
import { setupWSConnection } from 'y-websocket/bin/utils';

const wss = new WebSocketServer({ port: 1234 });
wss.on('connection', (ws, req) => {
  console.log('Client connected');
  setupWSConnection(ws, req);
});
```

Client (client.ts):
```typescript
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

const doc = new Y.Doc();
const provider = new WebsocketProvider('ws://localhost:1234', 'document', doc);

// Setup awareness
provider.awareness.setLocalState({
  name: 'User ' + Math.floor(Math.random() * 100),
  color: `hsl(${Math.random() * 360}, 70%, 45%)`
});

const yText = doc.getText('content');
yText.observe(() => {
  console.log('Content:', yText.toString());
});
```

### Example 2: Multi-Room Document Server

**User**: "Handle multiple documents with JWT auth"

**Response**:

```typescript
import { WebSocketServer } from 'ws';
import * as Y from 'yjs';
import jwt from 'jsonwebtoken';

const docs = new Map<string, Y.Doc>();

function getDoc(roomName: string): Y.Doc {
  if (!docs.has(roomName)) {
    docs.set(roomName, new Y.Doc());
  }
  return docs.get(roomName)!;
}

const wss = new WebSocketServer({ port: 1234 });

wss.on('connection', (ws, req) => {
  const token = req.headers['sec-websocket-protocol'];

  try {
    const user = jwt.verify(token, process.env.JWT_SECRET) as any;
    const roomName = new URL(req.url, 'http://localhost').searchParams.get('room');

    if (!roomName) {
      ws.close(4000, 'Room name required');
      return;
    }

    const doc = getDoc(roomName);
    // Setup Yjs sync for this doc...

  } catch (err) {
    ws.close(4001, 'Invalid token');
  }
});
```

### Example 3: Persistent Server with Git Commits

**User**: "Documents should persist and have version history"

**Response**:

```typescript
import { WebSocketServer } from 'ws';
import { LeveldbPersistence } from 'y-leveldb';
import { setPersistence, setupWSConnection } from 'y-websocket/bin/utils';
import simpleGit from 'simple-git';
import fs from 'fs/promises';

const ldb = new LeveldbPersistence('./yjs-data');
const git = simpleGit('./workspace');

// Setup persistence
setPersistence({
  bindState: async (docName, ydoc) => {
    // Load from LevelDB
    const persisted = await ldb.getYDoc(docName);
    Y.applyUpdate(ydoc, Y.encodeStateAsUpdate(persisted));

    // Track updates
    ydoc.on('update', async (update) => {
      await ldb.storeUpdate(docName, update);
    });
  },
  writeState: async (docName, ydoc) => {
    // On document close, write to file and commit
    const content = ydoc.getText('content').toString();
    const filePath = `./workspace/${docName}`;

    await fs.writeFile(filePath, content);
    await git.add(filePath);
    await git.commit(`Update ${docName}`, { '--author': 'Yjs Server <yjs@local>' });
  }
});

const wss = new WebSocketServer({ port: 1234 });
wss.on('connection', setupWSConnection);
```

## Best Practices

### Security

| Practice | Implementation |
|----------|---------------|
| Auth via header | Use `Sec-WebSocket-Protocol`, not query params |
| Validate JWT | Check signature, expiry, and claims |
| Rate limiting | Limit connections per IP/user |
| Path validation | Prevent directory traversal in doc names |

### Performance

| Practice | Implementation |
|----------|---------------|
| One Y.Doc per file | Don't share docs across unrelated content |
| Debounce persistence | Write to disk every 300ms, not every update |
| Cleanup on disconnect | Destroy Y.Doc when last client leaves |
| Monitor memory | Track doc count and memory usage |

### Reliability

| Practice | Implementation |
|----------|---------------|
| Exponential backoff | Client reconnection: 1s, 2s, 4s, 8s... max 30s |
| Client persistence | Use y-indexeddb for offline support |
| Server persistence | Use y-leveldb for crash recovery |
| Audit trail | Git commits for version history |

## Troubleshooting

### Connection Not Established

**Symptom**: WebSocket connection fails immediately

**Causes & Fixes**:
- **CORS**: Ensure server allows origin
- **Auth format**: Use `Sec-WebSocket-Protocol` header, not Bearer
- **Protocol**: y-websocket v2 vs v3 incompatibility

### Awareness Not Syncing

**Symptom**: Can't see other users' cursors

**Causes & Fixes**:
- Pass awareness to MonacoBinding: `new MonacoBinding(yText, model, editors, awareness)`
- Verify provider connected: `provider.wsconnected`
- Check local state set: `provider.awareness.getLocalState()`

### Documents Empty After Restart

**Symptom**: All content lost on server restart

**Causes & Fixes**:
- Add persistence layer (y-leveldb)
- Check LevelDB path exists and is writable
- Verify `bindState` loads persisted content

### Memory Growing Over Time

**Symptom**: Node.js process memory increasing

**Causes & Fixes**:
- Track active docs, destroy on last client leave
- Set maximum doc count, evict LRU
- Check for event listener leaks (remove on cleanup)

## Output Checklist

After implementing Yjs server, verify:

- [ ] Server starts without errors on specified port
- [ ] Clients can connect and receive sync messages
- [ ] Changes sync between multiple clients in real-time
- [ ] Awareness shows connected users correctly
- [ ] Cursor positions update across clients
- [ ] Documents persist across server restarts (if configured)
- [ ] Authentication rejects invalid tokens
- [ ] Memory usage remains stable over time
- [ ] Reconnection works after network interruption

## Related Resources

- **Monaco Integration**: Use `platxa-monaco-config` skill for editor setup
- **Frontend Hooks**: See `YjsProvider`, `useYjsDocument`, `useMonacoBinding`
- **Awareness Details**: See `references/awareness-protocol.md`
- **Persistence Options**: See `references/persistence-options.md`
- **Protocol Reference**: See `references/websocket-api.md`
