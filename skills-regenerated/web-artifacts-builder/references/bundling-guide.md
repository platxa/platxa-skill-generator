# Bundling Guide

How the Vite + Parcel + html-inline pipeline produces a single self-contained HTML artifact.

## Pipeline Overview

```
src/*.tsx  -->  Vite (dev)  -->  Parcel (prod build)  -->  html-inline  -->  bundle.html
                                  |                         |
                                  dist/index.html           Single file with
                                  dist/index.*.js           all JS/CSS inlined
                                  dist/index.*.css
```

Vite handles development (HMR, TypeScript, JSX transforms). Parcel handles production bundling with tree-shaking and minification. html-inline collapses the multi-file dist/ output into one HTML file.

## Parcel Configuration

The `.parcelrc` file enables TypeScript path alias resolution:

```json
{
  "extends": "@parcel/config-default",
  "resolvers": ["parcel-resolver-tspaths", "..."]
}
```

- `parcel-resolver-tspaths` reads `tsconfig.json` paths and resolves `@/` imports
- `"..."` falls back to the default Parcel resolvers for node_modules

## Build Command

```bash
pnpm exec parcel build index.html --dist-dir dist --no-source-maps
```

| Flag | Purpose |
|------|---------|
| `index.html` | Entry point (must be in project root) |
| `--dist-dir dist` | Output directory |
| `--no-source-maps` | Skip source maps (reduces bundle size) |

## Inlining

```bash
pnpm exec html-inline dist/index.html > bundle.html
```

html-inline reads the HTML, finds all `<script src="...">` and `<link rel="stylesheet" href="...">` tags, reads the referenced files, and replaces the tags with inline `<script>` and `<style>` blocks.

## Common Build Issues

### Path Alias Errors

```
@parcel/core: Failed to resolve '@/components/ui/button'
```

Fix: Ensure `.parcelrc` exists with `parcel-resolver-tspaths` and `tsconfig.json` has:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

### Missing index.html

Parcel requires `index.html` in the project root (not `src/`). The init script places it correctly. If moved, update the build command entry point.

### Large Bundle Size

Typical artifact bundles range from 80-200 KB. If exceeding 500 KB:

1. Check for accidentally imported large libraries (moment.js, lodash full)
2. Use tree-shakeable imports: `import { format } from "date-fns"` not `import * as dateFns`
3. Remove unused shadcn/ui component files from `src/components/ui/`
4. Check for embedded base64 images or large inline data

### Node Version Compatibility

| Node Version | Vite Version | Notes |
|-------------|-------------|-------|
| 18.x | Pinned to 5.4.11 | Last Vite 5 release supporting Node 18 |
| 20.x+ | Latest (6+) | Full support, recommended |

The init script auto-detects Node version and pins Vite accordingly.

## Dev Server vs Production Build

| Feature | Dev (Vite) | Prod (Parcel) |
|---------|-----------|---------------|
| Command | `pnpm dev` | `pnpm exec parcel build` |
| Output | In-memory, served at localhost:5173 | dist/ directory |
| Source maps | Yes (inline) | No (disabled) |
| Minification | No | Yes |
| Tree-shaking | Partial | Full |
| HMR | Yes | No |

Use `pnpm dev` during development for fast iteration. Use the bundle script only when ready to produce the final artifact.
