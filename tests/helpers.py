"""Helper functions for creating test skill directories.

This module provides utility functions to create test skill directories
with various configurations for testing the validation scripts.

All operations use REAL file system - NO mocks or simulations.
"""

from __future__ import annotations

from pathlib import Path


def create_skill_dir(
    base_dir: Path,
    name: str = "test-skill",
    *,
    with_scripts: bool = False,
    with_references: bool = False,
) -> Path:
    """Create a skill directory structure.

    Args:
        base_dir: Base directory to create the skill in
        name: Name of the skill directory
        with_scripts: Create scripts/ subdirectory
        with_references: Create references/ subdirectory

    Returns:
        Path to the created skill directory

    Example:
        >>> skill_dir = create_skill_dir(tmp_path, "my-skill", with_scripts=True)
        >>> (skill_dir / "scripts").exists()
        True
    """
    skill_dir = base_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    if with_scripts:
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

    if with_references:
        refs_dir = skill_dir / "references"
        refs_dir.mkdir(exist_ok=True)

    return skill_dir


def create_skill_md(
    skill_dir: Path,
    name: str,
    description: str,
    *,
    tools: list[str] | None = None,
    model: str | None = None,
    content: str = "# Skill\n\nInstructions here.\n",
    include_frontmatter: bool = True,
) -> Path:
    """Create a SKILL.md file with frontmatter.

    Args:
        skill_dir: Directory to create SKILL.md in
        name: Skill name for frontmatter
        description: Skill description for frontmatter
        tools: Optional list of allowed tools
        model: Optional model specification
        content: Markdown content after frontmatter
        include_frontmatter: Whether to include frontmatter delimiters

    Returns:
        Path to the created SKILL.md file

    Example:
        >>> skill_md = create_skill_md(skill_dir, "my-skill", "Does things")
        >>> skill_md.exists()
        True
    """
    lines: list[str] = []

    if include_frontmatter:
        lines.append("---")
        lines.append(f"name: {name}")
        lines.append(f"description: {description}")

        if tools:
            lines.append("tools:")
            for tool in tools:
                lines.append(f"  - {tool}")

        if model:
            lines.append(f"model: {model}")

        lines.append("---")
        lines.append("")

    lines.append(content)

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("\n".join(lines))

    return skill_md


def create_executable_script(
    scripts_dir: Path,
    name: str,
    content: str = '#!/bin/bash\necho "test"',
    *,
    executable: bool = True,
) -> Path:
    """Create a shell script in the scripts directory.

    Args:
        scripts_dir: Directory to create script in
        name: Script filename (without .sh extension if not provided)
        content: Script content
        executable: Whether to make the script executable

    Returns:
        Path to the created script

    Example:
        >>> script = create_executable_script(scripts_dir, "test.sh")
        >>> script.stat().st_mode & 0o111 != 0  # Is executable
        True
    """
    if not name.endswith(".sh") and not name.endswith(".py"):
        name = f"{name}.sh"

    script_path = scripts_dir / name
    script_path.write_text(content)

    if executable:
        script_path.chmod(0o755)

    return script_path


def create_reference_file(
    refs_dir: Path,
    name: str,
    content: str = "# Reference\n\nContent here.\n",
) -> Path:
    """Create a reference markdown file.

    Args:
        refs_dir: References directory
        name: Filename (without .md extension if not provided)
        content: Markdown content

    Returns:
        Path to the created reference file

    Example:
        >>> ref = create_reference_file(refs_dir, "guide")
        >>> ref.name
        'guide.md'
    """
    if not name.endswith(".md"):
        name = f"{name}.md"

    ref_path = refs_dir / name
    ref_path.write_text(content)

    return ref_path


def create_complete_skill(
    base_dir: Path,
    name: str = "test-skill",
    description: str = "A test skill for validation testing.",
    *,
    tools: list[str] | None = None,
    with_script: bool = True,
    with_reference: bool = True,
) -> Path:
    """Create a complete, valid skill directory structure.

    Creates a skill directory with:
    - SKILL.md with valid frontmatter
    - Optionally scripts/ with executable script
    - Optionally references/ with markdown file

    Args:
        base_dir: Base directory to create skill in
        name: Skill name (also used for directory)
        description: Skill description
        tools: List of allowed tools
        with_script: Include scripts/ directory with test script
        with_reference: Include references/ directory with guide

    Returns:
        Path to the created skill directory

    Example:
        >>> skill_dir = create_complete_skill(tmp_path)
        >>> (skill_dir / "SKILL.md").exists()
        True
        >>> (skill_dir / "scripts" / "test.sh").exists()
        True
    """
    if tools is None:
        tools = ["Read", "Write", "Bash"]

    skill_dir = create_skill_dir(
        base_dir,
        name,
        with_scripts=with_script,
        with_references=with_reference,
    )

    create_skill_md(
        skill_dir,
        name=name,
        description=description,
        tools=tools,
        content=f"""# {name.replace("-", " ").title()}

This is a test skill for validation testing.

## Usage

Use this skill for automated testing.

## Examples

```bash
/skill-name
```
""",
    )

    if with_script:
        create_executable_script(
            skill_dir / "scripts",
            "test.sh",
            """#!/bin/bash
# Test script for validation
echo "Running test script"
exit 0
""",
        )

    if with_reference:
        create_reference_file(
            skill_dir / "references",
            "guide.md",
            """# Reference Guide

This is a reference document for the test skill.

## Section 1

Reference content here.

## Section 2

More reference content.
""",
        )

    return skill_dir


def generate_long_text(tokens: int, method: str = "words") -> str:
    """Generate text of exactly the specified token count using tiktoken.

    Args:
        tokens: Target token count (exact)
        method: Generation method ("words" or "lorem")

    Returns:
        Generated text string with exactly the specified token count.

    Note:
        Uses tiktoken cl100k_base encoding for accurate token counting.
        Iteratively builds text until target token count is reached.
    """
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
    except ImportError:
        # Fallback if tiktoken not available - use conservative estimate
        words_needed = tokens  # 1:1 ratio as fallback
        base_words = [
            "the",
            "skill",
            "provides",
            "functionality",
            "for",
            "testing",
            "validation",
            "code",
            "development",
            "automation",
            "system",
            "process",
            "data",
            "output",
            "input",
            "configuration",
            "setup",
        ]
        words = []
        for i in range(words_needed):
            words.append(base_words[i % len(base_words)])
        return " ".join(words)

    if method == "lorem":
        base_phrase = (
            "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do "
            "eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        )
    else:
        # Use varied words for more realistic token distribution
        base_phrase = (
            "The skill provides functionality for testing validation code "
            "development automation system process data output input "
            "configuration setup implementation verification analysis "
            "generation transformation processing handling management. "
        )

    # Build text iteratively until we reach target token count
    text = ""
    while True:
        current_tokens = len(encoding.encode(text))
        if current_tokens >= tokens:
            break
        text += base_phrase

    # Trim to exact token count
    encoded = encoding.encode(text)
    if len(encoded) > tokens:
        encoded = encoded[:tokens]
        text = encoding.decode(encoded)

    return text


def generate_long_lines(line_count: int, chars_per_line: int = 80) -> str:
    """Generate text with the specified number of lines.

    Args:
        line_count: Number of lines to generate
        chars_per_line: Approximate characters per line

    Returns:
        Generated multi-line text
    """
    lines = []
    for i in range(line_count):
        line = f"Line {i + 1}: " + "x" * (chars_per_line - 10)
        lines.append(line)
    return "\n".join(lines)
