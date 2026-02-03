# OKLCH Color Conversion Reference

Technical reference for OKLCH to Hex color conversion.

## What is OKLCH?

OKLCH is a **perceptually uniform** color space that provides:

- **Predictable lightness:** Equal steps in L produce visually equal brightness changes
- **Consistent chroma:** Colors at same chroma appear equally saturated
- **Intuitive hue:** 0-360° color wheel similar to HSL

### OKLCH Components

| Component | Range | Description |
|-----------|-------|-------------|
| **L** (Lightness) | 0-1 (or 0-100%) | Perceptual brightness |
| **C** (Chroma) | 0-0.4+ | Color intensity/saturation |
| **H** (Hue) | 0-360° | Color angle on wheel |

### Example Values

```css
/* Purple - Primary */
oklch(52% 0.18 300)  /* L=52%, C=0.18, H=300° */

/* Teal - Accent */
oklch(75% 0.15 180)  /* L=75%, C=0.15, H=180° */

/* Dark Gray - Neutral */
oklch(20% 0.02 270)  /* L=20%, C=0.02 (nearly gray), H=270° */
```

## Conversion Pipeline

```
OKLCH → OKLab → Linear sRGB → sRGB → Hex
```

### Step 1: OKLCH to OKLab

Convert from polar (L, C, H) to cartesian (L, a, b):

```python
import math

def oklch_to_oklab(l, c, h):
    """Convert OKLCH to OKLab coordinates."""
    a = c * math.cos(math.radians(h))
    b = c * math.sin(math.radians(h))
    return l, a, b
```

### Step 2: OKLab to Linear sRGB

Apply the OKLab to linear RGB matrix transformation:

```python
def oklab_to_linear_rgb(l, a, b):
    """Convert OKLab to linear sRGB."""
    # Intermediate LMS-like values
    l_ = l + 0.3963377774 * a + 0.2158037573 * b
    m_ = l - 0.1055613458 * a - 0.0638541728 * b
    s_ = l - 0.0894841775 * a - 1.2914855480 * b

    # Cube the values
    l_cubed = l_ ** 3
    m_cubed = m_ ** 3
    s_cubed = s_ ** 3

    # Matrix to linear sRGB
    r = +4.0767416621 * l_cubed - 3.3077115913 * m_cubed + 0.2309699292 * s_cubed
    g = -1.2684380046 * l_cubed + 2.6097574011 * m_cubed - 0.3413193965 * s_cubed
    b = -0.0041960863 * l_cubed - 0.7034186147 * m_cubed + 1.7076147010 * s_cubed

    return r, g, b
```

### Step 3: Linear sRGB to sRGB

Apply gamma correction:

```python
def linear_to_srgb(c):
    """Apply sRGB gamma correction."""
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1/2.4)) - 0.055
```

### Step 4: sRGB to Hex

Convert 0-1 values to 0-255 and format as hex:

```python
def rgb_to_hex(r, g, b):
    """Convert sRGB floats to hex string."""
    # Clamp to valid range
    r = max(0, min(1, r))
    g = max(0, min(1, g))
    b = max(0, min(1, b))

    # Convert to 8-bit integers
    r_int = round(r * 255)
    g_int = round(g * 255)
    b_int = round(b * 255)

    return f"#{r_int:02X}{g_int:02X}{b_int:02X}"
```

## Complete Conversion Function

```python
import math

def oklch_to_hex(l: float, c: float, h: float) -> str:
    """
    Convert OKLCH color to hex.

    Args:
        l: Lightness (0-1 or 0-100 if percentage)
        c: Chroma (typically 0-0.4)
        h: Hue (0-360 degrees)

    Returns:
        Hex color string (#RRGGBB)
    """
    # Normalize lightness if percentage
    if l > 1:
        l = l / 100

    # OKLCH to OKLab
    a = c * math.cos(math.radians(h))
    b = c * math.sin(math.radians(h))

    # OKLab to linear sRGB
    l_ = l + 0.3963377774 * a + 0.2158037573 * b
    m_ = l - 0.1055613458 * a - 0.0638541728 * b
    s_ = l - 0.0894841775 * a - 1.2914855480 * b

    l_cubed = l_ ** 3
    m_cubed = m_ ** 3
    s_cubed = s_ ** 3

    r_lin = +4.0767416621 * l_cubed - 3.3077115913 * m_cubed + 0.2309699292 * s_cubed
    g_lin = -1.2684380046 * l_cubed + 2.6097574011 * m_cubed - 0.3413193965 * s_cubed
    b_lin = -0.0041960863 * l_cubed - 0.7034186147 * m_cubed + 1.7076147010 * s_cubed

    # Linear to sRGB gamma correction
    def gamma(x):
        if x <= 0.0031308:
            return 12.92 * x
        return 1.055 * (x ** (1/2.4)) - 0.055

    r = gamma(r_lin)
    g = gamma(g_lin)
    b = gamma(b_lin)

    # Clamp and convert to hex
    r = max(0, min(1, r))
    g = max(0, min(1, g))
    b = max(0, min(1, b))

    return f"#{round(r*255):02X}{round(g*255):02X}{round(b*255):02X}"
```

## Color Palette Examples

### Platxa Brand Colors

| Name | OKLCH | Hex |
|------|-------|-----|
| Primary (Purple) | oklch(52% 0.18 300) | #8B35A8 |
| Accent (Teal) | oklch(75% 0.15 180) | #2ECCC4 |
| Dark | oklch(20% 0.02 270) | #1C1C21 |
| Light | oklch(95% 0.01 270) | #F0F0F0 |
| Background | oklch(98% 0.005 270) | #FAFAFA |

### Generating Variations

```python
def generate_palette(base_l, base_c, base_h):
    """Generate light/dark variations of a color."""
    variations = {
        'lightest': oklch_to_hex(base_l + 0.35, base_c * 0.3, base_h),
        'lighter': oklch_to_hex(base_l + 0.2, base_c * 0.5, base_h),
        'light': oklch_to_hex(base_l + 0.1, base_c * 0.7, base_h),
        'base': oklch_to_hex(base_l, base_c, base_h),
        'dark': oklch_to_hex(base_l - 0.1, base_c * 1.1, base_h),
        'darker': oklch_to_hex(base_l - 0.2, base_c * 1.2, base_h),
        'darkest': oklch_to_hex(base_l - 0.3, base_c * 1.3, base_h),
    }
    return variations
```

## Why OKLCH over HSL?

| Aspect | HSL | OKLCH |
|--------|-----|-------|
| Perceptual uniformity | Poor | Excellent |
| Yellow/blue balance | Yellow appears lighter | Balanced |
| Chroma consistency | Varies with hue | Consistent |
| Accessibility | Hard to predict contrast | Predictable |

### Example: Same "50% Lightness"

```css
/* HSL - yellow appears much brighter than blue */
hsl(60, 100%, 50%)   /* Yellow - appears very bright */
hsl(240, 100%, 50%)  /* Blue - appears much darker */

/* OKLCH - perceptually equal brightness */
oklch(70% 0.2 100)   /* Yellow - actually 70% light */
oklch(50% 0.2 260)   /* Blue - actually 50% light */
```

## Browser Support

OKLCH is supported in modern browsers:
- Chrome 111+
- Firefox 113+
- Safari 15.4+
- Edge 111+

For Odoo (which needs broader support), always convert to hex.
