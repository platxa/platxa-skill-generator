# netlify.toml Configuration Reference

File-based configuration for Netlify builds, deploys, redirects, and headers. Place at the repository root.

## Build Settings

```toml
[build]
  command = "npm run build"
  publish = "dist"
  functions = "netlify/functions"
  base = "packages/web"           # Monorepo subdirectory
  ignore = "git diff --quiet HEAD^ HEAD -- src/"
```

## Environment Variables

```toml
[build.environment]
  NODE_VERSION = "20"
  NPM_FLAGS = "--prefer-offline"

[context.production.environment]
  NODE_ENV = "production"
  NEXT_PUBLIC_API_URL = "https://api.prod.example.org"

[context.deploy-preview.environment]
  NODE_ENV = "staging"
```

## Framework Presets

| Framework | command | publish |
|-----------|---------|---------|
| Next.js | `npm run build` | `.next` |
| Vite | `npm run build` | `dist` |
| Astro | `npm run build` | `dist` |
| SvelteKit | `npm run build` | `build` |
| Gatsby | `npm run build` | `public` |
| Static | (omit) | `.` |

## Redirects and Rewrites

```toml
# SPA client-side routing fallback
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

# API proxy to backend
[[redirects]]
  from = "/api/*"
  to = "https://api.backend.example.org/:splat"
  status = 200
  force = true

# Permanent redirect
[[redirects]]
  from = "/old-page"
  to = "/new-page"
  status = 301
```

## Custom Headers

```toml
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

## Context Overrides

Different settings per deploy context (production, deploy-preview, branch-deploy, or named branch):

```toml
[context.production]
  command = "npm run build:prod"

[context.deploy-preview]
  command = "npm run build:preview"

[context.staging]
  command = "npm run build:staging"
  [context.staging.environment]
    API_BASE = "https://staging-api.example.org"
```

## Asset Processing

```toml
[build.processing.css]
  bundle = true
  minify = true

[build.processing.js]
  bundle = true
  minify = true

[build.processing.html]
  pretty_urls = true

[build.processing.images]
  compress = true
```

## Build Plugins

```toml
[[plugins]]
  package = "@netlify/plugin-lighthouse"
  [plugins.inputs]
    output_path = "reports/lighthouse.html"
```

## Validation

Dry-run to verify configuration without deploying:

```bash
npx netlify build --dry
```
