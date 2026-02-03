# Platxa Component Library Browser Specification

**Priority:** P1 (High)
**Status:** Specification Complete

## Overview

The Component Library Browser enables visual browsing, previewing, and selecting Odoo website sections and components. It integrates with the Preview Service to provide real-time previews of components with brand tokens applied.

## User Experience

### Component Browser Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                     Component Library Browser                       │
├──────────────────┬─────────────────────────────────────────────────┤
│  Categories      │           Component Preview                      │
│  ─────────────   │  ┌─────────────────────────────────────────┐    │
│  □ Hero          │  │                                         │    │
│  ▣ Features      │  │     [Live Preview with Brand Colors]    │    │
│  □ Content       │  │                                         │    │
│  □ Testimonials  │  └─────────────────────────────────────────┘    │
│  □ CTA           │                                                 │
│  □ Team          │  Component: Features Grid                       │
│  □ Pricing       │  ─────────────────────────────────────────      │
│  □ FAQ           │  Columns: 3  •  Icons: Yes  •  Style: Cards     │
│  □ Contact       │                                                 │
│  □ Footer        │  [Customize]        [Add to Page]               │
│                  │                                                 │
│  ─────────────   ├─────────────────────────────────────────────────│
│  Search: ______  │  Variants                                       │
│                  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐                    │
│                  │  │ 2  │ │ 3  │ │ 4  │ │ 6  │  columns           │
│                  │  └────┘ └────┘ └────┘ └────┘                    │
└──────────────────┴─────────────────────────────────────────────────┘
```

## Component Categories

### 1. Hero Sections

| Component | Description | Variants |
|-----------|-------------|----------|
| `hero_banner` | Full-width hero with CTA | Image BG, Video BG, Gradient |
| `hero_split` | Side-by-side image/text | Left/Right image |
| `hero_centered` | Centered text hero | With/without image |
| `hero_slider` | Carousel hero | 2-5 slides |

### 2. Feature Sections

| Component | Description | Variants |
|-----------|-------------|----------|
| `features_grid` | Grid of feature cards | 2/3/4/6 columns |
| `features_list` | Vertical feature list | With/without icons |
| `features_tabs` | Tabbed features | Horizontal/Vertical tabs |
| `features_icons` | Icon-focused features | Circle/Square icons |

### 3. Content Sections

| Component | Description | Variants |
|-----------|-------------|----------|
| `text_block` | Simple text content | Centered/Left aligned |
| `text_image` | Text with image | Left/Right image |
| `timeline` | Chronological content | Vertical/Horizontal |
| `masonry` | Masonry grid layout | 2/3/4 columns |

### 4. Social Proof

| Component | Description | Variants |
|-----------|-------------|----------|
| `testimonials_cards` | Testimonial cards | 1/2/3 columns |
| `testimonials_slider` | Testimonial carousel | With/without photos |
| `logos` | Client logo strip | Static/Scrolling |
| `stats` | Statistics display | 3/4/6 stats |

### 5. Call-to-Action

| Component | Description | Variants |
|-----------|-------------|----------|
| `cta_banner` | Full-width CTA | With/without image |
| `cta_split` | Split CTA section | Left/Right content |
| `cta_newsletter` | Newsletter signup | Inline/Stacked form |
| `cta_download` | Download CTA | Single/Multiple downloads |

### 6. Team Sections

| Component | Description | Variants |
|-----------|-------------|----------|
| `team_grid` | Team member grid | 2/3/4 columns |
| `team_cards` | Detailed team cards | With/without socials |
| `team_carousel` | Team carousel | Auto/Manual scroll |

### 7. Pricing Sections

| Component | Description | Variants |
|-----------|-------------|----------|
| `pricing_cards` | Pricing comparison | 2/3/4 plans |
| `pricing_table` | Feature comparison | Simple/Detailed |
| `pricing_toggle` | Monthly/Annual toggle | With/without savings |

### 8. FAQ Sections

| Component | Description | Variants |
|-----------|-------------|----------|
| `faq_accordion` | Collapsible FAQ | Single/Multi open |
| `faq_grid` | FAQ grid layout | 2/3 columns |
| `faq_tabs` | Categorized FAQ | Category tabs |

### 9. Contact Sections

| Component | Description | Variants |
|-----------|-------------|----------|
| `contact_form` | Contact form | Simple/Detailed |
| `contact_split` | Form + info | Left/Right form |
| `contact_map` | With map | Above/Below form |

### 10. Footer Sections

| Component | Description | Variants |
|-----------|-------------|----------|
| `footer_simple` | Simple footer | Single/Multi row |
| `footer_columns` | Multi-column | 3/4/5 columns |
| `footer_mega` | Mega footer | With newsletter |

## API Specification

### REST Endpoints

```
GET  /api/components                    # List all components
GET  /api/components/{category}         # List by category
GET  /api/components/{category}/{id}    # Get component details
GET  /api/components/{category}/{id}/preview  # Get preview HTML
POST /api/components/{category}/{id}/customize # Customize component
```

### Component Schema

```json
{
  "id": "features_grid",
  "category": "features",
  "name": "Features Grid",
  "description": "Display features in a responsive grid layout",
  "thumbnail": "/static/thumbnails/features_grid.png",
  "variants": [
    {"id": "2col", "name": "2 Columns", "columns": 2},
    {"id": "3col", "name": "3 Columns", "columns": 3},
    {"id": "4col", "name": "4 Columns", "columns": 4}
  ],
  "options": {
    "show_icons": {"type": "boolean", "default": true},
    "icon_style": {"type": "select", "options": ["circle", "square", "none"]},
    "card_style": {"type": "select", "options": ["shadow", "border", "flat"]}
  },
  "tokens_used": ["primary", "accent", "background"],
  "qweb_template": "s_features_grid"
}
```

### Preview Request

```json
POST /api/components/features/features_grid/preview
{
  "variant": "3col",
  "options": {
    "show_icons": true,
    "icon_style": "circle",
    "card_style": "shadow"
  },
  "tokens": {
    "colors": {
      "primary": {"hex": "#8B35A8"},
      "accent": {"hex": "#2ECCC4"}
    }
  },
  "sample_content": true
}
```

### Preview Response

```json
{
  "html": "<section class=\"s_features_grid pt64 pb64\">...</section>",
  "css": ":root { --o-color-1: #8B35A8; ... }",
  "scripts": []
}
```

## Frontend Integration

### React Component

```typescript
import { ComponentBrowser } from '@platxa/component-library';

