#!/usr/bin/env python3
"""
Token Sync - Transform Brand Kit tokens to Odoo SCSS variables.

Converts modern design tokens (OKLCH colors, spacing, typography)
into Odoo-compatible SCSS variable definitions.

Usage:
    python sync_tokens.py --input tokens.css --output primary_variables.scss
    python sync_tokens.py --input tokens.json --output theme/static/src/scss/
"""

import argparse
import json
import logging
import math
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ColorToken:
    """Represents a color token."""

    name: str
    hex_value: str
    oklch: tuple[float, float, float] | None = None
    role: str = "custom"


@dataclass
class SpacingToken:
    """Represents spacing tokens."""

    unit: int = 8
    scale: dict[str, int] = field(
        default_factory=lambda: {
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32,
            "2xl": 48,
            "3xl": 64,
        }
    )


@dataclass
class TypographyToken:
    """Represents typography tokens."""

    sans: str = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    mono: str = "'JetBrains Mono', 'Fira Code', monospace"
    base_size: str = "16px"


@dataclass
class TokenSet:
    """Complete set of design tokens."""

    colors: dict[str, ColorToken] = field(default_factory=dict)
    spacing: SpacingToken = field(default_factory=SpacingToken)
    typography: TypographyToken = field(default_factory=TypographyToken)
    meta: dict[str, str] = field(default_factory=dict)


class OKLCHConverter:
    """Convert OKLCH colors to hex."""

    @staticmethod
    def oklch_to_hex(lightness: float, c: float, h: float) -> str:
        """
        Convert OKLCH to hex color.

        Args:
            l: Lightness (0-1)
            c: Chroma (0-0.4 typical)
            h: Hue (0-360 degrees)

        Returns:
            Hex color string (#RRGGBB)
        """
        # OKLCH to OKLab (polar to cartesian)
        a = c * math.cos(math.radians(h))
        b = c * math.sin(math.radians(h))

        # OKLab to linear sRGB
        l_ = lightness + 0.3963377774 * a + 0.2158037573 * b
        m_ = lightness - 0.1055613458 * a - 0.0638541728 * b
        s_ = lightness - 0.0894841775 * a - 1.2914855480 * b

        l_cubed = l_**3
        m_cubed = m_**3
        s_cubed = s_**3

        # Matrix transformation to linear sRGB
        r_linear = +4.0767416621 * l_cubed - 3.3077115913 * m_cubed + 0.2309699292 * s_cubed
        g_linear = -1.2684380046 * l_cubed + 2.6097574011 * m_cubed - 0.3413193965 * s_cubed
        b_linear = -0.0041960863 * l_cubed - 0.7034186147 * m_cubed + 1.7076147010 * s_cubed

        # Linear sRGB to sRGB (gamma correction)
        def gamma_correct(x: float) -> float:
            if x <= 0.0031308:
                return 12.92 * x
            return 1.055 * (x ** (1 / 2.4)) - 0.055

        r = gamma_correct(r_linear)
        g = gamma_correct(g_linear)
        b_val = gamma_correct(b_linear)

        # Clamp to 0-1 range
        r = max(0, min(1, r))
        g = max(0, min(1, g))
        b_val = max(0, min(1, b_val))

        # Convert to hex
        r_int = round(r * 255)
        g_int = round(g * 255)
        b_int = round(b_val * 255)

        return f"#{r_int:02X}{g_int:02X}{b_int:02X}"

    @staticmethod
    def parse_oklch(oklch_str: str) -> tuple[float, float, float] | None:
        """
        Parse OKLCH string.

        Args:
            oklch_str: String like "oklch(52% 0.18 300)"

        Returns:
            Tuple of (lightness, chroma, hue) or None if invalid
        """
        match = re.match(
            r"oklch\(\s*(\d+(?:\.\d+)?)\s*%?\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s*\)",
            oklch_str.strip(),
            re.IGNORECASE,
        )
        if not match:
            return None

        lightness = float(match.group(1))
        c = float(match.group(2))
        h = float(match.group(3))

        # Normalize lightness if given as percentage
        if lightness > 1:
            lightness = lightness / 100

        return (lightness, c, h)


