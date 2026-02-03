#!/usr/bin/env python3
"""generate-index.py - Build static index.json for the skills registry.

Usage:
    python3 scripts/generate-index.py                    # Output to stdout
    python3 scripts/generate-index.py -o skills/index.json  # Write to file
    python3 scripts/generate-index.py --pretty            # Pretty-printed JSON

Reads all skills from skills/ directory and manifest.yaml to produce a static
index.json containing metadata, token counts, categories, and quality info
for every skill in the registry.

Output schema:
    {
        "version": "1.0.0",
        "generated_at": "2026-02-03T12:00:00Z",
        "skills_count": 37,
        "skills": {
            "code-documenter": {
                "name": "code-documenter",
                "description": "...",
                "category": "devtools",
                "tier": 0,
                "source": "local",
                "allowed_tools": ["Read", "Write", ...],
                "token_counts": {
                    "skill_md": 1235,
                    "references": 2370,
                    "total": 3605
                },
                "metadata": { ... }
            },
            ...
        },
        "categories": { "devtools": 5, "frontend": 8, ... }
    }
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

# Add scripts dir to path so we can import count-tokens functions
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

_spec = spec_from_file_location("count_tokens_mod", SCRIPTS_DIR / "count-tokens.py")
assert _spec is not None and _spec.loader is not None
count_tokens_mod = module_from_spec(_spec)
_spec.loader.exec_module(count_tokens_mod)
analyze_skill = count_tokens_mod.analyze_skill


def parse_frontmatter(skill_md: Path) -> dict[str, Any]:
    """Extract all fields from SKILL.md YAML frontmatter.

    Returns dict with name, description, allowed_tools, metadata, etc.
    """
    try:
        text = skill_md.read_text()
    except OSError:
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    fm_text = match.group(1)

    # Use PyYAML if available, fall back to manual parsing
    try:
        import yaml

        fm = yaml.safe_load(fm_text)
        if not isinstance(fm, dict):
            return {}

        result: dict[str, Any] = {}
        if "name" in fm:
            result["name"] = str(fm["name"])
        if "description" in fm:
            result["description"] = str(fm["description"])

        # Handle both "tools" and "allowed-tools" field names
        tools = fm.get("allowed-tools") or fm.get("tools")
        if isinstance(tools, list):
            result["allowed_tools"] = [str(t) for t in tools]

        # Extract metadata block
        if "metadata" in fm and isinstance(fm["metadata"], dict):
            result["metadata"] = fm["metadata"]

        return result
    except ImportError:
        # Manual parsing fallback
        result = {}
        for line in fm_text.splitlines():
            if line.startswith("name:"):
                result["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("description:"):
                result["description"] = line.split(":", 1)[1].strip()
        return result


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load manifest.yaml and return skills dict."""
    if not manifest_path.exists():
        return {}

    try:
        import yaml

        with open(manifest_path) as f:
            m = yaml.safe_load(f)
        return m if isinstance(m, dict) else {}
    except (ImportError, Exception):
        return {}


