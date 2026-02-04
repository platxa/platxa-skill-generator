# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "huggingface-hub>=1.1.4",
#     "markdown-it-py>=3.0.0",
#     "python-dotenv>=1.2.1",
#     "pyyaml>=6.0.3",
#     "requests>=2.32.5",
# ]
# ///

"""Manage evaluation results in Hugging Face model cards.

Supports multiple methods for adding evaluation data:
- Extract existing evaluation tables from README content
- Import benchmark scores from Artificial Analysis API
- View and validate existing model-index entries
- Check for open PRs to prevent duplicate contributions

Usage:
    uv run evaluation_manager.py inspect-tables --repo-id "owner/model"
    uv run evaluation_manager.py extract-readme --repo-id "owner/model" --table 1
    uv run evaluation_manager.py import-aa --creator-slug "x" --model-name "y" --repo-id "z"
    uv run evaluation_manager.py get-prs --repo-id "owner/model"
    uv run evaluation_manager.py show --repo-id "owner/model"
    uv run evaluation_manager.py validate --repo-id "owner/model"
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Any

VERSION = "1.3.0"


def _load_env() -> None:
    """Load .env if python-dotenv is available."""
    try:
        import dotenv

        dotenv.load_dotenv()
    except ModuleNotFoundError:
        pass


def _require_yaml() -> Any:
    import yaml

    return yaml


def _require_requests() -> Any:
    import requests

    return requests


def _require_markdown_it() -> Any:
    from markdown_it import MarkdownIt

    return MarkdownIt


def _require_model_card() -> Any:
    from huggingface_hub import ModelCard

    return ModelCard


def _normalize_name(name: str) -> set[str]:
    """Normalize a model name to a set of lowercase tokens for matching."""
    cleaned = re.sub(r"\*\*", "", name)
    cleaned = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cleaned)
    cleaned = cleaned.lower().replace("-", " ").replace("_", " ")
    return {t for t in cleaned.split() if t}


def _parse_markdown_tables(readme_content: str) -> list[list[list[str]]]:
    """Parse markdown tables from README, ignoring code blocks."""
    MarkdownIt = _require_markdown_it()
    md = MarkdownIt()
    tokens = md.parse(readme_content)

    tables: list[list[list[str]]] = []
    current_table: list[list[str]] = []
    in_table = False

    for token in tokens:
        if token.type == "table_open":
            in_table = True
            current_table = []
        elif token.type == "table_close":
            in_table = False
            if current_table:
                tables.append(current_table)
        elif in_table and token.type == "inline" and token.content:
            if token.content.strip():
                if not current_table or len(current_table[-1]) == 0:
                    current_table.append([])
                current_table[-1].append(token.content.strip())

    return tables


def _has_numeric_scores(table: list[list[str]]) -> bool:
    """Check if a table likely contains evaluation scores."""
    numeric_count = 0
    for row in table[1:]:  # Skip header
        for cell in row:
            if re.match(r"^\d+\.?\d*%?$", cell.strip()):
                numeric_count += 1
    return numeric_count >= 2


def cmd_inspect_tables(args: argparse.Namespace) -> int:
    """Show all tables in a model's README with structure info."""
    ModelCard = _require_model_card()
    card = ModelCard.load(args.repo_id)
    tables = _parse_markdown_tables(card.text)

    if not tables:
        print(f"No tables found in README of {args.repo_id}")
        return 1

    for i, table in enumerate(tables):
        has_scores = _has_numeric_scores(table)
        marker = " [EVAL]" if has_scores else ""
        print(f"\n--- Table {i + 1}{marker} ---")
        if table:
            header = table[0] if table[0] else []
            print(f"Columns ({len(header)}): {header}")
            for j, row in enumerate(table[:4]):
                print(f"  Row {j}: {row}")
            if len(table) > 4:
                print(f"  ... ({len(table) - 4} more rows)")
    return 0


