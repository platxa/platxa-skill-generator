# Metadata Generator

Generate optional metadata fields for skill frontmatter.

## Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| version | string | No | Semantic version (e.g., "1.0.0") |
| author | string | No | Creator name or identifier |
| tags | list[string] | No | Categorization tags |

## Metadata Schema

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SkillMetadata:
    version: str
    author: str | None
    tags: list[str]
    created_at: datetime
    generator_version: str

GENERATOR_VERSION = "1.0.0"
```

## Version Generation

### Initial Version

```python
def generate_initial_version() -> str:
    """Generate initial version for new skills."""
    return "1.0.0"
```

### Version Bumping

```python
from enum import Enum

class VersionBump(Enum):
    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features
    PATCH = "patch"  # Bug fixes

def bump_version(current: str, bump: VersionBump) -> str:
    """Bump semantic version."""
    parts = current.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current}")

    major, minor, patch = map(int, parts)

    if bump == VersionBump.MAJOR:
        return f"{major + 1}.0.0"
    elif bump == VersionBump.MINOR:
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"
```

### Version Validation

```python
import re

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

def validate_version(version: str) -> bool:
    """Validate semantic version format."""
    return bool(VERSION_PATTERN.match(version))
```

## Author Generation

### Source Priority

```python
def generate_author(
    explicit_author: str | None = None,
    git_config: dict | None = None,
    env_vars: dict | None = None
) -> str | None:
    """Generate author from available sources."""

    # 1. Explicit author takes priority
    if explicit_author:
        return explicit_author

    # 2. Try git config
    if git_config:
        name = git_config.get("user.name")
        email = git_config.get("user.email")
        if name and email:
            return f"{name} <{email}>"
        if name:
            return name

    # 3. Try environment variables
    if env_vars:
        if "SKILL_AUTHOR" in env_vars:
            return env_vars["SKILL_AUTHOR"]
        if "USER" in env_vars:
            return env_vars["USER"]

    # 4. No author available
    return None
```

### Git Config Extraction

```python
import subprocess

def get_git_config() -> dict:
    """Extract git user config."""
    config = {}

    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            config["user.name"] = result.stdout.strip()

        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            config["user.email"] = result.stdout.strip()

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return config
```

## Tag Generation

### Automatic Tag Detection

```python
DOMAIN_TAGS = {
    # Development
    "api": ["api", "backend", "web"],
    "frontend": ["frontend", "ui", "web"],
    "database": ["database", "sql", "data"],
    "testing": ["testing", "qa", "automation"],
    "devops": ["devops", "ci-cd", "deployment"],

    # Languages
    "python": ["python", "programming"],
    "javascript": ["javascript", "programming"],
    "typescript": ["typescript", "programming"],

    # Domains
    "documentation": ["documentation", "technical-writing"],
    "security": ["security", "compliance"],
    "performance": ["performance", "optimization"],
}

SKILL_TYPE_TAGS = {
    "builder": ["generator", "scaffolding"],
    "guide": ["tutorial", "learning"],
    "automation": ["workflow", "automation"],
    "analyzer": ["analysis", "inspection"],
    "validator": ["validation", "linting"],
}

def detect_tags(
    description: str,
    skill_type: str,
    domain: str
) -> list[str]:
    """Detect appropriate tags from skill metadata."""
    tags = set()
    desc_lower = description.lower()

    # Add skill type tag
    tags.add(skill_type)

    # Add skill type associated tags
    type_tags = SKILL_TYPE_TAGS.get(skill_type, [])
    tags.update(type_tags[:1])  # Add first type tag

    # Detect domain tags
    for keyword, domain_tags in DOMAIN_TAGS.items():
        if keyword in desc_lower or keyword in domain.lower():
            tags.update(domain_tags[:2])  # Add up to 2 domain tags

    # Detect technology keywords
    tech_keywords = [
        "react", "vue", "angular", "node",
        "docker", "kubernetes", "aws", "azure",
        "postgres", "mongodb", "redis",
        "openapi", "graphql", "rest",
    ]
    for tech in tech_keywords:
        if tech in desc_lower:
            tags.add(tech)

    return sorted(tags)[:8]  # Limit to 8 tags
