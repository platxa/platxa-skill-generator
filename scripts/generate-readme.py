#!/usr/bin/env python3
"""generate-readme.py - Auto-generate skills/README.md from registry data.

Usage:
    python3 scripts/generate-readme.py                    # Write to skills/README.md
    python3 scripts/generate-readme.py -o /path/to/out.md # Write to custom path
    python3 scripts/generate-readme.py --dry-run          # Print to stdout

Produces a README.md with:
    - Skills table (name, description, category, tier badge, tokens, install cmd)
    - Category breakdown
    - Quality standards
    - Installation methods
"""

from __future__ import annotations

import argparse
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent
SKILLS_DIR = PROJECT_ROOT / "skills"

_spec = spec_from_file_location("generate_index_mod", SCRIPTS_DIR / "generate-index.py")
assert _spec is not None and _spec.loader is not None
generate_index_mod = module_from_spec(_spec)
_spec.loader.exec_module(generate_index_mod)
generate_index = generate_index_mod.generate_index

TIER_BADGES = {
    0: "Internal",
    1: "Essential",
    2: "Useful",
    3: "Experimental",
}

SOURCE_LABELS = {
    "local": "Platxa",
    "anthropic": "Anthropic",
    "vercel": "Vercel",
    "obra": "Obra",
}


