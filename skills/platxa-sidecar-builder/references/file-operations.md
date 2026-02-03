# File Operations Reference

## Chokidar Configuration

### Production Setup

```typescript
import chokidar from 'chokidar';

const watcher = chokidar.watch('/workspace', {
  persistent: true,
  ignored: [
    '**/node_modules',
    '**/.git',
    '**/__pycache__',
    '**/.venv',
    '**/.*',  // Hidden files
  ],
  // Wait for writes to complete
  awaitWriteFinish: {
    stabilityThreshold: 500,  // Wait 500ms after last change
    pollInterval: 100,
  },
  alwaysStat: true,  // Provide file stats
  usePolling: false,  // Use native fs.watch (faster)
});
```

### Event Handling

| Event | Trigger | Use Case |
|-------|---------|----------|
| `add` | New file created | Sync to clients |
| `change` | File modified | Update Yjs doc |
| `unlink` | File deleted | Remove from sync |
| `addDir` | Directory created | Optional tracking |
| `unlinkDir` | Directory deleted | Optional tracking |
| `ready` | Initial scan complete | Start processing |
| `error` | Watcher error | Log and recover |

### Debouncing Pattern

```typescript
const debounceTimers = new Map<string, NodeJS.Timeout>();

function debounced(path: string, callback: () => void, delay = 300) {
  if (debounceTimers.has(path)) {
    clearTimeout(debounceTimers.get(path)!);
  }
  debounceTimers.set(path, setTimeout(() => {
    callback();
    debounceTimers.delete(path);
  }, delay));
}

watcher.on('change', (path) => {
  debounced(path, () => processFileChange(path));
});
```

## Git Operations with simple-git

### Initialization

```typescript
import { simpleGit } from 'simple-git';

const git = simpleGit({
  baseDir: '/workspace',
  trimmed: true,
  timeout: 30000,  // 30s for long operations
});

await git.init();
await git.addConfig('user.name', 'Platxa Editor');
await git.addConfig('user.email', 'editor@platxa.local');
```

### Common Operations

```typescript
// Stage and commit
await git.add('.');
const result = await git.commit('Update module');

// Check status
const status = await git.status();
console.log('Staged:', status.staged);
console.log('Modified:', status.modified);

// Get diff
const diff = await git.diff(['path/to/file.py']);

// View history
const log = await git.log({ maxCount: 10 });

// Reset changes
await git.reset(['--hard']);  // Discard all changes
await git.checkout(['path/to/file.py']);  // Discard specific file
```

### Auto-Commit on Save

```typescript
const pendingCommits = new Map<string, NodeJS.Timeout>();

async function autoCommit(path: string) {
  // Debounce commits (wait 5s after last change)
  if (pendingCommits.has(path)) {
    clearTimeout(pendingCommits.get(path)!);
  }

  pendingCommits.set(path, setTimeout(async () => {
    try {
      await git.add(path);
      await git.commit(`Auto-save: ${path}`);
      logger.info({ path }, 'Auto-committed');
    } catch (error) {
      logger.error({ error, path }, 'Auto-commit failed');
    }
    pendingCommits.delete(path);
  }, 5000));
}
```

## File System Operations

### Safe File Writing

```typescript
import fs from 'fs/promises';
import path from 'path';

async function writeFileSafe(filePath: string, content: string) {
  const dir = path.dirname(filePath);

  // Ensure directory exists
  await fs.mkdir(dir, { recursive: true });

  // Write to temp file first (atomic write)
  const tempPath = `${filePath}.tmp`;
  await fs.writeFile(tempPath, content, 'utf-8');
  await fs.rename(tempPath, filePath);
}
```

### Directory Traversal Prevention

```typescript
function isPathSafe(basePath: string, requestedPath: string): boolean {
  const resolved = path.resolve(basePath, requestedPath);
  return resolved.startsWith(path.resolve(basePath));
}

// Usage
app.get('/files/:path', async (req) => {
  const filePath = req.params.path;

  if (!isPathSafe('/workspace', filePath)) {
    return reply.status(403).send({ error: 'Invalid path' });
  }

  const content = await fs.readFile(`/workspace/${filePath}`, 'utf-8');
  return { content };
});
```

### File Listing with Filtering

```typescript
async function listFiles(dir: string, filter?: RegExp): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files: string[] = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
        files.push(...await listFiles(fullPath, filter));
      }
    } else if (!filter || filter.test(entry.name)) {
      files.push(fullPath);
    }
  }

  return files;
}

// List Python files
const pythonFiles = await listFiles('/workspace', /\.py$/);
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| `ENOENT` | File not found | Return 404 or create |
| `EACCES` | Permission denied | Log and report |
| `ENOSPC` | Disk full | Alert operator |
| `EMFILE` | Too many open files | Increase ulimit |

```typescript
try {
  await fs.readFile(path, 'utf-8');
} catch (error) {
  if (error.code === 'ENOENT') {
    return { content: '', exists: false };
  }
  throw error;
}
```
