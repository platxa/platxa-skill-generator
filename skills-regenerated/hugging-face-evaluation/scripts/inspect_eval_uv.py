# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "inspect-ai>=0.3.0",
#     "inspect-evals",
#     "openai",
# ]
# ///

"""Run inspect-ai evaluations via HF Jobs or locally.

Evaluates models using HF inference provider endpoints. For local GPU
evaluation with vLLM, use inspect_vllm_uv.py instead.

Usage (standalone):
    python inspect_eval_uv.py --model "meta-llama/Llama-2-7b-hf" --task "mmlu"

Usage (HF Jobs):
    hf jobs uv run inspect_eval_uv.py \\
        --flavor cpu-basic --secret HF_TOKEN=$HF_TOKEN \\
        -- --model "meta-llama/Llama-2-7b-hf" --task "mmlu"
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _inspect_evals_tasks_root() -> Path | None:
    """Return the installed inspect_evals package path if available."""
    try:
        import inspect_evals

        return Path(inspect_evals.__file__).parent
    except Exception:
        return None


def _normalize_task(task: str) -> str:
    """Allow lighteval-style suite|task|shots strings by extracting task name."""
    if "|" in task:
        parts = task.split("|")
        if len(parts) >= 2 and parts[1]:
            return parts[1]
    return task


def main() -> None:
    """Entry point for inspect-ai evaluation runner."""
    parser = argparse.ArgumentParser(description="inspect-ai evaluation runner")
    parser.add_argument("--model", required=True, help="HF model ID")
    parser.add_argument("--task", required=True, help="inspect-ai task (e.g. mmlu, gsm8k)")
    parser.add_argument("--limit", type=int, default=None, help="Max samples to evaluate")
    parser.add_argument("--tasks-root", default=None, help="Path to inspect task files")
    parser.add_argument(
        "--sandbox",
        default="local",
        help="Sandbox backend (default: local for HF Jobs without Docker)",
    )
    args = parser.parse_args()

    # Propagate HF token to all expected env vars
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        os.environ.setdefault("HUGGING_FACE_HUB_TOKEN", hf_token)
        os.environ.setdefault("HF_HUB_TOKEN", hf_token)

    task = _normalize_task(args.task)
    tasks_root = Path(args.tasks_root) if args.tasks_root else _inspect_evals_tasks_root()
    if tasks_root and not tasks_root.exists():
        tasks_root = None

    cmd = [
        "inspect",
        "eval",
        task,
        "--model",
        f"hf-inference-providers/{args.model}",
        "--log-level",
        "info",
        "--max-connections",
        "1",
        "--temperature",
        "0.001",
    ]

    if args.sandbox:
        cmd.extend(["--sandbox", args.sandbox])
    if args.limit:
        cmd.extend(["--limit", str(args.limit)])

    try:
        subprocess.run(cmd, check=True, cwd=tasks_root)
        print("Evaluation complete.")
    except subprocess.CalledProcessError as exc:
        location = f" (cwd={tasks_root})" if tasks_root else ""
        print(
            f"Evaluation failed with exit code {exc.returncode}{location}",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    main()
