# Wrangler Configuration Reference

Configuration for Cloudflare Workers and Pages via `wrangler.jsonc` (recommended) or `wrangler.toml`. Place at the project root.

## Worker Configuration

Minimal `wrangler.jsonc` for a Worker:

```jsonc
{
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2024-12-01",
  "compatibility_flags": ["nodejs_compat"]
}
```

## Pages Configuration

Minimal `wrangler.jsonc` for a Pages project with Functions:

```jsonc
{
  "name": "my-site",
  "pages_build_output_dir": "dist",
  "compatibility_date": "2024-12-01"
}
```

## Bindings

### D1 Database

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-db",
      "database_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  ]
}
```

Access in Worker: `env.DB.prepare("SELECT * FROM users").all()`

### KV Namespace

```jsonc
{
  "kv_namespaces": [
    {
      "binding": "MY_KV",
      "id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }
  ]
}
```

Access in Worker: `env.MY_KV.get(key)`, `env.MY_KV.put(key, value)`

### R2 Bucket

```jsonc
{
  "r2_buckets": [
    {
      "binding": "BUCKET",
      "bucket_name": "my-bucket"
    }
  ]
}
```

Access in Worker: `env.BUCKET.put(key, data)`, `env.BUCKET.get(key)`

### Durable Objects

```jsonc
{
  "durable_objects": {
    "bindings": [
      {
        "name": "COUNTER",
        "class_name": "Counter"
      }
    ]
  },
  "migrations": [
    {
      "tag": "v1",
      "new_classes": ["Counter"]
    }
  ]
}
```

### Workers AI

```jsonc
{
  "ai": {
    "binding": "AI"
  }
}
```

Access in Worker: `env.AI.run("@cf/meta/llama-3.1-8b-instruct", { prompt: "..." })`

### Queues

```jsonc
{
  "queues": {
    "producers": [
      { "binding": "MY_QUEUE", "queue": "my-queue" }
    ],
    "consumers": [
      { "queue": "my-queue", "max_batch_size": 10 }
    ]
  }
}
```

### Service Bindings

```jsonc
{
  "services": [
    {
      "binding": "AUTH_SERVICE",
      "service": "auth-worker"
    }
  ]
}
```

## Environments

Define per-environment overrides:

```jsonc
{
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2024-12-01",
  "env": {
    "staging": {
      "vars": {
        "ENVIRONMENT": "staging",
        "API_URL": "https://staging-api.example.org"
      },
      "routes": [
        { "pattern": "staging.example.org/*", "zone_name": "example.org" }
      ]
    },
    "production": {
      "vars": {
        "ENVIRONMENT": "production",
        "API_URL": "https://api.example.org"
      },
      "routes": [
        { "pattern": "api.example.org/*", "zone_name": "example.org" }
      ]
    }
  }
}
```

Deploy to environment: `npx wrangler deploy --env staging`

## Routes and Custom Domains

```jsonc
{
  "routes": [
    { "pattern": "api.example.org/*", "zone_name": "example.org" }
  ]
}
```

Or use a custom domain (automatic DNS + SSL):

```jsonc
{
  "routes": [
    { "pattern": "api.example.org", "custom_domain": true }
  ]
}
```

## Cron Triggers

```jsonc
{
  "triggers": {
    "crons": ["0 */6 * * *", "0 0 * * MON"]
  }
}
```

Handler in Worker:

```typescript
export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    // Runs on cron schedule
  }
};
```

## Build and Upload Settings

```jsonc
{
  "minify": true,
  "node_compat": true,
  "upload_source_maps": true,
  "limits": {
    "cpu_ms": 50
  },
  "placement": {
    "mode": "smart"
  }
}
```

## Assets (Static Files)

Serve static assets alongside a Worker:

```jsonc
{
  "assets": {
    "directory": "./public",
    "binding": "ASSETS"
  }
}
```

## Compatibility Flags

Common flags to enable newer runtime features:

| Flag | Purpose |
|------|---------|
| `nodejs_compat` | Enable Node.js built-in module support |
| `streams_enable_constructors` | Enable ReadableStream constructors |
| `transformstream_enable_standard_constructor` | Standard TransformStream |
| `url_standard` | Standard URL API behavior |

```jsonc
{
  "compatibility_flags": ["nodejs_compat"]
}
```
