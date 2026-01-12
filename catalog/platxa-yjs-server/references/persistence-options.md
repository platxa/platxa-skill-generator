# Yjs Persistence Options Reference

Storage backends for document durability.

## Persistence Comparison

| Backend | Environment | Use Case | Recovery |
|---------|-------------|----------|----------|
| In-memory | Any | Development | None |
| y-indexeddb | Browser | Offline support | Client-side |
| y-leveldb | Node.js | Server persistence | Server-side |
| File system | Node.js | Git integration | Server-side |

## y-indexeddb (Browser)

Client-side persistence for offline editing:

```typescript
import { IndexeddbPersistence } from 'y-indexeddb';

const doc = new Y.Doc();
const persistence = new IndexeddbPersistence('doc-name', doc);

persistence.on('synced', () => {
  console.log('Loaded from IndexedDB');
});

// Data survives page reload
// Syncs with server when WebSocket reconnects
```

## y-leveldb (Node.js)

Server-side persistence for crash recovery:

```typescript
import { LeveldbPersistence } from 'y-leveldb';

const ldb = new LeveldbPersistence('./yjs-data');

// Get persisted document
const doc = await ldb.getYDoc('document-name');

// Store updates
doc.on('update', (update) => {
  ldb.storeUpdate('document-name', update);
});

// Clear document
await ldb.clearDocument('document-name');
```

## y-websocket Persistence API

Integrate with y-websocket server:

```typescript
import { setPersistence } from 'y-websocket/bin/utils';
import { LeveldbPersistence } from 'y-leveldb';

const ldb = new LeveldbPersistence('./data');

setPersistence({
  bindState: async (docName, ydoc) => {
    const persisted = await ldb.getYDoc(docName);
    Y.applyUpdate(ydoc, Y.encodeStateAsUpdate(persisted));

    ydoc.on('update', (update) => {
      ldb.storeUpdate(docName, update);
    });
  },
  writeState: async (docName, ydoc) => {
    // Called when document closes
  }
});
```

## File System Persistence

Custom persistence with file writes:

```typescript
import fs from 'fs/promises';

async function saveToFile(docName: string, ydoc: Y.Doc) {
  const content = ydoc.getText('content').toString();
  await fs.writeFile(`./workspace/${docName}`, content, 'utf-8');
}

async function loadFromFile(docName: string, ydoc: Y.Doc) {
  try {
    const content = await fs.readFile(`./workspace/${docName}`, 'utf-8');
    ydoc.getText('content').insert(0, content);
  } catch (e) {
    // New file
  }
}
```

## Debounced Persistence

Avoid excessive writes:

```typescript
const pendingWrites = new Map<string, NodeJS.Timeout>();

function debouncedPersist(docName: string, ydoc: Y.Doc, delay = 300) {
  if (pendingWrites.has(docName)) {
    clearTimeout(pendingWrites.get(docName));
  }

  pendingWrites.set(docName, setTimeout(async () => {
    await saveToFile(docName, ydoc);
    pendingWrites.delete(docName);
  }, delay));
}
```

## Backup Strategy

| Strategy | Frequency | Retention |
|----------|-----------|-----------|
| LevelDB snapshot | Continuous | Latest state |
| File system | On idle (300ms) | Current + git history |
| Git commit | On save | Full history |
| External backup | Daily | Point-in-time recovery |
