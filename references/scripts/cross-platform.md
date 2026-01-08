# Cross-Platform Script Compatibility

Ensure generated scripts work across Linux, macOS, and Windows.

## Compatibility Goals

| Goal | Description |
|------|-------------|
| Portable commands | Use POSIX-compliant commands |
| Path handling | Handle path separators correctly |
| Shell detection | Detect and adapt to available shells |
| Fallback options | Provide alternatives when commands unavailable |

## Platform Model

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

class Platform(Enum):
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"
    UNKNOWN = "unknown"

class Shell(Enum):
    BASH = "bash"
    ZSH = "zsh"
    SH = "sh"
    POWERSHELL = "powershell"
    CMD = "cmd"

@dataclass
class PlatformInfo:
    platform: Platform
    shell: Shell
    path_separator: str
    home_var: str
    null_device: str
    line_ending: str

@dataclass
class CommandMapping:
    posix: str
    windows_cmd: str | None
    windows_ps: str | None
    description: str
    requires: list[str] = field(default_factory=list)

@dataclass
class CompatibilityIssue:
    command: str
    line_number: int
    issue: str
    suggestion: str
    severity: str  # "error", "warning", "info"
```

## Platform Detector

```python
import os
import shutil
import subprocess
import sys

class PlatformDetector:
    """Detect platform and available tools."""

    def detect(self) -> PlatformInfo:
        """Detect current platform information."""
        platform = self._detect_platform()
        shell = self._detect_shell()

        return PlatformInfo(
            platform=platform,
            shell=shell,
            path_separator=self._get_path_separator(platform),
            home_var=self._get_home_var(platform),
            null_device=self._get_null_device(platform),
            line_ending=self._get_line_ending(platform)
        )

    def _detect_platform(self) -> Platform:
        """Detect operating system."""
        if sys.platform.startswith("linux"):
            return Platform.LINUX
        elif sys.platform == "darwin":
            return Platform.MACOS
        elif sys.platform == "win32":
            return Platform.WINDOWS
        return Platform.UNKNOWN

    def _detect_shell(self) -> Shell:
        """Detect available shell."""
        # Check SHELL environment variable
        shell_path = os.environ.get("SHELL", "")

        if "zsh" in shell_path:
            return Shell.ZSH
        elif "bash" in shell_path:
            return Shell.BASH
        elif shell_path:
            return Shell.SH

        # Windows
        if sys.platform == "win32":
            if shutil.which("pwsh") or shutil.which("powershell"):
                return Shell.POWERSHELL
            return Shell.CMD

        return Shell.SH

    def _get_path_separator(self, platform: Platform) -> str:
        """Get path separator for platform."""
        if platform == Platform.WINDOWS:
            return "\\"
        return "/"

    def _get_home_var(self, platform: Platform) -> str:
        """Get home directory variable."""
        if platform == Platform.WINDOWS:
            return "%USERPROFILE%"
        return "$HOME"

    def _get_null_device(self, platform: Platform) -> str:
        """Get null device path."""
        if platform == Platform.WINDOWS:
            return "NUL"
        return "/dev/null"

    def _get_line_ending(self, platform: Platform) -> str:
        """Get line ending for platform."""
        if platform == Platform.WINDOWS:
            return "\r\n"
        return "\n"

    def check_command(self, command: str) -> bool:
        """Check if command is available."""
        return shutil.which(command) is not None

    def get_available_commands(
        self,
        commands: list[str]
    ) -> dict[str, bool]:
        """Check availability of multiple commands."""
        return {cmd: self.check_command(cmd) for cmd in commands}
