---
name: platxa-sidecar-builder
description: Build Node.js sidecar services for real-time code editing platforms. Covers file watching, git operations, WebSocket servers, Yjs CRDT integration, REST APIs, and Kubernetes deployment patterns.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
metadata:
  version: "1.0.0"
  tags:
    - builder
    - nodejs
    - sidecar
    - yjs
    - websocket
    - kubernetes
---

# Platxa Sidecar Builder

Build Node.js sidecar services for real-time collaborative code editing platforms.

## Overview

This skill helps create sidecar services that power code editors like Replit, CodeSandbox, or the Platxa IDE. A sidecar runs alongside the main application (e.g., Odoo) in the same Kubernetes pod, handling:

| Component | Purpose |
|-----------|---------|
| **File Watcher** | Detect file changes with chokidar |
| **Git Service** | Version control with simple-git |
| **WebSocket Server** | Real-time sync with ws library |
| **Yjs Integration** | CRDT-based collaborative editing |
| **REST API** | File operations, deployment triggers |
| **Process Manager** | Execute odoo commands, module reloads |

**Integrates with**: `platxa-yjs-server` for Yjs server patterns.

## Workflow

### Step 1: Analyze Requirements

Determine what the sidecar needs to handle:
- File sync only → File watcher + REST API
- Real-time collaboration → Add WebSocket + Yjs
- Version control → Add Git service
- Deployment → Add Process manager

### Step 2: Create Project Structure

```
sidecar/
├── src/
│   ├── index.ts           # Entry point
│   ├── file-watcher.ts    # Chokidar integration
│   ├── git-service.ts     # Git operations
│   ├── websocket-server.ts # ws server
│   ├── yjs-service.ts     # Yjs CRDT sync
│   ├── api.ts             # Fastify REST API
│   ├── process-manager.ts # Child process handling
│   └── logging.ts         # Pino structured logging
├── package.json
├── tsconfig.json
└── Dockerfile
```

### Step 3: Implement Core Services

Use the templates below for each component.

### Step 4: Add Kubernetes Deployment

Create Pod manifest with native sidecar pattern (K8s 1.33+).

### Step 5: Validate Integration

- File changes sync to clients
- Git commits work correctly
- WebSocket reconnection handles network issues
- Graceful shutdown works

## Templates

### Entry Point

```typescript
// src/index.ts
import { FileWatcher } from './file-watcher';
import { GitService } from './git-service';
import { WebSocketServer } from './websocket-server';
import { YjsService } from './yjs-service';
import { createApiServer } from './api';
import { logger } from './logging';

async function main() {
  const workspacePath = process.env.WORKSPACE_PATH || '/workspace';
  const apiPort = parseInt(process.env.API_PORT || '3000');
  const wsPort = parseInt(process.env.WS_PORT || '3001');

  // Initialize services
  const gitService = new GitService(workspacePath);
  const yjsService = new YjsService();
  const wsServer = new WebSocketServer(wsPort, yjsService);
  const fileWatcher = new FileWatcher({
    workspacePath,
    ignored: ['**/node_modules', '**/.git', '**/__pycache__'],
  });

  await gitService.initialize();
  await wsServer.start();

  // File changes trigger Yjs updates
  fileWatcher.onChange(async (path, type) => {
    if (type === 'change' || type === 'add') {
      const content = await fs.promises.readFile(
        `${workspacePath}/${path}`, 'utf-8'
      );
      yjsService.reconcileWithFile(path, content);
      wsServer.broadcast({ type: 'file-changed', path });
    }
  });

  // Start REST API
  await createApiServer(apiPort, { gitService, yjsService, fileWatcher });

  logger.info({ workspacePath, apiPort, wsPort }, 'Sidecar started');

  // Graceful shutdown
  process.on('SIGTERM', async () => {
    logger.info('Shutting down...');
    await fileWatcher.close();
    await wsServer.stop();
    process.exit(0);
  });
}

main().catch((error) => {
  logger.fatal({ error }, 'Startup failed');
  process.exit(1);
});
```

