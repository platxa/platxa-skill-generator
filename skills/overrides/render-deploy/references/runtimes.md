# Render Runtimes

## Native Runtimes

| Runtime | Versions | Default | Version Source |
|---------|----------|---------|----------------|
| `node` | 14-21 | 20 | `package.json` engines |
| `python` | 3.8-3.12 | 3.11 | `runtime.txt` or `Pipfile` |
| `go` | 1.20-1.23 | Latest | `go.mod` |
| `ruby` | 3.0-3.3 | 3.3 | `.ruby-version` or `Gemfile` |
| `rust` | Latest | Latest | Cargo |
| `elixir` | Latest | Latest | Mix |

## Build & Start by Language

**Node.js**: Detects npm/yarn/pnpm/bun from lockfile.
```yaml
buildCommand: npm ci && npm run build
startCommand: npm start
```

**Python**: Detects pip/poetry/pipenv/uv from lockfile.
```yaml
buildCommand: pip install -r requirements.txt
startCommand: gunicorn app:app --bind 0.0.0.0:$PORT    # Flask
startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT  # FastAPI
startCommand: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT  # Django
```

**Go**:
```yaml
buildCommand: go build -o bin/app .
startCommand: ./bin/app
```

**Ruby**:
```yaml
buildCommand: bundle install && bundle exec rails assets:precompile
startCommand: bundle exec puma -C config/puma.rb
```

## Container Runtimes

**Docker** (`runtime: docker`): Build from Dockerfile.
```yaml
runtime: docker
dockerfilePath: ./Dockerfile
dockerContext: .
```

**Image** (`runtime: image`): Deploy pre-built image.
```yaml
runtime: image
image: ghcr.io/org/app:v1.2.3
```

## Static Runtime

```yaml
runtime: static
buildCommand: npm ci && npm run build
staticPublishPath: ./dist    # React: ./build, Next.js: ./out, Gatsby: ./public
```

## Comparison

| Runtime | Build Speed | Cold Start | Best For |
|---------|-------------|------------|----------|
| Node.js | Fast | Fast | APIs, full-stack (Next.js, Remix) |
| Python | Medium | Medium | Data apps, ML, Django/Flask/FastAPI |
| Go | Fast | Very fast | High-perf APIs, microservices |
| Docker | Varies | Medium | Custom deps, multi-language |
| Static | Very fast | N/A | SPAs, docs, marketing sites |
