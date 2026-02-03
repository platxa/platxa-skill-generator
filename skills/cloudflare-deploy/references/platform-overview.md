# Cloudflare Platform Overview

Condensed reference covering core deployment products. For full docs: https://developers.cloudflare.com

## Workers (Serverless Compute)

V8 isolates on 300+ locations. Sub-millisecond cold starts.

```typescript
// Module Worker (recommended)
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    return new Response('Hello World!');
  }
};
```

Config (`wrangler.jsonc`): `name`, `main`, `compatibility_date`, `bindings`.
Deploy: `npx wrangler deploy`

## Pages (JAMstack / Full-Stack)

Git-based deploys with preview URLs per branch. Supports Pages Functions (file-based routing on Workers runtime).

Deploy methods:
1. Git integration (Dashboard → Workers & Pages → Connect to Git)
2. Direct upload: `npx wrangler pages deploy ./dist`
3. CLI: `npm create cloudflare@latest`

## D1 (SQLite Database)

Serverless SQLite. 10GB per DB. 30-day Time Travel recovery.

```bash
wrangler d1 create my-db
wrangler d1 execute my-db --command "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
```

Bind in `wrangler.jsonc`: `{ "d1_databases": [{ "binding": "DB", "database_name": "my-db" }] }`
Access: `env.DB.prepare("SELECT * FROM users").all()`

## KV (Key-Value Store)

Eventually consistent (60s propagation). Read-optimized. 25MiB max value.

```bash
wrangler kv namespace create MY_KV
```

API: `env.MY_KV.put(key, value)`, `env.MY_KV.get(key)`, `env.MY_KV.delete(key)`

## R2 (Object Storage)

S3-compatible. Zero egress fees. Strong write consistency.

```bash
wrangler r2 bucket create my-bucket
```

Workers API: `env.BUCKET.put(key, data)`, `env.BUCKET.get(key)`, `env.BUCKET.list()`

## Durable Objects (Stateful Coordination)

Single-instance per ID. Strong consistency. WebSocket support. Use for: real-time collaboration, rate limiting, counters, sessions.

## Wrangler CLI

```bash
npm install -g wrangler
wrangler login                    # OAuth auth
wrangler dev                      # Local dev server
wrangler deploy                   # Deploy to production
wrangler d1/kv/r2/...             # Manage bindings
CLOUDFLARE_API_TOKEN=xxx          # CI/CD auth
```

## Product Selection

| Need | Product |
|------|---------|
| Run code at edge | Workers |
| Full-stack web app | Pages + Functions |
| SQL database | D1 |
| Key-value cache | KV |
| File/blob storage | R2 |
| Stateful coordination | Durable Objects |
| Task scheduling | Cron Triggers / Queues |
| Real-time video | Stream |
| DNS/CDN | managed by default |
