# Render Blueprint Specification

`render.yaml` in repo root defines infrastructure as code.

## Root Structure

```yaml
services: []         # Web, worker, cron, static, private
databases: []        # PostgreSQL, Redis
envVarGroups: []     # Reusable env var groups
previews:
  generation: auto_preview | manual | none
```

## Service Types

| Type | Purpose | Public URL | Port Required |
|------|---------|-----------|---------------|
| `web` | HTTP servers, APIs | Yes | Yes (0.0.0.0:$PORT) |
| `worker` | Background jobs | No | No |
| `cron` | Scheduled tasks | No | No |
| `web` + `static` | Static sites via CDN | Yes | No |
| `pserv` | Internal-only services | No | Yes |

**Required fields** (all types): `name`, `type`, `runtime`, `buildCommand`, `startCommand`
**Cron extra**: `schedule` (cron syntax, UTC)
**Static extra**: `staticPublishPath` (e.g., `./dist`)

## Plans and Regions

| Plan | RAM | CPU | Price |
|------|-----|-----|-------|
| `free` | 512MB | 0.5 | Free (750 hrs/mo, spins down after 15min idle) |
| `starter` | 512MB | 0.5 | $7/mo |
| `standard` | 2GB | 1 | $25/mo |
| `pro` | 4GB | 2 | $85/mo |

**Always default to `plan: free`.** Regions: `oregon` (default), `ohio`, `virginia`, `frankfurt`, `singapore`.

## Environment Variables

```yaml
envVars:
  - key: NODE_ENV                    # 1. Hardcoded value
    value: production
  - key: SESSION_SECRET              # 2. Auto-generated secret
    generateValue: true
  - key: API_KEY                     # 3. User fills in Dashboard
    sync: false
  - key: DATABASE_URL                # 4. Database reference
    fromDatabase:
      name: postgres
      property: connectionString     # or host, port, user, password, database
  - key: API_URL                     # 5. Service reference
    fromService:
      name: api-server
      type: web
      property: host                 # or port, hostport
  - fromGroup: shared-config         # 6. Shared group
```

## Databases

```yaml
databases:
  - name: postgres
    databaseName: app_prod
    user: app_user
    plan: free           # 1GB storage, 97MB RAM
    postgresMajorVersion: "15"
  - name: redis
    plan: free
    maxmemoryPolicy: allkeys-lru
```

## Scaling and Health

```yaml
# Manual scaling
numInstances: 3

# Autoscaling (paid plans)
scaling:
  minInstances: 1
  maxInstances: 5
  targetCPUPercent: 60

# Health check
healthCheckPath: /health

# Build filters (monorepos)
buildFilter:
  paths: [frontend/**]
  ignoredPaths: [frontend/**/*.test.js]
```

## Static Site Routing

```yaml
routes:
  - type: rewrite          # SPA catch-all
    source: /*
    destination: /index.html
headers:
  - path: /static/*
    name: Cache-Control
    value: public, max-age=31536000, immutable
```

Full docs: https://render.com/docs/blueprint-spec
