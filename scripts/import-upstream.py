#!/usr/bin/env python3
"""import-upstream.py - Fetch, validate, and import skills from upstream repos.

Usage:
    python3 scripts/import-upstream.py                     # Discover + import all
    python3 scripts/import-upstream.py --source anthropic  # Only from one source
    python3 scripts/import-upstream.py --dry-run            # Preview without PRs
    python3 scripts/import-upstream.py --threshold 8.0      # Require score >= 8.0
    python3 scripts/import-upstream.py --list               # List discoverable skills

Fetches skills from upstream repos defined in manifest.yaml sources,
runs full validation (structure, frontmatter, tokens, security, quality score),
and only imports skills scoring >= threshold (default 7.0).

In non-dry-run mode, creates a git branch and opens a PR for each passing skill
using the gh CLI.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
MANIFEST_PATH = SKILLS_DIR / "manifest.yaml"

DEFAULT_THRESHOLD = 7.0

# Load scoring module
_spec = spec_from_file_location("score_mod", SCRIPTS_DIR / "score-skill.py")
assert _spec is not None and _spec.loader is not None
score_mod = module_from_spec(_spec)
_spec.loader.exec_module(score_mod)
score_skill = score_mod.score_skill
assign_badge = score_mod.assign_badge


def load_manifest() -> dict[str, Any]:
    """Load manifest.yaml."""
    try:
        import yaml

        with open(MANIFEST_PATH) as f:
            return yaml.safe_load(f) or {}
    except (ImportError, FileNotFoundError):
        return {}


def clone_source(source_name: str, source_info: dict[str, Any], cache_dir: Path) -> Path | None:
    """Clone or update a source repo into cache_dir.

    Returns path to the skills subdirectory, or None on failure.
    """
    repo_url = source_info.get("repo", "")
    skills_path = source_info.get("path", "skills")

    if not repo_url:
        print(f"  Skip {source_name}: no repo URL", file=sys.stderr)
        return None

    repo_dir = cache_dir / source_name
    if repo_dir.exists():
        # Update existing clone
        result = subprocess.run(
            ["git", "-C", str(repo_dir), "fetch", "--depth=1", "origin"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            subprocess.run(
                ["git", "-C", str(repo_dir), "reset", "--hard", "origin/HEAD"],
                capture_output=True,
                timeout=10,
            )
    else:
        result = subprocess.run(
            ["git", "clone", "--depth=1", repo_url, str(repo_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"  Failed to clone {source_name}: {result.stderr.strip()}", file=sys.stderr)
            return None

    skills_dir = repo_dir / skills_path
    if not skills_dir.is_dir():
        print(f"  No {skills_path}/ in {source_name}", file=sys.stderr)
        return None

    return skills_dir


def discover_skills(
    source_name: str,
    source_skills_dir: Path,
    existing_skills: set[str],
) -> list[dict[str, Any]]:
    """Discover new skills from an upstream source not already in manifest."""
    discovered = []
    for skill_dir in sorted(source_skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue
        if skill_dir.name in existing_skills:
            continue

        discovered.append({
            "name": skill_dir.name,
            "source": source_name,
            "path": str(skill_dir),
        })

    return discovered


def validate_and_score(skill_dir: Path) -> dict[str, Any]:
    """Run full validation pipeline on a skill directory.

    Returns dict with 'passed', 'score', 'badge', 'errors'.
    """
    result: dict[str, Any] = {"passed": True, "score": 0.0, "badge": "Flagged", "errors": []}

    # Check SKILL.md exists
    if not (skill_dir / "SKILL.md").exists():
        result["passed"] = False
        result["errors"].append("Missing SKILL.md")
        return result

    # Run structure validation
    struct_result = subprocess.run(
        [str(SCRIPTS_DIR / "validate-structure.sh"), str(skill_dir)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if struct_result.returncode != 0:
        result["errors"].append("Structure validation failed")

    # Run frontmatter validation
    fm_result = subprocess.run(
        [str(SCRIPTS_DIR / "validate-frontmatter.sh"), str(skill_dir)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if fm_result.returncode != 0:
        result["errors"].append("Frontmatter validation failed")
        result["passed"] = False
        return result

    # Run security check
    sec_result = subprocess.run(
        [str(SCRIPTS_DIR / "security-check.sh"), str(skill_dir)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    security_passed = sec_result.returncode == 0
    if not security_passed:
        result["errors"].append("Security check failed")

    # Quality scoring
    try:
        report = score_skill(skill_dir)
        overall = report["overall_score"]
        badge = assign_badge(overall, security_passed=security_passed)
        result["score"] = overall
        result["badge"] = badge
    except Exception as e:
        result["errors"].append(f"Scoring failed: {e}")
        result["passed"] = False

    return result


def import_skill(
    skill_info: dict[str, Any],
    *,
    threshold: float,
    dry_run: bool,
) -> dict[str, Any]:
    """Import a single upstream skill: validate, score, optionally create PR.

    Returns result dict with import status.
    """
    name = skill_info["name"]
    source = skill_info["source"]
    source_path = Path(skill_info["path"])

    # Validate and score in-place from the cached upstream
    validation = validate_and_score(source_path)
    score = validation["score"]
    badge = validation["badge"]

    status: dict[str, Any] = {
        "name": name,
        "source": source,
        "score": score,
        "badge": badge,
        "errors": validation["errors"],
        "imported": False,
    }

    if not validation["passed"]:
        status["reason"] = "validation failed"
        return status

    if score < threshold:
        status["reason"] = f"score {score:.1f} < threshold {threshold:.1f}"
        return status

    # Skill passes — copy to local skills dir
    target_dir = SKILLS_DIR / name
    if target_dir.exists():
        status["reason"] = "already exists locally"
        return status

    if dry_run:
        status["imported"] = True
        status["reason"] = "dry-run: would import"
        return status

    # Copy skill
    shutil.copytree(source_path, target_dir)

    # Create branch and PR
    branch = f"import/{name}"
    try:
        subprocess.run(["git", "checkout", "-b", branch], capture_output=True, check=True, timeout=10)
        subprocess.run(["git", "add", str(target_dir)], capture_output=True, check=True, timeout=10)
        subprocess.run(
            ["git", "commit", "-m", f"feat: Import {name} from {source} (score {score:.1f})"],
            capture_output=True,
            check=True,
            timeout=10,
        )
        subprocess.run(["git", "push", "-u", "origin", branch], capture_output=True, check=True, timeout=30)

        pr_body = (
            f"## Import upstream skill: {name}\n\n"
            f"- **Source**: {source}\n"
            f"- **Quality Score**: {score:.1f}/10.0\n"
            f"- **Badge**: {badge}\n\n"
            f"Auto-imported by `import-upstream.py`."
        )
        subprocess.run(
            ["gh", "pr", "create", "--title", f"Import {name} from {source}", "--body", pr_body],
            capture_output=True,
            check=True,
            timeout=30,
        )
        status["imported"] = True
        status["reason"] = "PR created"
    except subprocess.CalledProcessError as e:
        status["reason"] = f"git/gh error: {e}"
    finally:
        # Return to main branch
        subprocess.run(["git", "checkout", "main"], capture_output=True, timeout=10)

    return status


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import and validate upstream skills for the registry"
    )
    parser.add_argument(
        "--source",
        help="Only import from this source (e.g. anthropic, vercel, obra)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Minimum quality score to import (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and score without creating PRs",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_only",
        help="List discoverable skills without importing",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    manifest = load_manifest()
    sources = manifest.get("sources", {})
    existing_skills = set(manifest.get("skills", {}).keys())

    if args.source:
        if args.source not in sources:
            print(f"Error: Unknown source '{args.source}'. Available: {', '.join(sources)}", file=sys.stderr)
            return 1
        sources = {args.source: sources[args.source]}

    # Clone sources and discover skills
    cache_dir = Path(tempfile.mkdtemp(prefix="skill-import-"))
    all_discovered: list[dict[str, Any]] = []

    print(f"Scanning {len(sources)} source(s)...", file=sys.stderr)
    for src_name, src_info in sources.items():
        print(f"  Cloning {src_name}...", file=sys.stderr)
        skills_dir = clone_source(src_name, src_info, cache_dir)
        if skills_dir is None:
            continue

        discovered = discover_skills(src_name, skills_dir, existing_skills)
        all_discovered.extend(discovered)
        print(f"  Found {len(discovered)} new skill(s) in {src_name}", file=sys.stderr)

    if not all_discovered:
        print("No new skills discovered.", file=sys.stderr)
        shutil.rmtree(cache_dir, ignore_errors=True)
        return 0

    if args.list_only:
        if args.json:
            print(json.dumps(all_discovered, indent=2))
        else:
            print(f"\nDiscoverable skills ({len(all_discovered)}):\n")
            for s in all_discovered:
                print(f"  {s['name']:<35} [{s['source']}]")
        shutil.rmtree(cache_dir, ignore_errors=True)
        return 0

    # Validate, score, and import
    results: list[dict[str, Any]] = []
    imported = 0
    skipped = 0

    print(f"\nEvaluating {len(all_discovered)} skill(s) (threshold: {args.threshold})...\n", file=sys.stderr)
    for skill_info in all_discovered:
        name = skill_info["name"]
        result = import_skill(skill_info, threshold=args.threshold, dry_run=args.dry_run)
        results.append(result)

        icon = "✓" if result["imported"] else "✗"
        score_str = f"{result['score']:.1f}" if result["score"] > 0 else "?"
        print(
            f"  {icon} {name:<35} score={score_str}  {result.get('reason', '')}",
            file=sys.stderr,
        )

        if result["imported"]:
            imported += 1
        else:
            skipped += 1

    # Summary
    print(f"\nImported: {imported}, Skipped: {skipped}", file=sys.stderr)

    if args.json:
        print(json.dumps(results, indent=2))

    # Cleanup
    shutil.rmtree(cache_dir, ignore_errors=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
