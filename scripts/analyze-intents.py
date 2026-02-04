"""analyze-intents.py - Analyze intent extraction results and produce summary report.

Usage:
    python3 scripts/analyze-intents.py                          # Human-readable report
    python3 scripts/analyze-intents.py --json                   # JSON output
    python3 scripts/analyze-intents.py --output report.json     # Write JSON to file
    python3 scripts/analyze-intents.py .claude/intents          # Custom intents dir

Reads all intent JSON files from .claude/intents/ and categorizes skills
by confidence tier (high >= 0.7, medium 0.5-0.7, low < 0.5).  Identifies
skills needing enrichment and produces a summary report.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_intents(intents_dir: Path) -> list[dict[str, Any]]:
    """Load all intent JSON files from a directory."""
    intents: list[dict[str, Any]] = []
    for f in sorted(intents_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "skill_name" in data:
                intents.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return intents


def categorize_by_confidence(
    intents: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Categorize intents into confidence tiers."""
    tiers: dict[str, list[dict[str, Any]]] = {
        "high": [],
        "medium": [],
        "low": [],
    }
    for intent in intents:
        confidence = intent.get("confidence_score", 0.0)
        if confidence >= 0.7:
            tiers["high"].append(intent)
        elif confidence >= 0.5:
            tiers["medium"].append(intent)
        else:
            tiers["low"].append(intent)
    return tiers


def identify_enrichment_needs(intent: dict[str, Any]) -> list[str]:
    """Identify specific areas where a skill needs enrichment."""
    needs: list[str] = []

    if not intent.get("description"):
        needs.append("missing description")

    refs = intent.get("reference_topics", [])
    if len(refs) == 0:
        needs.append("no reference documentation")

    scripts = intent.get("script_descriptions", [])
    if len(scripts) == 0:
        needs.append("no executable scripts")

    concepts = intent.get("key_concepts", [])
    if len(concepts) < 3:
        needs.append("few key concepts extracted")

    workflows = intent.get("key_workflows", [])
    if len(workflows) < 3:
        needs.append("few workflows identified")

    domain = intent.get("domain", {})
    if not domain.get("subdomains"):
        needs.append("no subdomains detected")

    return needs


def build_report(intents: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the full analysis report."""
    tiers = categorize_by_confidence(intents)

    # Sort each tier by confidence descending
    for tier_list in tiers.values():
        tier_list.sort(key=lambda x: -x.get("confidence_score", 0))

    # Build per-skill summaries with enrichment needs
    tier_summaries: dict[str, list[dict[str, Any]]] = {}
    for tier_name, tier_intents in tiers.items():
        summaries: list[dict[str, Any]] = []
        for intent in tier_intents:
            entry: dict[str, Any] = {
                "skill_name": intent.get("skill_name", "unknown"),
                "confidence": intent.get("confidence_score", 0.0),
                "skill_type": intent.get("skill_type", "unknown"),
                "domain": intent.get("domain", {}).get("primary_domain", "unknown"),
            }
            needs = identify_enrichment_needs(intent)
            if needs:
                entry["enrichment_needs"] = needs
            summaries.append(entry)
        tier_summaries[tier_name] = summaries

    # Skill type distribution
    type_counts: dict[str, int] = {}
    for intent in intents:
        st = intent.get("skill_type", "unknown")
        type_counts[st] = type_counts.get(st, 0) + 1

    # Domain distribution
    domain_counts: dict[str, int] = {}
    for intent in intents:
        d = intent.get("domain", {}).get("primary_domain", "unknown")
        domain_counts[d] = domain_counts.get(d, 0) + 1

    confidences = [i.get("confidence_score", 0.0) for i in intents]

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_skills": len(intents),
        "confidence_summary": {
            "high": len(tiers["high"]),
            "medium": len(tiers["medium"]),
            "low": len(tiers["low"]),
            "average": round(sum(confidences) / len(confidences), 2) if confidences else 0,
            "min": round(min(confidences), 2) if confidences else 0,
            "max": round(max(confidences), 2) if confidences else 0,
        },
        "tiers": tier_summaries,
        "type_distribution": dict(sorted(type_counts.items(), key=lambda x: -x[1])),
        "domain_distribution": dict(sorted(domain_counts.items(), key=lambda x: -x[1])),
        "needs_enrichment": [
            i.get("skill_name", "unknown")
            for i in intents
            if len(identify_enrichment_needs(i)) >= 3
        ],
    }


def print_report(report: dict[str, Any]) -> None:
    """Print the report in human-readable format."""
    cs = report["confidence_summary"]

    print("=" * 60)
    print("Intent Extraction Analysis Report")
    print("=" * 60)
    print(f"  Total skills analyzed: {report['total_skills']}")
    print(f"  Average confidence:    {cs['average']:.2f}")
    print(f"  Range:                 {cs['min']:.2f} - {cs['max']:.2f}")
    print()
    print(f"  High (>= 0.7):  {cs['high']}")
    print(f"  Medium (0.5-0.7): {cs['medium']}")
    print(f"  Low (< 0.5):    {cs['low']}")

    for tier_name in ("high", "medium", "low"):
        skills = report["tiers"][tier_name]
        if not skills:
            continue
        print()
        print(f"── {tier_name.upper()} confidence ({len(skills)}) ──")
        for s in skills:
            needs = s.get("enrichment_needs", [])
            suffix = f"  [{', '.join(needs)}]" if needs else ""
            print(f"  {s['confidence']:.2f}  {s['skill_name']:<40} {s['skill_type']:<12}{suffix}")

    print()
    print("── Type Distribution ──")
    for t, count in report["type_distribution"].items():
        print(f"  {t:<12} {count}")

    print()
    print("── Domain Distribution ──")
    for d, count in report["domain_distribution"].items():
        print(f"  {d:<24} {count}")

    enrichment = report.get("needs_enrichment", [])
    if enrichment:
        print()
        print(f"── Skills Needing Enrichment ({len(enrichment)}) ──")
        for name in enrichment:
            print(f"  - {name}")

    print()
    print("=" * 60)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze intent extraction results and produce summary report"
    )
    parser.add_argument(
        "intents_dir",
        type=Path,
        nargs="?",
        default=None,
        help="Path to intents directory (default: .claude/intents)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (default: human-readable)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON report to file",
    )

    args = parser.parse_args()

    if args.intents_dir is None:
        project_root = Path(__file__).parent.parent
        args.intents_dir = project_root / ".claude" / "intents"

    if not args.intents_dir.is_dir():
        print(f"Error: Not a directory: {args.intents_dir}", file=sys.stderr)
        return 1

    intents = load_intents(args.intents_dir)
    if not intents:
        print(f"Error: No intent files found in {args.intents_dir}", file=sys.stderr)
        return 1

    report = build_report(intents)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", "utf-8")
        cs = report["confidence_summary"]
        print(
            f"Report: {report['total_skills']} skills — "
            f"{cs['high']} high, {cs['medium']} medium, {cs['low']} low",
            file=sys.stderr,
        )
    elif args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