function PageBuilder() {
  const handleComponentSelect = (component: Component, config: ComponentConfig) => {
    // Add component to page
    addSectionToPage(component.id, config);
  };

  return (
    <ComponentBrowser
      tokens={brandTokens}
      onSelect={handleComponentSelect}
      previewUrl="/api/components"
    />
  );
}
```

### Component Browser Props

```typescript
interface ComponentBrowserProps {
  tokens: BrandTokens;           // Current brand tokens for preview
  onSelect: (component: Component, config: ComponentConfig) => void;
  previewUrl?: string;           // API base URL
  categories?: string[];         // Filter categories
  searchEnabled?: boolean;       // Enable search
  variantSelector?: boolean;     // Show variant selector
  customizePanel?: boolean;      // Show customization panel
}
```

## Backend Implementation

### Component Registry

```python
# component_registry.py
from dataclasses import dataclass
from typing import Any

@dataclass
class ComponentDefinition:
    id: str
    category: str
    name: str
    description: str
    template: str
    variants: list[dict[str, Any]]
    options: dict[str, dict[str, Any]]
    tokens_used: list[str]

class ComponentRegistry:
    def __init__(self):
        self._components: dict[str, ComponentDefinition] = {}
        self._load_builtin_components()

    def get_component(self, category: str, component_id: str) -> ComponentDefinition | None:
        key = f"{category}/{component_id}"
        return self._components.get(key)

    def list_by_category(self, category: str) -> list[ComponentDefinition]:
        return [c for c in self._components.values() if c.category == category]

    def search(self, query: str) -> list[ComponentDefinition]:
        query_lower = query.lower()
        return [
            c for c in self._components.values()
            if query_lower in c.name.lower() or query_lower in c.description.lower()
        ]

    def _load_builtin_components(self):
        # Load from templates directory
        pass
```

### Preview Generator

```python
# component_preview.py
from jinja2 import Environment, FileSystemLoader

