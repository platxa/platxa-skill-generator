# Vercel Project Configuration

Reference for `vercel.json` settings that control build behavior, routing, headers, and environment configuration.

## vercel.json Basics

Place `vercel.json` at the project root. It overrides auto-detected settings.

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm ci",
  "devCommand": "npm run dev"
}
```

## Build Configuration

| Field | Type | Description |
|-------|------|-------------|
| `framework` | string | Override auto-detected framework (`nextjs`, `vite`, `astro`, etc.) |
| `buildCommand` | string | Custom build command (replaces framework default) |
| `outputDirectory` | string | Directory containing build output |
| `installCommand` | string | Custom install command (default: auto-detected from lockfile) |
| `ignoreCommand` | string | Script that returns exit 0 to skip build, exit 1 to proceed |

## Framework Build Defaults

| Framework | Build Command | Output Dir | Install |
|-----------|--------------|------------|---------|
| Next.js | `next build` | `.next` | `npm install` |
| Vite | `vite build` | `dist` | `npm install` |
| Astro | `astro build` | `dist` | `npm install` |
| SvelteKit | `vite build` | `.svelte-kit/output` | `npm install` |
| Nuxt | `nuxt build` | `.output` | `npm install` |
| Remix | `remix build` | `build` | `npm install` |
| Gatsby | `gatsby build` | `public` | `npm install` |
| Static HTML | (none) | `.` | (none) |

## Rewrites and Redirects

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.backend.example.org/:path*" },
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "redirects": [
    { "source": "/old", "destination": "/new", "permanent": true },
    { "source": "/blog/:slug", "destination": "https://blog.example.org/:slug", "statusCode": 308 }
  ]
}
```

SPA fallback rewrite (serves `index.html` for all non-file routes):

```json
{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
```

## Headers

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    },
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

## Environment Variables

Environment variables are configured per-environment in the Vercel Dashboard or via the Vercel CLI:

```bash
vercel env add DATABASE_URL production
vercel env ls
vercel env pull .env.local
```

In `vercel.json`, reference build-time env vars:

```json
{
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "https://api.prod.example.org"
    }
  }
}
```

## Monorepo Configuration

For monorepos with multiple deployable packages, set the root directory in project settings or use `vercel.json`:

```json
{
  "rootDirectory": "packages/web",
  "buildCommand": "cd ../.. && npm run build --workspace=packages/web",
  "outputDirectory": "packages/web/dist"
}
```

## Serverless Function Configuration

```json
{
  "functions": {
    "api/*.js": {
      "memory": 1024,
      "maxDuration": 30
    },
    "api/heavy-task.js": {
      "memory": 3008,
      "maxDuration": 60
    }
  }
}
```

| Field | Default | Range |
|-------|---------|-------|
| `memory` | 1024 MB | 128-3008 MB |
| `maxDuration` | 10s (Hobby), 60s (Pro) | 1-300s |

## Cron Jobs

```json
{
  "crons": [
    { "path": "/api/daily-cleanup", "schedule": "0 0 * * *" },
    { "path": "/api/hourly-sync", "schedule": "0 * * * *" }
  ]
}
```
