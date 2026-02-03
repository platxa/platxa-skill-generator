#!/usr/bin/env python3
"""generate-badges.py - Generate SVG trust badges for skills.

Usage:
    python3 scripts/generate-badges.py                    # Write to badges/
    python3 scripts/generate-badges.py -o /path/to/dir    # Custom output
    python3 scripts/generate-badges.py --skills-dir DIR   # Custom skills dir
    python3 scripts/generate-badges.py --dry-run           # Print summary only

Produces shields.io-style flat SVG badges based on quality scores:
    badges/
    ├── <skill-name>.svg        # Per-skill trust badge
    ├── _verified.svg           # Static Verified badge template
    ├── _reviewed.svg           # Static Reviewed badge template
    ├── _unverified.svg         # Static Unverified badge template
    └── _flagged.svg            # Static Flagged badge template

Badge levels (from score-skill.py assign_badge):
    Verified   — green  (score >= 8.0 AND security passed)
    Reviewed   — blue   (score >= 7.0)
    Unverified — yellow (score >= 5.0)
    Flagged    — red    (score < 5.0 or security failed)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent
SKILLS_DIR = PROJECT_ROOT / "skills"

# Load score-skill.py functions
_score_spec = spec_from_file_location("score_skill_mod", SCRIPTS_DIR / "score-skill.py")
assert _score_spec is not None and _score_spec.loader is not None
_score_mod = module_from_spec(_score_spec)
_score_spec.loader.exec_module(_score_mod)
score_skill = _score_mod.score_skill  # type: ignore[attr-defined]
assign_badge = _score_mod.assign_badge  # type: ignore[attr-defined]

BADGE_COLORS: dict[str, str] = {
    "Verified": "#4c1",
    "Reviewed": "#007ec6",
    "Unverified": "#dfb317",
    "Flagged": "#e05d44",
}

LABEL = "trust"


def _text_width(text: str) -> int:
    """Estimate rendered text width in pixels for Verdana 11px."""
    wide = set("mwMW")
    narrow = set("ijl!|:;.,1")
    width = 0.0
    for ch in text:
        if ch in wide:
            width += 8.5
        elif ch in narrow:
            width += 4.5
        else:
            width += 6.8
    return int(width) + 1


def generate_badge_svg(label: str, message: str, color: str) -> str:
    """Generate a shields.io-style flat SVG badge.

    Produces an accessible SVG with label (left, grey) and message
    (right, colored) sections.
    """
    label_width = _text_width(label) + 10
    message_width = _text_width(message) + 10
    total_width = label_width + message_width

    label_x = label_width / 2
    message_x = label_width + message_width / 2

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20"'
        f' role="img" aria-label="{label}: {message}">\n'
        f"  <title>{label}: {message}</title>\n"
        f'  <linearGradient id="s" x2="0" y2="100%">\n'
        f'    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>\n'
        f'    <stop offset="1" stop-opacity=".1"/>\n'
        f"  </linearGradient>\n"
        f'  <clipPath id="r">\n'
        f'    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>\n'
        f"  </clipPath>\n"
        f'  <g clip-path="url(#r)">\n'
        f'    <rect width="{label_width}" height="20" fill="#555"/>\n'
        f'    <rect x="{label_width}" width="{message_width}" height="20" fill="{color}"/>\n'
        f'    <rect width="{total_width}" height="20" fill="url(#s)"/>\n'
        f"  </g>\n"
        f'  <g fill="#fff" text-anchor="middle"'
        f' font-family="Verdana,Geneva,DejaVu Sans,sans-serif"'
        f' text-rendering="geometricPrecision" font-size="110">\n'
        f'    <text aria-hidden="true" x="{label_x * 10:.0f}" y="150"'
        f' fill="#010101" fill-opacity=".3" transform="scale(.1)">{label}</text>\n'
        f'    <text x="{label_x * 10:.0f}" y="140"'
        f' transform="scale(.1)" fill="#fff">{label}</text>\n'
        f'    <text aria-hidden="true" x="{message_x * 10:.0f}" y="150"'
        f' fill="#010101" fill-opacity=".3" transform="scale(.1)">{message}</text>\n'
        f'    <text x="{message_x * 10:.0f}" y="140"'
        f' transform="scale(.1)" fill="#fff">{message}</text>\n'
        f"  </g>\n"
        f"</svg>\n"
    )


def _run_security_check(skill_dir: Path) -> bool:
    """Run security-check.sh on a skill directory. Returns True if clean."""
    sec_script = SCRIPTS_DIR / "security-check.sh"
    if not sec_script.exists():
        return True
    try:
        result = subprocess.run(
            [str(sec_script), str(skill_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def generate_badges(
    skills_dir: Path,
    output_dir: Path,
    *,
    dry_run: bool = False,
) -> dict:
    """Generate badge SVGs for all skills in the catalog.

    Returns a summary dict with badge counts and per-skill results.
    """
    skill_dirs = sorted(
        d
        for d in skills_dir.iterdir()
        if d.is_dir()
        and (d / "SKILL.md").exists()
        and d.name not in {"__pycache__", ".git", "node_modules"}
    )

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    badge_counts: dict[str, int] = {
        "Verified": 0,
        "Reviewed": 0,
        "Unverified": 0,
        "Flagged": 0,
    }

    for skill_dir in skill_dirs:
        name = skill_dir.name
        try:
            report = score_skill(skill_dir)
            score = report["overall_score"]
            security_passed = _run_security_check(skill_dir)
            badge = assign_badge(score, security_passed=security_passed)
        except Exception as exc:
            print(f"  Warning: Failed to score {name}: {exc}", file=sys.stderr)
            badge = "Flagged"
            score = 0.0

        color = BADGE_COLORS.get(badge, "#9f9f9f")
        badge_counts[badge] = badge_counts.get(badge, 0) + 1

        if not dry_run:
            svg = generate_badge_svg(LABEL, badge, color)
            (output_dir / f"{name}.svg").write_text(svg)

        results.append({"name": name, "score": round(score, 2), "badge": badge})

    # Generate static per-level badge templates
    if not dry_run:
        for level, color in BADGE_COLORS.items():
            svg = generate_badge_svg(LABEL, level, color)
            (output_dir / f"_{level.lower()}.svg").write_text(svg)

    return {
        "total": len(results),
        "output_dir": str(output_dir),
        "badges": badge_counts,
        "skills": results,
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate SVG trust badges for skills based on quality scores"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "badges",
        help="Output directory for badge SVGs (default: badges/)",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=SKILLS_DIR,
        help="Skills directory (default: skills/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output summary as JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary without writing files",
    )

    args = parser.parse_args()

    if not args.skills_dir.is_dir():
        print(f"Error: Not a directory: {args.skills_dir}", file=sys.stderr)
        return 1

    summary = generate_badges(args.skills_dir, args.output_dir, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        action = "Would generate" if args.dry_run else "Generated"
        print(f"{action} {summary['total']} badge(s) in {args.output_dir}")
        for level in ("Verified", "Reviewed", "Unverified", "Flagged"):
            count = summary["badges"].get(level, 0)
            if count:
                print(f"  {level}: {count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