### File Watcher

```typescript
// src/file-watcher.ts
import chokidar from 'chokidar';
import { logger } from './logging';

interface WatcherConfig {
  workspacePath: string;
  ignored?: string[];
}

export class FileWatcher {
  private watcher: chokidar.FSWatcher;
  private debounceTimers = new Map<string, NodeJS.Timeout>();

  constructor(config: WatcherConfig) {
    this.watcher = chokidar.watch(config.workspacePath, {
      persistent: true,
      ignored: config.ignored || [],
      awaitWriteFinish: { stabilityThreshold: 500, pollInterval: 100 },
      alwaysStat: true,
    });
  }

  onChange(callback: (path: string, type: 'add' | 'change' | 'unlink') => void) {
    const debounced = (path: string, type: 'add' | 'change' | 'unlink') => {
      if (this.debounceTimers.has(path)) {
        clearTimeout(this.debounceTimers.get(path)!);
      }
      this.debounceTimers.set(path, setTimeout(() => {
        callback(path, type);
        this.debounceTimers.delete(path);
      }, 300));
    };

    this.watcher.on('add', (path) => debounced(path, 'add'));
    this.watcher.on('change', (path) => debounced(path, 'change'));
    this.watcher.on('unlink', (path) => debounced(path, 'unlink'));
    return this;
  }

  async close() {
    for (const timer of this.debounceTimers.values()) clearTimeout(timer);
    await this.watcher.close();
  }
}
```

### Git Service

```typescript
// src/git-service.ts
import { simpleGit, SimpleGit } from 'simple-git';
import { logger } from './logging';

export class GitService {
  private git: SimpleGit;

  constructor(workspacePath: string) {
    this.git = simpleGit({ baseDir: workspacePath, timeout: 30000 });
  }

  async initialize() {
    await this.git.init();
    await this.git.addConfig('user.name', 'Platxa Editor');
    await this.git.addConfig('user.email', 'editor@platxa.local');
  }

  async commit(message: string): Promise<string> {
    await this.git.add('.');
    const result = await this.git.commit(message);
    logger.info({ commit: result.commit }, 'Committed');
    return result.commit;
  }

  async status() {
    return this.git.status();
  }

  async diff(path?: string) {
    return path ? this.git.diff([path]) : this.git.diff();
  }

  async log(count = 10) {
    return this.git.log({ maxCount: count });
  }
}
```

### WebSocket Server

```typescript
// src/websocket-server.ts
import WebSocket, { Server } from 'ws';
import { logger } from './logging';
import { YjsService } from './yjs-service';

export class WebSocketServer {
  private wss: Server;
  private clients = new Map<WebSocket, { id: string; lastPing: number }>();

  constructor(private port: number, private yjsService: YjsService) {
    this.wss = new Server({ port });
  }

  async start() {
    this.wss.on('connection', (ws, req) => {
      const clientId = `client_${Date.now()}`;
      this.clients.set(ws, { id: clientId, lastPing: Date.now() });

      logger.info({ clientId, total: this.clients.size }, 'Client connected');

      ws.on('message', (data) => this.handleMessage(ws, data));
      ws.on('close', () => this.handleClose(ws));
      ws.on('pong', () => {
        const client = this.clients.get(ws);
        if (client) client.lastPing = Date.now();
      });
    });

    // Heartbeat every 30s
    setInterval(() => {
      for (const [ws, client] of this.clients) {
        if (Date.now() - client.lastPing > 60000) {
          ws.terminate();
        } else {
          ws.ping();
        }
      }
    }, 30000);

    logger.info({ port: this.port }, 'WebSocket server started');
  }

  private handleMessage(ws: WebSocket, data: WebSocket.Data) {
    try {
      const msg = JSON.parse(data.toString());
      if (msg.type === 'yjs-update') {
        this.yjsService.applyUpdate(msg.docName, new Uint8Array(msg.update));
        this.broadcast(msg, ws);
      }
    } catch (error) {
      logger.error({ error }, 'Message handling failed');
    }
  }

  private handleClose(ws: WebSocket) {
    const client = this.clients.get(ws);
    this.clients.delete(ws);
    logger.info({ clientId: client?.id }, 'Client disconnected');
  }

  broadcast(message: any, exclude?: WebSocket) {
    const data = JSON.stringify(message);
    for (const [ws] of this.clients) {
      if (ws !== exclude && ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    }
  }

  async stop() {
    for (const [ws] of this.clients) ws.close();
    this.wss.close();
  }
}
```

