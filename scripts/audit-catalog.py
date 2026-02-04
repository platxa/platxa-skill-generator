#!/usr/bin/env python3
"""audit-catalog.py - Full validation + scoring audit across all catalog skills.

Usage:
    python3 scripts/audit-catalog.py                    # Human-readable report
    python3 scripts/audit-catalog.py --json             # JSON report
    python3 scripts/audit-catalog.py --threshold 8.0    # Custom pass threshold
    python3 scripts/audit-catalog.py --category backend # Filter by category

Runs validation, scoring, and duplicate checks across ALL skills and outputs
an aggregate report with per-skill scores and overall catalog health metrics.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent
SKILLS_DIR = PROJECT_ROOT / "skills"

_score_spec = spec_from_file_location("score_skill_mod", SCRIPTS_DIR / "score-skill.py")
assert _score_spec is not None and _score_spec.loader is not None
score_skill_mod = module_from_spec(_score_spec)
_score_spec.loader.exec_module(score_skill_mod)
score_skill = score_skill_mod.score_skill
assign_badge = score_skill_mod.assign_badge

# Import index generation for manifest data
_idx_spec = spec_from_file_location("gen_index_mod", SCRIPTS_DIR / "generate-index.py")
assert _idx_spec is not None and _idx_spec.loader is not None
gen_index_mod = module_from_spec(_idx_spec)
_idx_spec.loader.exec_module(gen_index_mod)
load_manifest = gen_index_mod.load_manifest


def run_validate_all(skill_dir: Path) -> tuple[bool, str]:
    """Run validate-all.sh on a skill directory."""
    validate_script = SCRIPTS_DIR / "validate-all.sh"
    if not validate_script.exists():
        return False, "validate-all.sh not found"

    try:
        result = subprocess.run(
            [str(validate_script), str(skill_dir), "--json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0, result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError) as e:
        return False, str(e)


def run_duplicate_check(skill_dir: Path) -> bool:
    """Run check-duplicates.py on a skill directory. Returns True if unique."""
    dup_script = SCRIPTS_DIR / "check-duplicates.py"
    if not dup_script.exists():
        return True

    try:
        result = subprocess.run(
            ["python3", str(dup_script), str(skill_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def run_security_check(skill_dir: Path) -> bool:
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


def audit_catalog(
    skills_dir: Path,
    threshold: float = 7.0,
    category_filter: str | None = None,
) -> dict[str, Any]:
    """Run full audit across all skills."""
    manifest_path = skills_dir / "manifest.yaml"
    manifest = load_manifest(manifest_path)
    manifest_skills = manifest.get("skills", {})

    results: list[dict[str, Any]] = []
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    cat_counts: dict[str, int] = {}
    cat_passed: dict[str, int] = {}
    cat_score_sums: dict[str, float] = {}
    tier_stats: dict[int, dict[str, int]] = {}
    source_stats: dict[str, dict[str, int]] = {}
    score_sum = 0.0
    badge_counts: dict[str, int] = {}

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name in ("overrides", ".git", "__pycache__", "badges"):
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue

        skill_name = skill_dir.name
        manifest_info = manifest_skills.get(skill_name, {})
        category = manifest_info.get("category", "uncategorized")
        tier = manifest_info.get("tier", 0)
        source = (
            "local" if manifest_info.get("local", False) else manifest_info.get("source", "unknown")
        )

        # Apply category filter
        if category_filter and category != category_filter:
            continue

        # Run scoring
        score_report = score_skill(skill_dir)
        score_report["threshold"] = threshold
        score_report["passed"] = score_report["overall_score"] >= threshold

        # Run duplicate check
        dup_passed = run_duplicate_check(skill_dir)

        # Run security check
        sec_passed = run_security_check(skill_dir)

        # Assign badge using score + security result
        badge = assign_badge(score_report["overall_score"], security_passed=sec_passed)

        entry: dict[str, Any] = {
            "name": skill_name,
            "category": category,
            "tier": tier,
            "source": source,
            "overall_score": score_report["overall_score"],
            "badge": badge,
            "passed": score_report["passed"] and dup_passed and sec_passed,
            "duplicate_check": "pass" if dup_passed else "fail",
            "security_check": "pass" if sec_passed else "fail",
            "dimensions": {k: v["score"] for k, v in score_report["dimensions"].items()},
        }

        results.append(entry)

        if entry["passed"]:
            total_passed += 1
        else:
            total_failed += 1

        score_sum += score_report["overall_score"]

        # Aggregate stats
        badge_counts[badge] = badge_counts.get(badge, 0) + 1

        cat_counts[category] = cat_counts.get(category, 0) + 1
        cat_score_sums[category] = cat_score_sums.get(category, 0.0) + score_report["overall_score"]
        if entry["passed"]:
            cat_passed[category] = cat_passed.get(category, 0) + 1

        if tier not in tier_stats:
            tier_stats[tier] = {"count": 0, "passed": 0}
        tier_stats[tier]["count"] += 1
        if entry["passed"]:
            tier_stats[tier]["passed"] += 1

        if source not in source_stats:
            source_stats[source] = {"count": 0, "passed": 0}
        source_stats[source]["count"] += 1
        if entry["passed"]:
            source_stats[source]["passed"] += 1

    total = total_passed + total_failed + total_skipped
    avg_score = round(score_sum / total, 2) if total > 0 else 0.0

    # Compute category averages
    category_averages = {}
    for cat in sorted(cat_counts):
        count = cat_counts[cat]
        category_averages[cat] = {
            "count": count,
            "passed": cat_passed.get(cat, 0),
            "avg_score": round(cat_score_sums[cat] / count, 2),
        }

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "threshold": threshold,
        "summary": {
            "total": total,
            "passed": total_passed,
            "failed": total_failed,
            "pass_rate": round(total_passed / total * 100, 1) if total > 0 else 0,
            "average_score": avg_score,
        },
        "badges": badge_counts,
        "by_category": category_averages,
        "by_tier": {str(k): v for k, v in sorted(tier_stats.items())},
        "by_source": dict(sorted(source_stats.items())),
        "skills": results,
    }


def print_human_readable(report: dict[str, Any]) -> None:
    """Print human-readable audit report."""
    summary = report["summary"]

    print("=" * 60)
    print("Skills Catalog Audit Report")
    print("=" * 60)
    print(f"  Generated: {report['generated_at']}")
    print(f"  Threshold: {report['threshold']}")
    print()

    print(f"  Total skills:   {summary['total']}")
    print(f"  Passed:         {summary['passed']}")
    print(f"  Failed:         {summary['failed']}")
    print(f"  Pass rate:      {summary['pass_rate']}%")
    print(f"  Average score:  {summary['average_score']}/10.0")
    print()

    # Badge distribution
    print("  Badges:")
    for badge, count in sorted(report["badges"].items()):
        print(f"    {badge:<12} {count}")
    print()

    # Category breakdown
    print("-" * 60)
    print(f"  {'Category':<20} {'Count':>5} {'Passed':>6} {'Avg':>6}")
    print("-" * 60)
    for cat, stats in report["by_category"].items():
        print(f"  {cat:<20} {stats['count']:>5} {stats['passed']:>6} {stats['avg_score']:>6}")
    print()

    # Per-skill results
    print("-" * 60)
    print(f"  {'Skill':<30} {'Score':>6} {'Badge':<12} {'Status'}")
    print("-" * 60)

    for skill in sorted(report["skills"], key=lambda s: -s["overall_score"]):
        status = "✓" if skill["passed"] else "✗"
        flags = ""
        if skill["duplicate_check"] != "pass":
            flags += " [DUP]"
        if skill.get("security_check") != "pass":
            flags += " [SEC]"
        print(
            f"  {skill['name']:<30} {skill['overall_score']:>5}/10 {skill['badge']:<12} {status}{flags}"
        )

    print()
    print("=" * 60)

    if summary["pass_rate"] >= 80:
        print("✓ Catalog health: GOOD")
    elif summary["pass_rate"] >= 60:
        print("⚠ Catalog health: FAIR")
    else:
        print("✗ Catalog health: NEEDS ATTENTION")

    print("=" * 60)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run full audit across all catalog skills")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=SKILLS_DIR,
        help="Skills directory (default: skills/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=7.0,
        help="Minimum passing score (default: 7.0)",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filter by category",
    )

    args = parser.parse_args()

    if not args.skills_dir.is_dir():
        print(f"Error: Not a directory: {args.skills_dir}", file=sys.stderr)
        return 1

    report = audit_catalog(args.skills_dir, args.threshold, args.category)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human_readable(report)

    # Exit 1 if any skills failed
    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
