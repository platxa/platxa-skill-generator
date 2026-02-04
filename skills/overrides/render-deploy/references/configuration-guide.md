# Render Configuration Guide

Essential configuration patterns for Render deployments.

## Port Binding (CRITICAL)

Web services MUST bind to `0.0.0.0:$PORT`. Render sets `PORT` (default 10000).

| Language | Code |
|----------|------|
| Node/Express | `app.listen(process.env.PORT \|\| 3000, '0.0.0.0')` |
| Python/Flask | `app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))` |
| Python/FastAPI | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Python/Django | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |
| Go | `http.ListenAndServe(":"+os.Getenv("PORT"), nil)` |
| Ruby/Rails | `bundle exec puma -b tcp://0.0.0.0:$PORT` |

## Build Commands (Non-Interactive)

| Tool | Command |
|------|---------|
| npm | `npm ci` (not `npm install`) |
| yarn | `yarn install --frozen-lockfile` |
| pnpm | `pnpm install --frozen-lockfile` |
| pip | `pip install -r requirements.txt` |
| bundler | `bundle install --jobs=4 --retry=3` |
| apt | `apt-get install -y <pkg>` |

With build step: `npm ci && npm run build`
Django static: `pip install -r requirements.txt && python manage.py collectstatic --no-input`
Prisma: `npm ci && npx prisma migrate deploy`

## Database Connections

Use `fromDatabase` for automatic internal URLs (`.render-internal.com`):
```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: postgres
      property: connectionString
```

Connection pooling recommended: `max: 20`, `idleTimeoutMillis: 30000`.

## Health Checks

Add `/health` endpoint returning `200 OK`:
```javascript
app.get('/health', (req, res) => res.status(200).json({ status: 'ok' }));
```

Configure: `healthCheckPath: /health`

## Free Tier Limits

- 512MB RAM, 0.5 CPU, 750 hrs/mo, 100GB bandwidth
- PostgreSQL: 1GB storage, 97MB RAM
- Spins down after 15min idle (~30s cold start)

## Common Issues

| Symptom | Fix |
|---------|-----|
| Port binding error | Bind to `0.0.0.0:$PORT` |
| Build timeout (15min) | Use `npm ci`, remove unused deps |
| Missing env vars | Declare all in render.yaml, use `sync: false` for secrets |
| DB connection refused | Use `fromDatabase` for internal URLs |
| SPA 404s on routes | Add rewrite rule: `source: /* -> destination: /index.html` |
| OOM (exit 137) | Reduce memory or upgrade plan |
