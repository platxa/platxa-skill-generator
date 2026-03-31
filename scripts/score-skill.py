#!/usr/bin/env python3
"""Score a Claude Code skill across 5 quality dimensions.

Produces a 0-10 weighted score with per-dimension breakdown.
Zero external dependencies (stdlib + yaml only).

Usage:
    score-skill.py <skill-directory> [--json] [--verbose]

Exit codes:
    0 - Score >= 7.0 (APPROVE)
    1 - Score < 7.0 (REVISE/REJECT)
    2 - Usage error
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Try yaml, fall back to regex parsing
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class DimensionScore:
    name: str
    score: float  # 0.0 - 10.0
    weight: float  # 0.0 - 1.0
    signals_positive: list[str] = field(default_factory=list)
    signals_negative: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class QualityReport:
    overall_score: float
    passed: bool
    recommendation: str  # APPROVE, REVISE, REJECT
    dimensions: dict[str, DimensionScore] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DIMENSION_WEIGHTS = {
    "spec_compliance": 0.25,
    "content_depth": 0.25,
    "example_quality": 0.20,
    "structure": 0.15,
    "token_efficiency": 0.15,
}

VALID_TOOLS = {
    "Read",
    "Write",
    "Edit",
    "MultiEdit",
    "Glob",
    "Grep",
    "LS",
    "Bash",
    "Task",
    "Agent",
    "Skill",
    "WebFetch",
    "WebSearch",
    "AskUserQuestion",
    "TodoWrite",
    "KillShell",
    "BashOutput",
    "NotebookEdit",
}

PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bFIXME\b",
    r"\bXXX\b",
    r"\byour\s+\w+\s+here\b",
    r"\badd\s+content\s+here\b",
    r"\bplaceholder\b",
    r"\blorem\s+ipsum\b",
]

GENERIC_PHRASES = [
    "best practices",
    "as needed",
    "various options",
    "it is important to note",
    "in order to",
    "for the purpose of",
    "due to the fact that",
    "at this point in time",
    "in terms of",
    "general approach",
    "typical workflow",
    "standard process",
    "commonly accepted",
    "widely used",
]

LLM_FAVORITE_WORDS = [
    "delves",
    "crucial",
    "landscape",
    "leveraging",
    "showcasing",
    "underscores",
    "insights",
    "groundbreaking",
    "comprehensive",
    "transformative",
    "paradigm",
    "synergy",
    "holistic",
    "cutting-edge",
    "game-changing",
    "world-class",
]

OVER_EXPLANATION_PATTERNS = [
    # Explaining basic file format concepts Claude already knows
    r"\b(?:pdf|json|yaml|xml|csv|html|css)\b.{0,30}\b(?:is a|are a|stands for|which is|format that)\b",
    # Explaining basic programming concepts
    r"\b(?:function|variable|class|loop|array|string|integer)\b.{0,30}\b(?:is a|are a|which is|refers to)\b",
    # Explaining what common tools do
    r"\b(?:git|docker|npm|pip|bash)\b.{0,30}\b(?:is a|are a|tool that|which is)\b",
    # Verbose introductory filler
    r"(?:before we begin|before getting started|first and foremost|it is worth noting that)",
    r"(?:in this skill|this skill will|the purpose of this skill is to)",
]

SYNONYM_GROUPS = [
    {"endpoint", "url", "route", "path"},
    {"function", "method", "procedure", "subroutine"},
    {"directory", "folder", "dir"},
    {"repository", "repo", "codebase"},
    {"parameter", "argument", "arg", "param"},
    {"error", "exception", "fault", "failure"},
]

TIME_SENSITIVE_PATTERNS = [
    r"\b(?:before|after)\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b",
    r"\bas\s+of\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b",
    r"\bas\s+of\s+\d{4}\b",
    r"\bcurrently\s+in\s+(?:version|v)\s*\d",
    r"\bsince\s+(?:version|v)\s*\d+\.\d+",
    r"\bdeprecated\s+(?:in|since|after)\s+\d{4}\b",
    r"\buntil\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b",
]

KNOWN_CODE_LANGUAGES = {
    "bash",
    "sh",
    "python",
    "py",
    "javascript",
    "js",
    "typescript",
    "ts",
    "json",
    "yaml",
    "yml",
    "html",
    "css",
    "go",
    "rust",
    "java",
    "ruby",
    "sql",
    "xml",
    "toml",
    "ini",
    "dockerfile",
    "makefile",
    "c",
    "cpp",
    "text",
    "markdown",
    "md",
    "diff",
    "shell",
    "zsh",
    "powershell",
}


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def extract_frontmatter(content: str) -> tuple[str, str]:
    """Extract YAML frontmatter and body from SKILL.md content."""
    if not content.startswith("---"):
        return "", content

    end = content.find("\n---", 3)
    if end == -1:
        return "", content

    frontmatter = content[4:end].strip()
    body = content[end + 4 :].strip()
    return frontmatter, body


def parse_frontmatter(frontmatter_str: str) -> dict:
    """Parse YAML frontmatter into a dict."""
    if not frontmatter_str:
        return {}

    if HAS_YAML:
        try:
            return yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError:
            return {}

    # Fallback: regex parsing for key fields
    result = {}
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_str, re.MULTILINE)
    if name_match:
        result["name"] = name_match.group(1).strip().strip("\"'")

    desc_match = re.search(r"^description:\s*(.+)$", frontmatter_str, re.MULTILINE)
    if desc_match:
        result["description"] = desc_match.group(1).strip().strip("\"'")

    # Extract allowed-tools or tools list
    tools_match = re.findall(r"^\s+-\s+(\w+)\s*$", frontmatter_str, re.MULTILINE)
    if tools_match:
        result["allowed-tools"] = tools_match

    return result


def extract_code_blocks(body: str) -> list[dict]:
    """Extract fenced code blocks with language and content."""
    blocks = []
    for match in re.finditer(r"^```(\w*)\s*\n(.*?)^```", body, re.MULTILINE | re.DOTALL):
        lang = match.group(1).lower().strip()
        content = match.group(2).strip()
        blocks.append({"language": lang, "content": content, "length": len(content)})
    return blocks


def extract_headings(body: str) -> list[tuple[int, str]]:
    """Extract markdown headings with level and text."""
    headings = []
    for match in re.finditer(r"^(#{1,6})\s+(.+)$", body, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        headings.append((level, text))
    return headings


def extract_markdown_links(body: str) -> list[str]:
    """Extract relative file paths from markdown links like [text](path.md)."""
    links = []
    for match in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", body):
        path = match.group(2).strip()
        # Skip URLs and anchors
        if path.startswith(("http://", "https://", "#", "mailto:")):
            continue
        links.append(path)
    return links


def strip_code_blocks(body: str) -> str:
    """Remove fenced code blocks from content for prose analysis."""
    return re.sub(r"^```\w*\s*\n.*?^```", "", body, flags=re.MULTILINE | re.DOTALL)


def count_sentences(text: str) -> int:
    """Count sentences in prose paragraphs (approximate)."""
    prose = strip_code_blocks(text)
    # Keep only lines that look like prose (not headings, lists, tables, checklists)
    prose_lines = []
    for line in prose.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith(("-", "*", "+")) and len(stripped) < 80:
            continue
        if stripped.startswith(("- [", "- |", "|")):
            continue
        if re.match(r"^\d+\.\s", stripped) and len(stripped) < 80:
            continue
        prose_lines.append(stripped)
    joined = " ".join(prose_lines)
    sentences = re.split(r"[.!?]+", joined)
    return len([s for s in sentences if len(s.strip().split()) >= 3])


def word_count_prose(text: str) -> int:
    """Count words in prose (excluding code blocks)."""
    prose = strip_code_blocks(text)
    words = re.findall(r"\b\w+\b", prose)
    return len(words)


def type_token_ratio(text: str) -> float:
    """Calculate vocabulary diversity (unique words / total words)."""
    prose = strip_code_blocks(text)
    words = [w.lower() for w in re.findall(r"\b[a-z]+\b", prose)]
    if len(words) < 10:
        return 0.0
    return len(set(words)) / len(words)


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------


def score_spec_compliance(frontmatter: dict) -> DimensionScore:
    """Score spec compliance: frontmatter validity, field formats."""
    dim = DimensionScore(
        name="spec_compliance", score=10.0, weight=DIMENSION_WEIGHTS["spec_compliance"]
    )

    # Check frontmatter exists
    if not frontmatter:
        dim.score = 0.0
        dim.signals_negative.append("No valid frontmatter found")
        dim.suggestions.append("Add YAML frontmatter with --- delimiters")
        return dim

    # Check name
    name = frontmatter.get("name", "")
    if not name:
        dim.score -= 3.0
        dim.signals_negative.append("Missing name field")
        dim.suggestions.append("Add name field to frontmatter")
    else:
        if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$", name):
            dim.score -= 2.0
            dim.signals_negative.append(f"Invalid name format: {name}")
            dim.suggestions.append(
                "Name must be hyphen-case (lowercase, hyphens, start with letter)"
            )
        elif len(name) > 64:
            dim.score -= 1.0
            dim.signals_negative.append(f"Name too long: {len(name)} chars")
        else:
            dim.signals_positive.append(f"Valid name: {name}")

    # Check description
    desc = frontmatter.get("description", "")
    if not desc:
        dim.score -= 3.0
        dim.signals_negative.append("Missing description field")
        dim.suggestions.append("Add description field to frontmatter")
    else:
        if len(desc) > 1024:
            dim.score -= 1.0
            dim.signals_negative.append(f"Description too long: {len(desc)} chars")
        elif len(desc) < 20:
            dim.score -= 1.0
            dim.signals_negative.append(f"Description too short: {len(desc)} chars")
            dim.suggestions.append(
                "Description should explain what the skill does and when to use it"
            )
        else:
            dim.signals_positive.append(f"Description length: {len(desc)} chars")

        # Check third-person form (Anthropic best practice: always write in third person)
        desc_lower = desc.strip().lower()
        first_person = re.match(r"^(i can|i will|i help|i am|i\'m)\b", desc_lower)
        second_person = re.match(r"^(you can|you will|you should|your)\b", desc_lower)
        if first_person:
            dim.score -= 1.5
            dim.signals_negative.append("Description uses first person (starts with 'I ...')")
            dim.suggestions.append(
                "Write description in third person: 'Processes files...' not 'I can help you...'"
            )
        elif second_person:
            dim.score -= 1.0
            dim.signals_negative.append("Description uses second person (starts with 'You ...')")
            dim.suggestions.append(
                "Write description in third person: 'Generates reports...' not 'You can use this...'"
            )

        # Check for trigger context (description should say WHEN to use, not just WHAT)
        trigger_patterns = [
            r"\buse\s+when\b",
            r"\buse\s+this\b",
            r"\bwhen\s+(?:the\s+)?user\b",
            r"\bwhen\s+working\b",
            r"\bwhen\s+you\b",
            r"\btrigger\b",
            r"\binvoke\b",
            r"\bactivate\b",
        ]
        has_trigger = any(re.search(p, desc, re.IGNORECASE) for p in trigger_patterns)
        if has_trigger:
            dim.signals_positive.append("Description includes trigger context (when to use)")
        elif len(desc) >= 20:
            dim.score -= 0.5
            dim.signals_negative.append("Description lacks trigger context")
            dim.suggestions.append(
                "Add when to use the skill: 'Use when working with PDFs' or 'Use when the user mentions...'"
            )

        # Check for vague descriptions
        vague_patterns = [
            r"^helps?\s+with\s+\w+$",
            r"^does?\s+stuff\b",
            r"^processes?\s+data$",
            r"^handles?\s+things\b",
            r"^a?\s*(?:simple|basic|general)\s+(?:tool|helper|utility)\b",
        ]
        is_vague = any(re.search(p, desc_lower) for p in vague_patterns)
        if is_vague:
            dim.score -= 1.0
            dim.signals_negative.append("Description is too vague")
            dim.suggestions.append(
                "Be specific: include what the skill does AND specific contexts/triggers"
            )

    # Check tools
    tools = frontmatter.get("allowed-tools", frontmatter.get("tools", []))
    if tools:
        invalid = [t for t in tools if t not in VALID_TOOLS]
        if invalid:
            dim.score -= 1.0
            dim.signals_negative.append(f"Invalid tools: {', '.join(invalid)}")
        else:
            dim.signals_positive.append(f"Valid tools: {len(tools)} declared")

    dim.score = max(0.0, dim.score)
    return dim


def score_content_depth(body: str) -> DimensionScore:
    """Score content depth: real expertise vs generic filler."""
    dim = DimensionScore(
        name="content_depth", score=10.0, weight=DIMENSION_WEIGHTS["content_depth"]
    )

    prose = strip_code_blocks(body).lower()

    # Check for placeholders (skip lines that describe/warn about placeholders)
    negation_words = {"no ", "remove", "avoid", "without", "don't", "never", "not "}
    placeholder_count = 0
    for line in prose.splitlines():
        line_lower = line.strip().lower()
        if any(neg in line_lower for neg in negation_words):
            continue
        for pattern in PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, line_lower, re.IGNORECASE)
            placeholder_count += len(matches)

    if placeholder_count > 0:
        deduction = min(placeholder_count * 1.5, 6.0)
        dim.score -= deduction
        dim.signals_negative.append(f"Found {placeholder_count} placeholder(s)")
        dim.suggestions.append("Remove all placeholder text (TODO, TBD, FIXME, etc.)")

    # Check for generic phrases
    generic_count = 0
    generic_found = []
    for phrase in GENERIC_PHRASES:
        count = prose.count(phrase)
        if count > 0:
            generic_count += count
            generic_found.append(phrase)

    if generic_count > 5:
        dim.score -= 2.0
        dim.signals_negative.append(f"High generic phrase density: {generic_count} occurrences")
        dim.suggestions.append(
            f"Replace generic phrases with specifics: {', '.join(generic_found[:3])}"
        )
    elif generic_count > 2:
        dim.score -= 1.0
        dim.signals_negative.append(f"Some generic phrases: {generic_count} occurrences")

    # Check for LLM-favorite words
    llm_count = 0
    llm_found = []
    for word in LLM_FAVORITE_WORDS:
        count = prose.count(word)
        if count > 0:
            llm_count += count
            llm_found.append(word)

    if llm_count > 3:
        dim.score -= 1.5
        dim.signals_negative.append(f"LLM-favorite words detected: {', '.join(llm_found)}")
        dim.suggestions.append("Replace vague buzzwords with specific technical terms")
    elif llm_count > 0:
        dim.score -= 0.5

    # Check type-token ratio (vocabulary diversity)
    ttr = type_token_ratio(body)
    if ttr > 0:
        if ttr < 0.3:
            dim.score -= 2.0
            dim.signals_negative.append(f"Low vocabulary diversity: {ttr:.2f}")
            dim.suggestions.append("Use more varied vocabulary — content may be repetitive")
        elif ttr < 0.4:
            dim.score -= 0.5
            dim.signals_negative.append(f"Moderate vocabulary diversity: {ttr:.2f}")
        else:
            dim.signals_positive.append(f"Good vocabulary diversity: {ttr:.2f}")

    # Positive: specific numbers, tool names, version refs
    specific_patterns = [
        (r"\b\d+\s*(?:bytes?|chars?|characters?|lines?|tokens?)\b", "size constraints"),
        (r"\bRFC\s*\d+\b", "RFC references"),
        (r"\bv(?:ersion)?\s*\d+\.\d+", "version references"),
        (r"\b\d+%\b", "percentages"),
    ]
    for pattern, label in specific_patterns:
        if re.search(pattern, body, re.IGNORECASE):
            dim.signals_positive.append(f"Contains {label}")

    # Check for over-explanation of concepts Claude already knows
    overexplain_count = 0
    for pattern in OVER_EXPLANATION_PATTERNS:
        overexplain_count += len(re.findall(pattern, prose, re.IGNORECASE))

    if overexplain_count >= 3:
        dim.score -= 1.5
        dim.signals_negative.append(f"Over-explains basic concepts ({overexplain_count} instances)")
        dim.suggestions.append(
            "Remove explanations of concepts Claude already knows (e.g., what PDFs or git are)"
        )
    elif overexplain_count >= 1:
        dim.score -= 0.5
        dim.signals_negative.append(
            f"Some over-explanation of basic concepts ({overexplain_count} instance(s))"
        )

    # Check for time-sensitive content that will become stale
    time_sensitive_count = 0
    for pattern in TIME_SENSITIVE_PATTERNS:
        time_sensitive_count += len(re.findall(pattern, prose, re.IGNORECASE))

    if time_sensitive_count > 0:
        dim.score -= min(time_sensitive_count * 0.5, 1.5)
        dim.signals_negative.append(
            f"Time-sensitive content ({time_sensitive_count} instance(s)) will become stale"
        )
        dim.suggestions.append(
            "Avoid dates and version-specific references that will become outdated"
        )

    # Check terminology consistency (multiple synonyms from the same group)
    inconsistent_groups: list[tuple[str, str]] = []
    words_in_prose = set(re.findall(r"\b[a-z]+\b", prose))
    for group in SYNONYM_GROUPS:
        found = [term for term in group if term in words_in_prose]
        if len(found) >= 2:
            inconsistent_groups.append((found[0], found[1]))

    if len(inconsistent_groups) >= 2:
        examples = [f"{a}/{b}" for a, b in inconsistent_groups[:2]]
        dim.score -= 1.0
        dim.signals_negative.append(f"Inconsistent terminology: {', '.join(examples)}")
        dim.suggestions.append("Pick one term per concept and use it consistently")
    elif len(inconsistent_groups) == 1:
        a, b = inconsistent_groups[0]
        dim.score -= 0.5
        dim.signals_negative.append(f"Mixed terminology: {a}/{b}")

    dim.score = max(0.0, dim.score)
    return dim


def score_example_quality(body: str) -> DimensionScore:
    """Score example quality: code blocks, language labels, substance."""
    dim = DimensionScore(
        name="example_quality", score=10.0, weight=DIMENSION_WEIGHTS["example_quality"]
    )

    blocks = extract_code_blocks(body)

    if not blocks:
        dim.score = 2.0
        dim.signals_negative.append("No fenced code blocks found")
        dim.suggestions.append("Add at least 2 code examples showing realistic usage")
        return dim

    # Count and quality-check blocks
    labeled = [b for b in blocks if b["language"]]
    unlabeled = [b for b in blocks if not b["language"]]
    substantial = [b for b in blocks if b["length"] > 20]
    trivial = [b for b in blocks if b["length"] <= 20]

    dim.signals_positive.append(f"{len(blocks)} code block(s) found")

    # Deduct for too few blocks
    if len(blocks) < 2:
        dim.score -= 2.0
        dim.suggestions.append("Add more code examples (minimum 2 recommended)")

    # Deduct for unlabeled blocks
    if unlabeled:
        deduction = min(len(unlabeled) * 0.5, 2.0)
        dim.score -= deduction
        dim.signals_negative.append(f"{len(unlabeled)} code block(s) without language label")
        dim.suggestions.append("Add language labels to all code blocks (```python, ```bash, etc.)")

    # Deduct for trivial blocks
    if trivial and len(trivial) > len(substantial):
        dim.score -= 1.5
        dim.signals_negative.append(f"{len(trivial)} trivial code block(s) (<20 chars)")
        dim.suggestions.append("Make code examples more substantial and realistic")

    # Bonus for labeled blocks with known languages
    valid_lang = [b for b in labeled if b["language"] in KNOWN_CODE_LANGUAGES]
    if valid_lang:
        dim.signals_positive.append(f"{len(valid_lang)} block(s) with recognized languages")

    # Check parseable YAML/JSON blocks
    for block in blocks:
        if block["language"] in ("yaml", "yml", "json"):
            try:
                if block["language"] == "json":
                    json.loads(block["content"])
                elif HAS_YAML and yaml is not None:
                    yaml.safe_load(block["content"])
                dim.signals_positive.append(f"Valid {block['language']} example")
            except Exception:
                dim.score -= 0.5
                dim.signals_negative.append(f"Invalid {block['language']} syntax in code block")
                dim.suggestions.append(f"Fix {block['language']} syntax error in code example")

    dim.score = max(0.0, dim.score)
    return dim


def score_structure(body: str, skill_dir: Path) -> DimensionScore:
    """Score document structure: sections, headings, organization."""
    dim = DimensionScore(name="structure", score=10.0, weight=DIMENSION_WEIGHTS["structure"])

    headings = extract_headings(body)
    h2_headings = [h for h in headings if h[0] == 2]
    h2_names = [h[1].lower() for h in h2_headings]

    # Check required sections
    has_overview = any("overview" in n for n in h2_names)
    has_workflow = any(w in " ".join(h2_names) for w in ["workflow", "process", "steps", "usage"])
    has_examples = any("example" in n for n in h2_names)

    if not has_overview:
        dim.score -= 2.0
        dim.signals_negative.append("Missing Overview section")
        dim.suggestions.append("Add ## Overview section explaining what the skill does")

    if not has_workflow:
        dim.score -= 1.5
        dim.signals_negative.append("Missing Workflow/Process section")
        dim.suggestions.append("Add ## Workflow section with step-by-step instructions")

    if not has_examples:
        dim.score -= 1.0
        dim.signals_negative.append("Missing Examples section")
        dim.suggestions.append("Add ## Examples section with realistic usage demos")

    if has_overview:
        dim.signals_positive.append("Has Overview section")
    if has_workflow:
        dim.signals_positive.append("Has Workflow/Process section")
    if has_examples:
        dim.signals_positive.append("Has Examples section")

    # Check h2 count (minimum 3)
    if len(h2_headings) < 3:
        dim.score -= 1.5
        dim.signals_negative.append(f"Only {len(h2_headings)} h2 section(s) (minimum 3)")
        dim.suggestions.append("Add more top-level sections for better organization")
    else:
        dim.signals_positive.append(f"{len(h2_headings)} h2 sections")

    # Check heading hierarchy (no skipping levels)
    prev_level = 1
    skips = 0
    for level, _ in headings:
        if level > prev_level + 1:
            skips += 1
        prev_level = level

    if skips > 0:
        dim.score -= min(skips * 0.5, 1.5)
        dim.signals_negative.append(f"Heading hierarchy skips {skips} level(s)")
        dim.suggestions.append("Don't skip heading levels (e.g., ## to #### without ###)")

    # Progressive disclosure: check reference depth and TOC
    _check_progressive_disclosure(body, skill_dir, dim)

    dim.score = max(0.0, dim.score)
    return dim


def _check_progressive_disclosure(body: str, skill_dir: Path, dim: DimensionScore) -> None:
    """Check progressive disclosure patterns: reference depth and TOC in long files."""
    skill_links = extract_markdown_links(body)
    if not skill_links:
        return

    # Check for nested references (files that SKILL.md links to should not link to more files)
    nested_count = 0
    nested_files: list[str] = []
    for link in skill_links:
        ref_path = skill_dir / link
        if not ref_path.is_file():
            continue
        try:
            ref_content = ref_path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        ref_links = extract_markdown_links(ref_content)
        # Filter to relative file links that exist in the skill directory
        nested_refs = [rl for rl in ref_links if (skill_dir / rl).is_file()]
        if nested_refs:
            nested_count += len(nested_refs)
            nested_files.append(link)

    if nested_count > 0:
        dim.score -= min(nested_count * 0.5, 1.5)
        dim.signals_negative.append(
            f"Nested references found: {', '.join(nested_files)} link to other files"
        )
        dim.suggestions.append(
            "Keep references one level deep from SKILL.md — Claude partially reads nested references"
        )
    elif skill_links:
        dim.signals_positive.append("References are one level deep (good progressive disclosure)")

    # Check that reference files >100 lines have a table of contents
    missing_toc: list[str] = []
    for link in skill_links:
        ref_path = skill_dir / link
        if not ref_path.is_file() or ref_path.suffix != ".md":
            continue
        try:
            ref_content = ref_path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        ref_lines = ref_content.count("\n") + 1
        if ref_lines <= 100:
            continue
        # Check for TOC indicators: "Contents", "Table of Contents", or 3+ internal links
        ref_lower = ref_content.lower()
        has_toc = (
            "## contents" in ref_lower
            or "## table of contents" in ref_lower
            or "# contents" in ref_lower
            or ref_lower.count("](#") >= 3
        )
        if not has_toc:
            missing_toc.append(f"{link} ({ref_lines} lines)")

    if missing_toc:
        dim.score -= min(len(missing_toc) * 0.5, 1.0)
        dim.signals_negative.append(f"Long reference files without TOC: {', '.join(missing_toc)}")
        dim.suggestions.append("Add ## Contents section to reference files over 100 lines")


def score_token_efficiency(content: str, body: str, skill_dir: Path) -> DimensionScore:
    """Score token efficiency: right-sized content, not too thin or bloated."""
    dim = DimensionScore(
        name="token_efficiency", score=10.0, weight=DIMENSION_WEIGHTS["token_efficiency"]
    )

    lines = content.count("\n") + 1
    words = word_count_prose(body)

    # Line count sweet spot: 50-500
    if lines < 30:
        dim.score -= 4.0
        dim.signals_negative.append(f"Too short: {lines} lines")
        dim.suggestions.append("Skill needs more content — add sections, examples, details")
    elif lines < 50:
        dim.score -= 2.0
        dim.signals_negative.append(f"Thin content: {lines} lines")
        dim.suggestions.append("Consider adding more examples or detail")
    elif lines > 500:
        dim.score -= 2.0
        dim.signals_negative.append(f"Too long: {lines} lines (max 500)")
        dim.suggestions.append("Move detailed content to references/ files")
    elif lines > 450:
        dim.score -= 1.0
        dim.signals_negative.append(f"Approaching limit: {lines}/500 lines")
    else:
        dim.signals_positive.append(f"Good length: {lines} lines")

    # Word count check
    if words < 100:
        dim.score -= 2.0
        dim.signals_negative.append(f"Very few prose words: {words}")
    elif words > 4000:
        dim.score -= 1.0
        dim.signals_negative.append(f"High word count: {words}")
        dim.suggestions.append("Consider being more concise or offloading to references")
    else:
        dim.signals_positive.append(f"Word count: {words}")

    # Average sentence length
    sentence_count = count_sentences(body)
    if sentence_count > 0:
        avg_sentence_len = words / sentence_count
        if avg_sentence_len > 30:
            dim.score -= 1.5
            dim.signals_negative.append(f"Long sentences: avg {avg_sentence_len:.0f} words")
            dim.suggestions.append("Break up long sentences for clarity")
        elif avg_sentence_len > 25:
            dim.score -= 0.5
            dim.signals_negative.append(
                f"Somewhat long sentences: avg {avg_sentence_len:.0f} words"
            )

    # Check references exist for long skills
    refs_dir = skill_dir / "references"
    if lines > 300 and not refs_dir.is_dir():
        dim.score -= 1.0
        dim.signals_negative.append("Long SKILL.md but no references/ directory")
        dim.suggestions.append(
            "Offload detailed content to references/ files for progressive disclosure"
        )
    elif refs_dir.is_dir():
        ref_count = len(list(refs_dir.glob("**/*.md")))
        if ref_count > 0:
            dim.signals_positive.append(f"Has {ref_count} reference file(s)")

    dim.score = max(0.0, dim.score)
    return dim


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def aggregate(dimensions: list[DimensionScore]) -> QualityReport:
    """Aggregate dimension scores into overall quality report."""
    total_weight = sum(d.weight for d in dimensions)
    weighted_sum = sum(d.score * d.weight for d in dimensions)
    overall = weighted_sum / total_weight if total_weight > 0 else 0.0
    overall = round(overall, 1)

    if overall >= 8.0:
        recommendation = "APPROVE"
    elif overall >= 6.0:
        recommendation = "REVISE"
    else:
        recommendation = "REJECT"

    passed = overall >= 7.0

    suggestions = []
    for d in sorted(dimensions, key=lambda x: x.score):
        suggestions.extend(d.suggestions[:2])

    return QualityReport(
        overall_score=overall,
        passed=passed,
        recommendation=recommendation,
        dimensions={d.name: d for d in dimensions},
        suggestions=suggestions[:10],
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def format_human(report: QualityReport) -> str:
    """Format report for human consumption."""
    lines = []
    lines.append("")
    lines.append("Quality Score Report")
    lines.append("=" * 50)
    lines.append("")

    for dim in report.dimensions.values():
        bar = "█" * int(dim.score) + "░" * (10 - int(dim.score))
        pct = int(dim.weight * 100)
        lines.append(f"  {dim.name:<20s} {dim.score:>4.1f}/10  [{bar}]  ({pct}%)")

    lines.append("")
    lines.append("-" * 50)
    lines.append(f"  {'OVERALL':<20s} {report.overall_score:>4.1f}/10  → {report.recommendation}")
    lines.append("-" * 50)

    if report.suggestions:
        lines.append("")
        lines.append("Suggestions:")
        for s in report.suggestions:
            lines.append(f"  • {s}")

    lines.append("")
    return "\n".join(lines)


def format_verbose(report: QualityReport) -> str:
    """Format report with per-check details."""
    lines = [format_human(report)]

    lines.append("Detailed Signals")
    lines.append("=" * 50)

    for dim in report.dimensions.values():
        lines.append(f"\n  [{dim.name}] {dim.score:.1f}/10")
        for s in dim.signals_positive:
            lines.append(f"    ✓ {s}")
        for s in dim.signals_negative:
            lines.append(f"    ✗ {s}")

    lines.append("")
    return "\n".join(lines)


def format_json(report: QualityReport) -> str:
    """Format report as JSON."""
    data = {
        "overall_score": report.overall_score,
        "passed": report.passed,
        "recommendation": report.recommendation,
        "dimensions": {
            name: {
                "score": dim.score,
                "weight": dim.weight,
                "positive": dim.signals_positive,
                "negative": dim.signals_negative,
                "suggestions": dim.suggestions,
            }
            for name, dim in report.dimensions.items()
        },
        "suggestions": report.suggestions,
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def score_skill(skill_dir: Path) -> QualityReport:
    """Score a skill directory and return quality report."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        dim = DimensionScore(name="spec_compliance", score=0.0, weight=1.0)
        dim.signals_negative.append("SKILL.md not found")
        return QualityReport(
            overall_score=0.0,
            passed=False,
            recommendation="REJECT",
            dimensions={"spec_compliance": dim},
            suggestions=["Create SKILL.md with valid frontmatter"],
        )

    content = skill_md.read_text()
    frontmatter_str, body = extract_frontmatter(content)
    frontmatter = parse_frontmatter(frontmatter_str)

    dimensions = [
        score_spec_compliance(frontmatter),
        score_content_depth(body),
        score_example_quality(body),
        score_structure(body, skill_dir),
        score_token_efficiency(content, body, skill_dir),
    ]

    return aggregate(dimensions)


def main() -> int:
    args = sys.argv[1:]

    if not args or "-h" in args or "--help" in args:
        print("Usage: score-skill.py <skill-directory> [--json] [--verbose]")
        return 2

    json_output = "--json" in args
    verbose = "--verbose" in args
    skill_dir = Path([a for a in args if not a.startswith("-")][0])

    if not skill_dir.is_dir():
        print(f"Error: Not a directory: {skill_dir}", file=sys.stderr)
        return 2

    report = score_skill(skill_dir)

    if json_output:
        print(format_json(report))
    elif verbose:
        print(format_verbose(report))
    else:
        print(format_human(report))

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
