#!/usr/bin/env python3
"""check-duplicates.py - Detect duplicate or redundant skills.

Usage:
    python3 scripts/check-duplicates.py <skill-directory>
    python3 scripts/check-duplicates.py --audit <catalog-directory>

Detection layers:
    1. Exact name match  -> ERROR (exit 1)
    2. Fuzzy name match  -> WARNING (ratio >= 0.85)
    3. Description similarity -> WARNING (ratio >= 0.80)

Exit codes: 0 = no duplicates, 1 = exact duplicate found
"""

from __future__ import annotations

import argparse
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


def parse_frontmatter(skill_md: Path) -> tuple[str, str]:
    """Extract name and description from SKILL.md frontmatter.

    Returns:
        (name, description) tuple. Empty strings if not found.
    """
    try:
        text = skill_md.read_text()
    except OSError:
        return "", ""

    # Match YAML frontmatter between --- delimiters
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return "", ""

    fm = match.group(1)
    name = ""
    description = ""
    for line in fm.splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip()
        elif line.startswith("description:"):
            description = line.split(":", 1)[1].strip()

    return name, description


def collect_skills(catalog_dir: Path, skip_dir: Path | None = None) -> list[tuple[str, str, Path]]:
    """Collect (name, description, path) from all SKILL.md files under catalog_dir."""
    skills: list[tuple[str, str, Path]] = []
    if not catalog_dir.is_dir():
        return skills

    for skill_md in sorted(catalog_dir.glob("*/SKILL.md")):
        skill_path = skill_md.parent
        if skip_dir and skill_path.resolve() == skip_dir.resolve():
            continue
        name, desc = parse_frontmatter(skill_md)
        if name:
            skills.append((name, desc, skill_path))

    return skills


def normalize_name(name: str) -> str:
    """Strip common prefixes and hyphens, lowercase."""
    n = name.lower()
    for prefix in ("platxa-", "odoo-"):
        if n.startswith(prefix):
            n = n[len(prefix) :]
    return n.replace("-", "")


def check_exact_name(
    target_name: str, skills: list[tuple[str, str, Path]]
) -> list[tuple[str, Path]]:
    """Return skills with exact same name."""
    return [(n, p) for n, _, p in skills if n == target_name]


def check_fuzzy_name(
    target_name: str,
    skills: list[tuple[str, str, Path]],
    threshold: float = 0.85,
) -> list[tuple[str, Path, float]]:
    """Return skills with fuzzy name match above threshold."""
    norm_target = normalize_name(target_name)
    matches: list[tuple[str, Path, float]] = []
    for name, _, path in skills:
        if name == target_name:
            continue  # skip exact (handled separately)
        norm = normalize_name(name)
        ratio = SequenceMatcher(None, norm_target, norm).ratio()
        if ratio >= threshold:
            matches.append((name, path, ratio))
    return matches


def check_description_similarity(
    target_desc: str,
    skills: list[tuple[str, str, Path]],
    threshold: float = 0.80,
) -> list[tuple[str, Path, float]]:
    """Return skills with similar descriptions above threshold."""
    if not target_desc:
        return []
    matches: list[tuple[str, Path, float]] = []
    for name, desc, path in skills:
        if not desc:
            continue
        ratio = SequenceMatcher(None, target_desc.lower(), desc.lower()).ratio()
        if ratio >= threshold:
            matches.append((name, path, ratio))
    return matches


def check_skill(skill_dir: Path, catalog_dir: Path | None = None) -> int:
    """Check a single skill against catalog. Returns exit code."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print("ERROR: SKILL.md not found", file=sys.stderr)
        return 1

    target_name, target_desc = parse_frontmatter(skill_md)
    if not target_name:
        print("ERROR: No name in frontmatter", file=sys.stderr)
        return 1

    # Determine catalog directory
    if catalog_dir is None:
        # Try parent directory (skill is likely inside catalog/)
        catalog_dir = skill_dir.parent

    skills = collect_skills(catalog_dir, skip_dir=skill_dir)

    has_error = False

    # Layer 1: Exact name match
    exact = check_exact_name(target_name, skills)
    for name, path in exact:
        print(f"ERROR: Exact duplicate name '{name}' in {path}", file=sys.stderr)
        has_error = True

    # Layer 2: Fuzzy name match
    fuzzy = check_fuzzy_name(target_name, skills)
    for name, path, ratio in fuzzy:
        print(
            f"WARNING: Similar name '{name}' (ratio={ratio:.2f}) in {path}",
            file=sys.stderr,
        )

    # Layer 3: Description similarity
    desc_matches = check_description_similarity(target_desc, skills)
    for name, path, ratio in desc_matches:
        print(
            f"WARNING: Similar description to '{name}' (ratio={ratio:.2f}) in {path}",
            file=sys.stderr,
        )

    if has_error:
        return 1

    print(f"No duplicates found for '{target_name}'")
    return 0


def audit_catalog(catalog_dir: Path) -> int:
    """Check all skills in catalog against each other. Returns exit code."""
    if not catalog_dir.is_dir():
        print(f"ERROR: Not a directory: {catalog_dir}", file=sys.stderr)
        return 1

    all_skills = collect_skills(catalog_dir)
    if not all_skills:
        print("No skills found in catalog")
        return 0

    has_error = False
    seen_pairs: set[tuple[str, ...]] = set()

    for i, (name_a, desc_a, path_a) in enumerate(all_skills):
        others = all_skills[:i] + all_skills[i + 1 :]

        # Exact name
        for name_b, _, path_b in others:
            pair = tuple(sorted([name_a, name_b]))
            if name_a == name_b and pair not in seen_pairs:
                seen_pairs.add(pair)
                print(
                    f"ERROR: Duplicate name '{name_a}': {path_a} and {path_b}",
                    file=sys.stderr,
                )
                has_error = True

        # Fuzzy name
        for name_b, path_b, ratio in check_fuzzy_name(name_a, others):
            pair = tuple(sorted([name_a, name_b]))
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                print(
                    f"WARNING: Similar names '{name_a}' <-> '{name_b}' "
                    f"(ratio={ratio:.2f}): {path_a} and {path_b}",
                    file=sys.stderr,
                )

        # Description similarity
        if desc_a:
            for name_b, path_b, ratio in check_description_similarity(desc_a, others):
                pair = tuple(sorted([name_a, name_b]))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    print(
                        f"WARNING: Similar descriptions '{name_a}' <-> '{name_b}' "
                        f"(ratio={ratio:.2f}): {path_a} and {path_b}",
                        file=sys.stderr,
                    )

    if has_error:
        return 1

    print(f"Audit complete: {len(all_skills)} skills checked")
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Detect duplicate skills")
    parser.add_argument(
        "path",
        type=Path,
        help="Skill directory (or catalog directory with --audit)",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Audit entire catalog for cross-duplicates",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="Catalog directory to compare against (default: parent of skill dir)",
    )

    args = parser.parse_args()

    if args.audit:
        return audit_catalog(args.path)
    else:
        return check_skill(args.path, catalog_dir=args.catalog)


if __name__ == "__main__":
    sys.exit(main())
