# Platxa Preview Service Architecture

**Priority:** P0 (Critical for Production)
**Status:** Design Complete

## Executive Summary

The Preview Service enables real-time visual preview of generated Odoo themes without requiring a full Odoo installation. This is the critical differentiator for a Lovable-like experience.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (React/Vue)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Brand Editor │  │ Page Builder │  │     Preview Panel        │  │
│  │   (tokens)   │  │  (sections)  │  │  (iframe + live reload)  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘  │
│         │                 │                        │                │
│         └─────────────────┼────────────────────────┘                │
│                           │                                         │
│                    WebSocket (Yjs CRDT)                             │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                      Preview Service (Python)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Token Sync   │  │ Template     │  │     Static File          │  │
│  │ (OKLCH→CSS)  │  │ Renderer     │  │     Server               │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Hot Reload   │  │ Asset        │  │     SCSS Compiler        │  │
│  │ Manager      │  │ Bundler      │  │     (libsass)            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Preview Server

**Technology:** FastAPI + Uvicorn

**Responsibilities:**
- Serve rendered HTML previews
- Compile SCSS to CSS on-the-fly
- Handle WebSocket connections for live reload
- Manage preview sessions

```python
# preview_server.py
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sass

app = FastAPI()

class PreviewSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.tokens: dict = {}
        self.pages: dict = {}
        self.websockets: list[WebSocket] = []

    async def broadcast_reload(self):
        """Notify all connected clients to reload."""
        for ws in self.websockets:
            await ws.send_json({"type": "reload"})

sessions: dict[str, PreviewSession] = {}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = sessions.setdefault(session_id, PreviewSession(session_id))
    session.websockets.append(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "token_update":
                session.tokens = data["tokens"]
                await session.broadcast_reload()
            elif data["type"] == "page_update":
                session.pages[data["page_id"]] = data["content"]
                await session.broadcast_reload()
    finally:
        session.websockets.remove(websocket)

@app.get("/preview/{session_id}/{page_type}")
async def preview_page(session_id: str, page_type: str):
    session = sessions.get(session_id)
    if not session:
        return HTMLResponse("<h1>Session not found</h1>", status_code=404)

    html = render_preview(session, page_type)
    return HTMLResponse(html)
```

### 2. Template Renderer

**Technology:** Jinja2 (mimics QWeb for preview)

**Responsibilities:**
- Render QWeb-like templates to HTML
- Inject CSS variables from tokens
- Handle dynamic content placeholders

```python
# template_renderer.py
from jinja2 import Environment, BaseLoader
from pathlib import Path

class PreviewRenderer:
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self.section_templates = self._load_section_templates()

    def render_page(self, page_config: dict, tokens: dict) -> str:
        """Render a complete page preview."""
        sections_html = ""
        for section in page_config.get("sections", []):
            section_html = self._render_section(section, tokens)
            sections_html += section_html

        return self._wrap_in_layout(sections_html, tokens, page_config)

    def _render_section(self, section: dict, tokens: dict) -> str:
        """Render a single section."""
        template_name = section.get("type", "hero")
        template = self.section_templates.get(template_name)
        if not template:
            return f"<!-- Section {template_name} not found -->"

        return template.render(
            section=section,
            tokens=tokens,
        )

    def _wrap_in_layout(self, content: str, tokens: dict, page: dict) -> str:
        """Wrap content in page layout with CSS."""
        css = self._generate_css(tokens)
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page.get('title', 'Preview')}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <style>{css}</style>
    <script>
        // Live reload connection
        const ws = new WebSocket(`ws://${{location.host}}/ws/{page.get('session_id', 'default')}`);
        ws.onmessage = (e) => {{
            const data = JSON.parse(e.data);
            if (data.type === 'reload') location.reload();
        }};
    </script>
