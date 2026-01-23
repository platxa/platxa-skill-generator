---
name: platxa-preview-service
description: Live preview service for Odoo themes with real-time token updates, SCSS compilation, and WebSocket hot reload.
version: 1.0.0
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Platxa Preview Service

Enable real-time visual preview of generated Odoo themes without requiring a full Odoo installation.

## Overview

The Preview Service is the critical component that enables a Lovable-like experience for Odoo website generation. It provides:

- **Real-time Preview**: See changes instantly as you edit
- **Token Injection**: Brand Kit colors applied live via CSS variables
- **SCSS Compilation**: Full Odoo SCSS pipeline simulation
- **WebSocket Hot Reload**: Sub-100ms update latency
- **Section Library**: Preview all available sections

## Quick Start

### Start Preview Server

```bash
# Development mode
python scripts/preview_server.py --dev --port 8080

# With specific tokens
python scripts/preview_server.py --tokens path/to/tokens.json
```

### Create Preview Session

```bash
# Via CLI
python scripts/preview_cli.py create-session --tokens tokens.json

# Returns session ID for preview URL
# Preview at: http://localhost:8080/preview/{session_id}/about
```

### Update Preview

```bash
# Update tokens
python scripts/preview_cli.py update-tokens --session abc123 --tokens new_tokens.json

# Update page
python scripts/preview_cli.py update-page --session abc123 --page about --config page.json
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

### Component Overview

```
┌─────────────────────────────────────────────┐
│            Preview Service                   │
├─────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────────┐   │
│  │ REST API    │  │ WebSocket Server    │   │
│  │ (FastAPI)   │  │ (Live Reload)       │   │
│  └─────────────┘  └─────────────────────┘   │
│                                             │
│  ┌─────────────┐  ┌─────────────────────┐   │
│  │ Template    │  │ SCSS Compiler       │   │
│  │ Renderer    │  │ (libsass)           │   │
│  └─────────────┘  └─────────────────────┘   │
│                                             │
│  ┌─────────────┐  ┌─────────────────────┐   │
│  │ Token Sync  │  │ Section Library     │   │
│  │ (OKLCH→CSS) │  │ (HTML Templates)    │   │
│  └─────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────┘
```

## API Reference

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/sessions` | Create session | Returns `{session_id}` |
| `GET /api/sessions/{id}` | Get session | Returns session config |
| `DELETE /api/sessions/{id}` | Delete session | Cleanup resources |
| `PUT /api/sessions/{id}/tokens` | Update tokens | Triggers reload |
| `POST /api/sessions/{id}/pages` | Update page | Add/modify page |
| `GET /preview/{id}/{page}` | Render preview | Returns HTML |

### WebSocket Protocol

Connect to `/ws/{session_id}` for live updates.

**Client → Server:**
```json
{"type": "token_update", "tokens": {...}}
{"type": "page_update", "page_id": "about", "content": {...}}
```

**Server → Client:**
```json
{"type": "reload"}
{"type": "css_update", "css": "..."}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PREVIEW_PORT` | 8080 | Server port |
| `PREVIEW_HOST` | 0.0.0.0 | Server host |
| `SESSION_TIMEOUT` | 1800 | Session timeout (seconds) |
| `MAX_SESSIONS` | 100 | Max concurrent sessions |
| `SCSS_CACHE_SIZE` | 50 | CSS cache entries |

### Token Schema

```json
{
  "meta": {
    "name": "Brand Kit Name",
    "version": "1.0.0"
  },
  "colors": {
    "primary": {"hex": "#8B35A8", "oklch": [0.52, 0.18, 300]},
    "accent": {"hex": "#2ECCC4", "oklch": [0.75, 0.15, 180]},
    "neutral": {
      "dark": {"hex": "#1C1C21"},
      "light": {"hex": "#F0F0F0"},
      "background": {"hex": "#FAFAFA"}
    }
  },
  "typography": {
    "families": {
      "sans": "'Inter', sans-serif",
      "mono": "'JetBrains Mono', monospace"
    }
  },
  "spacing": {
    "unit": 8
  }
}
```

## Integration

### With platxa-token-sync

Preview inherits token sync for consistent colors:

```python
from platxa_preview import PreviewSession
from platxa_token_sync import sync_tokens

# Sync tokens and create preview
scss_vars = sync_tokens(brand_kit)
session = PreviewSession(tokens=brand_kit)
```

### With platxa-odoo-page

Preview generated pages instantly:

```python
from platxa_preview import PreviewSession
from platxa_odoo_page import generate_page

# Generate and preview
page_config = generate_page(PageConfig(page_type='about', ...))
session.add_page('about', page_config)
```

### With Frontend Editor

```typescript
// React/Vue integration
import { PreviewClient } from '@platxa/preview-client';

const preview = new PreviewClient(sessionId);

// Real-time token updates
const handleColorChange = (color: string) => {
  preview.updateTokens({
    colors: { primary: { hex: color } }
  });
};

// Embed preview iframe
<iframe src={`${PREVIEW_URL}/preview/${sessionId}/about`} />
```

## Development

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend assets)
- libsass

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python scripts/preview_server.py --dev

# Run tests
pytest tests/
```

### Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Load tests
locust -f tests/load/locustfile.py
```

## Deployment

### Docker

```bash
docker build -t platxa/preview-service .
docker run -p 8080:8080 platxa/preview-service
```

### Kubernetes

```bash
kubectl apply -f k8s/preview-deployment.yaml
kubectl apply -f k8s/preview-service.yaml
```

## Performance

| Metric | Target | Measured |
|--------|--------|----------|
| Preview render | < 200ms | ~150ms |
| Live reload | < 100ms | ~80ms |
| Concurrent sessions | 1000+ | Tested 500 |
| Memory/session | < 50MB | ~30MB |

## Troubleshooting

### Preview Not Loading

1. Check session exists: `GET /api/sessions/{id}`
2. Verify tokens are valid JSON
3. Check browser console for WebSocket errors

### CSS Not Updating

1. Clear browser cache
2. Check SCSS compilation logs
3. Verify token format matches schema

### WebSocket Disconnects

1. Check session timeout settings
2. Verify network allows WebSocket
3. Check server logs for errors