def cmd_extract_readme(args: argparse.Namespace) -> int:
    """Extract evaluation table to model-index YAML."""
    yaml = _require_yaml()
    ModelCard = _require_model_card()

    card = ModelCard.load(args.repo_id)
    tables = _parse_markdown_tables(card.text)

    if not tables:
        print("No tables found in README", file=sys.stderr)
        return 1

    table_idx = (args.table or 1) - 1
    if table_idx >= len(tables) or table_idx < 0:
        print(f"Table {args.table} not found (have {len(tables)} tables)", file=sys.stderr)
        return 1

    table = tables[table_idx]
    if len(table) < 2:
        print("Table has no data rows", file=sys.stderr)
        return 1

    header = table[0]
    model_name = args.repo_id.split("/")[-1]
    if args.model_name_override:
        model_name = args.model_name_override

    results = []
    for row in table[1:]:
        for col_idx, cell in enumerate(row):
            if col_idx < len(header):
                value = cell.strip().rstrip("%")
                try:
                    num_value = float(value)
                    metric_name = header[col_idx].strip()
                    results.append(
                        {
                            "task": {"type": args.task_type or "text-generation"},
                            "dataset": {
                                "name": args.dataset_name or "Custom Benchmarks",
                                "type": "custom",
                            },
                            "metrics": [
                                {
                                    "name": metric_name,
                                    "type": re.sub(r"[^a-z0-9]", "_", metric_name.lower()),
                                    "value": num_value,
                                }
                            ],
                        }
                    )
                except ValueError:
                    continue

    if not results:
        print("No numeric scores extracted", file=sys.stderr)
        return 1

    model_index = {"model-index": [{"name": model_name, "results": results}]}
    output = yaml.dump(model_index, default_flow_style=False, sort_keys=False)
    print(output)

    if args.apply or args.create_pr:
        print(f"Would {'apply' if args.apply else 'create PR'} to {args.repo_id}")
        print("(Full implementation in upstream evaluation_manager.py)")

    return 0


def cmd_import_aa(args: argparse.Namespace) -> int:
    """Import benchmark scores from Artificial Analysis API."""
    yaml = _require_yaml()
    requests = _require_requests()

    api_key = os.getenv("AA_API_KEY")
    if not api_key:
        print("AA_API_KEY not set", file=sys.stderr)
        return 1

    url = "https://api.artificialanalysis.ai/v0/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    target = f"{args.creator_slug}/{args.model_name}"
    model_data = None
    for model in data.get("data", []):
        if model.get("slug", "").lower() == target.lower():
            model_data = model
            break

    if not model_data:
        print(f"Model '{target}' not found in Artificial Analysis", file=sys.stderr)
        return 1

    results = []
    for benchmark in model_data.get("benchmarks", []):
        results.append(
            {
                "task": {"type": "text-generation"},
                "dataset": {
                    "name": benchmark["name"],
                    "type": benchmark.get("id", "custom"),
                },
                "metrics": [
                    {
                        "name": benchmark["name"],
                        "type": benchmark.get("id", "score"),
                        "value": benchmark["score"],
                    }
                ],
                "source": {
                    "name": "Artificial Analysis",
                    "url": f"https://artificialanalysis.ai/models/{target}",
                },
            }
        )

    model_index = {"model-index": [{"name": args.model_name, "results": results}]}
    print(yaml.dump(model_index, default_flow_style=False, sort_keys=False))
    return 0