### Kubernetes Deployment

```yaml
# k8s/sidecar-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: platxa-instance
spec:
  containers:
  - name: odoo
    image: odoo:18.0
    ports:
    - containerPort: 8069
    volumeMounts:
    - name: workspace
      mountPath: /mnt/addons

  initContainers:
  - name: editor-sync
    image: platxa/sidecar:latest
    restartPolicy: Always  # Native sidecar (K8s 1.33+)
    ports:
    - containerPort: 3000  # REST API
    - containerPort: 3001  # WebSocket
    env:
    - name: WORKSPACE_PATH
      value: /mnt/addons
    - name: API_PORT
      value: "3000"
    - name: WS_PORT
      value: "3001"
    volumeMounts:
    - name: workspace
      mountPath: /mnt/addons

  volumes:
  - name: workspace
    emptyDir: {}
```

## Examples

### Example 1: Basic File Sync Sidecar

**User**: "Create a sidecar that watches files and exposes a REST API"

**Response**:

```typescript
// Minimal sidecar with file watching and REST API
import Fastify from 'fastify';
import chokidar from 'chokidar';
import fs from 'fs/promises';

const app = Fastify({ logger: true });
const workspace = process.env.WORKSPACE_PATH || '/workspace';

// File watcher
const watcher = chokidar.watch(workspace, {
  ignored: ['**/node_modules', '**/.git'],
  awaitWriteFinish: { stabilityThreshold: 500 },
});

watcher.on('change', (path) => {
  app.log.info({ path }, 'File changed');
});

// REST endpoints
app.get('/files', async () => {
  const files = await fs.readdir(workspace, { recursive: true });
  return { files };
});

app.get('/files/:path', async (req) => {
  const content = await fs.readFile(`${workspace}/${req.params.path}`, 'utf-8');
  return { content };
});

app.put('/files/:path', async (req) => {
  await fs.writeFile(`${workspace}/${req.params.path}`, req.body.content);
  return { success: true };
});

await app.listen({ port: 3000, host: '0.0.0.0' });
```

### Example 2: Deploy Module to Odoo

**User**: "Add endpoint to reload Odoo modules"

**Response**:

```typescript
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

app.post('/deploy/:module', async (req) => {
  const { module } = req.params;

  try {
    // Commit changes first
    await gitService.commit(`Deploy ${module}`);

    // Reload module in Odoo
    const { stdout, stderr } = await execAsync(
      `odoo -c /etc/odoo/odoo.conf -u ${module} --stop-after-init`,
      { timeout: 60000 }
    );

    return { success: true, commit: await gitService.log(1) };
  } catch (error) {
    return { success: false, error: error.message };
  }
});
```

## Output Checklist

When building a sidecar service, verify:

- [ ] File watcher detects changes correctly
- [ ] Debouncing prevents duplicate events
- [ ] Git operations work (init, commit, status)
- [ ] WebSocket connections are stable
- [ ] Heartbeat detects stale connections
- [ ] Yjs documents sync between clients
- [ ] REST API handles all file operations
- [ ] Graceful shutdown closes all resources
- [ ] Structured logging captures events
- [ ] Kubernetes pod mounts shared volume

## Related Skills

- **platxa-yjs-server**: Detailed Yjs server patterns and awareness protocol
- **platxa-k8s-ops**: Kubernetes operations and debugging
- **platxa-logging**: Structured logging with correlation IDs
