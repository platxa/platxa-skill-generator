---
name: platxa-token-sync
description: Transform Brand Kit design tokens (OKLCH colors, spacing, typography) into Odoo-compatible SCSS variables. Bridges the gap between modern design systems and Odoo's theming architecture.
version: 1.0.0
allowed-tools: Read, Write, Bash, Glob
---

# Platxa Token Sync

Transform design tokens from Platxa Brand Kit format into Odoo-compatible SCSS variables.

## Overview

This skill automatically converts modern design tokens (OKLCH color space, 8px grid spacing, semantic typography) into Odoo's SCSS variable system, ensuring consistent branding across your website studio and Odoo themes.

## Workflow

### Step 1: Parse Brand Kit Tokens

Read tokens from supported input formats:

**CSS Custom Properties:**
```css
:root {
  --color-primary: oklch(52% 0.18 300);
  --color-accent: oklch(75% 0.15 180);
  --color-neutral: oklch(20% 0.02 270);
  --space-base: 8px;
  --font-sans: 'Inter', sans-serif;
}
```

**JSON Token File:**
```json
{
  "colors": {
    "primary": { "oklch": [0.52, 0.18, 300], "hex": "#8B35A8" },
    "accent": { "oklch": [0.75, 0.15, 180], "hex": "#2ECCC4" },
    "neutral": { "oklch": [0.20, 0.02, 270], "hex": "#1C1C21" }
  },
  "spacing": { "base": 8, "scale": [4, 8, 12, 16, 24, 32, 48, 64] },
  "typography": { "sans": "Inter", "mono": "JetBrains Mono" }
}
```

### Step 2: Convert OKLCH to Hex

OKLCH provides perceptually uniform colors. Convert to hex for Odoo compatibility:

```python
def oklch_to_hex(l: float, c: float, h: float) -> str:
    """
    Convert OKLCH to hex color.

    Args:
        l: Lightness (0-1)
        c: Chroma (0-0.4 typical)
        h: Hue (0-360 degrees)

    Returns:
        Hex color string (#RRGGBB)
    """
    # OKLCH → OKLab
    a = c * math.cos(math.radians(h))
    b = c * math.sin(math.radians(h))

    # OKLab → Linear sRGB (via matrix)
    # Linear sRGB → sRGB (gamma correction)
    # sRGB → Hex
    ...
```

### Step 3: Map to Odoo Color System

Odoo uses 5 customizable colors with the `o_cc` (color customizer) system:

| Odoo Variable | Purpose | Brand Kit Mapping |
|---------------|---------|-------------------|
| `$o-color-1` | Primary brand color | `--color-primary` |
| `$o-color-2` | Accent/CTA color | `--color-accent` |
| `$o-color-3` | Dark neutral | `--color-neutral` |
| `$o-color-4` | Light neutral | Auto-generate (95% lightness) |
| `$o-color-5` | Background | Auto-generate (98% lightness) |

**60-30-10 Rule Application:**
- 60% → Background/neutral (`$o-color-5`)
- 30% → Primary brand (`$o-color-1`)
- 10% → Accent/CTA (`$o-color-2`)

### Step 4: Generate Odoo SCSS

Output `primary_variables.scss` for prepending before Bootstrap:

```scss
// ============================================
// Platxa Token Sync - Generated Variables
// DO NOT EDIT - Regenerate with sync_tokens.py
// ============================================

// Brand Colors (from Brand Kit)
$o-color-1: #8B35A8 !default;  // Primary
$o-color-2: #2ECCC4 !default;  // Accent
$o-color-3: #1C1C21 !default;  // Dark
$o-color-4: #F0F0F0 !default;  // Light
$o-color-5: #FAFAFA !default;  // Background

// Semantic Aliases
$o-brand-primary: $o-color-1;
$o-brand-secondary: $o-color-2;
$o-brand-dark: $o-color-3;
$o-brand-light: $o-color-4;

// Typography
$o-font-family-sans-serif: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !default;
$o-font-family-monospace: 'JetBrains Mono', 'Fira Code', monospace !default;

// Spacing (8px grid)
$o-spacer: 8px !default;
$o-spacers: (
  0: 0,
  1: 4px,
  2: 8px,
  3: 12px,
  4: 16px,
  5: 24px,
  6: 32px,
  7: 48px,
  8: 64px,
) !default;
```

