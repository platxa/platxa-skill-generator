# Glossary Generator

Generate glossary.md files with clear term definitions for skills.

## Glossary Purpose

| Feature | Description |
|---------|-------------|
| Term clarity | Define skill-specific terminology |
| Quick reference | Alphabetical lookup of concepts |
| Onboarding | Help new users understand vocabulary |
| Consistency | Establish standard definitions |

## Glossary Model

```python
from dataclasses import dataclass, field
from enum import Enum

class TermCategory(Enum):
    CORE = "core"              # Fundamental concepts
    TECHNICAL = "technical"    # Technical terms
    WORKFLOW = "workflow"      # Process-related terms
    OUTPUT = "output"          # Output/artifact terms
    CONFIG = "config"          # Configuration terms

@dataclass
class GlossaryTerm:
    term: str
    definition: str
    category: TermCategory
    aliases: list[str] = field(default_factory=list)
    see_also: list[str] = field(default_factory=list)
    example: str | None = None

@dataclass
class GlossaryConfig:
    skill_name: str
    skill_type: str
    include_categories: list[TermCategory] = field(default_factory=list)
    max_terms: int = 50
    include_examples: bool = True
    include_see_also: bool = True

@dataclass
class GlossaryResult:
    terms: list[GlossaryTerm]
    categories_used: list[TermCategory]
    total_terms: int
    estimated_tokens: int
```

## Term Extractor

```python
import re
from typing import Set

class TermExtractor:
    """Extract terms from skill content for glossary."""

    # Common technical terms to detect
    TECHNICAL_PATTERNS = [
        r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b',  # CamelCase
        r'\b[a-z]+_[a-z_]+\b',                # snake_case
        r'\b[a-z]+-[a-z-]+\b',                # kebab-case
        r'`[^`]+`',                            # Code spans
    ]

    # Common skill terms
    SKILL_VOCABULARY = {
        "skill": "A Claude Code extension that provides specialized capabilities",
        "SKILL.md": "The main file defining a skill's behavior and instructions",
        "frontmatter": "YAML metadata at the start of SKILL.md",
        "reference": "Additional documentation files in the references/ directory",
        "invocation": "The act of calling a skill using /skill-name",
        "token": "A unit of text processing, roughly 4 characters",
        "token budget": "Maximum tokens allowed for skill content",
        "validation": "Checking skill files for correctness",
        "quality score": "Numeric rating of skill quality (0-10)",
    }

    def extract_terms(
        self,
        content: str,
        existing_terms: Set[str] | None = None
    ) -> list[str]:
        """Extract potential glossary terms from content."""
        terms = set()
        existing = existing_terms or set()

        # Extract from technical patterns
        for pattern in self.TECHNICAL_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                term = match.strip('`').lower()
                if len(term) > 2 and term not in existing:
                    terms.add(term)

        # Extract capitalized phrases (potential concepts)
        caps_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        for match in re.findall(caps_pattern, content):
            if len(match) > 3:
                terms.add(match.lower())

        # Extract quoted terms
        quoted = re.findall(r'"([^"]+)"', content)
        for term in quoted:
            if len(term.split()) <= 3:
                terms.add(term.lower())

        return sorted(terms)

    def categorize_term(self, term: str, context: str) -> TermCategory:
        """Categorize a term based on context."""
        term_lower = term.lower()

        # Check for workflow terms
        workflow_indicators = [
            "step", "phase", "stage", "process", "flow",
            "workflow", "pipeline", "sequence"
        ]
        if any(ind in term_lower for ind in workflow_indicators):
            return TermCategory.WORKFLOW

        # Check for config terms
        config_indicators = [
            "config", "setting", "option", "parameter",
            "flag", "argument", "variable"
        ]
        if any(ind in term_lower for ind in config_indicators):
            return TermCategory.CONFIG

        # Check for output terms
        output_indicators = [
            "output", "result", "artifact", "file",
            "report", "generated", "created"
        ]
        if any(ind in term_lower for ind in output_indicators):
            return TermCategory.OUTPUT

        # Check context for technical indicators
        if re.search(r'`[^`]*' + re.escape(term) + r'[^`]*`', context):
            return TermCategory.TECHNICAL

        return TermCategory.CORE