</head>
<body>
    {content}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

    def _generate_css(self, tokens: dict) -> str:
        """Generate CSS from design tokens."""
        colors = tokens.get("colors", {})
        return f"""
:root {{
    --o-color-1: {colors.get('primary', {}).get('hex', '#8B35A8')};
    --o-color-2: {colors.get('accent', {}).get('hex', '#2ECCC4')};
    --o-color-3: {colors.get('neutral', {}).get('dark', {}).get('hex', '#1C1C21')};
    --o-color-4: {colors.get('neutral', {}).get('light', {}).get('hex', '#F0F0F0')};
    --o-color-5: {colors.get('neutral', {}).get('background', {}).get('hex', '#FAFAFA')};
}}

.o_cc.o_cc1 {{ background-color: var(--o-color-1); }}
.o_cc.o_cc2 {{ background-color: var(--o-color-2); }}
.o_cc.o_cc3 {{ background-color: var(--o-color-3); }}
.o_cc.o_cc4 {{ background-color: var(--o-color-4); }}
.o_cc.o_cc5 {{ background-color: var(--o-color-5); }}

.text-primary {{ color: var(--o-color-1) !important; }}
.btn-primary {{
    background-color: var(--o-color-1);
    border-color: var(--o-color-1);
}}
.btn-secondary {{
    background-color: var(--o-color-2);
    border-color: var(--o-color-2);
}}
"""
```

### 3. SCSS Compiler

**Technology:** libsass (via sass package)

**Responsibilities:**
- Compile Odoo SCSS to CSS
- Inject token variables
- Handle Bootstrap integration

```python
# scss_compiler.py
import sass
from pathlib import Path

class SCSSCompiler:
    def __init__(self, bootstrap_path: Path | None = None):
        self.bootstrap_path = bootstrap_path or Path("vendor/bootstrap/scss")

    def compile(self, scss_content: str, tokens: dict) -> str:
        """Compile SCSS with injected tokens."""
        variables = self._tokens_to_scss(tokens)
        full_scss = f"{variables}\n{scss_content}"

        try:
            css = sass.compile(
                string=full_scss,
                include_paths=[str(self.bootstrap_path)],
                output_style="compressed",
            )
            return css
        except sass.CompileError as e:
            return f"/* SCSS Error: {e} */"

    def _tokens_to_scss(self, tokens: dict) -> str:
        """Convert tokens to SCSS variables."""
        colors = tokens.get("colors", {})
        spacing = tokens.get("spacing", {})
        typography = tokens.get("typography", {})

        return f"""
// Generated from Brand Kit tokens
$o-color-1: {colors.get('primary', {}).get('hex', '#8B35A8')} !default;
$o-color-2: {colors.get('accent', {}).get('hex', '#2ECCC4')} !default;
$o-color-3: {colors.get('neutral', {}).get('dark', {}).get('hex', '#1C1C21')} !default;
$o-color-4: {colors.get('neutral', {}).get('light', {}).get('hex', '#F0F0F0')} !default;
$o-color-5: {colors.get('neutral', {}).get('background', {}).get('hex', '#FAFAFA')} !default;

$primary: $o-color-1;
$secondary: $o-color-2;
$body-bg: $o-color-5;
$body-color: $o-color-3;

$o-spacer: {spacing.get('unit', 8)}px !default;

$font-family-sans-serif: {typography.get('families', {}).get('sans', "'Inter', sans-serif")} !default;
$font-family-monospace: {typography.get('families', {}).get('mono', "'JetBrains Mono', monospace")} !default;
"""
```

### 4. Hot Reload Manager

**Technology:** Watchdog + WebSockets

**Responsibilities:**
- Watch for file changes
- Debounce rapid changes
- Trigger selective reloads

```python
# hot_reload.py
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable

class HotReloadManager:
    def __init__(self, watch_paths: list[str], on_change: Callable):
        self.watch_paths = watch_paths
        self.on_change = on_change
        self.observer = Observer()
        self._debounce_task = None
        self._pending_changes = set()

    def start(self):
        """Start watching for changes."""
        handler = self._create_handler()
        for path in self.watch_paths:
            self.observer.schedule(handler, path, recursive=True)
        self.observer.start()

    def stop(self):
        """Stop watching."""
        self.observer.stop()
        self.observer.join()

    def _create_handler(self):
        manager = self

        class ChangeHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if not event.is_directory:
                    manager._queue_change(event.src_path)

        return ChangeHandler()

    def _queue_change(self, path: str):
        """Queue a change with debouncing."""
        self._pending_changes.add(path)

        if self._debounce_task:
            self._debounce_task.cancel()

        async def process():
            await asyncio.sleep(0.1)  # 100ms debounce
            changes = list(self._pending_changes)
            self._pending_changes.clear()
            await self.on_change(changes)

        self._debounce_task = asyncio.create_task(process())