### Step 5: Validate Output

Run validation checks:

1. **SCSS Syntax:** Ensure generated SCSS compiles
2. **Contrast Ratios:** Verify WCAG AA compliance (4.5:1 for text)
3. **Required Variables:** All 5 Odoo colors must be defined
4. **No Duplicates:** Check for variable name collisions

## Usage

### CLI Commands

```bash
# Sync from CSS tokens to Odoo module
python scripts/sync_tokens.py \
  --input tokens.css \
  --output theme_name/static/src/scss/primary_variables.scss

# Sync from JSON tokens
python scripts/sync_tokens.py \
  --input tokens.json \
  --output theme_name/static/src/scss/primary_variables.scss

# Generate with validation report
python scripts/sync_tokens.py \
  --input tokens.css \
  --output primary_variables.scss \
  --validate \
  --report report.json

# Dry run (preview without writing)
python scripts/sync_tokens.py \
  --input tokens.css \
  --dry-run
```

### Integration with Theme Generation

When generating an Odoo theme, call token sync first:

```python
# In platxa-odoo-theme workflow
1. Run platxa-token-sync to generate primary_variables.scss
2. Generate theme structure
3. Include generated SCSS in manifest assets:
   'assets': {
       'web.assets_frontend': [
           ('prepend', 'theme_name/static/src/scss/primary_variables.scss'),
       ]
   }
```

## Input Specifications

### CSS Custom Properties Format

```css
:root {
  /* Colors - OKLCH or Hex */
  --color-primary: oklch(52% 0.18 300);
  --color-primary-hex: #8B35A8;  /* Fallback */
  --color-accent: oklch(75% 0.15 180);
  --color-neutral-dark: oklch(20% 0.02 270);
  --color-neutral-light: oklch(95% 0.01 270);
  --color-background: oklch(98% 0.005 270);

  /* Spacing - Base unit and scale */
  --space-unit: 8px;
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;

  /* Typography */
  --font-family-sans: 'Inter', sans-serif;
  --font-family-mono: 'JetBrains Mono', monospace;
  --font-size-base: 16px;
  --line-height-base: 1.5;
}
```

### JSON Token Format

```json
{
  "meta": {
    "name": "Platxa Brand Kit",
    "version": "1.0.0"
  },
  "colors": {
    "primary": {
      "oklch": [0.52, 0.18, 300],
      "hex": "#8B35A8",
      "role": "brand"
    },
    "accent": {
      "oklch": [0.75, 0.15, 180],
      "hex": "#2ECCC4",
      "role": "cta"
    },
    "neutral": {
      "dark": { "oklch": [0.20, 0.02, 270], "hex": "#1C1C21" },
      "light": { "oklch": [0.95, 0.01, 270], "hex": "#F0F0F0" },
      "background": { "oklch": [0.98, 0.005, 270], "hex": "#FAFAFA" }
    }
  },
  "spacing": {
    "unit": 8,
    "scale": {
      "xs": 4, "sm": 8, "md": 16, "lg": 24,
      "xl": 32, "2xl": 48, "3xl": 64
    }
  },
  "typography": {
    "families": {
      "sans": "'Inter', -apple-system, sans-serif",
      "mono": "'JetBrains Mono', monospace"
    },
    "sizes": {
      "base": "16px",
      "sm": "14px",
      "lg": "18px"
    }
  }
}
```

## Output Specifications

### primary_variables.scss

This file MUST be prepended before Bootstrap in Odoo's asset bundle:

```python
# In __manifest__.py
'assets': {
    'web.assets_frontend': [
        ('prepend', 'module_name/static/src/scss/primary_variables.scss'),
        'module_name/static/src/scss/theme.scss',
    ],
},
```

