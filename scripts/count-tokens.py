#!/usr/bin/env python3
"""count-tokens.py - Count tokens in skill files.

Usage: count-tokens.py <skill-directory> [--json] [--warn-threshold N]

Provides accurate token counts using tiktoken (cl100k_base encoding)
with fallback to word-based estimation.

Supports .skillconfig file for custom limits (useful for meta-skills).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TypedDict

# Try to import tiktoken for accurate counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class FileTokens(TypedDict):
    """Token count for a single file."""
    path: str
    tokens: int
    lines: int
    method: str


class TokenReport(TypedDict):
    """Complete token count report."""
    skill_name: str
    skill_md_tokens: int
    skill_md_lines: int
    ref_total_tokens: int
    ref_files: list[FileTokens]
    total_tokens: int
    method: str
    warnings: list[str]
    passed: bool
    custom_limits: bool


# Default budget limits
DEFAULT_LIMITS = {
    'skill_md_tokens': 5000,
    'skill_md_lines': 500,
    'single_ref_tokens': 2000,
    'total_ref_tokens': 10000,
    'total_skill_tokens': 15000,
}


def load_skill_config(skill_dir: Path) -> dict:
    """Load custom limits from .skillconfig if present.

    The .skillconfig file can contain:
    - skip_token_validation: true  (skip all token checks)
    - limits: { total_ref_tokens: 200000, ... }  (custom limits)

    Returns:
        Dict with 'skip_validation' bool and 'limits' dict
    """
    config_path = skill_dir / ".skillconfig"
    result = {'skip_validation': False, 'limits': DEFAULT_LIMITS.copy()}

    if not config_path.exists():
        return result

    try:
        config = json.loads(config_path.read_text())

        # Check for skip flag
        if config.get('skip_token_validation', False):
            result['skip_validation'] = True

        # Merge custom limits
        if 'limits' in config:
            result['limits'].update(config['limits'])

        return result
    except (json.JSONDecodeError, OSError):
        return result


def count_tokens_tiktoken(text: str) -> int:
    """Count tokens using tiktoken (accurate)."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def count_tokens_estimate(text: str) -> int:
    """Estimate tokens from word count (fallback)."""
    words = len(text.split())
    # Average ~1.3 tokens per word for English/markdown
    return int(words * 1.3)


def count_tokens(text: str) -> tuple[int, str]:
    """Count tokens with best available method."""
    if TIKTOKEN_AVAILABLE:
        return count_tokens_tiktoken(text), "tiktoken"
    else:
        return count_tokens_estimate(text), "estimate"


def count_lines(text: str) -> int:
    """Count lines in text."""
    return len(text.split('\n'))