def build_skill_entry(
    skill_dir: Path,
    manifest_skills: dict[str, Any],
) -> dict[str, Any] | None:
    """Build a single skill entry for the index.

    Returns None if the skill directory is invalid (no SKILL.md).
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    dir_name = skill_dir.name

    # Parse SKILL.md frontmatter
    fm = parse_frontmatter(skill_md)
    if not fm.get("name"):
        return None

    # Get manifest info
    manifest_info = manifest_skills.get(dir_name, {})

    # Determine source
    if manifest_info.get("local", False):
        source = "local"
    elif "source" in manifest_info:
        source = manifest_info["source"]
    else:
        source = "unknown"

    # Get token counts
    token_report = analyze_skill(skill_dir)

    entry: dict[str, Any] = {
        "name": fm["name"],
        "description": fm.get("description", ""),
        "category": manifest_info.get("category", "uncategorized"),
        "tier": manifest_info.get("tier", 0),
        "source": source,
        "token_counts": {
            "skill_md": token_report["skill_md_tokens"],
            "references": token_report["ref_total_tokens"],
            "total": token_report["total_tokens"],
        },
    }

    # Optional fields
    if "allowed_tools" in fm:
        entry["allowed_tools"] = fm["allowed_tools"]

    if "metadata" in fm:
        entry["metadata"] = fm["metadata"]

    if manifest_info.get("sha"):
        entry["sha"] = manifest_info["sha"]

    if manifest_info.get("ref"):
        entry["ref"] = manifest_info["ref"]

    if manifest_info.get("compatibility"):
        entry["compatibility"] = manifest_info["compatibility"]

    return entry


def generate_index(skills_dir: Path) -> dict[str, Any]:
    """Generate the complete index.json structure.

    Args:
        skills_dir: Path to the skills/ directory.

    Returns:
        Complete index dict ready for JSON serialization.
    """
    manifest_path = skills_dir / "manifest.yaml"
    manifest = load_manifest(manifest_path)
    manifest_skills = manifest.get("skills", {})

    skills: dict[str, Any] = {}
    categories: dict[str, int] = {}

    # Walk all skill directories
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        # Skip non-skill directories
        if skill_dir.name in ("overrides", ".git", "__pycache__"):
            continue

        entry = build_skill_entry(skill_dir, manifest_skills)
        if entry is None:
            continue

        skills[skill_dir.name] = entry

        # Accumulate category counts
        cat = entry["category"]
        categories[cat] = categories.get(cat, 0) + 1

    # Sort categories by count descending
    sorted_categories = dict(sorted(categories.items(), key=lambda x: -x[1]))

    return {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skills_count": len(skills),
        "skills": skills,
        "categories": sorted_categories,
    }


def generate_search_index(full_index: dict[str, Any]) -> list[dict[str, Any]]:
    """Build lightweight search index for client-side full-text search.

    Each entry contains searchable text fields (name, description, category,
    tags) plus metadata for display. Designed for fuzzy matching in CLI tools
    without needing a server.

    Args:
        full_index: The full index dict from generate_index().

    Returns:
        List of search entries, one per skill.
    """
    entries: list[dict[str, Any]] = []
    for skill in full_index["skills"].values():
        tags = skill.get("metadata", {}).get("tags", [])
        entries.append(
            {
                "name": skill["name"],
                "description": skill.get("description", ""),
                "category": skill.get("category", ""),
                "tier": skill.get("tier", 0),
                "tokens": skill.get("token_counts", {}).get("total", 0),
                "source": skill.get("source", ""),
                "tags": tags,
            }
        )
    return entries


def search_skills(
    search_entries: list[dict[str, Any]],
    query: str,
) -> list[tuple[dict[str, Any], float]]:
    """Fuzzy text search across search index entries.

    Scores each entry by matching query tokens against name, description,
    category, and tags. Supports prefix matching and partial word matching.

    Args:
        search_entries: List from generate_search_index().
        query: User search query string.

    Returns:
        List of (entry, score) tuples sorted by score descending,
        filtered to entries with score > 0.
    """
    query_lower = query.lower()
    tokens = query_lower.split()
    if not tokens:
        return []

    results: list[tuple[dict[str, Any], float]] = []
    for entry in search_entries:
        score = 0.0
        name = entry["name"].lower()
        desc = entry.get("description", "").lower()
        cat = entry.get("category", "").lower()
        tag_str = " ".join(t.lower() for t in entry.get("tags", []))

        for token in tokens:
            # Exact name match (highest weight)
            if token == name:
                score += 10.0
            elif token in name:
                score += 5.0
            elif name.startswith(token) or any(
                part.startswith(token) for part in name.split("-")
            ):
                score += 3.0

            # Category match
            if token == cat:
                score += 4.0
            elif token in cat:
                score += 2.0

            # Tag match
            if token in tag_str:
                score += 3.0

            # Description match
            if token in desc:
                score += 1.0

        if score > 0:
            results.append((entry, score))

    results.sort(key=lambda x: (-x[1], x[0]["name"]))
    return results


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate static index.json for the skills registry"
    )
    parser.add_argument(
        "skills_dir",
        type=Path,
        nargs="?",
        default=None,
        help="Path to skills/ directory (default: auto-detect from project root)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write output to file instead of stdout",
    )
    parser.add_argument(
        "--search-index",
        type=Path,
        default=None,
        metavar="PATH",
        help="Also write search-index.json to PATH",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )

    args = parser.parse_args()

    # Auto-detect skills directory
    if args.skills_dir is None:
        project_root = SCRIPTS_DIR.parent
        args.skills_dir = project_root / "skills"

    if not args.skills_dir.is_dir():
        print(f"Error: Not a directory: {args.skills_dir}", file=sys.stderr)
        return 1

    index = generate_index(args.skills_dir)

    indent = 2 if args.pretty else None
    json_str = json.dumps(index, indent=indent, ensure_ascii=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_str + "\n")
        print(
            f"Generated index.json: {index['skills_count']} skills, "
            f"{len(index['categories'])} categories",
            file=sys.stderr,
        )
    else:
        print(json_str)

    if args.search_index:
        search = generate_search_index(index)
        args.search_index.parent.mkdir(parents=True, exist_ok=True)
        args.search_index.write_text(
            json.dumps(search, indent=indent, ensure_ascii=False) + "\n"
        )
        print(
            f"Generated search-index.json: {len(search)} entries",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
