"""extract-skill-intent.py - Extract structured intent from an upstream skill directory.

Usage:
    python3 scripts/extract-skill-intent.py skills/figma
    python3 scripts/extract-skill-intent.py skills/figma --json
    python3 scripts/extract-skill-intent.py skills/figma --output .claude/intents/figma.json

Reads an upstream skill directory (SKILL.md + references/ + scripts/) and outputs
structured intent JSON matching the platxa-skill-generator discovery agent input format.

The extracted intent captures the *idea* behind the skill — its domain, purpose,
key workflows, tool needs, and reference topics — without copying the upstream code.
This intent feeds the regeneration pipeline to produce Platxa-native skills.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Skill type classification keywords ──────────────────────────────
# Each type has unique indicator keywords.  Description presence is
# weighted 10x heavier than body presence because the description is
# the author's stated intent — the body provides supporting evidence.

SKILL_TYPE_INDICATORS: dict[str, list[str]] = {
    "builder": [
        "generate",
        "create",
        "build",
        "scaffold",
        "produce",
        "construct",
        "make",
        "output",
        "template",
        "boilerplate",
    ],
    "guide": [
        "guide",
        "tutorial",
        "how-to",
        "explain",
        "teach",
        "document",
        "reference",
        "learn",
        "best practice",
        "pattern",
        "convention",
    ],
    "automation": [
        "automate",
        "workflow",
        "pipeline",
        "batch",
        "schedule",
        "orchestrate",
        "process",
        "deploy",
        "ci/cd",
        "hook",
    ],
    "analyzer": [
        "analyze",
        "inspect",
        "review",
        "check",
        "audit",
        "scan",
        "examine",
        "evaluate",
        "report",
        "metric",
    ],
    "validator": [
        "validate",
        "verify",
        "lint",
        "test",
        "assert",
        "confirm",
        "ensure",
        "comply",
        "security",
        "quality",
    ],
}

# ── Valid Claude Code tools ─────────────────────────────────────────

VALID_TOOLS: set[str] = {
    "Read",
    "Write",
    "Edit",
    "MultiEdit",
    "Glob",
    "Grep",
    "LS",
    "Bash",
    "Task",
    "WebFetch",
    "WebSearch",
    "AskUserQuestion",
    "TodoWrite",
    "KillShell",
    "BashOutput",
    "NotebookEdit",
}

# ── Content-based tool mapping ──────────────────────────────────────
# Maps body content keywords to likely tool dependencies.

CONTENT_TOOL_MAPPING: dict[str, list[str]] = {
    "file": ["Read", "Write"],
    "search": ["Grep", "Glob"],
    "execute": ["Bash"],
    "command": ["Bash"],
    "script": ["Bash"],
    "web": ["WebFetch", "WebSearch"],
    "fetch": ["WebFetch"],
    "browser": ["WebFetch"],
    "user input": ["AskUserQuestion"],
    "prompt": ["AskUserQuestion"],
    "task": ["Task"],
    "subagent": ["Task"],
    "notebook": ["NotebookEdit"],
}


# ── Extraction functions ────────────────────────────────────────────


def parse_frontmatter(skill_md: Path) -> dict[str, Any]:
    """Extract YAML frontmatter from SKILL.md."""
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    fm: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if line.startswith("name:"):
            fm["name"] = line.split(":", 1)[1].strip().strip("\"'")
        elif line.startswith("description:"):
            fm["description"] = line.split(":", 1)[1].strip().strip("\"'")
    return fm


def extract_body(skill_md: Path) -> str:
    """Extract body content after frontmatter."""
    text = skill_md.read_text(encoding="utf-8")
    body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", text, count=1, flags=re.DOTALL)
    return body


def classify_skill_type(description: str, body: str) -> tuple[str, dict[str, int]]:
    """Classify skill type from description and body keywords.

    Uses **unique keyword presence** (not occurrence count) to prevent
    keyword repetition from inflating scores.  Description presence is
    weighted 10x heavier than body presence because the description is
    the author's stated intent — the body provides supporting evidence.

    With 10x weight, a single description keyword hit (10 pts) outweighs
    up to 9 body keyword hits.  This ensures the description's intent
    dominates while the body still serves as a tie-breaker when the
    description is ambiguous or silent.

    Returns the classified type and per-type scores for transparency.
    """
    desc_lower = description.lower()
    body_lower = body.lower()

    scores = dict.fromkeys(SKILL_TYPE_INDICATORS, 0)

    for skill_type, keywords in SKILL_TYPE_INDICATORS.items():
        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword)
            desc_present = 1 if re.search(pattern, desc_lower) else 0
            body_present = 1 if re.search(pattern, body_lower) else 0
            scores[skill_type] += desc_present * 10 + body_present * 1

    best_type = max(scores, key=lambda k: scores[k])
    return (best_type, scores) if scores[best_type] > 0 else ("guide", scores)


def extract_headers(body: str) -> list[str]:
    """Extract markdown headers from body content."""
    return re.findall(r"^#+\s+(.+)", body, re.MULTILINE)


def extract_key_workflows(body: str, headers: list[str]) -> list[str]:
    """Extract key workflows from numbered lists and procedural sections."""
    workflows: list[str] = []

    # Numbered steps
    numbered = re.findall(r"^\s*\d+\.\s+(.+)", body, re.MULTILINE)
    for step in numbered:
        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", step)
        clean = re.sub(r"`(.+?)`", r"\1", clean).strip(".")
        workflows.append(clean)

    # Workflow-related headers
    for header in headers:
        if re.search(
            r"(step|phase|stage|workflow|flow|process|task|setup|config|install)",
            header,
            re.IGNORECASE,
        ):
            workflows.append(header)

    return workflows


def extract_tool_dependencies(fm: dict[str, Any], body: str) -> list[str]:
    """Determine tool dependencies from frontmatter and content analysis."""
    tools: set[str] = set()

    # From frontmatter
    fm_tools = fm.get("allowed-tools") or fm.get("tools")
    if isinstance(fm_tools, list):
        for t in fm_tools:
            if str(t) in VALID_TOOLS:
                tools.add(str(t))

    # Always include Read as baseline
    tools.add("Read")

    # From body content
    body_lower = body.lower()
    for keyword, tool_list in CONTENT_TOOL_MAPPING.items():
        if keyword in body_lower:
            tools.update(tool_list)

    return sorted(tools)


def extract_reference_topics(refs_dir: Path) -> list[dict[str, str]]:
    """Extract reference topics from references/ directory."""
    topics: list[dict[str, str]] = []
    for ref_file in sorted(refs_dir.glob("**/*.md")):
        try:
            content = ref_file.read_text(encoding="utf-8")
        except OSError:
            continue

        # Get topic name from first header or filename
        header_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
        topic_name = header_match.group(1) if header_match else ref_file.stem.replace("-", " ")

        # Get first non-header, non-empty lines as summary
        lines = content.splitlines()
        summary_lines: list[str] = []
        in_body = False
        for line in lines:
            if line.startswith("#"):
                in_body = True
                continue
            if in_body and line.strip():
                summary_lines.append(line.strip())
                if len(summary_lines) >= 3:
                    break

        summary = " ".join(summary_lines)
        topics.append({"topic": topic_name, "summary": summary})

    return topics


def extract_script_descriptions(scripts_dir: Path) -> list[dict[str, str]]:
    """Extract script purpose descriptions from scripts/ directory."""
    scripts: list[dict[str, str]] = []
    for script_file in sorted(scripts_dir.iterdir()):
        if not script_file.is_file():
            continue

        try:
            content = script_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        purpose = ""
        if script_file.suffix == ".py":
            # Python docstring
            doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if not doc_match:
                doc_match = re.search(r"'''(.*?)'''", content, re.DOTALL)
            if doc_match:
                purpose = doc_match.group(1).strip().split("\n")[0]
        elif script_file.suffix == ".sh":
            # Bash comment header
            for line in content.splitlines():
                if line.startswith("#") and not line.startswith("#!"):
                    purpose = line.lstrip("# ").strip()
                    break

        scripts.append(
            {
                "file": script_file.name,
                "language": "python" if script_file.suffix == ".py" else "bash",
                "purpose": purpose or f"{script_file.name} script",
            }
        )

    return scripts


def detect_domain(fm: dict[str, Any], body: str) -> dict[str, Any]:
    """Detect the primary domain and subdomains from content analysis."""
    description = fm.get("description", "")
    name = fm.get("name", "")
    combined = f"{name} {description} {body}"

    domain_signals: dict[str, tuple[str, ...]] = {
        "Design Tooling": ("figma", "design", "ui/ux", "mockup", "prototype", "sketch"),
        "Browser Automation": ("playwright", "browser", "selenium", "puppeteer", "e2e test"),
        "Observability": (
            "sentry",
            "monitoring",
            "logging",
            "metrics",
            "tracing",
            "observability",
            "error tracking",
            "alerting",
            "incident",
        ),
        "Generative Art": ("generative", "algorithmic", "p5.js", "creative coding", "particle"),
        "ML/AI": ("hugging face", "model", "training", "dataset", "inference", "llm"),
        "DevOps": ("deploy", "ci/cd", "kubernetes", "docker", "infrastructure", "cloud"),
        "Documentation": ("documentation", "docs", "docstring", "api doc", "readme"),
        "Version Control": ("git", "commit", "branch", "merge", "pull request", "pr"),
        "Security": ("security", "vulnerability", "cve", "threat", "penetration", "auth"),
        "Frontend": ("react", "vue", "angular", "css", "tailwind", "component", "frontend"),
        "Backend": ("api", "rest", "graphql", "database", "server", "backend", "endpoint"),
        "Testing": ("test", "assertion", "coverage", "tdd", "unit test", "integration test"),
        "Data Management": ("data", "sql", "csv", "json", "transform", "pipeline", "etl"),
        "Project Management": ("linear", "jira", "kanban", "sprint", "backlog", "roadmap"),
        "Media Processing": ("image", "video", "audio", "transcribe", "speech", "media"),
        "Document Processing": ("pdf", "docx", "pptx", "xlsx", "spreadsheet", "presentation"),
    }

    name_desc = f"{name} {description}".lower()
    domain_scores: dict[str, int] = {}
    for domain, signals in domain_signals.items():
        score = 0
        for s in signals:
            if s in name_desc:
                score += 5
            if s in combined.lower():
                score += 1
        domain_scores[domain] = score

    primary_domain = max(domain_scores, key=lambda d: domain_scores[d])
    if domain_scores[primary_domain] == 0:
        primary_domain = "General Development"

    # Subdomains: any domain with score >= 4 (excluding primary)
    sorted_domains = sorted(domain_scores.items(), key=lambda x: -x[1])
    subdomains = [d for d, _ in sorted_domains[1:4] if domain_scores[d] >= 4]

    # Expertise level from content complexity
    word_count = len(combined.split())
    code_blocks = len(re.findall(r"```", body))
    if word_count > 500 and code_blocks > 200:
        expertise_level = "advanced"
    elif word_count > 200 or code_blocks > 50:
        expertise_level = "intermediate"
    else:
        expertise_level = "beginner"

    return {
        "primary_domain": primary_domain,
        "subdomains": subdomains,
        "expertise_level": expertise_level,
    }


def calculate_confidence(
    fm: dict[str, Any],
    body: str,
    headers: list[str],
    reference_topics: list[dict[str, str]],
    script_descriptions: list[dict[str, str]],
) -> float:
    """Calculate confidence score for the extracted intent.

    Higher confidence = richer source material for regeneration.

    Scoring is designed so that SKILL.md-only skills (no references or
    scripts) cap at ~0.5, while rich skills with supporting materials
    can reach 0.9+.  This ensures the regeneration pipeline knows when
    it needs to supplement with web research.

    Budget:
        SKILL.md content (desc + body + headers + code) = up to 0.50
        Supporting materials (references + scripts)      = up to 0.50
    """
    score = 0.0

    # Description quality
    desc = fm.get("description", "")
    if len(desc) > 100:
        score += 0.1
    elif len(desc) > 50:
        score += 0.07
    elif len(desc) > 20:
        score += 0.04

    # Body richness
    word_count = len(body.split())
    if word_count > 300:
        score += 0.2
    elif word_count > 150:
        score += 0.13

    # Headers (structure indicator)
    if len(headers) > 5:
        score += 0.1
    elif len(headers) > 3:
        score += 0.07
    elif len(headers) > 1:
        score += 0.04

    # Code blocks
    code_blocks = len(re.findall(r"```", body))
    if code_blocks > 3:
        score += 0.06
    elif code_blocks > 1:
        score += 0.03

    # References
    if len(reference_topics) > 2:
        score += 0.3
    elif len(reference_topics) > 0:
        score += 0.22

    # Scripts
    if len(script_descriptions) > 2:
        score += 0.15
    elif len(script_descriptions) > 0:
        score += 0.12

    return min(score, 1.0)


def extract_key_concepts(body: str, headers: list[str]) -> list[str]:
    """Extract key concepts from bold text, headers, and terminology."""
    concepts: list[str] = []

    # Bold text
    bold = re.findall(r"\*\*(.+?)\*\*", body)
    for b in bold:
        clean = b.strip()
        if len(clean) > 3 and len(clean) < 80 and "IMPORTANT" not in clean:
            concepts.append(clean)

    # Headers as concepts (skip generic ones)
    generic_headers = {
        "overview",
        "introduction",
        "getting started",
        "usage",
        "examples",
        "notes",
        "references",
        "see also",
    }
    for h in headers:
        if h.lower().strip() not in generic_headers and len(h) < 60:
            concepts.append(h)

    # Deduplicate preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for c in concepts:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique[:15]


def extract_skill_intent(skill_dir: Path) -> dict[str, Any]:
    """Extract structured intent from an upstream skill directory.

    Returns a JSON-serializable dict matching the discovery agent input format.
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    # Parse components
    fm = parse_frontmatter(skill_md)
    body = extract_body(skill_md)
    headers = extract_headers(body)

    # Classify
    skill_type, type_scores = classify_skill_type(fm.get("description", ""), body)

    # Domain
    domain = detect_domain(fm, body)

    # Key concepts and workflows
    key_concepts = extract_key_concepts(body, headers)
    key_workflows = extract_key_workflows(body, headers)

    # Tool dependencies
    tool_deps = extract_tool_dependencies(fm, body)

    # References
    refs_dir = skill_dir / "references"
    reference_topics = extract_reference_topics(refs_dir) if refs_dir.is_dir() else []

    # Scripts
    scripts_dir = skill_dir / "scripts"
    script_descriptions = extract_script_descriptions(scripts_dir) if scripts_dir.is_dir() else []

    # Confidence
    confidence = calculate_confidence(fm, body, headers, reference_topics, script_descriptions)

    # Structure inventory
    structure: list[str] = []
    ref_count = len(list(refs_dir.glob("**/*"))) if refs_dir.is_dir() else 0
    if ref_count:
        structure.append(f"references/ ({ref_count} files)")
    script_count = len(list(scripts_dir.glob("**/*"))) if scripts_dir.is_dir() else 0
    if script_count:
        structure.append(f"scripts/ ({script_count} files)")
    for subdir in sorted(skill_dir.iterdir()):
        if subdir.is_dir() and subdir.name not in ("references", "scripts", "__pycache__"):
            d = subdir.name
            count = len(list(subdir.glob("**/*")))
            structure.append(f"{d}/ ({count} files)")

    return {
        "skill_name": fm.get("name", skill_dir.name),
        "skill_type": skill_type,
        "skill_type_scores": type_scores,
        "description": fm.get("description", ""),
        "domain": domain,
        "key_concepts": key_concepts,
        "key_workflows": key_workflows,
        "tool_dependencies": tool_deps,
        "reference_topics": reference_topics,
        "script_descriptions": script_descriptions,
        "confidence_score": round(confidence, 2),
        "upstream_structure": structure,
        "extracted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def print_human_readable(intent: dict[str, Any]) -> None:
    """Print intent in a human-readable format."""
    name = intent.get("skill_name", "unknown")
    confidence = intent.get("confidence_score", 0)
    skill_type = intent.get("skill_type", "unknown")
    domain = intent.get("domain", {})

    print("=" * 60)
    print(f"Intent Extraction: {name}")
    print(f"  Skill Type:    {skill_type}")
    print(f"  Domain:        {domain.get('primary_domain', 'unknown')}")
    print(f"  Expertise:     {domain.get('expertise_level', 'unknown')}")
    print(f"  Confidence:    {confidence:.2f}")

    desc = intent.get("description", "")
    if desc:
        print("  Description:")
        words = desc.split()
        line = "    "
        for word in words:
            if len(line) + len(word) + 1 > 72:
                print(line)
                line = "    "
            line += word + " "
        if line.strip():
            print(line)

    concepts = intent.get("key_concepts", [])
    if concepts:
        print(f"  Key Concepts ({len(concepts)}):")
        for c in concepts[:5]:
            print(f"    - {c}")
        if len(concepts) > 5:
            print(f"    ... and {len(concepts) - 5} more")

    workflows = intent.get("key_workflows", [])
    if workflows:
        print(f"  Key Workflows ({len(workflows)}):")
        for i, w in enumerate(workflows[:5], 1):
            print(f"    {i}. {w}")

    tools = intent.get("tool_dependencies", [])
    if tools:
        print(f"  Tool Dependencies: {', '.join(tools)}")

    refs = intent.get("reference_topics", [])
    if refs:
        print(f"  Reference Topics ({len(refs)}):")
        for r in refs[:5]:
            summary = r.get("summary", "")
            topic = r.get("topic", "")
            if summary:
                short = summary[:60] + "..." if len(summary) > 60 else summary
                print(f"    - {topic} — {short}")
            else:
                print(f"    - {topic}")

    scripts = intent.get("script_descriptions", [])
    if scripts:
        print(f"  Scripts ({len(scripts)}):")
        for s in scripts:
            print(f"    {s.get('file', '')} ({s.get('language', '')}): {s.get('purpose', '')}")

    structure = intent.get("upstream_structure", [])
    if structure:
        print(f"  Structure: {', '.join(structure)}")

    type_scores = intent.get("skill_type_scores", {})
    if type_scores:
        top_types = sorted(type_scores.items(), key=lambda x: -x[1])
        scores_str = ", ".join(f"{t}={s}" for t, s in top_types if s > 0)
        if scores_str:
            print(f"  Type Scores: {scores_str}")

    print("=" * 60)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract structured intent from an upstream skill directory"
    )
    parser.add_argument("skill_dir", type=Path, help="Path to the upstream skill directory")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (default: human-readable)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON output to file instead of stdout",
    )

    args = parser.parse_args()

    if not args.skill_dir.is_dir():
        print(f"Error: Not a directory: {args.skill_dir}", file=sys.stderr)
        return 1

    skill_md = args.skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: SKILL.md not found in {args.skill_dir}", file=sys.stderr)
        return 1

    try:
        intent = extract_skill_intent(args.skill_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(intent, indent=2, ensure_ascii=False) + "\n", "utf-8")
        name = intent.get("skill_name", "unknown")
        confidence = intent.get("confidence_score", 0)
        print(f"Intent extracted: {name} (confidence={confidence:.2f})", file=sys.stderr)
    elif args.json:
        print(json.dumps(intent, indent=2, ensure_ascii=False))
    else:
        print_human_readable(intent)

    return 0


if __name__ == "__main__":
    sys.exit(main())