def cmd_get_prs(args: argparse.Namespace) -> int:
    """List open pull requests for a model repository."""
    from huggingface_hub import HfApi

    api = HfApi()
    discussions = api.get_repo_discussions(args.repo_id, repo_type="model")

    open_prs = [d for d in discussions if d.is_pull_request and d.status == "open"]

    if not open_prs:
        print(f"No open PRs for {args.repo_id}")
        return 0

    print(f"Open PRs for {args.repo_id}:")
    for pr in open_prs:
        print(f"  #{pr.num}: {pr.title}")
        print(f"    Author: {pr.author}")
        print(f"    URL: https://huggingface.co/{args.repo_id}/discussions/{pr.num}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Show existing model-index entries."""
    yaml = _require_yaml()
    ModelCard = _require_model_card()

    card = ModelCard.load(args.repo_id)
    model_index = card.data.get("model-index") if card.data else None

    if not model_index:
        print(f"No model-index found in {args.repo_id}")
        return 0

    print(yaml.dump({"model-index": model_index}, default_flow_style=False, sort_keys=False))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate model-index entries for compliance."""
    ModelCard = _require_model_card()

    card = ModelCard.load(args.repo_id)
    model_index = card.data.get("model-index") if card.data else None

    if not model_index:
        print(f"No model-index to validate in {args.repo_id}")
        return 1

    errors = 0
    for entry in model_index:
        name = entry.get("name", "")
        if "**" in name or "[" in name:
            print(f"ERROR: Model name contains markdown: {name}")
            errors += 1

        for result in entry.get("results", []):
            if not result.get("task", {}).get("type"):
                print("ERROR: Missing task.type in result")
                errors += 1
            for metric in result.get("metrics", []):
                if not isinstance(metric.get("value"), (int, float)):
                    print(f"ERROR: Non-numeric metric value: {metric.get('value')}")
                    errors += 1

    if errors == 0:
        print(f"model-index in {args.repo_id} is valid ({len(model_index)} entries)")
    else:
        print(f"Found {errors} validation errors")
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="evaluation_manager",
        description="Manage evaluation results in Hugging Face model cards",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    # inspect-tables
    p_inspect = sub.add_parser("inspect-tables", help="Inspect README tables")
    p_inspect.add_argument("--repo-id", required=True, help="HF repo ID (owner/model)")

    # extract-readme
    p_extract = sub.add_parser("extract-readme", help="Extract eval table to YAML")
    p_extract.add_argument("--repo-id", required=True, help="HF repo ID")
    p_extract.add_argument("--table", type=int, help="Table number (1-indexed)")
    p_extract.add_argument("--model-column-index", type=int, help="Column index for model")
    p_extract.add_argument("--model-name-override", help="Exact model name text")
    p_extract.add_argument("--task-type", help="Task type for model-index")
    p_extract.add_argument("--dataset-name", help="Dataset name override")
    p_extract.add_argument("--apply", action="store_true", help="Push changes directly")
    p_extract.add_argument("--create-pr", action="store_true", help="Create a PR")

    # import-aa
    p_import = sub.add_parser("import-aa", help="Import from Artificial Analysis")
    p_import.add_argument("--creator-slug", required=True, help="AA creator slug")
    p_import.add_argument("--model-name", required=True, help="AA model name")
    p_import.add_argument("--repo-id", required=True, help="HF repo ID")
    p_import.add_argument("--create-pr", action="store_true", help="Create a PR")

    # get-prs
    p_prs = sub.add_parser("get-prs", help="Check open PRs")
    p_prs.add_argument("--repo-id", required=True, help="HF repo ID")

    # show
    p_show = sub.add_parser("show", help="Show model-index entries")
    p_show.add_argument("--repo-id", required=True, help="HF repo ID")

    # validate
    p_validate = sub.add_parser("validate", help="Validate model-index")
    p_validate.add_argument("--repo-id", required=True, help="HF repo ID")

    return parser


COMMANDS = {
    "inspect-tables": cmd_inspect_tables,
    "extract-readme": cmd_extract_readme,
    "import-aa": cmd_import_aa,
    "get-prs": cmd_get_prs,
    "show": cmd_show,
    "validate": cmd_validate,
}


def main() -> int:
    """Entry point."""
    _load_env()
    parser = build_parser()
    args = parser.parse_args()
    handler = COMMANDS.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