```

## API Endpoints

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sessions` | POST | Create preview session |
| `/api/sessions/{id}` | GET | Get session status |
| `/api/sessions/{id}` | DELETE | Destroy session |
| `/api/sessions/{id}/tokens` | PUT | Update design tokens |
| `/api/sessions/{id}/pages` | POST | Add/update page |
| `/preview/{id}/{page}` | GET | Render page preview |

### WebSocket Events

| Event | Direction | Payload |
|-------|-----------|---------|
| `token_update` | Client → Server | `{tokens: {...}}` |
| `page_update` | Client → Server | `{page_id, content}` |
| `section_update` | Client → Server | `{page_id, section_id, content}` |
| `reload` | Server → Client | `{}` |
| `css_update` | Server → Client | `{css: "..."}` |

## Deployment Architecture

### Development Mode

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  preview:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./templates:/app/templates
      - ./tokens:/app/tokens
    environment:
      - RELOAD=true
```

### Production Mode (Kubernetes)

```yaml
# preview-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: platxa-preview
spec:
  replicas: 3
  selector:
    matchLabels:
      app: platxa-preview
  template:
    spec:
      containers:
        - name: preview
          image: platxa/preview-service:latest
          ports:
            - containerPort: 8080
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
```

## Performance Considerations

### Caching Strategy

1. **Template Cache**: Pre-compiled Jinja2 templates (in-memory)
2. **CSS Cache**: Compiled SCSS per token hash (Redis)
3. **Asset Cache**: Static assets with content-hash URLs (CDN)

### Scaling

- **Horizontal**: Multiple preview service instances behind load balancer
- **Session Affinity**: WebSocket connections require sticky sessions
- **Resource Limits**: Memory cap per session to prevent DoS

## Security

### Session Isolation

- Each preview session has unique ID (UUID)
- Sessions expire after 30 minutes of inactivity
- No cross-session data access

### Input Validation

- Token values sanitized before CSS injection
- Template content escaped to prevent XSS
- Rate limiting on API endpoints

### Authentication

- Preview URLs can be optionally protected
- Integration with Platxa auth system
- Temporary preview tokens for sharing

## Integration Points

### With Frontend Editor

```typescript
// Frontend integration
const previewClient = new PreviewClient(sessionId);

// Update tokens in real-time
previewClient.updateTokens({
  colors: {
    primary: { hex: '#8B35A8', oklch: [0.52, 0.18, 300] }
  }
});

// Update page content
previewClient.updatePage('about', {
  sections: [
    { type: 'hero', title: 'About Us', ... },
    { type: 'story', content: '...' },
  ]
});
```

### With Skill Generators

```python
# Generate and preview
from platxa_preview import PreviewClient

async def generate_with_preview(config):
    # Create preview session
    client = PreviewClient()
    session = await client.create_session()

    # Generate theme
    theme_files = generate_theme(config)

    # Update preview
    await session.update_tokens(config.tokens)
    for page in config.pages:
        await session.update_page(page.type, page.content)

    # Return preview URL
    return f"https://preview.platxa.dev/{session.id}"
```

## Implementation Phases

### Phase 1: Core Preview (Week 1-2)
- [ ] FastAPI server setup
- [ ] Basic template rendering
- [ ] CSS variable injection
- [ ] WebSocket live reload

### Phase 2: Full Integration (Week 3-4)
- [ ] SCSS compilation
- [ ] Section library integration
- [ ] Page generator integration
- [ ] Hot reload optimization

### Phase 3: Production Ready (Week 5-6)
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Caching layer
- [ ] Monitoring/alerting

## Success Metrics

| Metric | Target |
|--------|--------|
| Preview render time | < 200ms |
| Live reload latency | < 100ms |
| Concurrent sessions | 1000+ |
| Memory per session | < 50MB |
| Uptime | 99.9% |
