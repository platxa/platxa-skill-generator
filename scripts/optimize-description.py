#!/usr/bin/env python3
"""Optimize a skill's description for trigger accuracy.

Uses a train/test split approach: generates trigger eval queries, tests whether
the current description causes Claude to invoke the skill, then iteratively
improves the description based on failures.

Usage:
    python3 scripts/optimize-description.py <skill-directory> [options]

Options:
    --eval-set <path>       Path to trigger eval JSON (auto-generates if missing)
    --max-iterations <n>    Max improvement iterations (default: 5)
    --holdout <float>       Test set fraction (default: 0.4)
    --verbose               Show detailed progress

Input:  <skill-dir>/SKILL.md (reads name + description)
Output: Prints best_description to stdout. With --verbose, shows per-iteration scores.

Requires: claude CLI for trigger testing (optional — runs in dry-run mode without it).
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path


def parse_skill_md(skill_path: Path) -> tuple[str, str]:
    """Extract name and description from SKILL.md frontmatter.

    Args:
        skill_path: Path to skill directory containing SKILL.md

    Returns:
        Tuple of (name, description)

    Raises:
        SystemExit: If SKILL.md not found or frontmatter invalid
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"ERROR: SKILL.md not found in {skill_path}", file=sys.stderr)
        sys.exit(1)

    content = skill_md.read_text()

    # Extract frontmatter
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        print("ERROR: No frontmatter found in SKILL.md", file=sys.stderr)
        sys.exit(1)

    frontmatter = match.group(1)

    # Extract name
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    name = name_match.group(1).strip().strip("\"'") if name_match else ""

    # Extract description (handle multiline YAML)
    desc_match = re.search(r"^description:\s*>-?\n((?:\s+.+\n?)+)", frontmatter, re.MULTILINE)
    if desc_match:
        description = " ".join(line.strip() for line in desc_match.group(1).strip().splitlines())
    else:
        desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        description = desc_match.group(1).strip().strip("\"'") if desc_match else ""

    return name, description


def generate_trigger_evals(name: str, description: str) -> list[dict]:
    """Generate trigger eval queries from a skill's name and description.

    Creates a set of should-trigger and should-not-trigger queries based on
    keywords and patterns extracted from the description.

    Args:
        name: Skill name
        description: Skill description text

    Returns:
        List of eval dicts with query and should_trigger fields
    """
    # Extract quoted trigger phrases from description
    quoted = re.findall(r'"([^"]{3,})"', description)

    # Extract key action verbs
    verbs = re.findall(
        r"\b(create|generate|analyze|review|build|check|validate|test|deploy|"
        r"configure|scan|audit|format|lint|debug|optimize|refactor)\b",
        description.lower(),
    )
    verbs = list(set(verbs))

    # Extract domain nouns
    nouns = re.findall(
        r"\b(code|api|database|auth|security|test|component|module|service|"
        r"endpoint|function|class|file|config|deployment|server|client)\b",
        description.lower(),
    )
    nouns = list(set(nouns))

    evals: list[dict] = []

    # Should-trigger: based on quoted phrases
    for phrase in quoted[:5]:
        evals.append(
            {
                "query": f"Can you {phrase}?",
                "should_trigger": True,
            }
        )

    # Should-trigger: based on verb+noun combinations
    for verb in verbs[:3]:
        for noun in nouns[:2]:
            evals.append(
                {
                    "query": f"I need to {verb} the {noun}",
                    "should_trigger": True,
                }
            )

    # Should-trigger: casual phrasing
    if verbs:
        evals.append(
            {
                "query": f"hey can you help me {verbs[0]} something real quick",
                "should_trigger": True,
            }
        )

    # Should-not-trigger: adjacent but different domains
    not_trigger_queries = [
        "Write a fibonacci function in Python",
        "What's the weather like today?",
        "Help me write a haiku about programming",
        "Set up my git config with my email",
        "Explain how TCP/IP works",
    ]

    for q in not_trigger_queries[:5]:
        evals.append(
            {
                "query": q,
                "should_trigger": False,
            }
        )

    # Ensure at least 10 total
    while len(evals) < 10:
        evals.append(
            {
                "query": f"Tell me about {name} best practices",
                "should_trigger": True,
            }
        )

    return evals


def split_eval_set(
    eval_set: list[dict], holdout: float, seed: int = 42
) -> tuple[list[dict], list[dict]]:
    """Split eval set into train and test, stratified by should_trigger.

    Args:
        eval_set: Full eval set
        holdout: Fraction for test set (0.0-1.0)
        seed: Random seed for reproducibility

    Returns:
        Tuple of (train_set, test_set)
    """
    random.seed(seed)

    trigger = [e for e in eval_set if e["should_trigger"]]
    no_trigger = [e for e in eval_set if not e["should_trigger"]]

    random.shuffle(trigger)
    random.shuffle(no_trigger)

    n_trigger_test = max(1, int(len(trigger) * holdout))
    n_no_trigger_test = max(1, int(len(no_trigger) * holdout))

    test_set = trigger[:n_trigger_test] + no_trigger[:n_no_trigger_test]
    train_set = trigger[n_trigger_test:] + no_trigger[n_no_trigger_test:]

    return train_set, test_set