```

## Command Mapper

```python
class CommandMapper:
    """Map commands to cross-platform alternatives."""

    # Command mappings for common operations
    MAPPINGS: dict[str, CommandMapping] = {
        # File operations
        "cat": CommandMapping(
            posix="cat",
            windows_cmd="type",
            windows_ps="Get-Content",
            description="Display file contents"
        ),
        "ls": CommandMapping(
            posix="ls",
            windows_cmd="dir",
            windows_ps="Get-ChildItem",
            description="List directory contents"
        ),
        "cp": CommandMapping(
            posix="cp",
            windows_cmd="copy",
            windows_ps="Copy-Item",
            description="Copy files"
        ),
        "mv": CommandMapping(
            posix="mv",
            windows_cmd="move",
            windows_ps="Move-Item",
            description="Move/rename files"
        ),
        "rm": CommandMapping(
            posix="rm",
            windows_cmd="del",
            windows_ps="Remove-Item",
            description="Remove files"
        ),
        "mkdir": CommandMapping(
            posix="mkdir -p",
            windows_cmd="mkdir",
            windows_ps="New-Item -ItemType Directory -Force",
            description="Create directory"
        ),
        "rmdir": CommandMapping(
            posix="rm -rf",
            windows_cmd="rmdir /s /q",
            windows_ps="Remove-Item -Recurse -Force",
            description="Remove directory"
        ),

        # Text processing
        "grep": CommandMapping(
            posix="grep",
            windows_cmd="findstr",
            windows_ps="Select-String",
            description="Search text patterns"
        ),
        "sed": CommandMapping(
            posix="sed",
            windows_cmd=None,  # No direct equivalent
            windows_ps="ForEach-Object { $_ -replace }",
            description="Stream editor"
        ),
        "awk": CommandMapping(
            posix="awk",
            windows_cmd=None,
            windows_ps=None,  # Complex, needs custom
            description="Pattern processing"
        ),
        "head": CommandMapping(
            posix="head",
            windows_cmd=None,
            windows_ps="Select-Object -First",
            description="First lines of file"
        ),
        "tail": CommandMapping(
            posix="tail",
            windows_cmd=None,
            windows_ps="Select-Object -Last",
            description="Last lines of file"
        ),
        "wc": CommandMapping(
            posix="wc",
            windows_cmd="find /c /v \"\"",
            windows_ps="Measure-Object",
            description="Count lines/words"
        ),

        # System
        "which": CommandMapping(
            posix="which",
            windows_cmd="where",
            windows_ps="Get-Command",
            description="Locate command"
        ),
        "echo": CommandMapping(
            posix="echo",
            windows_cmd="echo",
            windows_ps="Write-Output",
            description="Print text"
        ),
        "pwd": CommandMapping(
            posix="pwd",
            windows_cmd="cd",
            windows_ps="Get-Location",
            description="Current directory"
        ),
        "env": CommandMapping(
            posix="env",
            windows_cmd="set",
            windows_ps="Get-ChildItem Env:",
            description="Environment variables"
        ),

        # Permissions
        "chmod": CommandMapping(
            posix="chmod",
            windows_cmd=None,
            windows_ps="Set-Acl",
            description="Change permissions"
        ),
        "chown": CommandMapping(
            posix="chown",
            windows_cmd=None,
            windows_ps="Set-Acl",
            description="Change owner"
        ),
    }

    # Commands to avoid (platform-specific)
    AVOID_COMMANDS = {
        "readlink": "Use realpath or Python os.path.realpath",
        "stat": "Output differs between platforms",
        "file": "Not available on Windows",
        "xargs": "Behavior differs, use loops instead",
        "tee": "Not available on Windows CMD",
        "diff": "Output differs between platforms",
    }

    def get_mapping(self, command: str) -> CommandMapping | None:
        """Get mapping for a command."""
        return self.MAPPINGS.get(command)

    def get_alternative(
        self,
        command: str,
        platform: Platform,
        shell: Shell
    ) -> str | None:
        """Get platform-specific alternative."""
        mapping = self.MAPPINGS.get(command)
        if not mapping:
            return None

        if platform == Platform.WINDOWS:
            if shell == Shell.POWERSHELL:
                return mapping.windows_ps
            return mapping.windows_cmd

        return mapping.posix

    def should_avoid(self, command: str) -> tuple[bool, str | None]:
        """Check if command should be avoided."""
        if command in self.AVOID_COMMANDS:
            return True, self.AVOID_COMMANDS[command]
        return False, None
```

## Compatibility Checker

```python
import re

class CompatibilityChecker:
    """Check scripts for cross-platform compatibility."""

    def __init__(self):
        self.mapper = CommandMapper()
        self.detector = PlatformDetector()

    def check_script(self, content: str) -> list[CompatibilityIssue]:
        """Check script for compatibility issues."""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Skip comments and empty lines
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            issues.extend(self._check_line(line, i))

        return issues

    def _check_line(self, line: str, line_num: int) -> list[CompatibilityIssue]:
        """Check a single line for issues."""
        issues = []

        # Extract commands from line
        commands = self._extract_commands(line)

        for cmd in commands:
            # Check if command should be avoided
            avoid, reason = self.mapper.should_avoid(cmd)
            if avoid:
                issues.append(CompatibilityIssue(
                    command=cmd,
                    line_number=line_num,
                    issue=f"Command '{cmd}' has platform differences",
                    suggestion=reason or "Consider alternative",
                    severity="warning"
                ))

            # Check for platform-specific patterns
            issues.extend(self._check_patterns(line, line_num))

        return issues

    def _extract_commands(self, line: str) -> list[str]:
        """Extract command names from line."""
        # Simple extraction - first word of each pipe segment
        commands = []
        segments = line.split("|")

        for segment in segments:
            segment = segment.strip()
            # Skip variable assignments
            if "=" in segment.split()[0] if segment.split() else True:
                continue

            words = segment.split()
            if words:
                cmd = words[0].strip("$()\"'")
                if cmd and not cmd.startswith("-"):
                    commands.append(cmd)

        return commands

    def _check_patterns(
        self,
        line: str,
        line_num: int
    ) -> list[CompatibilityIssue]:
        """Check for problematic patterns."""
        issues = []

        # Check for hardcoded paths
        if "/home/" in line or "/Users/" in line:
            issues.append(CompatibilityIssue(
                command="path",
                line_number=line_num,
                issue="Hardcoded path detected",
                suggestion="Use $HOME or ~ instead",
                severity="warning"
            ))

        # Check for /dev/null
        if "/dev/null" in line:
            issues.append(CompatibilityIssue(
                command="redirect",
                line_number=line_num,
                issue="/dev/null not available on Windows",
                suggestion="Use platform detection or 2>&1",
                severity="info"
            ))

        # Check for bash-specific syntax
        if "[[" in line:
            issues.append(CompatibilityIssue(
                command="test",
                line_number=line_num,
                issue="[[ ]] is bash-specific",
                suggestion="Use [ ] for POSIX compatibility",
                severity="warning"
            ))

        # Check for bash arrays
        if re.search(r'\w+\[\d+\]', line) or "declare -a" in line:
            issues.append(CompatibilityIssue(
                command="array",
                line_number=line_num,
                issue="Arrays are bash-specific",
                suggestion="Use positional parameters or files",
                severity="warning"
            ))

        # Check for process substitution
        if "<(" in line or ">(" in line:
            issues.append(CompatibilityIssue(
                command="substitution",
                line_number=line_num,
                issue="Process substitution is bash-specific",
                suggestion="Use temporary files instead",
                severity="warning"
            ))

        return issues