```

## Glossary Generator

```python
class GlossaryGenerator:
    """Generate glossary.md content."""

    def __init__(self, config: GlossaryConfig):
        self.config = config
        self.extractor = TermExtractor()

    def generate(
        self,
        skill_content: str,
        custom_terms: list[GlossaryTerm] | None = None
    ) -> GlossaryResult:
        """Generate glossary from skill content."""
        terms = []

        # Add custom terms first
        if custom_terms:
            terms.extend(custom_terms)

        # Add standard skill vocabulary
        for term, definition in self.extractor.SKILL_VOCABULARY.items():
            if not any(t.term.lower() == term.lower() for t in terms):
                terms.append(GlossaryTerm(
                    term=term,
                    definition=definition,
                    category=TermCategory.CORE
                ))

        # Extract and add discovered terms
        extracted = self.extractor.extract_terms(
            skill_content,
            {t.term.lower() for t in terms}
        )

        for term_str in extracted[:self.config.max_terms - len(terms)]:
            category = self.extractor.categorize_term(term_str, skill_content)

            # Skip if category not included
            if (self.config.include_categories and
                    category not in self.config.include_categories):
                continue

            terms.append(GlossaryTerm(
                term=term_str,
                definition=f"[Definition needed for: {term_str}]",
                category=category
            ))

        # Sort alphabetically
        terms.sort(key=lambda t: t.term.lower())

        # Filter by max terms
        terms = terms[:self.config.max_terms]

        # Calculate tokens
        estimated_tokens = self._estimate_tokens(terms)

        return GlossaryResult(
            terms=terms,
            categories_used=list(set(t.category for t in terms)),
            total_terms=len(terms),
            estimated_tokens=estimated_tokens
        )

    def _estimate_tokens(self, terms: list[GlossaryTerm]) -> int:
        """Estimate token count for glossary."""
        tokens = 50  # Header overhead

        for term in terms:
            # Term + definition
            tokens += len(term.term.split()) + len(term.definition.split())
            # Aliases
            tokens += len(term.aliases) * 2
            # See also
            tokens += len(term.see_also) * 2
            # Example
            if term.example:
                tokens += len(term.example.split())

        return tokens

    def format_markdown(self, result: GlossaryResult) -> str:
        """Format glossary as markdown."""
        lines = []

        # Header
        lines.append("# Glossary")
        lines.append("")
        lines.append(f"Key terms and definitions for {self.config.skill_name}.")
        lines.append("")

        # Quick navigation
        lines.append("## Quick Navigation")
        lines.append("")
        letters = sorted(set(t.term[0].upper() for t in result.terms))
        nav = " | ".join(f"[{l}](#{l.lower()})" for l in letters)
        lines.append(nav)
        lines.append("")

        # Terms by letter
        current_letter = None
        for term in result.terms:
            first_letter = term.term[0].upper()

            if first_letter != current_letter:
                current_letter = first_letter
                lines.append(f"## {current_letter}")
                lines.append("")

            # Term entry
            lines.append(f"### {term.term}")
            lines.append("")
            lines.append(f"*{term.category.value}*")
            lines.append("")
            lines.append(term.definition)
            lines.append("")

            # Aliases
            if term.aliases and self.config.include_examples:
                aliases = ", ".join(f"`{a}`" for a in term.aliases)
                lines.append(f"**Also known as:** {aliases}")
                lines.append("")

            # Example
            if term.example and self.config.include_examples:
                lines.append("**Example:**")
                lines.append(f"> {term.example}")
                lines.append("")

            # See also
            if term.see_also and self.config.include_see_also:
                refs = ", ".join(f"[{s}](#{s.lower().replace(' ', '-')})"
                                for s in term.see_also)
                lines.append(f"**See also:** {refs}")
                lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"*{result.total_terms} terms defined*")

        return "\n".join(lines)