class ContrastChecker:
    """Check color contrast ratios for accessibility."""

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """Convert hex to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def relative_luminance(r: int, g: int, b: int) -> float:
        """Calculate relative luminance per WCAG 2.1."""

        def adjust(c: int) -> float:
            c_normalized = c / 255
            if c_normalized <= 0.03928:
                return c_normalized / 12.92
            return ((c_normalized + 0.055) / 1.055) ** 2.4

        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    @classmethod
    def contrast_ratio(cls, color1: str, color2: str) -> float:
        """
        Calculate contrast ratio between two colors.

        Args:
            color1: Hex color (#RRGGBB)
            color2: Hex color (#RRGGBB)

        Returns:
            Contrast ratio (1-21)
        """
        rgb1 = cls.hex_to_rgb(color1)
        rgb2 = cls.hex_to_rgb(color2)

        l1 = cls.relative_luminance(*rgb1)
        l2 = cls.relative_luminance(*rgb2)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    @classmethod
    def check_wcag_aa(cls, foreground: str, background: str) -> tuple[float, bool]:
        """
        Check if colors pass WCAG AA contrast requirements.

        Returns:
            (contrast_ratio, passes_aa)
        """
        ratio = cls.contrast_ratio(foreground, background)
        return ratio, ratio >= 4.5


class TokenParser:
    """Parse tokens from various input formats."""

    @staticmethod
    def parse_css(content: str) -> TokenSet:
        """Parse CSS custom properties format."""
        tokens = TokenSet()

        # Parse colors
        color_patterns = [
            (r"--color-primary:\s*([^;]+)", "primary", "brand"),
            (r"--color-accent:\s*([^;]+)", "accent", "cta"),
            (r"--color-neutral(?:-dark)?:\s*([^;]+)", "neutral_dark", "neutral"),
            (r"--color-neutral-light:\s*([^;]+)", "neutral_light", "neutral"),
            (r"--color-background:\s*([^;]+)", "background", "background"),
        ]

        for pattern, name, role in color_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1).strip()

                # Check if OKLCH
                oklch = OKLCHConverter.parse_oklch(value)
                if oklch:
                    hex_val = OKLCHConverter.oklch_to_hex(*oklch)
                    tokens.colors[name] = ColorToken(name, hex_val, oklch, role)
                elif value.startswith("#"):
                    tokens.colors[name] = ColorToken(name, value.upper(), None, role)

        # Parse spacing
        space_match = re.search(r"--space-(?:unit|base):\s*(\d+)px", content)
        if space_match:
            tokens.spacing.unit = int(space_match.group(1))

        # Parse typography
        font_sans_match = re.search(r"--font-(?:family-)?sans:\s*([^;]+)", content)
        if font_sans_match:
            tokens.typography.sans = font_sans_match.group(1).strip()

        font_mono_match = re.search(r"--font-(?:family-)?mono:\s*([^;]+)", content)
        if font_mono_match:
            tokens.typography.mono = font_mono_match.group(1).strip()

        return tokens

    @staticmethod
    def parse_json(content: str) -> TokenSet:
        """Parse JSON token format."""
        data = json.loads(content)
        tokens = TokenSet()

        # Parse meta
        if "meta" in data:
            tokens.meta = data["meta"]

        # Parse colors
        if "colors" in data:
            colors = data["colors"]

            def extract_color(obj: Any, name: str, role: str) -> ColorToken | None:
                if isinstance(obj, dict):
                    hex_val = obj.get("hex", "")
                    oklch = tuple(obj["oklch"]) if "oklch" in obj else None
                    if hex_val:
                        return ColorToken(name, hex_val.upper(), oklch, role)
                return None

            if "primary" in colors:
                token = extract_color(colors["primary"], "primary", "brand")
                if token:
                    tokens.colors["primary"] = token

            if "accent" in colors:
                token = extract_color(colors["accent"], "accent", "cta")
                if token:
                    tokens.colors["accent"] = token

            if "neutral" in colors:
                neutral = colors["neutral"]
                if isinstance(neutral, dict):
                    if "dark" in neutral:
                        token = extract_color(neutral["dark"], "neutral_dark", "neutral")
                        if token:
                            tokens.colors["neutral_dark"] = token
                    if "light" in neutral:
                        token = extract_color(neutral["light"], "neutral_light", "neutral")
                        if token:
                            tokens.colors["neutral_light"] = token
                    if "background" in neutral:
                        token = extract_color(neutral["background"], "background", "background")
                        if token:
                            tokens.colors["background"] = token

        # Parse spacing
        if "spacing" in data:
            spacing = data["spacing"]
            if "unit" in spacing:
                tokens.spacing.unit = spacing["unit"]
            if "scale" in spacing:
                tokens.spacing.scale = spacing["scale"]

        # Parse typography
        if "typography" in data:
            typo = data["typography"]
            if "families" in typo:
                families = typo["families"]
                if "sans" in families:
                    tokens.typography.sans = families["sans"]
                if "mono" in families:
                    tokens.typography.mono = families["mono"]

        return tokens


class OdooSCSSGenerator:
    """Generate Odoo-compatible SCSS from tokens."""

    # Default fallback colors
    DEFAULT_COLORS = {
        "primary": "#8B35A8",
        "accent": "#2ECCC4",
        "neutral_dark": "#1C1C21",
        "neutral_light": "#F0F0F0",
        "background": "#FAFAFA",
    }

    def __init__(self, tokens: TokenSet):
        self.tokens = tokens
        self.warnings: list[str] = []

    def _get_color(self, key: str) -> str:
        """Get color value with fallback."""
        if key in self.tokens.colors:
            return self.tokens.colors[key].hex_value
        return self.DEFAULT_COLORS.get(key, "#888888")

    def _generate_color_variations(self, base_hex: str) -> dict[str, str]:
        """Generate lighter/darker variations of a color."""
        # Simple lightness adjustment (proper implementation would use OKLCH)
        rgb = ContrastChecker.hex_to_rgb(base_hex)

        def adjust_lightness(rgb: tuple[int, int, int], factor: float) -> str:
            if factor > 1:
                # Lighten
                r = round(rgb[0] + (255 - rgb[0]) * (factor - 1))
                g = round(rgb[1] + (255 - rgb[1]) * (factor - 1))
                b = round(rgb[2] + (255 - rgb[2]) * (factor - 1))
            else:
                # Darken
                r = round(rgb[0] * factor)
                g = round(rgb[1] * factor)
                b = round(rgb[2] * factor)

            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            return f"#{r:02X}{g:02X}{b:02X}"

        return {
            "light": adjust_lightness(rgb, 1.3),
            "dark": adjust_lightness(rgb, 0.7),
        }

    def _check_contrasts(self) -> list[str]:
        """Check color contrasts and return warnings."""
        warnings = []

        primary = self._get_color("primary")
        background = self._get_color("background")

        ratio, passes = ContrastChecker.check_wcag_aa(primary, background)
        if not passes:
            warnings.append(
                f"Primary ({primary}) on background ({background}) has contrast ratio "
                f"{ratio:.2f}:1 (minimum 4.5:1 required)"
            )

        accent = self._get_color("accent")
        ratio, passes = ContrastChecker.check_wcag_aa(accent, background)
        if not passes:
            warnings.append(
                f"Accent ({accent}) on background ({background}) has contrast ratio "
                f"{ratio:.2f}:1 (minimum 4.5:1 required)"
            )

        return warnings

    def generate(self) -> str:
        """Generate Odoo SCSS variables."""
        self.warnings = self._check_contrasts()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version = self.tokens.meta.get("version", "1.0.0")

        # Get colors with fallbacks
        primary = self._get_color("primary")
        accent = self._get_color("accent")
        dark = self._get_color("neutral_dark")
        light = self._get_color("neutral_light")
        background = self._get_color("background")

        # Generate spacing scale
        unit = self.tokens.spacing.unit
        spacers = [
            0,
            unit // 2,
            unit,
            unit + unit // 2,
            unit * 2,
            unit * 3,
            unit * 4,
            unit * 6,
            unit * 8,
        ]

        scss = f"""// ============================================
// Platxa Token Sync - Generated Variables
// Generated: {timestamp}
// Version: {version}
// DO NOT EDIT - Regenerate with sync_tokens.py
// ============================================

// ----------------------------------------
// Brand Colors (Odoo Color Customizer)
// ----------------------------------------
// These map to Odoo's o_cc1-5 color classes

$o-color-1: {primary} !default;  // Primary brand color (30%)
$o-color-2: {accent} !default;   // Accent/CTA color (10%)
$o-color-3: {dark} !default;     // Dark neutral
$o-color-4: {light} !default;    // Light neutral
$o-color-5: {background} !default; // Background (60%)

// ----------------------------------------
// Semantic Color Aliases
// ----------------------------------------

$o-brand-primary: $o-color-1;
$o-brand-secondary: $o-color-2;
$o-brand-dark: $o-color-3;
$o-brand-light: $o-color-4;
$o-brand-bg: $o-color-5;

// ----------------------------------------
// Typography
// ----------------------------------------

$o-font-family-sans-serif: {self.tokens.typography.sans} !default;
$o-font-family-monospace: {self.tokens.typography.mono} !default;

// ----------------------------------------
// Spacing (8px grid system)
// ----------------------------------------

$o-spacer: {unit}px !default;
$o-spacers: (
  0: 0,
  1: {spacers[1]}px,
  2: {spacers[2]}px,
  3: {spacers[3]}px,
  4: {spacers[4]}px,
  5: {spacers[5]}px,
  6: {spacers[6]}px,
  7: {spacers[7]}px,
  8: {spacers[8]}px,
) !default;

// ----------------------------------------
// Utility Classes (Optional)
// ----------------------------------------

// Generate utility classes for brand colors
@each $i, $color in (1: $o-color-1, 2: $o-color-2, 3: $o-color-3, 4: $o-color-4, 5: $o-color-5) {{
  .bg-brand-#{{$i}} {{
    background-color: $color !important;
  }}
  .text-brand-#{{$i}} {{
    color: $color !important;
  }}
}}
"""
        return scss

    def get_validation_report(self) -> dict[str, Any]:
        """Generate validation report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "colors": {
                name: {"hex": token.hex_value, "oklch": token.oklch, "role": token.role}
                for name, token in self.tokens.colors.items()
            },
            "spacing": {"unit": self.tokens.spacing.unit, "scale": self.tokens.spacing.scale},
            "typography": {
                "sans": self.tokens.typography.sans,
                "mono": self.tokens.typography.mono,
            },
            "warnings": self.warnings,
            "passed": len(self.warnings) == 0,
        }


