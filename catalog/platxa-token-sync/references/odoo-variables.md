# Odoo SCSS Variables Reference

Complete reference for Odoo's SCSS variable system.

## Color System

### Color Customizer Variables (o_cc)

Odoo's Website Builder uses 5 customizable colors:

| Variable | CSS Class | Purpose |
|----------|-----------|---------|
| `$o-color-1` | `.o_cc1` | Primary brand color |
| `$o-color-2` | `.o_cc2` | Secondary/accent color |
| `$o-color-3` | `.o_cc3` | Tertiary color (often dark) |
| `$o-color-4` | `.o_cc4` | Quaternary color (often light) |
| `$o-color-5` | `.o_cc5` | Background/neutral color |

### Usage in QWeb Templates

```xml
<!-- Background color -->
<section class="o_cc o_cc1">
    <div class="container">
        <!-- Content with primary color background -->
    </div>
</section>

<!-- Text color -->
<h2 class="text-o-color-2">Accent Heading</h2>
```

### Bootstrap Integration

Odoo maps colors to Bootstrap variables:

```scss
// In Odoo's Bootstrap overrides
$primary: $o-color-1;
$secondary: $o-color-2;
$dark: $o-color-3;
$light: $o-color-4;
```

## Typography Variables

### Font Families

```scss
// Sans-serif (body text, headings)
$o-font-family-sans-serif: 'Inter', -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !default;

// Monospace (code blocks)
$o-font-family-monospace: 'JetBrains Mono', 'Fira Code',
    SFMono-Regular, Menlo, Monaco, Consolas, monospace !default;
```

### Font Sizes

```scss
$o-font-size-base: 1rem !default;  // 16px
$o-font-size-sm: 0.875rem !default;  // 14px
$o-font-size-lg: 1.125rem !default;  // 18px

$o-h1-font-size: 2.5rem !default;
$o-h2-font-size: 2rem !default;
$o-h3-font-size: 1.75rem !default;
$o-h4-font-size: 1.5rem !default;
$o-h5-font-size: 1.25rem !default;
$o-h6-font-size: 1rem !default;
```

## Spacing System

### Base Spacer

```scss
$o-spacer: 8px !default;
```

### Spacer Scale

```scss
$o-spacers: (
  0: 0,           // 0px
  1: 4px,         // 0.5 * base
  2: 8px,         // 1 * base
  3: 12px,        // 1.5 * base
  4: 16px,        // 2 * base
  5: 24px,        // 3 * base
  6: 32px,        // 4 * base
  7: 48px,        // 6 * base
  8: 64px,        // 8 * base
) !default;
```

### Usage

```scss
// In your SCSS
.my-section {
    padding: map-get($o-spacers, 5);  // 24px
    margin-bottom: $o-spacer * 3;     // 24px
}
```

## Asset Bundle Prepending

**Critical:** Variables must be prepended before Bootstrap loads.

```python
# In __manifest__.py
'assets': {
    'web.assets_frontend': [
        # Prepend variables BEFORE Bootstrap
        ('prepend', 'theme_name/static/src/scss/primary_variables.scss'),

        # Regular styles load after Bootstrap
        'theme_name/static/src/scss/theme.scss',
    ],
},
```

### Why Prepend?

Bootstrap and Odoo use `!default` flags:

```scss
// Bootstrap's default
$primary: #0d6efd !default;

// Your prepended variable overrides it
$primary: #8B35A8 !default;  // This wins if loaded first
```

## Variable Naming Conventions

| Prefix | Purpose | Example |
|--------|---------|---------|
| `$o-` | Odoo core variables | `$o-color-1`, `$o-spacer` |
| `$o-brand-` | Brand/theme semantics | `$o-brand-primary` |
| `$o-font-` | Typography | `$o-font-family-sans-serif` |
| `$o-btn-` | Button styles | `$o-btn-primary-bg` |
| `$o-navbar-` | Navigation | `$o-navbar-height` |

## Complete Variable Template

```scss
// ============================================
// Theme Variables (prepend before Bootstrap)
// ============================================

// Colors
$o-color-1: #8B35A8 !default;
$o-color-2: #2ECCC4 !default;
$o-color-3: #1C1C21 !default;
$o-color-4: #F0F0F0 !default;
$o-color-5: #FAFAFA !default;

// Semantic aliases
$o-brand-primary: $o-color-1;
$o-brand-secondary: $o-color-2;
$o-brand-dark: $o-color-3;
$o-brand-light: $o-color-4;
$o-brand-bg: $o-color-5;

// Typography
$o-font-family-sans-serif: 'Inter', sans-serif !default;
$o-font-family-monospace: 'JetBrains Mono', monospace !default;

// Spacing
$o-spacer: 8px !default;
$o-spacers: (0: 0, 1: 4px, 2: 8px, 3: 12px, 4: 16px, 5: 24px, 6: 32px) !default;

// Bootstrap overrides
$primary: $o-color-1;
$secondary: $o-color-2;
$body-bg: $o-color-5;
$body-color: $o-color-3;
$font-family-sans-serif: $o-font-family-sans-serif;
$font-family-monospace: $o-font-family-monospace;
$spacer: $o-spacer;
```
