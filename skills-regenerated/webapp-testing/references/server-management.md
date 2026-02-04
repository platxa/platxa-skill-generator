# Server Management with with_server.py

Advanced usage, troubleshooting, and configuration for the bundled server lifecycle helper.

## Basic Usage

```bash
# Single server
python scripts/with_server.py --server "npm run dev" --port 5173 -- python checks.py

# Multiple servers
python scripts/with_server.py \
  --server "cd api && uvicorn main:app --port 8000" --port 8000 \
  --server "cd web && npm run dev" --port 5173 \
  -- python checks.py
```

## How It Works

1. Starts each server as a subprocess using `shell=True`
2. Polls `localhost:<port>` via TCP socket every 500ms until connection succeeds
3. After all servers are ready, runs the specified command
4. On exit (success or failure), terminates all server processes via `SIGTERM`
5. If `SIGTERM` does not stop a server within 5 seconds, sends `SIGKILL`

## CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--server "<cmd>"` | Server command (repeatable) | Required |
| `--port <int>` | Port to poll for readiness (must match `--server` count) | Required |
| `--timeout <int>` | Seconds to wait per server before failing | 30 |

## Common Server Commands

| Framework | Command | Default Port |
|-----------|---------|--------------|
| Vite (React/Vue/Svelte) | `npm run dev` | 5173 |
| Next.js | `npm run dev` | 3000 |
| Create React App | `npm start` | 3000 |
| Django | `python manage.py runserver 0.0.0.0:8000` | 8000 |
| FastAPI | `uvicorn main:app --port 8000` | 8000 |
| Flask | `flask run --port 5000` | 5000 |
| Express | `node server.js` | 3000 |
| Go | `go run ./cmd/server` | 8080 |

## Troubleshooting

### Server fails to start within timeout

Increase the timeout:

```bash
python scripts/with_server.py --server "npm run build && npm start" --port 3000 --timeout 120 -- python checks.py
```

If the build step takes a long time, run the build separately first:

```bash
npm run build
python scripts/with_server.py --server "npm start" --port 3000 -- python checks.py
```

### Port already in use

Find and kill the process using the port:

```bash
lsof -ti:5173 | xargs kill -9
```

Or use a different port:

```bash
python scripts/with_server.py --server "PORT=5174 npm run dev" --port 5174 -- python checks.py
```

### Server starts but check script cannot connect

Ensure the server binds to `0.0.0.0` or `localhost`, not `127.0.0.1` only. Some frameworks need explicit host configuration:

```bash
# Vite
python scripts/with_server.py --server "npx vite --host 0.0.0.0" --port 5173 -- python checks.py

# Django
python scripts/with_server.py --server "python manage.py runserver 0.0.0.0:8000" --port 8000 -- python checks.py
```

### Orphan processes after interruption

If `with_server.py` is killed with `SIGKILL` (kill -9), child processes may survive. Clean up manually:

```bash
# Find node/python processes on the expected ports
lsof -ti:5173,8000 | xargs kill
```

## Integration with CI

```yaml
# GitHub Actions example
- name: Run webapp validation
  run: |
    npm ci
    pip install playwright && playwright install chromium --with-deps
    python scripts/with_server.py --server "npm run dev" --port 5173 --timeout 60 \
      -- python validate_app.py
```

The exit code of `with_server.py` matches the exit code of the command it runs. A non-zero exit fails the CI step.
