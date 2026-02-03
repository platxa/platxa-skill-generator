# REST API & Process Management

## Fastify API Setup

```typescript
import Fastify from 'fastify';
import fastifyMultipart from '@fastify/multipart';

const app = Fastify({
  logger: {
    level: 'info',
    transport: {
      target: 'pino-pretty',
      options: { colorize: true },
    },
  },
});

// File upload support
await app.register(fastifyMultipart, {
  limits: { fileSize: 10 * 1024 * 1024 },  // 10MB
});

await app.listen({ port: 3000, host: '0.0.0.0' });
```

## File API Endpoints

```typescript
// List files
app.get('/files', async () => {
  const files = await listFiles('/workspace');
  return { files };
});

// Read file
app.get('/files/:path', async (req, reply) => {
  const path = decodeURIComponent(req.params.path);
  if (!isPathSafe('/workspace', path)) {
    return reply.status(403).send({ error: 'Invalid path' });
  }

  try {
    const content = await fs.readFile(`/workspace/${path}`, 'utf-8');
    return { path, content };
  } catch (error) {
    return reply.status(404).send({ error: 'File not found' });
  }
});

// Write file
app.put('/files/:path', async (req, reply) => {
  const path = decodeURIComponent(req.params.path);
  const { content } = req.body as { content: string };

  await fs.mkdir(dirname(`/workspace/${path}`), { recursive: true });
  await fs.writeFile(`/workspace/${path}`, content, 'utf-8');
  return { success: true };
});

// Delete file
app.delete('/files/:path', async (req) => {
  const path = decodeURIComponent(req.params.path);
  await fs.unlink(`/workspace/${path}`);
  return { success: true };
});

// Upload file
app.post('/files/:path/upload', async (req) => {
  const data = await req.file();
  const chunks: Buffer[] = [];
  for await (const chunk of data.file) chunks.push(chunk);

  const buffer = Buffer.concat(chunks);
  await fs.writeFile(`/workspace/${req.params.path}`, buffer);
  return { success: true, size: buffer.length };
});
```

## Git Endpoints

```typescript
// Get status
app.get('/git/status', async () => {
  const status = await gitService.status();
  return {
    staged: status.staged,
    modified: status.modified,
    untracked: status.not_added,
  };
});

// Commit changes
app.post('/git/commit', async (req) => {
  const { message } = req.body as { message: string };
  const commit = await gitService.commit(message);
  return { commit };
});

// Get diff
app.get('/git/diff', async (req) => {
  const { path } = req.query as { path?: string };
  const diff = await gitService.diff(path);
  return { diff };
});

// Get log
app.get('/git/log', async (req) => {
  const { count = 10 } = req.query as { count?: number };
  const log = await gitService.log(count);
  return { commits: log.all };
});
```

## Process Execution

### Safe Command Execution

```typescript
import { exec, spawn } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Allowed commands whitelist
const ALLOWED_COMMANDS = ['odoo', 'pip', 'python3'];

function isCommandAllowed(cmd: string): boolean {
  const binary = cmd.split(' ')[0];
  return ALLOWED_COMMANDS.includes(binary);
}

async function executeCommand(cmd: string, timeout = 60000) {
  if (!isCommandAllowed(cmd)) {
    throw new Error(`Command not allowed: ${cmd}`);
  }

  const { stdout, stderr } = await execAsync(cmd, {
    timeout,
    maxBuffer: 10 * 1024 * 1024,  // 10MB
    cwd: '/workspace',
  });

  return { stdout, stderr };
}
```

### Odoo Module Operations

```typescript
// Reload module
app.post('/deploy/:module', async (req, reply) => {
  const { module } = req.params;

  // Validate module name
  if (!/^[a-z_][a-z0-9_]*$/.test(module)) {
    return reply.status(400).send({ error: 'Invalid module name' });
  }

  try {
    // Auto-commit first
    await gitService.commit(`Deploy: ${module}`);

    // Reload module
    const result = await executeCommand(
      `odoo -c /etc/odoo/odoo.conf -u ${module} --stop-after-init`
    );

    return { success: true, output: result.stdout };
  } catch (error) {
    return reply.status(500).send({ error: error.message });
  }
});

// Install module
app.post('/install/:module', async (req) => {
  const { module } = req.params;

  const result = await executeCommand(
    `odoo -c /etc/odoo/odoo.conf -i ${module} --stop-after-init`
  );

  return { success: true, output: result.stdout };
});
```

### Streaming Output

```typescript
app.get('/logs/odoo', { websocket: true }, (connection) => {
  const tail = spawn('tail', ['-f', '/var/log/odoo/odoo.log']);

  tail.stdout.on('data', (data) => {
    connection.socket.send(data.toString());
  });

  connection.socket.on('close', () => {
    tail.kill();
  });
});
```

## Graceful Shutdown

```typescript
const shutdownHandlers: (() => Promise<void>)[] = [];

function onShutdown(handler: () => Promise<void>) {
  shutdownHandlers.push(handler);
}

async function shutdown() {
  logger.info('Shutdown started');

  for (const handler of shutdownHandlers) {
    try {
      await handler();
    } catch (error) {
      logger.error({ error }, 'Shutdown handler failed');
    }
  }

  logger.info('Shutdown complete');
  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

// Register cleanup handlers
onShutdown(async () => await app.close());
onShutdown(async () => await fileWatcher.close());
onShutdown(async () => await wsServer.stop());
```

## Health Check

```typescript
app.get('/health', async () => {
  return {
    status: 'ok',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    connections: wsServer.clientCount,
  };
});

app.get('/ready', async (req, reply) => {
  // Check all dependencies
  const checks = {
    workspace: await checkWorkspace(),
    git: await checkGit(),
    websocket: wsServer.isRunning,
  };

  const allHealthy = Object.values(checks).every(Boolean);

  if (!allHealthy) {
    return reply.status(503).send({ status: 'not ready', checks });
  }

  return { status: 'ready', checks };
});
```

## Error Handling Middleware

```typescript
app.setErrorHandler((error, req, reply) => {
  logger.error({
    error: error.message,
    stack: error.stack,
    url: req.url,
    method: req.method,
  }, 'Request error');

  if (error.code === 'ENOENT') {
    return reply.status(404).send({ error: 'Not found' });
  }

  if (error.code === 'EACCES') {
    return reply.status(403).send({ error: 'Permission denied' });
  }

  return reply.status(500).send({ error: 'Internal server error' });
});
```