def analyze_skill(skill_dir: Path, warn_threshold: int = 80) -> TokenReport:
    """
    Analyze token counts for a skill directory.

    Args:
        skill_dir: Path to skill directory
        warn_threshold: Percentage threshold for warnings (default 80%)

    Returns:
        TokenReport with all counts and warnings
    """
    warnings: list[str] = []
    skill_name = skill_dir.name

    # Load custom config if present
    config = load_skill_config(skill_dir)
    limits = config['limits']
    custom_limits = config['limits'] != DEFAULT_LIMITS or config['skip_validation']

    # Check SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return TokenReport(
            skill_name=skill_name,
            skill_md_tokens=0,
            skill_md_lines=0,
            ref_total_tokens=0,
            ref_files=[],
            total_tokens=0,
            method="none",
            warnings=["SKILL.md not found"],
            passed=False,
            custom_limits=False
        )

    skill_content = skill_md.read_text()
    skill_md_tokens, method = count_tokens(skill_content)
    skill_md_lines = count_lines(skill_content)

    # Skip validation if configured
    if config['skip_validation']:
        # Still count but don't enforce limits
        ref_files: list[FileTokens] = []
        ref_total_tokens = 0
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in sorted(refs_dir.rglob("*.md")):
                content = ref_file.read_text()
                tokens, _ = count_tokens(content)
                lines = count_lines(content)
                rel_path = str(ref_file.relative_to(skill_dir))
                ref_files.append(FileTokens(
                    path=rel_path, tokens=tokens, lines=lines, method=method
                ))
                ref_total_tokens += tokens

        return TokenReport(
            skill_name=skill_name,
            skill_md_tokens=skill_md_tokens,
            skill_md_lines=skill_md_lines,
            ref_total_tokens=ref_total_tokens,
            ref_files=ref_files,
            total_tokens=skill_md_tokens + ref_total_tokens,
            method=method,
            warnings=["Token validation skipped (.skillconfig)"],
            passed=True,
            custom_limits=True
        )

    # Check SKILL.md limits
    if skill_md_tokens > limits['skill_md_tokens']:
        warnings.append(
            f"SKILL.md exceeds token limit: {skill_md_tokens} > {limits['skill_md_tokens']}"
        )
    elif skill_md_tokens > limits['skill_md_tokens'] * warn_threshold / 100:
        warnings.append(
            f"SKILL.md approaching token limit: {skill_md_tokens} ({warn_threshold}% of {limits['skill_md_tokens']})"
        )

    if skill_md_lines > limits['skill_md_lines']:
        warnings.append(
            f"SKILL.md exceeds line limit: {skill_md_lines} > {limits['skill_md_lines']}"
        )
    elif skill_md_lines > limits['skill_md_lines'] * warn_threshold / 100:
        warnings.append(
            f"SKILL.md approaching line limit: {skill_md_lines} ({warn_threshold}% of {limits['skill_md_lines']})"
        )

    # Check references
    ref_files = []
    ref_total_tokens = 0

    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        for ref_file in sorted(refs_dir.rglob("*.md")):
            content = ref_file.read_text()
            tokens, _ = count_tokens(content)
            lines = count_lines(content)

            rel_path = str(ref_file.relative_to(skill_dir))
            ref_files.append(FileTokens(
                path=rel_path,
                tokens=tokens,
                lines=lines,
                method=method
            ))
            ref_total_tokens += tokens

            # Check per-file limit
            if tokens > limits['single_ref_tokens']:
                warnings.append(
                    f"{rel_path} exceeds limit: {tokens} > {limits['single_ref_tokens']}"
                )
            elif tokens > limits['single_ref_tokens'] * warn_threshold / 100:
                warnings.append(
                    f"{rel_path} approaching limit: {tokens} ({warn_threshold}% of {limits['single_ref_tokens']})"
                )

    # Check total references
    if ref_total_tokens > limits['total_ref_tokens']:
        warnings.append(
            f"Total references exceed limit: {ref_total_tokens} > {limits['total_ref_tokens']}"
        )
    elif ref_total_tokens > limits['total_ref_tokens'] * warn_threshold / 100:
        warnings.append(
            f"Total references approaching limit: {ref_total_tokens} ({warn_threshold}% of {limits['total_ref_tokens']})"
        )

    # Total skill tokens
    total_tokens = skill_md_tokens + ref_total_tokens

    if total_tokens > limits['total_skill_tokens']:
        warnings.append(
            f"Total skill exceeds limit: {total_tokens} > {limits['total_skill_tokens']}"
        )
    elif total_tokens > limits['total_skill_tokens'] * warn_threshold / 100:
        warnings.append(
            f"Total skill approaching limit: {total_tokens} ({warn_threshold}% of {limits['total_skill_tokens']})"
        )

    # Determine pass/fail
    passed = (
        skill_md_tokens <= limits['skill_md_tokens'] and
        skill_md_lines <= limits['skill_md_lines'] and
        ref_total_tokens <= limits['total_ref_tokens'] and
        total_tokens <= limits['total_skill_tokens'] and
        all(f['tokens'] <= limits['single_ref_tokens'] for f in ref_files)
    )

    return TokenReport(
        skill_name=skill_name,
        skill_md_tokens=skill_md_tokens,
        skill_md_lines=skill_md_lines,
        ref_total_tokens=ref_total_tokens,
        ref_files=ref_files,
        total_tokens=total_tokens,
        method=method,
        warnings=warnings,
        passed=passed,
        custom_limits=custom_limits
    )


def print_report(report: TokenReport) -> None:
    """Print human-readable token report."""
    print(f"Token Count Report: {report['skill_name']}")
    if report.get('custom_limits'):
        print("(Using custom limits from .skillconfig)")
    print("━" * 50)
    print()

    # SKILL.md
    print("SKILL.md:")
    print(f"  Tokens: {report['skill_md_tokens']:,} / {DEFAULT_LIMITS['skill_md_tokens']:,}")
    print(f"  Lines:  {report['skill_md_lines']:,} / {DEFAULT_LIMITS['skill_md_lines']:,}")
    print()

    # References
    if report['ref_files']:
        print("References:")
        for f in report['ref_files']:
            print(f"  {f['path']}: {f['tokens']:,} tokens")
        print("  ────────────────────────────")
        print(f"  Total: {report['ref_total_tokens']:,} / {DEFAULT_LIMITS['total_ref_tokens']:,}")
        print()

    # Total
    print(f"Total Skill: {report['total_tokens']:,} / {DEFAULT_LIMITS['total_skill_tokens']:,} tokens")
    print(f"Method: {report['method']}")
    print()

    # Warnings
    if report['warnings']:
        print("Warnings:")
        for w in report['warnings']:
            print(f"  ⚠ {w}")
        print()

    # Result
    print("━" * 50)
    if report['passed']:
        print("✓ PASSED - Within token budget")
    else:
        print("✗ FAILED - Exceeds token budget")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Count tokens in skill files"
    )
    parser.add_argument(
        "skill_dir",
        type=Path,
        help="Path to skill directory"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--warn-threshold",
        type=int,
        default=80,
        help="Warning threshold percentage (default: 80)"
    )

    args = parser.parse_args()

    if not args.skill_dir.is_dir():
        print(f"Error: Not a directory: {args.skill_dir}", file=sys.stderr)
        return 1

    report = analyze_skill(args.skill_dir, args.warn_threshold)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return 0 if report['passed'] else 1


if __name__ == "__main__":
    sys.exit(main())
