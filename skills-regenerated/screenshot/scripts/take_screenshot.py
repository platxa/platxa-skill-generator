#!/usr/bin/env python3
"""Cross-platform screenshot helper.

Captures screenshots on macOS (screencapture), Linux (scrot, gnome-screenshot,
or ImageMagick import), and directs Windows users to take_screenshot.ps1.

Usage:
    python3 take_screenshot.py                       # full screen, OS default
    python3 take_screenshot.py --mode temp           # full screen, temp dir
    python3 take_screenshot.py --path out/shot.png   # explicit path
    python3 take_screenshot.py --active-window       # focused window
    python3 take_screenshot.py --region 0,0,800,600  # pixel region
    python3 take_screenshot.py --app "Safari"        # macOS app capture
    python3 take_screenshot.py --window-id 12345     # specific window ID
    python3 take_screenshot.py --list-windows --app X # list macOS windows
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path


def _timestamp() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _default_filename(fmt: str = "png") -> str:
    return f"screenshot-{_timestamp()}.{fmt}"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _mac_default_dir() -> Path:
    try:
        proc = subprocess.run(
            ["defaults", "read", "com.apple.screencapture", "location"],
            check=False,
            capture_output=True,
            text=True,
        )
        loc = proc.stdout.strip()
        if loc:
            return Path(loc).expanduser()
    except OSError:
        pass
    return Path.home() / "Desktop"


def _default_dir(system: str) -> Path:
    home = Path.home()
    if system == "Darwin":
        return _mac_default_dir()
    for candidate in [home / "Pictures" / "Screenshots", home / "Pictures"]:
        if candidate.exists():
            return candidate
    return home


def resolve_output(requested: str | None, mode: str, fmt: str, system: str) -> Path:
    """Determine the output file path based on user input and mode."""
    if requested:
        path = Path(requested).expanduser()
        if path.is_dir() or requested.endswith(("/", "\\")):
            path.mkdir(parents=True, exist_ok=True)
            path = path / _default_filename(fmt)
        elif not path.suffix:
            path = path.with_suffix(f".{fmt}")
        _ensure_parent(path)
        return path

    if mode == "temp":
        path = Path(tempfile.gettempdir()) / _default_filename(fmt)
        _ensure_parent(path)
        return path

    dest = _default_dir(system) / _default_filename(fmt)
    _ensure_parent(dest)
    return dest


def _run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(f"required command not found: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"command failed ({exc.returncode}): {' '.join(cmd)}") from exc


def _parse_region(value: str) -> tuple[int, int, int, int]:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("region must be x,y,w,h")
    try:
        x, y, w, h = (int(p) for p in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("region values must be integers") from exc
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("region width and height must be positive")
    return x, y, w, h


# ---------------------------------------------------------------------------
# macOS
# ---------------------------------------------------------------------------


def capture_macos(args: argparse.Namespace, output: Path) -> None:
    """Capture on macOS using screencapture."""
    cmd = ["screencapture", "-x", f"-t{args.format}"]
    if args.interactive:
        cmd.append("-i")
    if args.window_id is not None:
        cmd.append(f"-l{args.window_id}")
    elif args.region is not None:
        x, y, w, h = args.region
        cmd.append(f"-R{x},{y},{w},{h}")
    cmd.append(str(output))
    _run(cmd)


# ---------------------------------------------------------------------------
# Linux
# ---------------------------------------------------------------------------


def capture_linux(args: argparse.Namespace, output: Path) -> None:
    """Capture on Linux using the first available tool."""
    scrot = shutil.which("scrot")
    gnome = shutil.which("gnome-screenshot")
    imagemagick = shutil.which("import")

    if args.region is not None:
        x, y, w, h = args.region
        if scrot:
            _run(["scrot", "-a", f"{x},{y},{w},{h}", str(output)])
            return
        if imagemagick:
            _run(
                [
                    "import",
                    "-window",
                    "root",
                    "-crop",
                    f"{w}x{h}+{x}+{y}",
                    str(output),
                ]
            )
            return
        raise SystemExit("region capture requires scrot or ImageMagick (import)")

    if args.window_id is not None:
        if imagemagick:
            _run(["import", "-window", str(args.window_id), str(output)])
            return
        raise SystemExit("window-id capture requires ImageMagick (import)")

    if args.active_window:
        if scrot:
            _run(["scrot", "-u", str(output)])
            return
        if gnome:
            _run(["gnome-screenshot", "-w", "-f", str(output)])
            return
        raise SystemExit("active-window capture requires scrot or gnome-screenshot")

    if scrot:
        _run(["scrot", str(output)])
        return
    if gnome:
        _run(["gnome-screenshot", "-f", str(output)])
        return
    if imagemagick:
        _run(["import", "-window", "root", str(output)])
        return
    raise SystemExit("no screenshot tool found; install scrot, gnome-screenshot, or ImageMagick")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", help="output file path or directory; overrides --mode")
    parser.add_argument(
        "--mode",
        choices=("default", "temp"),
        default="default",
        help="save to OS default location or temp directory",
    )
    parser.add_argument("--format", default="png", help="image format (default: png)")
    parser.add_argument(
        "--app",
        help="macOS only: capture windows matching this app name",
    )
    parser.add_argument(
        "--window-name",
        help="macOS only: filter by window title substring",
    )
    parser.add_argument(
        "--list-windows",
        action="store_true",
        help="macOS only: list matching windows instead of capturing",
    )
    parser.add_argument("--region", type=_parse_region, help="pixel region as x,y,w,h")
    parser.add_argument("--window-id", type=int, help="capture a specific window ID")
    parser.add_argument(
        "--active-window",
        action="store_true",
        help="capture the focused window",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="interactive selection (macOS only)",
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Check for mutually exclusive flag combinations."""
    exclusive = [
        ("--region", args.region is not None),
        ("--window-id", args.window_id is not None),
        ("--active-window", args.active_window),
        ("--app", bool(args.app)),
        ("--interactive", args.interactive),
    ]
    active = [name for name, on in exclusive if on]
    if len(active) > 1:
        raise SystemExit(f"choose only one of {', '.join(active)}; they are mutually exclusive")


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args)

    system = os.environ.get("SCREENSHOT_PLATFORM") or platform.system()

    if system != "Darwin" and (args.app or args.window_name or args.list_windows):
        raise SystemExit("--app, --window-name, and --list-windows are macOS only")

    output = resolve_output(args.path, args.mode, args.format, system)

    if system == "Darwin":
        capture_macos(args, output)
    elif system == "Linux":
        capture_linux(args, output)
    elif system == "Windows":
        raise SystemExit("on Windows use the PowerShell helper: take_screenshot.ps1")
    else:
        raise SystemExit(f"unsupported platform: {system}")

    print(output)


if __name__ == "__main__":
    main()
