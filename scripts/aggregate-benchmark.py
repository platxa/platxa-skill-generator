#!/usr/bin/env python3
"""Aggregate eval run results into a benchmark.json summary.

Reads grading.json and timing.json from each eval run directory, computes
per-configuration statistics (pass_rate, time, tokens with mean/stddev),
and outputs benchmark.json matching Anthropic's skill-creator schema.

Usage:
    python3 scripts/aggregate-benchmark.py <iteration-dir> --skill-name <name>

Input:  <iteration-dir>/<eval-name>/<config>/grading.json, timing.json
Output: <iteration-dir>/benchmark.json

See references/validation/eval-schema.md for the full benchmark.json schema.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


def compute_stats(values: list[float]) -> dict[str, float]:
    """Compute mean and standard deviation for a list of values.

    Args:
        values: List of numeric values

    Returns:
        Dict with mean and stddev keys
    """
    if not values:
        return {"mean": 0.0, "stddev": 0.0}

    n = len(values)
    mean = sum(values) / n

    if n < 2:
        return {"mean": round(mean, 3), "stddev": 0.0}

    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    stddev = math.sqrt(variance)

    return {"mean": round(mean, 3), "stddev": round(stddev, 3)}


def load_run_data(run_dir: Path) -> dict | None:
    """Load grading and timing data from a run directory.

    Args:
        run_dir: Path to a run directory (e.g., eval-name/with_skill/)

    Returns:
        Dict with pass_rate, time_seconds, tokens, or None if data missing
    """
    grading_path = run_dir / "grading.json"
    timing_path = run_dir / "timing.json"

    result: dict = {}

    if grading_path.exists():
        with open(grading_path) as f:
            grading = json.load(f)
        summary = grading.get("summary", {})
        result["pass_rate"] = summary.get("pass_rate", 0.0)
        result["passed"] = summary.get("passed", 0)
        result["failed"] = summary.get("failed", 0)
        result["total"] = summary.get("total", 0)
    else:
        result["pass_rate"] = 0.0
        result["passed"] = 0
        result["failed"] = 0
        result["total"] = 0

    if timing_path.exists():
        with open(timing_path) as f:
            timing = json.load(f)
        result["time_seconds"] = timing.get("total_duration_seconds", 0.0)
        result["tokens"] = timing.get("total_tokens", 0)
    else:
        result["time_seconds"] = 0.0
        result["tokens"] = 0

    return result


def aggregate(iteration_dir: Path, skill_name: str) -> dict:
    """Aggregate all run data in an iteration directory into benchmark.json.

    Scans iteration_dir for eval subdirectories, each containing
    with_skill/ and optionally without_skill/ run directories.

    Args:
        iteration_dir: Path to iteration directory
        skill_name: Name of the skill being benchmarked

    Returns:
        Benchmark dict matching Anthropic's schema
    """
    runs: list[dict] = []
    eval_ids: list[int] = []

    config_data: dict[str, list[dict]] = {
        "with_skill": [],
        "without_skill": [],
    }

    eval_id = 0
    for eval_dir in sorted(iteration_dir.iterdir()):
        if not eval_dir.is_dir():
            continue
        # Skip non-eval directories
        if eval_dir.name in ("benchmark.json", "benchmark.md"):
            continue

        eval_id += 1
        eval_ids.append(eval_id)
        eval_name = eval_dir.name

        for config in ("with_skill", "without_skill"):
            config_dir = eval_dir / config
            if not config_dir.is_dir():
                continue

            data = load_run_data(config_dir)
            if data is None:
                continue

            run = {
                "eval_id": eval_id,
                "eval_name": eval_name,
                "configuration": config,
                "run_number": 1,
                "result": {
                    "pass_rate": data["pass_rate"],
                    "passed": data["passed"],
                    "failed": data["failed"],
                    "total": data["total"],
                    "time_seconds": data["time_seconds"],
                    "tokens": data["tokens"],
                },
            }
            runs.append(run)
            config_data[config].append(data)

    # Compute per-configuration summaries
    run_summary: dict = {}
    for config, data_list in config_data.items():
        if not data_list:
            continue
        run_summary[config] = {
            "pass_rate": compute_stats([d["pass_rate"] for d in data_list]),
            "time_seconds": compute_stats([d["time_seconds"] for d in data_list]),
            "tokens": compute_stats([float(d["tokens"]) for d in data_list]),
        }

    # Compute delta if both configurations exist
    if "with_skill" in run_summary and "without_skill" in run_summary:
        ws = run_summary["with_skill"]
        wos = run_summary["without_skill"]
        delta_pr = ws["pass_rate"]["mean"] - wos["pass_rate"]["mean"]
        delta_time = ws["time_seconds"]["mean"] - wos["time_seconds"]["mean"]
        delta_tokens = ws["tokens"]["mean"] - wos["tokens"]["mean"]
        run_summary["delta"] = {
            "pass_rate": f"{delta_pr:+.2f}",
            "time_seconds": f"{delta_time:+.1f}",
            "tokens": f"{delta_tokens:+.0f}",
        }

    benchmark = {
        "metadata": {
            "skill_name": skill_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evals_run": eval_ids,
            "runs_per_configuration": 1,
        },
        "runs": runs,
        "run_summary": run_summary,
    }

    return benchmark


def main() -> None:
    """Run benchmark aggregation."""
    parser = argparse.ArgumentParser(description="Aggregate eval results into benchmark.json")
    parser.add_argument("iteration_dir", type=Path, help="Path to iteration directory")
    parser.add_argument(
        "--skill-name",
        required=True,
        help="Name of the skill being benchmarked",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path (default: <iteration-dir>/benchmark.json)",
    )

    args = parser.parse_args()

    if not args.iteration_dir.is_dir():
        print(f"ERROR: Not a directory: {args.iteration_dir}", file=sys.stderr)
        sys.exit(1)

    benchmark = aggregate(args.iteration_dir, args.skill_name)

    output_path = args.output or (args.iteration_dir / "benchmark.json")
    with open(output_path, "w") as f:
        json.dump(benchmark, f, indent=2)

    # Print summary
    summary = benchmark.get("run_summary", {})
    print(f"Benchmark: {args.skill_name}")
    print(f"  Evals: {len(benchmark['metadata']['evals_run'])}")
    print(f"  Runs: {len(benchmark['runs'])}")

    for config in ("with_skill", "without_skill"):
        if config in summary:
            s = summary[config]
            pr = s["pass_rate"]
            print(f"  {config}: pass_rate={pr['mean']:.2f}±{pr['stddev']:.2f}")

    if "delta" in summary:
        d = summary["delta"]
        print(f"  Delta: pass_rate={d['pass_rate']}, time={d['time_seconds']}s")

    print(f"  Output: {output_path}")


if __name__ == "__main__":
    main()