```

## Skill-Type Specific Terms

```python
SKILL_TYPE_TERMS: dict[str, list[GlossaryTerm]] = {
    "builder": [
        GlossaryTerm(
            term="template",
            definition="A reusable pattern for generating output",
            category=TermCategory.CORE
        ),
        GlossaryTerm(
            term="scaffold",
            definition="Initial structure created as a starting point",
            category=TermCategory.OUTPUT
        ),
        GlossaryTerm(
            term="generator",
            definition="Component that produces output from templates",
            category=TermCategory.TECHNICAL
        ),
    ],
    "guide": [
        GlossaryTerm(
            term="step",
            definition="A single action in a multi-step process",
            category=TermCategory.WORKFLOW
        ),
        GlossaryTerm(
            term="checkpoint",
            definition="A point to verify progress before continuing",
            category=TermCategory.WORKFLOW
        ),
        GlossaryTerm(
            term="prerequisite",
            definition="Requirement that must be met before starting",
            category=TermCategory.WORKFLOW
        ),
    ],
    "automation": [
        GlossaryTerm(
            term="trigger",
            definition="Event that initiates automated action",
            category=TermCategory.WORKFLOW
        ),
        GlossaryTerm(
            term="pipeline",
            definition="Sequence of automated processing steps",
            category=TermCategory.TECHNICAL
        ),
        GlossaryTerm(
            term="batch",
            definition="Group of items processed together",
            category=TermCategory.TECHNICAL
        ),
    ],
    "analyzer": [
        GlossaryTerm(
            term="metric",
            definition="Quantifiable measurement of code or content",
            category=TermCategory.OUTPUT
        ),
        GlossaryTerm(
            term="threshold",
            definition="Boundary value that triggers a classification",
            category=TermCategory.CONFIG
        ),
        GlossaryTerm(
            term="finding",
            definition="Individual issue or observation from analysis",
            category=TermCategory.OUTPUT
        ),
    ],
    "validator": [
        GlossaryTerm(
            term="rule",
            definition="Specific check applied during validation",
            category=TermCategory.CORE
        ),
        GlossaryTerm(
            term="violation",
            definition="Instance where content fails a rule",
            category=TermCategory.OUTPUT
        ),
        GlossaryTerm(
            term="severity",
            definition="Importance level of a violation (error/warning/info)",
            category=TermCategory.CONFIG
        ),
    ],
}

def get_skill_type_terms(skill_type: str) -> list[GlossaryTerm]:
    """Get predefined terms for skill type."""
    return SKILL_TYPE_TERMS.get(skill_type, [])
```

## Integration

```python
def generate_glossary(
    skill_name: str,
    skill_type: str,
    skill_content: str,
    output_path: str | None = None
) -> str:
    """Generate glossary for a skill."""
    config = GlossaryConfig(
        skill_name=skill_name,
        skill_type=skill_type,
        include_examples=True,
        include_see_also=True
    )

    generator = GlossaryGenerator(config)

    # Get skill-type specific terms
    type_terms = get_skill_type_terms(skill_type)

    # Generate glossary
    result = generator.generate(skill_content, type_terms)

    # Format as markdown
    content = generator.format_markdown(result)

    # Write if path provided
    if output_path:
        with open(output_path, "w") as f:
            f.write(content)

    return content
```

## Sample Output

```markdown
# Glossary

Key terms and definitions for api-doc-generator.

## Quick Navigation

A | D | E | F | I | O | Q | R | S | T | V

## A

### API endpoint

*technical*

A URL path that accepts requests and returns responses.

**Example:**
> `/api/v1/users` is an endpoint that returns user data

## D

### documentation

*output*

Generated reference material describing code or APIs.

**See also:** [template](#template), [output](#output)

## S

### SKILL.md

*core*

The main file defining a skill's behavior and instructions.

**Also known as:** `skill file`, `main skill`

---

*12 terms defined*
```