def validate_output_path(output_path: str) -> Path:
    """Validate output path for security."""
    resolved = Path(output_path).resolve()

    if "\x00" in str(resolved):
        raise ValueError("Invalid path: contains null bytes")

    cwd = Path.cwd().resolve()
    home = Path.home().resolve()
    tmp_dir = Path("/tmp").resolve()

    allowed_bases = [cwd, home, tmp_dir]

    is_allowed = any(
        resolved == base or str(resolved).startswith(str(base) + "/") for base in allowed_bases
    )

    if not is_allowed:
        raise ValueError(f"Output path must be within cwd, home, or /tmp: {resolved}")

    return resolved


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Transform Brand Kit tokens to Odoo SCSS variables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input tokens.css --output primary_variables.scss
  %(prog)s --input tokens.json --output theme/static/src/scss/ --validate
  %(prog)s --input tokens.css --dry-run
        """,
    )

    parser.add_argument("--input", "-i", required=True, help="Input token file (CSS or JSON)")
    parser.add_argument("--output", "-o", help="Output SCSS file or directory")
    parser.add_argument("--validate", "-v", action="store_true", help="Run validation checks")
    parser.add_argument("--report", "-r", help="Save validation report to JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Preview output without writing")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress info messages")

    args = parser.parse_args()

    if args.quiet:
        logger.setLevel(logging.WARNING)

    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    content = input_path.read_text(encoding="utf-8")

    # Parse tokens based on file extension
    if input_path.suffix.lower() == ".json":
        tokens = TokenParser.parse_json(content)
    else:
        tokens = TokenParser.parse_css(content)

    logger.info(f"Parsed {len(tokens.colors)} colors, spacing unit: {tokens.spacing.unit}px")

    # Generate SCSS
    generator = OdooSCSSGenerator(tokens)
    scss_output = generator.generate()

    # Show warnings
    for warning in generator.warnings:
        logger.warning(warning)

    # Dry run - just print
    if args.dry_run:
        print(scss_output)
        sys.exit(0)

    # Write output
    if args.output:
        output_path = validate_output_path(args.output)

        # If directory, use default filename
        if output_path.is_dir() or not output_path.suffix:
            output_path = output_path / "primary_variables.scss"
            output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(scss_output, encoding="utf-8")
        logger.info(f"Generated: {output_path}")
    else:
        print(scss_output)

    # Save validation report
    if args.report:
        report_path = validate_output_path(args.report)
        report = generator.get_validation_report()
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        logger.info(f"Report saved: {report_path}")

    # Exit with appropriate code
    if args.validate and generator.warnings:
        logger.warning("Validation completed with warnings")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