def build_readme(skills_dir: Path) -> str:
    """Generate the complete README.md content from registry data."""
    index = generate_index(skills_dir)
    skills = index["skills"]
    categories = index["categories"]

    local_count = sum(1 for s in skills.values() if s["source"] == "local")
    external_count = len(skills) - local_count

    lines: list[str] = []

    # Header
    lines.append("# Claude Code Skills Registry")
    lines.append("")
    lines.append("> A curated, quality-verified collection of production-ready skills for Claude Code CLI.")
    lines.append(">")
    lines.append("> **Maintained by**: [Platxa](https://platxa.com) | **License**: MIT | **Compatible with**: `npx skills`")
    lines.append("")
    lines.append(f"**{len(skills)} skills** across **{len(categories)} categories** — {local_count} local, {external_count} external")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Quick Install
    lines.append("## Quick Install")
    lines.append("")
    lines.append("```bash")
    lines.append("# Clone the repository")
    lines.append("git clone https://github.com/platxa/platxa-skill-generator.git")
    lines.append("cd platxa-skill-generator")
    lines.append("")
    lines.append("# Install a single skill")
    lines.append("./scripts/install-from-catalog.sh <skill-name>")
    lines.append("")
    lines.append("# Install to project instead of user directory")
    lines.append("./scripts/install-from-catalog.sh <skill-name> --project")
    lines.append("")
    lines.append("# Install all essential skills (tier 1)")
    lines.append("./scripts/install-from-catalog.sh --all --tier 1")
    lines.append("")
    lines.append("# List all available skills")
    lines.append("./scripts/install-from-catalog.sh --list")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Skills Table
    lines.append("## Skills Index")
    lines.append("")
    lines.append("| Skill | Description | Category | Tier | Tokens | Source | Install |")
    lines.append("|-------|-------------|----------|------|--------|--------|---------|")

    for name, skill in sorted(skills.items(), key=lambda x: (x[1]["tier"], x[1]["category"], x[0])):
        desc = skill.get("description", "")
        # Truncate long descriptions for the table
        if len(desc) > 80:
            desc = desc[:77] + "..."
        # Escape pipe characters in description
        desc = desc.replace("|", "\\|")

        cat = skill.get("category", "")
        tier = skill.get("tier", 0)
        tier_label = TIER_BADGES.get(tier, str(tier))
        tokens = skill.get("token_counts", {}).get("total", 0)
        source = SOURCE_LABELS.get(skill.get("source", ""), skill.get("source", ""))
        install_cmd = f"`./scripts/install-from-catalog.sh {name}`"

        lines.append(f"| [{name}](skills/{name}/SKILL.md) | {desc} | {cat} | {tier_label} | {tokens:,} | {source} | {install_cmd} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Categories Breakdown
    lines.append("## Categories")
    lines.append("")
    lines.append("| Category | Skills | Description |")
    lines.append("|----------|--------|-------------|")

    category_descriptions = {
        "backend": "Server-side services and APIs",
        "debugging": "Bug diagnosis and resolution",
        "design": "UI/UX design and frontend aesthetics",
        "devtools": "Developer productivity tools",
        "frontend": "Client-side components and UI",
        "git": "Git workflow automation",
        "infrastructure": "Kubernetes and cloud operations",
        "mobile": "Mobile app development",
        "observability": "Logging, monitoring, and tracing",
        "odoo": "Odoo ERP platform development",
        "security": "Authentication, encryption, secrets",
        "testing": "Test generation and automation",
        "workflow": "Agent workflow and orchestration",
    }

    for cat, count in sorted(categories.items()):
        cat_desc = category_descriptions.get(cat, "")
        lines.append(f"| {cat} | {count} | {cat_desc} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Tier System
    lines.append("## Skill Tiers")
    lines.append("")
    lines.append("| Tier | Label | Description | Count |")
    lines.append("|------|-------|-------------|-------|")

    tier_counts: dict[int, int] = {}
    for skill in skills.values():
        t = skill.get("tier", 0)
        tier_counts[t] = tier_counts.get(t, 0) + 1

    tier_descriptions = {
        0: "Platxa internal skills (local only)",
        1: "Essential, high-quality skills",
        2: "Useful, recommended skills",
        3: "Experimental or niche skills",
    }

    for tier in sorted(tier_counts.keys()):
        label = TIER_BADGES.get(tier, str(tier))
        desc = tier_descriptions.get(tier, "")
        count = tier_counts[tier]
        lines.append(f"| {tier} | {label} | {desc} | {count} |")

    lines.append("")
    lines.append("Install by tier: `./scripts/install-from-catalog.sh --all --tier 1`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Installation Methods
    lines.append("## Installation Methods")
    lines.append("")
    lines.append("### Method 1: Install Script (Recommended)")
    lines.append("")
    lines.append("```bash")
    lines.append("./scripts/install-from-catalog.sh <skill-name> [--user|--project]")
    lines.append("```")
    lines.append("")
    lines.append("| Flag | Description |")
    lines.append("|------|-------------|")
    lines.append("| `--user` | Install to `~/.claude/skills/` (default) |")
    lines.append("| `--project` | Install to `.claude/skills/` |")
    lines.append("| `--list` | List all available skills |")
    lines.append("| `--all` | Install all skills |")
    lines.append("| `--force` | Overwrite existing without prompting |")
    lines.append("| `--tier N` | Only install skills with tier <= N |")
    lines.append("| `--category X` | Only install skills matching category X |")
    lines.append("")
    lines.append("### Method 2: Manual Copy")
    lines.append("")
    lines.append("```bash")
    lines.append("cp -r skills/<skill-name> ~/.claude/skills/")
    lines.append("```")
    lines.append("")
    lines.append("### Method 3: Symbolic Link (Development)")
    lines.append("")
    lines.append("```bash")
    lines.append("ln -s $(pwd)/skills/<skill-name> ~/.claude/skills/<skill-name>")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Quality Standards
    lines.append("## Quality Standards")
    lines.append("")
    lines.append("All skills meet these requirements:")
    lines.append("")
    lines.append("| Requirement | Threshold |")
    lines.append("|-------------|-----------|")
    lines.append("| SKILL.md exists | Required |")
    lines.append("| Valid YAML frontmatter | Required |")
    lines.append("| Name (hyphen-case) | <= 64 chars |")
    lines.append("| Description | <= 1,024 chars |")
    lines.append("| Token budget (SKILL.md) | <= 5,000 recommended |")
    lines.append("| Token budget (total) | <= 15,000 recommended |")
    lines.append("| All validations pass | Required |")
    lines.append("")
    lines.append("```bash")
    lines.append("# Validate a skill")
    lines.append("./scripts/validate-all.sh skills/<skill-name>")
    lines.append("")
    lines.append("# Check token count")
    lines.append("python3 scripts/count-tokens.py skills/<skill-name>")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # External vs Local
    lines.append("## External vs Local Skills")
    lines.append("")
    lines.append(f"- **Local** ({local_count} skills): Created and maintained in this repo. Never overwritten by sync.")
    lines.append(f"- **External** ({external_count} skills): Synced from upstream repos (Anthropic, Vercel, Obra).")
    lines.append("")
    lines.append("```bash")
    lines.append("# Sync external skills from upstream")
    lines.append("./scripts/sync-catalog.sh sync")
    lines.append("")
    lines.append("# List sources")
    lines.append("./scripts/sync-catalog.sh list-external")
    lines.append("./scripts/sync-catalog.sh list-local")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Contributing
    lines.append("## Contributing")
    lines.append("")
    lines.append("See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full PR-based submission guide.")
    lines.append("")
    lines.append("```bash")
    lines.append("# Quick validation before submitting")
    lines.append("./scripts/validate-all.sh skills/my-skill-name")
    lines.append("python3 scripts/count-tokens.py skills/my-skill-name")
    lines.append("python3 scripts/check-duplicates.py skills/my-skill-name")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Footer
    lines.append("## License")
    lines.append("")
    lines.append("MIT License - See [LICENSE](../LICENSE) for details.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Auto-generated from registry data. {len(skills)} skills across {len(categories)} categories.*")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-generate skills/README.md from registry data"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output path (default: skills/README.md)",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=SKILLS_DIR,
        help="Skills directory (default: skills/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print to stdout instead of writing file",
    )

    args = parser.parse_args()

    if not args.skills_dir.is_dir():
        print(f"Error: Not a directory: {args.skills_dir}", file=sys.stderr)
        return 1

    readme = build_readme(args.skills_dir)

    if args.dry_run:
        print(readme)
    else:
        output = args.output or (args.skills_dir / "README.md")
        output.write_text(readme)
        # Count skills in output
        table_lines = [line for line in readme.splitlines() if line.startswith("| [")]
        print(f"Generated {output}: {len(table_lines)} skills", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