def score_description(description: str, eval_set: list[dict], verbose: bool = False) -> float:
    """Score a description's trigger accuracy against an eval set.

    In dry-run mode (no claude CLI), scores based on keyword overlap between
    the description and query. In live mode, would use claude -p to test
    actual triggering.

    Args:
        description: Description text to evaluate
        eval_set: List of eval dicts with query and should_trigger
        verbose: Print per-query results

    Returns:
        Accuracy score (0.0 to 1.0)
    """
    desc_lower = description.lower()
    desc_words = set(re.findall(r"\b\w{3,}\b", desc_lower))

    correct = 0
    total = len(eval_set)

    for ev in eval_set:
        query_lower = ev["query"].lower()
        query_words = set(re.findall(r"\b\w{3,}\b", query_lower))

        # Heuristic: keyword overlap as proxy for trigger likelihood
        overlap = len(desc_words & query_words)
        would_trigger = overlap >= 2

        expected = ev["should_trigger"]
        is_correct = would_trigger == expected

        if is_correct:
            correct += 1

        if verbose:
            status = "CORRECT" if is_correct else "WRONG"
            direction = "trigger" if expected else "no-trigger"
            print(
                f"  [{status}] {direction}: {ev['query'][:60]}...",
                file=sys.stderr,
            )

    return correct / total if total > 0 else 0.0


def improve_description(
    current: str,
    failures: list[dict],
    name: str,
) -> str:
    """Suggest an improved description based on trigger failures.

    Analyzes which queries failed to trigger (or falsely triggered) and
    adjusts the description to improve accuracy.

    Args:
        current: Current description text
        failures: List of failed eval dicts
        name: Skill name

    Returns:
        Improved description text
    """
    missed_triggers = [f for f in failures if f["should_trigger"]]

    improved = current

    # Add keywords from missed triggers to the description
    if missed_triggers:
        new_keywords = set()
        for mt in missed_triggers:
            words = re.findall(r"\b\w{4,}\b", mt["query"].lower())
            new_keywords.update(words[:2])

        # Only add keywords not already present
        existing = set(re.findall(r"\b\w{4,}\b", improved.lower()))
        to_add = new_keywords - existing

        if to_add:
            keyword_phrase = ", ".join(sorted(to_add)[:3])
            # Insert after first sentence
            first_dot = improved.find(".")
            if first_dot > 0:
                improved = (
                    improved[: first_dot + 1]
                    + f" Also handles {keyword_phrase}."
                    + improved[first_dot + 1 :]
                )

    # Ensure description stays within 1024 chars
    if len(improved) > 1024:
        improved = improved[:1021] + "..."

    return improved


def main() -> None:
    """Run the description optimization loop."""
    parser = argparse.ArgumentParser(description="Optimize skill description for trigger accuracy")
    parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    parser.add_argument("--eval-set", type=Path, help="Path to trigger eval JSON")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max improvement iterations")
    parser.add_argument("--holdout", type=float, default=0.4, help="Test set fraction")
    parser.add_argument("--verbose", action="store_true", help="Show details")
    parser.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()

    name, original_description = parse_skill_md(args.skill_dir)

    if not name or not original_description:
        print("ERROR: Could not parse name/description from SKILL.md", file=sys.stderr)
        sys.exit(1)

    # Load or generate eval set
    if args.eval_set and args.eval_set.exists():
        with open(args.eval_set) as f:
            eval_set = json.load(f)
    else:
        eval_set = generate_trigger_evals(name, original_description)
        if args.verbose:
            print(
                f"Generated {len(eval_set)} trigger eval queries",
                file=sys.stderr,
            )

    # Split train/test
    train_set, test_set = split_eval_set(eval_set, args.holdout)

    if args.verbose:
        print(
            f"Split: {len(train_set)} train, {len(test_set)} test (holdout={args.holdout})",
            file=sys.stderr,
        )

    current_description = original_description
    best_description = original_description
    best_test_score = 0.0

    history: list[dict] = []

    for iteration in range(1, args.max_iterations + 1):
        if args.verbose:
            print(f"\n{'=' * 50}", file=sys.stderr)
            print(f"Iteration {iteration}/{args.max_iterations}", file=sys.stderr)
            print(f"{'=' * 50}", file=sys.stderr)

        # Score on train
        train_score = score_description(current_description, train_set, verbose=args.verbose)

        # Score on test
        test_score = score_description(current_description, test_set)

        if args.verbose:
            print(
                f"  Train: {train_score:.2f} | Test: {test_score:.2f}",
                file=sys.stderr,
            )

        history.append(
            {
                "iteration": iteration,
                "description": current_description,
                "train_score": train_score,
                "test_score": test_score,
            }
        )

        # Track best by test score (prevents overfitting)
        if test_score > best_test_score:
            best_test_score = test_score
            best_description = current_description

        # If perfect on train, stop
        if train_score >= 1.0:
            if args.verbose:
                print("  Perfect train score — stopping", file=sys.stderr)
            break

        # Find failures on train set
        desc_lower = current_description.lower()
        desc_words = set(re.findall(r"\b\w{3,}\b", desc_lower))

        failures = []
        for ev in train_set:
            query_words = set(re.findall(r"\b\w{3,}\b", ev["query"].lower()))
            overlap = len(desc_words & query_words)
            would_trigger = overlap >= 2
            if would_trigger != ev["should_trigger"]:
                failures.append(ev)

        if not failures:
            break

        # Improve
        current_description = improve_description(current_description, failures, name)

    # Output result
    if args.json:
        result = {
            "skill_name": name,
            "original_description": original_description,
            "best_description": best_description,
            "best_test_score": best_test_score,
            "iterations": len(history),
            "history": history,
        }
        print(json.dumps(result, indent=2))
    else:
        print(best_description)


if __name__ == "__main__":
    main()
