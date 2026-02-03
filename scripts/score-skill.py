#!/usr/bin/env python3
"""score-skill.py - Multi-dimension quality scoring for skills.

Usage:
    python3 scripts/score-skill.py skills/code-documenter
    python3 scripts/score-skill.py skills/code-documenter --json
    python3 scripts/score-skill.py skills/code-documenter --threshold 8.0

Scores a skill across 5 dimensions (each 0-10):
    1. spec        - Frontmatter compliance (name, description, tools, metadata)
    2. content     - Description quality, no placeholders, real domain expertise
    3. structure   - Directory layout, file organization, executable scripts
    4. tokens      - Token budget compliance (under limits = higher score)
    5. completeness - References, examples, scripts, tags, metadata richness

Outputs a JSON report with per-dimension scores, overall weighted average,
and a badge recommendation (Verified >= 8.0, Reviewed >= 7.0, Unverified < 7.0).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).parent

_spec = spec_from_file_location("count_tokens_mod", SCRIPTS_DIR / "count-tokens.py")
assert _spec is not None and _spec.loader is not None
count_tokens_mod = module_from_spec(_spec)
_spec.loader.exec_module(count_tokens_mod)
analyze_skill = count_tokens_mod.analyze_skill

# Valid tools list from CLAUDE.md
VALID_TOOLS = {
    "Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "LS",
    "Bash", "Task", "WebFetch", "WebSearch", "AskUserQuestion",
    "TodoWrite", "KillShell", "BashOutput", "NotebookEdit",
}

# Each pattern is (regex, flags) so case-sensitivity is per-pattern.
_CI = re.IGNORECASE
_CS = 0  # case-sensitive

PLACEHOLDER_PATTERNS: list[tuple[str, int]] = [
    (r"\bTODO\b", _CS),
    (r"\bTBD\b", _CS),
    (r"\bFIXME\b", _CS),
    (r"\bHACK\b", _CS),
    (r"\bXXX\b", _CS),
    (r"\[insert\b", _CI),
    (r"\[your[- ]", _CI),
    (r"\bplaceholder\b", _CI),
    (r"lorem ipsum", _CI),
    (r"example\.com", _CI),
]

# AI-generated filler / slop patterns — generic phrases that signal
# restated defaults or lack of real domain expertise.
SLOP_PATTERNS: list[tuple[str, int]] = [
    # Generic filler phrases (case-insensitive — natural language)
    (r"it(?:'s| is) (?:important|essential|crucial|critical) to (?:note|remember|understand)", _CI),
    (r"(?:this|the) skill (?:helps|allows|enables) (?:you|users|the user) to", _CI),
    (r"in today(?:'s| s) (?:fast[- ]paced|modern|ever[- ]changing)", _CI),
    (r"best practices for (?:ensuring|maintaining|achieving)", _CI),
    (r"leverage(?:s|d|ing)? (?:the power|cutting[- ]edge|state[- ]of[- ]the[- ]art)", _CI),
    (r"a comprehensive (?:guide|overview|solution|approach|framework)", _CI),
    (r"seamless(?:ly)? integrat", _CI),
    (r"robust and scalable", _CI),
    (r"world[- ]class", _CI),
    # Restated defaults / contradictions
    (r"(?:simply|just) (?:use|run|execute|call) (?:this|the) (?:skill|tool|command)", _CI),
    (r"this skill (?:is|was) (?:designed|created|built) to", _CI),
    # Incomplete / stub content
    (r"add (?:more|additional) (?:details|content|information) here", _CI),
    (r"describe (?:your|the) .{0,20} here", _CI),
    (r"replace (?:this|the above) with", _CI),
    # Uppercase template variables like <YOUR_NAME> (case-sensitive to
    # avoid matching legitimate lowercase docs syntax like <type>)
    (r"<[A-Z][A-Z_]{2,}>", _CS),
]


def parse_frontmatter(skill_md: Path) -> dict[str, Any]:
    """Extract YAML frontmatter from SKILL.md."""
    try:
        text = skill_md.read_text()
    except OSError:
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    try:
        import yaml
        fm = yaml.safe_load(match.group(1))
        return fm if isinstance(fm, dict) else {}
    except (ImportError, Exception):
        return {}


def score_spec(skill_dir: Path) -> tuple[float, list[str]]:
    """Score frontmatter/spec compliance (0-10)."""
    skill_md = skill_dir / "SKILL.md"
    notes: list[str] = []

    if not skill_md.exists():
        return 0.0, ["SKILL.md missing"]

    text = skill_md.read_text()

    # Check frontmatter exists
    if not re.match(r"^---\s*\n", text):
        return 1.0, ["No YAML frontmatter"]

    fm = parse_frontmatter(skill_md)
    if not fm:
        return 1.0, ["Frontmatter parse failed"]

    score = 3.0  # Base for having valid frontmatter

    # name field
    name = fm.get("name", "")
    if name:
        score += 1.5
        if re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name) and len(name) <= 64:
            score += 0.5
        else:
            notes.append("Name format issues")
    else:
        notes.append("Missing name field")

    # description field
    desc = fm.get("description", "")
    if desc:
        score += 1.5
        if len(desc) <= 1024:
            score += 0.5
        else:
            notes.append(f"Description too long ({len(desc)} > 1024)")
    else:
        notes.append("Missing description field")

    # allowed-tools
    tools = fm.get("allowed-tools") or fm.get("tools")
    if isinstance(tools, list) and tools:
        score += 1.0
        invalid = [t for t in tools if t not in VALID_TOOLS]
        if invalid:
            score -= 0.5
            notes.append(f"Invalid tools: {invalid}")
    else:
        notes.append("No allowed-tools specified")

    # metadata block
    metadata = fm.get("metadata", {})
    if isinstance(metadata, dict) and metadata:
        score += 1.0
        if metadata.get("version"):
            score += 0.5
    else:
        notes.append("No metadata block")

    return min(score, 10.0), notes


def score_content(skill_dir: Path) -> tuple[float, list[str]]:
    """Score content quality (0-10)."""
    skill_md = skill_dir / "SKILL.md"
    notes: list[str] = []

    if not skill_md.exists():
        return 0.0, ["SKILL.md missing"]

    text = skill_md.read_text()

    # Strip frontmatter for body analysis
    body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.DOTALL)

    if not body.strip():
        return 0.0, ["Empty body content"]

    score = 0.0

    # Length check - meaningful content
    word_count = len(body.split())
    if word_count >= 50:
        score += 2.0
    elif word_count >= 20:
        score += 1.0
    else:
        notes.append(f"Very short body ({word_count} words)")

    # Has headers (structured content)
    headers = re.findall(r"^#+\s+.+", body, re.MULTILINE)
    if len(headers) >= 3:
        score += 2.0
    elif len(headers) >= 1:
        score += 1.0
    else:
        notes.append("No markdown headers")

    # Has code examples
    code_blocks = re.findall(r"```[\s\S]*?```", body)
    if len(code_blocks) >= 2:
        score += 2.0
    elif len(code_blocks) >= 1:
        score += 1.0
    else:
        notes.append("No code examples")

    # Has bullet/numbered lists
    lists = re.findall(r"^[\s]*[-*\d.]+\s+.+", body, re.MULTILINE)
    if len(lists) >= 3:
        score += 1.0
    elif len(lists) >= 1:
        score += 0.5

    # Placeholder and AI-slop detection
    placeholder_hits: list[str] = []
    for pattern, flags in PLACEHOLDER_PATTERNS:
        if re.search(pattern, body, flags):
            placeholder_hits.append(pattern)

    slop_hits: list[str] = []
    for pattern, flags in SLOP_PATTERNS:
        if re.search(pattern, body, flags):
            slop_hits.append(pattern)

    total_hits = len(placeholder_hits) + len(slop_hits)
    if total_hits == 0:
        score += 1.5
    else:
        # Proportional penalty: -0.5 per hit, up to -3.0
        penalty = min(total_hits * 0.5, 3.0)
        score -= penalty
        if placeholder_hits:
            notes.append(f"Placeholders ({len(placeholder_hits)}): {placeholder_hits[0]}")
        if slop_hits:
            notes.append(f"Generic filler ({len(slop_hits)}): {slop_hits[0]}")

    # Description quality (from frontmatter)
    fm = parse_frontmatter(skill_md)
    desc = fm.get("description", "")
    if len(desc) >= 50:
        score += 1.0
    elif len(desc) >= 20:
        score += 0.5
    else:
        notes.append("Short description")

    # Has trigger/usage guidance
    if re.search(r"(use when|trigger|invoke|usage|when to use)", body, re.IGNORECASE):
        score += 0.5

    return min(max(score, 0.0), 10.0), notes


def score_structure(skill_dir: Path) -> tuple[float, list[str]]:
    """Score directory structure (0-10)."""
    notes: list[str] = []

    if not skill_dir.is_dir():
        return 0.0, ["Not a directory"]

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return 0.0, ["SKILL.md missing"]

    score = 5.0  # Base for having SKILL.md in a directory

    # References directory
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        ref_files = list(refs_dir.glob("*.md"))
        if ref_files:
            score += 2.0
        else:
            score += 0.5
            notes.append("Empty references/ directory")
    else:
        notes.append("No references/ directory")

    # Scripts directory
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        script_files = list(scripts_dir.iterdir())
        if script_files:
            score += 1.5
            # Check executability
            non_exec = [
                f.name for f in script_files
                if f.suffix in (".sh", ".py") and not f.stat().st_mode & 0o111
            ]
            if non_exec:
                score -= 0.5
                notes.append(f"Non-executable scripts: {non_exec}")
        else:
            notes.append("Empty scripts/ directory")

    # Templates directory
    templates_dir = skill_dir / "templates"
    if templates_dir.is_dir() and list(templates_dir.iterdir()):
        score += 1.0

    # No unexpected files at root
    expected_root = {"SKILL.md", "references", "scripts", "templates", ".skillconfig", ".gitkeep"}
    unexpected = [
        f.name for f in skill_dir.iterdir()
        if f.name not in expected_root and not f.name.startswith(".")
    ]
    if unexpected:
        score -= 0.5
        notes.append(f"Unexpected files: {unexpected}")

    return min(max(score, 0.0), 10.0), notes


def score_tokens(skill_dir: Path) -> tuple[float, list[str]]:
    """Score token budget compliance (0-10)."""
    notes: list[str] = []

    try:
        report = analyze_skill(skill_dir)
    except Exception as e:
        return 0.0, [f"Token analysis failed: {e}"]

    total = report["total_tokens"]
    skill_md_tokens = report["skill_md_tokens"]

    score = 10.0  # Start at max, deduct for violations

    # SKILL.md token budget
    if skill_md_tokens > 10000:
        score -= 4.0
        notes.append(f"SKILL.md over hard limit ({skill_md_tokens:,} > 10,000)")
    elif skill_md_tokens > 5000:
        score -= 2.0
        notes.append(f"SKILL.md over recommended ({skill_md_tokens:,} > 5,000)")
    elif skill_md_tokens > 3000:
        score -= 0.5

    # Total token budget
    if total > 30000:
        score -= 4.0
        notes.append(f"Total over hard limit ({total:,} > 30,000)")
    elif total > 15000:
        score -= 2.0
        notes.append(f"Total over recommended ({total:,} > 15,000)")
    elif total > 10000:
        score -= 0.5

    # Line count
    skill_md_lines = report["skill_md_lines"]
    if skill_md_lines > 1000:
        score -= 2.0
        notes.append(f"SKILL.md too many lines ({skill_md_lines:,} > 1,000)")
    elif skill_md_lines > 500:
        score -= 1.0
        notes.append(f"SKILL.md over recommended lines ({skill_md_lines:,} > 500)")

    # Bonus for being well within budget
    if total < 3000 and skill_md_tokens < 2000:
        score = min(score + 0.5, 10.0)

    return min(max(score, 0.0), 10.0), notes


def score_completeness(skill_dir: Path) -> tuple[float, list[str]]:
    """Score completeness/richness (0-10)."""
    notes: list[str] = []
    score = 0.0

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return 0.0, ["SKILL.md missing"]

    fm = parse_frontmatter(skill_md)

    # Has tags
    metadata = fm.get("metadata", {})
    if isinstance(metadata, dict):
        tags = metadata.get("tags", [])
        if isinstance(tags, list) and len(tags) >= 2:
            score += 1.5
        elif isinstance(tags, list) and len(tags) >= 1:
            score += 0.75
        else:
            notes.append("No tags in metadata")

        # Has version
        if metadata.get("version"):
            score += 1.0
        else:
            notes.append("No version in metadata")

        # Has author
        if metadata.get("author"):
            score += 0.5
    else:
        notes.append("No metadata block")

    # Has references
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        ref_files = list(refs_dir.glob("**/*.md"))
        if len(ref_files) >= 3:
            score += 2.0
        elif len(ref_files) >= 1:
            score += 1.0
        else:
            notes.append("No reference files")
    else:
        notes.append("No references directory")

    # Has scripts
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir() and list(scripts_dir.iterdir()):
        score += 1.5
    else:
        notes.append("No helper scripts")

    # Body completeness
    text = skill_md.read_text()
    body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.DOTALL)

    # Has examples section
    if re.search(r"##?\s*(examples?|usage)", body, re.IGNORECASE):
        score += 1.0

    # Has output/template section
    if re.search(r"##?\s*(output|template|format|checklist)", body, re.IGNORECASE):
        score += 0.75

    # Has workflow/steps section
    if re.search(r"##?\s*(workflow|steps|process|phases?)", body, re.IGNORECASE):
        score += 0.75

    # allowed-tools specified
    tools = fm.get("allowed-tools") or fm.get("tools")
    if isinstance(tools, list) and tools:
        score += 1.0

    return min(max(score, 0.0), 10.0), notes


def score_expertise(skill_dir: Path) -> tuple[float, list[str]]:
    """Score expertise depth — real domain knowledge vs generic instructions (0-10).

    Uses structural heuristics that generalize across all domains, rather than
    hardcoded technology lists. Measures:
        1. Specificity density — ratio of specific tokens (identifiers, paths,
           numbers-with-units) to total prose words.
        2. Code block substance — structural code indicators (assignments,
           operators, function calls, flags) vs empty/pseudocode blocks.
        3. Vocabulary richness — type-token ratio. Expert content uses more
           unique terms; generic filler repeats vague words.
        4. Concrete references — file paths, config keys (snake_case/kebab-case
           compounds), numeric thresholds with units.
        5. Proper noun density — PascalCase and UPPER_CASE terms that indicate
           named technologies, standards, or protocols.
    """
    skill_md = skill_dir / "SKILL.md"
    notes: list[str] = []

    if not skill_md.exists():
        return 0.0, ["SKILL.md missing"]

    text = skill_md.read_text()
    body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.DOTALL)

    if not body.strip():
        return 0.0, ["Empty body"]

    score = 0.0

    # --- 1. Specificity density (up to 2.0) ---
    # Specific tokens: identifiers with dots/underscores/hyphens, paths, numbers with units
    specific_tokens = re.findall(
        r"(?:"
        r"\w+[._]\w+(?:[._]\w+)*"  # dotted/underscored identifiers: os.path, max_retries
        r"|[a-zA-Z0-9_-]+/[a-zA-Z0-9_./*-]+"  # file paths: src/utils/*.ts
        r"|\d+(?:\.\d+)*\s*(?:[kmgtKMGT]?[bB]|ms|[mun]?s|min|h|%|px|rem|em|pt|tokens|lines|bytes|MB|GB)"  # numbers with units
        r"|-{1,2}[a-zA-Z][\w-]*"  # CLI flags: --verbose, -v
        r")",
        body,
    )
    total_words = len(body.split())
    if total_words > 0:
        density = len(specific_tokens) / total_words
        if density >= 0.15:
            score += 2.0
        elif density >= 0.08:
            score += 1.5
        elif density >= 0.04:
            score += 1.0
        elif density >= 0.02:
            score += 0.5
        else:
            notes.append(f"Low specificity ({len(specific_tokens)}/{total_words} words)")

    # --- 2. Code block substance (up to 2.5) ---
    code_blocks = re.findall(r"```\w*\n([\s\S]*?)```", body)
    substantial_blocks = 0
    for block in code_blocks:
        # Structural code indicators that generalize across all languages/CLIs:
        # assignments, function calls, shell operators, flags, brackets
        indicators = sum([
            bool(re.search(r"[=:]\s*\S", block)),           # assignments: x = 1, key: val
            bool(re.search(r"\w+\(", block)),                # function calls: func(
            bool(re.search(r"[|>&]{1,2}", block)),           # shell/logical operators
            bool(re.search(r"-{1,2}[a-zA-Z]", block)),      # CLI flags: --flag, -v
            bool(re.search(r"[{}[\]]", block)),              # brackets/braces
            bool(re.search(r"^\s*\w+\s+\w+", block, re.MULTILINE)),  # command subcommand
        ])
        if indicators >= 2:
            substantial_blocks += 1

    if substantial_blocks >= 4:
        score += 2.5
    elif substantial_blocks >= 2:
        score += 1.5
    elif substantial_blocks >= 1:
        score += 0.75
    else:
        if code_blocks:
            notes.append(f"Code blocks lack substance ({len(code_blocks)} blocks, {substantial_blocks} substantial)")
        else:
            notes.append("No code blocks")

    # --- 3. Vocabulary richness / type-token ratio (up to 2.0) ---
    # Strip code blocks and markdown syntax for prose analysis
    prose = re.sub(r"```[\s\S]*?```", "", body)
    prose = re.sub(r"[#*|`_\[\]()]", " ", prose)
    words = [w.lower() for w in prose.split() if len(w) >= 3]
    if len(words) >= 20:
        unique_words = len(set(words))
        ttr = unique_words / len(words)
        if ttr >= 0.65:
            score += 2.0
        elif ttr >= 0.50:
            score += 1.5
        elif ttr >= 0.40:
            score += 1.0
        else:
            notes.append(f"Repetitive vocabulary (TTR={ttr:.2f})")

    # --- 4. Concrete references (up to 2.0) ---
    # File paths (slash-separated), config keys (multi-segment snake/kebab),
    # numbers with context (not bare digits)
    file_paths = re.findall(r"[a-zA-Z0-9_.-]+/[a-zA-Z0-9_./*-]+", body)
    config_keys = re.findall(r"\b[a-zA-Z][a-zA-Z0-9]*(?:[_-][a-zA-Z0-9]+){2,}\b", body)
    numbers_with_units = re.findall(
        r"\d+(?:\.\d+)*\s*(?:[kmgtKMGT]?[bB]|ms|[mun]?s|min|h|%|px|rem|em|pt|tokens|lines|bytes|MB|GB)\b",
        body,
    )
    concrete_count = len(set(file_paths)) + len(set(config_keys)) + len(numbers_with_units)
    if concrete_count >= 15:
        score += 2.0
    elif concrete_count >= 8:
        score += 1.5
    elif concrete_count >= 3:
        score += 1.0
    elif concrete_count >= 1:
        score += 0.5
    else:
        notes.append("Few concrete references")

    # --- 5. Proper noun / technical term density (up to 1.5) ---
    # PascalCase words (>=2 uppercase transitions) and UPPER_CASE abbreviations (>=3 chars)
    # These generalize across domains without a hardcoded tech list.
    pascal_case = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", body)  # WebSocket, FastAPI
    upper_abbrev = re.findall(r"\b[A-Z][A-Z0-9]{2,}\b", body)  # JWT, CORS, HPA, CRDT
    # Filter out common English abbreviations
    common_abbrev = {"THE", "AND", "FOR", "NOT", "BUT", "ALL", "THIS", "THAT", "WITH", "FROM", "MUST", "SHOULD"}
    tech_terms = set(pascal_case) | {a for a in upper_abbrev if a not in common_abbrev}
    if len(tech_terms) >= 8:
        score += 1.5
    elif len(tech_terms) >= 4:
        score += 1.0
    elif len(tech_terms) >= 2:
        score += 0.5
    else:
        notes.append("Few technical terms")

    return min(max(score, 0.0), 10.0), notes


def score_skill(skill_dir: Path) -> dict[str, Any]:
    """Run all 6 scoring dimensions and produce a report."""
    dimensions = {
        "spec": score_spec,
        "content": score_content,
        "structure": score_structure,
        "tokens": score_tokens,
        "completeness": score_completeness,
        "expertise": score_expertise,
    }

    weights = {
        "spec": 0.20,
        "content": 0.20,
        "structure": 0.10,
        "tokens": 0.15,
        "completeness": 0.15,
        "expertise": 0.20,
    }

    scores: dict[str, Any] = {}
    weighted_sum = 0.0

    for dim_name, scorer in dimensions.items():
        dim_score, dim_notes = scorer(skill_dir)
        scores[dim_name] = {
            "score": round(dim_score, 1),
            "weight": weights[dim_name],
            "notes": dim_notes,
        }
        weighted_sum += dim_score * weights[dim_name]

    overall = round(weighted_sum, 2)

    # Badge recommendation
    if overall >= 8.0:
        badge = "Verified"
    elif overall >= 7.0:
        badge = "Reviewed"
    elif overall >= 5.0:
        badge = "Unverified"
    else:
        badge = "Flagged"

    passed = overall >= 7.0

    return {
        "skill_name": skill_dir.name,
        "overall_score": overall,
        "passed": passed,
        "badge": badge,
        "threshold": 7.0,
        "dimensions": scores,
    }


def print_human_readable(report: dict[str, Any]) -> None:
    """Print a human-readable score report."""
    name = report["skill_name"]
    overall = report["overall_score"]
    badge = report["badge"]
    passed = report["passed"]

    print(f"{'='*50}")
    print(f"Quality Score: {name}")
    print(f"{'='*50}")
    print()

    for dim_name, dim_data in report["dimensions"].items():
        score = dim_data["score"]
        weight = dim_data["weight"]
        bar = "█" * int(score) + "░" * (10 - int(score))
        notes_str = ""
        if dim_data["notes"]:
            notes_str = f"  ({', '.join(dim_data['notes'][:2])})"
        print(f"  {dim_name:<14} {bar} {score:>4}/10  (w={weight}){notes_str}")

    print()
    print(f"  {'Overall':<14} {'':>10} {overall:>5}/10.0")
    print(f"  {'Badge':<14} {'':>10} {badge}")
    print()

    if passed:
        print("✓ PASSED (>= 7.0)")
    else:
        print("✗ FAILED (< 7.0)")

    print(f"{'='*50}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Score a skill across 5 quality dimensions"
    )
    parser.add_argument(
        "skill_dir",
        type=Path,
        help="Path to the skill directory",
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

    args = parser.parse_args()

    if not args.skill_dir.is_dir():
        print(f"Error: Not a directory: {args.skill_dir}", file=sys.stderr)
        return 1

    report = score_skill(args.skill_dir)
    report["threshold"] = args.threshold
    report["passed"] = report["overall_score"] >= args.threshold

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human_readable(report)

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
