# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "huggingface-hub>=0.26.0",
#     "python-dotenv>=1.2.1",
# ]
# ///

"""Submit inspect-ai evaluation jobs to HF Jobs infrastructure.

Wraps the inspect_eval_uv.py script for submission via ``hf jobs uv run``
with the requested hardware flavor.

Usage:
    uv run run_eval_job.py --model "Qwen/Qwen3-0.6B" --task "mmlu" --hardware "cpu-basic"
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import get_token

load_dotenv()

SCRIPT_PATH = Path(__file__).with_name("inspect_eval_uv.py").resolve()


def create_eval_job(
    model_id: str,
    task: str,
    hardware: str = "cpu-basic",
    hf_token: str | None = None,
    limit: int | None = None,
) -> None:
    """Submit an evaluation job using the HF Jobs CLI."""
    token = hf_token or os.getenv("HF_TOKEN") or get_token()
    if not token:
        raise ValueError("HF_TOKEN is required. Set it in environment or pass as argument.")

    if not SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Script not found at {SCRIPT_PATH}")

    print(f"Submitting eval job: {model_id} / {task} on {hardware}")

    cmd = [
        "hf",
        "jobs",
        "uv",
        "run",
        str(SCRIPT_PATH),
        "--flavor",
        hardware,
        "--secrets",
        f"HF_TOKEN={token}",
        "--",
        "--model",
        model_id,
        "--task",
        task,
    ]

    if limit:
        cmd.extend(["--limit", str(limit)])

    print("Executing:", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("hf jobs command failed", file=sys.stderr)
        raise


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Run inspect-ai evaluations on HF Jobs")
    parser.add_argument("--model", required=True, help="HF model ID")
    parser.add_argument("--task", required=True, help="inspect-ai task name")
    parser.add_argument(
        "--hardware",
        default="cpu-basic",
        help="Hardware flavor (cpu-basic, t4-small, a10g-small, etc.)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Max samples")
    args = parser.parse_args()

    create_eval_job(
        model_id=args.model,
        task=args.task,
        hardware=args.hardware,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
