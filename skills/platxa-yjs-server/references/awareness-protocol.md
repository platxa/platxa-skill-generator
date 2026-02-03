# Yjs Awareness Protocol Reference

User presence and cursor synchronization for collaborative editing.

## User Presence Structure

```typescript
interface UserPresence {
  id: string;           // Unique user identifier
  name: string;         // Display name
  color: string;        // Cursor color (HSL format)
  colorLight: string;   // Selection highlight color
  cursor?: CursorState; // Current cursor position
}

interface CursorState {
  anchor: { line: number; column: number };
  head: { line: number; column: number };
}
```

## Setting Local State

```typescript
provider.awareness.setLocalState({
  id: user.id,
  name: user.name,
  color: `hsl(${hue}, 70%, 45%)`,
  colorLight: `hsl(${hue}, 70%, 90%)`
});
```

## Color Generation

Generate consistent colors from user ID:

```typescript
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function generateUserColor(userId: string) {
  const hue = hashString(userId) % 360;
  return {
    color: `hsl(${hue}, 70%, 45%)`,
    colorLight: `hsl(${hue}, 70%, 90%)`
  };
}
```

## Event Handlers

### Awareness Change

Fires when any client's state changes:

```typescript
provider.awareness.on('change', ({ added, updated, removed }) => {
  added.forEach(clientId => console.log('User joined:', clientId));
  removed.forEach(clientId => console.log('User left:', clientId));
});
```

### Get All States

```typescript
const states = provider.awareness.getStates();
states.forEach((state, clientId) => {
  if (clientId !== provider.awareness.clientID) {
    console.log('Remote user:', state.name);
  }
});
```

## Cursor CSS Decorations

For Monaco editor cursor rendering:

```css
.yRemoteSelection {
  background-color: var(--user-color-light);
}

.yRemoteSelectionHead {
  position: absolute;
  border-left: 2px solid var(--user-color);
  height: 100%;
}

.yRemoteSelectionHead::after {
  content: attr(data-user-name);
  position: absolute;
  top: -1.2em;
  left: 0;
  font-size: 10px;
  background: var(--user-color);
  color: white;
  padding: 1px 4px;
  border-radius: 2px;
}
```

## Awareness Cleanup

Remove local state on disconnect:

```typescript
window.addEventListener('beforeunload', () => {
  provider.awareness.setLocalState(null);
});

// Or on provider destroy
provider.destroy();  // Automatically clears awareness
```

## Protocol Messages

| Message Type | Direction | Purpose |
|--------------|-----------|---------|
| Awareness Update | Bidirectional | State changes |
| Awareness Query | Client → Server | Request all states |
| Awareness States | Server → Client | All current states |

Awareness uses separate message channel from document sync.
