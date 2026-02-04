# Render Service Types

## Quick Comparison

| Feature | Web | Worker | Cron | Static | Private (`pserv`) |
|---------|-----|--------|------|--------|-------------------|
| Public URL | Yes | No | No | Yes (CDN) | No |
| Port binding | Required | No | No | N/A | Required |
| Health checks | Yes | No | No | N/A | Yes |
| Persistent | Yes | Yes | No (runs & exits) | Yes | Yes |
| Scaling | Yes | Yes | No | Yes | Yes |

## When to Use Each

**Web** (`type: web`): REST/GraphQL APIs, web apps, WebSocket servers, SSR (Next.js, Django, Rails). Gets HTTPS URL, load balancing, custom domains.

**Worker** (`type: worker`): Queue processors (Celery, BullMQ, Sidekiq), event consumers, background jobs. No public URL, long-running.

**Cron** (`type: cron`): Scheduled tasks (backups, reports, cleanup). Runs on schedule then exits. Schedule in UTC cron syntax.

Common schedules: `*/15 * * * *` (every 15min), `0 0 * * *` (daily midnight), `0 9 * * 1` (Monday 9AM).

**Static** (`type: web`, `runtime: static`): SPAs (React, Vue), static generators (Gatsby, Hugo), docs sites. Served via CDN, needs `staticPublishPath` and SPA rewrite rules.

**Private** (`type: pserv`): Internal APIs, microservices, DB proxies. Accessible only via `[name].render-internal.com` within same account.

## Minimal Examples

```yaml
# Web
- type: web
  name: api
  runtime: node
  buildCommand: npm ci
  startCommand: npm start

# Worker
- type: worker
  name: jobs
  runtime: python
  buildCommand: pip install -r requirements.txt
  startCommand: celery -A tasks worker

# Cron
- type: cron
  name: backup
  runtime: node
  schedule: "0 2 * * *"
  buildCommand: npm ci
  startCommand: node scripts/backup.js

# Static
- type: web
  name: frontend
  runtime: static
  buildCommand: npm ci && npm run build
  staticPublishPath: ./dist
```
