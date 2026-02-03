#!/usr/bin/env python3
"""build-pages.py - Build GitHub Pages site for .well-known/skills discovery.

Usage:
    python3 scripts/build-pages.py                # Build to _site/
    python3 scripts/build-pages.py -o docs/       # Build to custom dir

Produces a static site with:
    _site/
    ├── .well-known/
    │   └── skills/
    │       └── index.json          # Cloudflare RFC discovery endpoint
    ├── index.json                  # Full registry index
    ├── search-index.json           # Lightweight search index
    └── skills/
        └── {name}/
            └── SKILL.md            # Individual skill files

The .well-known/skills/index.json follows the Cloudflare RFC for
decentralized skill discovery.
"""

from __future__ import annotations

import argparse
import json
import shutil
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
generate_search_index = generate_index_mod.generate_search_index


def build_well_known_index(full_index: dict) -> dict:
    """Build the .well-known/skills/index.json for Cloudflare RFC discovery.

    This is a simplified version of the full index, containing only
    the fields needed for discovery: name, description, and URL.
    """
    skills = []
    for key, skill in full_index["skills"].items():
        entry = {
            "name": skill["name"],
            "description": skill.get("description", ""),
            "url": f"skills/{key}/SKILL.md",
        }
        if skill.get("category"):
            entry["category"] = skill["category"]
        if skill.get("metadata", {}).get("tags"):
            entry["tags"] = skill["metadata"]["tags"]
        skills.append(entry)

    return {
        "version": "1.0.0",
        "name": "Platxa Skills Registry",
        "description": "Quality-verified skills for Claude Code and 38+ AI agents",
        "homepage": "https://github.com/platxa/platxa-skill-generator",
        "skills_count": len(skills),
        "skills": skills,
    }


def build_site(output_dir: Path, skills_dir: Path) -> None:
    """Build the complete Pages site."""
    # Clean output
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # Generate full index
    full_index = generate_index(skills_dir)

    # Write full index.json
    index_path = output_dir / "index.json"
    index_path.write_text(json.dumps(full_index, indent=2, ensure_ascii=False) + "\n")
    print(f"  index.json: {full_index['skills_count']} skills")

    # Write search-index.json
    search = generate_search_index(full_index)
    search_path = output_dir / "search-index.json"
    search_path.write_text(json.dumps(search, indent=2, ensure_ascii=False) + "\n")
    print(f"  search-index.json: {len(search)} entries")

    # Write .well-known/skills/index.json
    well_known_dir = output_dir / ".well-known" / "skills"
    well_known_dir.mkdir(parents=True)
    wk_index = build_well_known_index(full_index)
    wk_path = well_known_dir / "index.json"
    wk_path.write_text(json.dumps(wk_index, indent=2, ensure_ascii=False) + "\n")
    print(f"  .well-known/skills/index.json: {wk_index['skills_count']} skills")

    # Copy skill files (SKILL.md only for lightweight serving)
    skills_out = output_dir / "skills"
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name in ("overrides", ".git", "__pycache__"):
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        dest_dir = skills_out / skill_dir.name
        dest_dir.mkdir(parents=True)
        shutil.copy2(skill_md, dest_dir / "SKILL.md")

    skill_count = len(list(skills_out.iterdir())) if skills_out.exists() else 0
    print(f"  skills/: {skill_count} SKILL.md files")

    # Create .nojekyll to serve dotfiles (.well-known)
    (output_dir / ".nojekyll").touch()

    print(f"\nSite built: {output_dir}/")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build GitHub Pages site for .well-known/skills discovery"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=PROJECT_ROOT / "_site",
        help="Output directory (default: _site/)",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=SKILLS_DIR,
        help="Skills directory (default: skills/)",
    )

    args = parser.parse_args()

    if not args.skills_dir.is_dir():
        print(f"Error: Not a directory: {args.skills_dir}", file=sys.stderr)
        return 1

    print("Building GitHub Pages site...")
    build_site(args.output, args.skills_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
