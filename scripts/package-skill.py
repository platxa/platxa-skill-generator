#!/usr/bin/env python3
"""Package a skill directory into a .skill archive for distribution.

Creates a tar.gz archive with the .skill extension containing the skill's
SKILL.md, references/, scripts/, and other supported files.

Usage:
    python3 scripts/package-skill.py <skill-directory> [--output <path>]

Output: <skill-name>.skill (tar.gz archive)

The .skill file can be installed with:
    tar xzf <name>.skill -C ~/.claude/skills/
"""

from __future__ import annotations

import argparse
import re
import sys
import tarfile
from pathlib import Path

ALLOWED_EXTENSIONS = {".md", ".sh", ".py", ".json", ".yaml", ".yml", ".txt", ".html"}

EXCLUDED_DIRS = {"__pycache__", ".git", "node_modules", "eval-workspace", "evals"}


def extract_name(skill_dir: Path) -> str:
    """Extract skill name from SKILL.md frontmatter.

    Args:
        skill_dir: Path to skill directory

    Returns:
        Skill name from frontmatter, or directory name as fallback
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return skill_dir.name

    content = skill_md.read_text()
    match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip("\"'")
    return skill_dir.name


def collect_files(skill_dir: Path) -> list[Path]:
    """Collect all distributable files from a skill directory.

    Includes SKILL.md, references/, scripts/, and assets/.
    Excludes __pycache__, .git, node_modules, eval workspaces.

    Args:
        skill_dir: Path to skill directory

    Returns:
        Sorted list of file paths relative to skill_dir
    """
    files: list[Path] = []

    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue

        # Skip excluded directories
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue

        # Skip files with disallowed extensions
        if path.suffix and path.suffix not in ALLOWED_EXTENSIONS:
            continue

        # Skip hidden files
        if any(part.startswith(".") for part in path.relative_to(skill_dir).parts):
            continue

        files.append(path)

    return files


def package_skill(skill_dir: Path, output_path: Path | None = None) -> Path:
    """Package a skill directory into a .skill archive.

    Args:
        skill_dir: Path to skill directory containing SKILL.md
        output_path: Optional output path (default: <name>.skill in cwd)

    Returns:
        Path to the created .skill file

    Raises:
        SystemExit: If SKILL.md not found or no files to package
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"ERROR: SKILL.md not found in {skill_dir}", file=sys.stderr)
        sys.exit(1)

    name = extract_name(skill_dir)
    files = collect_files(skill_dir)

    if not files:
        print("ERROR: No files to package", file=sys.stderr)
        sys.exit(1)

    if output_path is None:
        output_path = Path.cwd() / f"{name}.skill"

    # Create tar.gz archive with skill name as root directory
    with tarfile.open(output_path, "w:gz") as tar:
        for file_path in files:
            arcname = f"{name}/{file_path.relative_to(skill_dir)}"
            tar.add(file_path, arcname=arcname)

    return output_path


def main() -> None:
    """Package a skill for distribution."""
    parser = argparse.ArgumentParser(description="Package a skill directory into a .skill archive")
    parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    parser.add_argument("--output", type=Path, help="Output path (default: <name>.skill)")

    args = parser.parse_args()

    if not args.skill_dir.is_dir():
        print(f"ERROR: Not a directory: {args.skill_dir}", file=sys.stderr)
        sys.exit(1)

    output = package_skill(args.skill_dir, args.output)

    # Print summary
    name = extract_name(args.skill_dir)
    files = collect_files(args.skill_dir)
    size_kb = output.stat().st_size / 1024

    print(f"Packaged: {name}")
    print(f"  Files: {len(files)}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Output: {output}")
    print("\nInstall with:")
    print(f"  tar xzf {output.name} -C ~/.claude/skills/")


if __name__ == "__main__":
    main()