### Variable Naming Conventions

| Category | Odoo Convention | Example |
|----------|-----------------|---------|
| Colors | `$o-color-N` | `$o-color-1: #8B35A8;` |
| Brand | `$o-brand-*` | `$o-brand-primary: $o-color-1;` |
| Fonts | `$o-font-family-*` | `$o-font-family-sans-serif: 'Inter';` |
| Spacing | `$o-spacer`, `$o-spacers` | `$o-spacer: 8px;` |

## Validation Rules

### Color Contrast (WCAG AA)

Minimum contrast ratios:
- Normal text: 4.5:1
- Large text (18px+): 3:1
- UI components: 3:1

```python
def check_contrast(foreground: str, background: str) -> tuple[float, bool]:
    """
    Check contrast ratio between two colors.

    Returns:
        (ratio, passes_aa)
    """
    ratio = calculate_contrast_ratio(foreground, background)
    return ratio, ratio >= 4.5
```

### Required Odoo Variables

All themes MUST define:
- `$o-color-1` through `$o-color-5`
- `$o-font-family-sans-serif`
- `$o-spacer`

### SCSS Syntax Validation

```bash
# Validate SCSS compiles
sassc primary_variables.scss /dev/null
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Invalid OKLCH | Malformed color value | Use hex fallback or default palette |
| Missing token | Required token not in input | Apply sensible default |
| Contrast failure | Colors too similar | Warn and suggest alternatives |
| SCSS syntax | Template error | Check template and regenerate |

## Examples

### Example 1: Basic Token Sync

**Input (tokens.css):**
```css
:root {
  --color-primary: oklch(52% 0.18 300);
  --color-accent: oklch(75% 0.15 180);
}
```

**Command:**
```bash
python scripts/sync_tokens.py --input tokens.css --output primary_variables.scss
```

**Output (primary_variables.scss):**
```scss
$o-color-1: #8B35A8 !default;
$o-color-2: #2ECCC4 !default;
$o-color-3: #2D2D35 !default;  // Auto-generated dark
$o-color-4: #E8E8EC !default;  // Auto-generated light
$o-color-5: #F5F5F7 !default;  // Auto-generated bg
```

### Example 2: Full Brand Kit Sync

**Input (brand-kit.json):**
```json
{
  "colors": {
    "primary": { "hex": "#8B35A8" },
    "accent": { "hex": "#2ECCC4" },
    "neutral": {
      "dark": { "hex": "#1C1C21" },
      "light": { "hex": "#F0F0F0" },
      "background": { "hex": "#FAFAFA" }
    }
  },
  "spacing": { "unit": 8 },
  "typography": {
    "families": {
      "sans": "'Inter', sans-serif",
      "mono": "'JetBrains Mono', monospace"
    }
  }
}
```

**Output:**
```scss
// Colors
$o-color-1: #8B35A8 !default;
$o-color-2: #2ECCC4 !default;
$o-color-3: #1C1C21 !default;
$o-color-4: #F0F0F0 !default;
$o-color-5: #FAFAFA !default;

// Semantic
$o-brand-primary: $o-color-1;
$o-brand-secondary: $o-color-2;

// Typography
$o-font-family-sans-serif: 'Inter', sans-serif !default;
$o-font-family-monospace: 'JetBrains Mono', monospace !default;

// Spacing
$o-spacer: 8px !default;
$o-spacers: (0: 0, 1: 4px, 2: 8px, 3: 12px, 4: 16px, 5: 24px, 6: 32px, 7: 48px, 8: 64px) !default;
```

## Best Practices

1. **Always prepend** - SCSS variables must come before Bootstrap
2. **Use !default** - Allow downstream overrides
3. **Document sources** - Add comment header with generation timestamp
4. **Version tokens** - Track token version in output comments
5. **Validate contrast** - Run contrast checks before deployment
6. **Keep in sync** - Regenerate after brand kit changes