```

### Tag Validation

```python
TAG_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
MAX_TAG_LENGTH = 32
MAX_TAGS = 10

def validate_tag(tag: str) -> tuple[bool, str | None]:
    """Validate a single tag."""
    if not tag:
        return False, "Tag cannot be empty"

    if len(tag) > MAX_TAG_LENGTH:
        return False, f"Tag too long: {len(tag)} > {MAX_TAG_LENGTH}"

    if not TAG_PATTERN.match(tag):
        return False, "Tag must be lowercase alphanumeric with hyphens"

    return True, None

def validate_tags(tags: list[str]) -> list[str]:
    """Validate and clean tag list."""
    errors = []

    if len(tags) > MAX_TAGS:
        errors.append(f"Too many tags: {len(tags)} > {MAX_TAGS}")

    for tag in tags:
        valid, error = validate_tag(tag)
        if not valid:
            errors.append(f"Invalid tag '{tag}': {error}")

    return errors
```

## Complete Metadata Generator

```python
@dataclass
class MetadataResult:
    metadata: SkillMetadata
    warnings: list[str]

def generate_metadata(
    skill_type: str,
    description: str,
    domain: str,
    explicit_version: str | None = None,
    explicit_author: str | None = None,
    explicit_tags: list[str] | None = None
) -> MetadataResult:
    """Generate complete skill metadata."""

    warnings = []

    # Version
    if explicit_version:
        if validate_version(explicit_version):
            version = explicit_version
        else:
            warnings.append(f"Invalid version '{explicit_version}', using 1.0.0")
            version = "1.0.0"
    else:
        version = generate_initial_version()

    # Author
    git_config = get_git_config()
    author = generate_author(
        explicit_author=explicit_author,
        git_config=git_config,
        env_vars=dict(os.environ)
    )

    if not author:
        warnings.append("No author detected, field will be omitted")

    # Tags
    if explicit_tags:
        tags = explicit_tags
        tag_errors = validate_tags(tags)
        warnings.extend(tag_errors)
    else:
        tags = detect_tags(description, skill_type, domain)

    if not tags:
        warnings.append("No tags detected, consider adding manually")

    metadata = SkillMetadata(
        version=version,
        author=author,
        tags=tags,
        created_at=datetime.now(),
        generator_version=GENERATOR_VERSION
    )

    return MetadataResult(metadata=metadata, warnings=warnings)
```

## Frontmatter Output

### YAML Format

```yaml
---
name: api-doc-generator
description: Generate API documentation from OpenAPI specs
tools:
  - Read
  - Write
  - Glob
version: 1.0.0
author: John Doe <john@example.com>
tags:
  - builder
  - api
  - documentation
  - openapi
---
```

### Format Function

```python
def format_metadata_yaml(metadata: SkillMetadata) -> str:
    """Format metadata for YAML frontmatter."""
    lines = []

    # Version (always include)
    lines.append(f"version: {metadata.version}")

    # Author (optional)
    if metadata.author:
        # Quote if contains special chars
        if any(c in metadata.author for c in "<>:"):
            lines.append(f'author: "{metadata.author}"')
        else:
            lines.append(f"author: {metadata.author}")

    # Tags (optional)
    if metadata.tags:
        lines.append("tags:")
        for tag in sorted(metadata.tags):
            lines.append(f"  - {tag}")

    return "\n".join(lines)
```

## Integration

```python
def generate_frontmatter(
    name: str,
    description: str,
    tools: list[str],
    skill_type: str,
    domain: str,
    include_metadata: bool = True
) -> str:
    """Generate complete YAML frontmatter."""

    lines = ["---"]
    lines.append(f"name: {name}")

    # Multi-line description
    if "\n" in description or len(description) > 60:
        lines.append("description: |")
        for line in description.split("\n"):
            lines.append(f"  {line}")
    else:
        lines.append(f"description: {description}")

    # Tools
    lines.append("tools:")
    for tool in sorted(tools):
        lines.append(f"  - {tool}")

    # Optional metadata
    if include_metadata:
        result = generate_metadata(
            skill_type=skill_type,
            description=description,
            domain=domain
        )
        metadata_yaml = format_metadata_yaml(result.metadata)
        lines.append(metadata_yaml)

    lines.append("---")

    return "\n".join(lines)
```