class ComponentPreviewGenerator:
    def __init__(self, registry: ComponentRegistry, renderer: PreviewRenderer):
        self.registry = registry
        self.renderer = renderer
        self.env = Environment(loader=FileSystemLoader('templates/components'))

    def generate_preview(
        self,
        category: str,
        component_id: str,
        variant: str | None = None,
        options: dict[str, Any] | None = None,
        tokens: dict[str, Any] | None = None,
        sample_content: bool = True,
    ) -> dict[str, str]:
        component = self.registry.get_component(category, component_id)
        if not component:
            raise ValueError(f"Component not found: {category}/{component_id}")

        # Apply variant defaults
        config = self._apply_variant(component, variant)

        # Override with custom options
        if options:
            config.update(options)

        # Generate sample content if requested
        content = self._generate_sample_content(component) if sample_content else {}

        # Render template
        template = self.env.get_template(f"{component.template}.html")
        html = template.render(config=config, content=content, tokens=tokens or {})

        # Generate CSS
        css = self.renderer._generate_css(tokens or {})

        return {"html": html, "css": css, "scripts": []}
```

## File Structure

```
platxa-preview-service/
├── components/
│   ├── registry.py           # Component registry
│   ├── preview.py            # Preview generator
│   └── schemas.py            # Pydantic schemas
├── templates/
│   └── components/
│       ├── hero/
│       │   ├── hero_banner.html
│       │   ├── hero_split.html
│       │   └── hero_centered.html
│       ├── features/
│       │   ├── features_grid.html
│       │   ├── features_list.html
│       │   └── features_tabs.html
│       └── ...
├── static/
│   └── thumbnails/           # Component thumbnails
└── data/
    └── components.json       # Component definitions
```

## Sample Content System

Each component type has associated sample content generators:

```python
SAMPLE_CONTENT = {
    "hero": {
        "title": "Transform Your Business Today",
        "subtitle": "Innovative solutions for modern challenges",
        "cta_primary": "Get Started",
        "cta_secondary": "Learn More",
        "image": "/static/samples/hero-image.jpg"
    },
    "features": {
        "items": [
            {"icon": "fa-rocket", "title": "Fast Delivery", "description": "Quick turnaround times"},
            {"icon": "fa-shield", "title": "Secure", "description": "Enterprise-grade security"},
            {"icon": "fa-chart-line", "title": "Analytics", "description": "Real-time insights"},
            {"icon": "fa-headset", "title": "Support", "description": "24/7 customer support"}
        ]
    },
    "testimonials": {
        "items": [
            {"name": "Sarah Johnson", "role": "CEO, TechCorp", "quote": "Amazing service!", "avatar": "..."},
            {"name": "Mike Chen", "role": "CTO, StartupXYZ", "quote": "Highly recommend!", "avatar": "..."}
        ]
    }
}
```

## Integration with Page Builder

### Adding Component to Page

```typescript
// When user selects a component
const handleComponentAdd = async (componentId: string, config: ComponentConfig) => {
  // 1. Get component QWeb template
  const component = await fetchComponent(componentId);

  // 2. Generate Odoo-compatible XML
  const sectionXml = generateSectionXml(component, config);

  // 3. Add to page configuration
  pageConfig.sections.push({
    type: component.qweb_template,
    config: config,
    position: pageConfig.sections.length
  });

  // 4. Trigger preview refresh
  previewClient.updatePage(pageId, pageConfig);
};
```

### Drag-and-Drop Support

```typescript
// Component dragging
const handleDragStart = (component: Component) => {
  setDraggedComponent(component);
};

// Drop on page builder
const handleDrop = (position: number) => {
  if (draggedComponent) {
    insertComponent(draggedComponent, position);
    setDraggedComponent(null);
  }
};
```

## Performance Considerations

1. **Thumbnail Caching**: Pre-generated thumbnails for fast browsing
2. **Lazy Loading**: Load component details on hover/click
3. **Preview Caching**: Cache previews by token hash + config
4. **Virtual Scrolling**: For large component lists

## Accessibility

1. **Keyboard Navigation**: Full keyboard support for browsing
2. **Screen Readers**: ARIA labels and descriptions
3. **Focus Management**: Proper focus indicators
4. **Color Contrast**: Preview panel contrast checking

## Success Metrics

| Metric | Target |
|--------|--------|
| Component browser load time | < 500ms |
| Preview generation | < 200ms |
| Search latency | < 100ms |
| Thumbnails loaded | < 1s for visible |