```

## Portable Script Generator

```python
class PortableScriptGenerator:
    """Generate cross-platform compatible scripts."""

    PORTABLE_HEADER = '''#!/bin/sh
# Cross-platform compatible script
# Works on: Linux, macOS, Windows (Git Bash/WSL)

# Strict mode
set -eu

# Detect platform
detect_platform() {
    case "$(uname -s)" in
        Linux*)  echo "linux" ;;
        Darwin*) echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)       echo "unknown" ;;
    esac
}

PLATFORM=$(detect_platform)

# Cross-platform home directory
get_home() {
    if [ -n "${HOME:-}" ]; then
        echo "$HOME"
    elif [ -n "${USERPROFILE:-}" ]; then
        echo "$USERPROFILE"
    else
        echo ~
    fi
}

HOME_DIR=$(get_home)
'''

    PORTABLE_FUNCTIONS = '''
# Portable file operations
portable_mkdir() {
    mkdir -p "$1" 2>/dev/null || mkdir "$1"
}

portable_cp() {
    cp -r "$1" "$2" 2>/dev/null || cp "$1" "$2"
}

portable_rm() {
    rm -rf "$1" 2>/dev/null || rm -r "$1"
}

# Check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Portable path handling
normalize_path() {
    case "$1" in
        /*) echo "$1" ;;
        ~/*) echo "${HOME_DIR}${1#\~}" ;;
        *) echo "$(pwd)/$1" ;;
    esac
}
'''

    def generate_header(self) -> str:
        """Generate portable script header."""
        return self.PORTABLE_HEADER

    def generate_functions(self) -> str:
        """Generate portable helper functions."""
        return self.PORTABLE_FUNCTIONS

    def wrap_command(self, command: str, fallback: str | None = None) -> str:
        """Wrap command with availability check."""
        base_cmd = command.split()[0]

        if fallback:
            return f'''if command_exists {base_cmd}; then
    {command}
else
    {fallback}
fi'''
        return f'''if command_exists {base_cmd}; then
    {command}
else
    echo "Warning: {base_cmd} not available" >&2
fi'''

    def generate_portable_script(
        self,
        operations: list[dict]
    ) -> str:
        """Generate complete portable script."""
        lines = [self.PORTABLE_HEADER, self.PORTABLE_FUNCTIONS]

        lines.append("\n# Main script\n")

        for op in operations:
            op_type = op.get("type")
            if op_type == "mkdir":
                lines.append(f'portable_mkdir "{op["path"]}"')
            elif op_type == "copy":
                lines.append(f'portable_cp "{op["src"]}" "{op["dst"]}"')
            elif op_type == "remove":
                lines.append(f'portable_rm "{op["path"]}"')
            elif op_type == "command":
                cmd = op.get("command", "")
                fallback = op.get("fallback")
                lines.append(self.wrap_command(cmd, fallback))

        return "\n".join(lines)
```

## Integration

```python
def check_and_report(script_path: str) -> None:
    """Check script and report issues."""
    checker = CompatibilityChecker()

    with open(script_path) as f:
        content = f.read()

    issues = checker.check_script(content)

    if not issues:
        print("  ✓ No compatibility issues found")
        return

    print(f"  Found {len(issues)} compatibility issue(s):\n")

    for issue in issues:
        icon = {"error": "✗", "warning": "⚠", "info": "ℹ"}[issue.severity]
        print(f"  {icon} Line {issue.line_number}: {issue.issue}")
        print(f"      Suggestion: {issue.suggestion}")
        print()
```

## Compatibility Checklist

| Category | POSIX Compatible | Avoid |
|----------|------------------|-------|
| Conditionals | `[ ]` | `[[ ]]` |
| Variables | `$VAR` | `${VAR:?}` complex |
| Loops | `for x in ...` | `for ((i=0;...))` |
| Functions | `func() { }` | `function func` |
| Redirects | `2>&1` | `&>` |
| Strings | `"..."` | `$'...'` |
| Arrays | Positional `$@` | `array[0]` |
| Arithmetic | `$(( ))` | `let` |
