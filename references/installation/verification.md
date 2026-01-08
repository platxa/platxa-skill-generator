# Installation Verification

Verify installed skill files exist and are valid.

## Verification Checks

| Check | What It Validates | Severity |
|-------|-------------------|----------|
| File existence | Required files present | Critical |
| YAML frontmatter | Valid metadata in SKILL.md | Critical |
| File permissions | Files are readable | Critical |
| Content validity | Non-empty, parseable | Error |
| Cross-references | Links resolve correctly | Warning |
| Token budget | Within limits | Warning |

## Verification Model

```python
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

class CheckSeverity(Enum):
    CRITICAL = "critical"  # Installation failed
    ERROR = "error"        # Major issue
    WARNING = "warning"    # Should fix
    INFO = "info"          # Informational

class CheckStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class VerificationCheck:
    name: str
    description: str
    severity: CheckSeverity
    status: CheckStatus
    message: str | None
    details: dict | None

@dataclass
class VerificationResult:
    skill_name: str
    install_path: Path
    passed: bool
    checks: list[VerificationCheck]
    critical_failures: int
    errors: int
    warnings: int
```

## Installation Verifier

```python
import re
import yaml
from pathlib import Path

class InstallationVerifier:
    """Verify skill installation integrity."""

    REQUIRED_FILES = ["SKILL.md"]
    OPTIONAL_DIRS = ["references", "scripts"]

    def __init__(self, install_path: Path):
        self.install_path = install_path
        self.skill_name = install_path.name
        self.checks: list[VerificationCheck] = []

    def verify(self) -> VerificationResult:
        """Run all verification checks."""
        self.checks = []

        # Critical checks
        self._check_directory_exists()
        self._check_required_files()
        self._check_skill_md_frontmatter()
        self._check_file_permissions()

        # Error checks
        self._check_content_validity()
        self._check_encoding()

        # Warning checks
        self._check_cross_references()
        self._check_token_budget()
        self._check_naming_conventions()

        # Calculate results
        critical = sum(1 for c in self.checks
                      if c.severity == CheckSeverity.CRITICAL and c.status == CheckStatus.FAILED)
        errors = sum(1 for c in self.checks
                    if c.severity == CheckSeverity.ERROR and c.status == CheckStatus.FAILED)
        warnings = sum(1 for c in self.checks
                      if c.severity == CheckSeverity.WARNING and c.status == CheckStatus.FAILED)

        return VerificationResult(
            skill_name=self.skill_name,
            install_path=self.install_path,
            passed=critical == 0,
            checks=self.checks,
            critical_failures=critical,
            errors=errors,
            warnings=warnings
        )

    def _check_directory_exists(self) -> None:
        """Check installation directory exists."""
        check = VerificationCheck(
            name="directory_exists",
            description="Installation directory exists",
            severity=CheckSeverity.CRITICAL,
            status=CheckStatus.PASSED,
            message=None,
            details=None
        )

        if not self.install_path.exists():
            check.status = CheckStatus.FAILED
            check.message = f"Directory not found: {self.install_path}"
        elif not self.install_path.is_dir():
            check.status = CheckStatus.FAILED
            check.message = f"Path is not a directory: {self.install_path}"

        self.checks.append(check)

    def _check_required_files(self) -> None:
        """Check required files exist."""
        for filename in self.REQUIRED_FILES:
            file_path = self.install_path / filename
            check = VerificationCheck(
                name=f"file_exists_{filename}",
                description=f"Required file exists: {filename}",
                severity=CheckSeverity.CRITICAL,
                status=CheckStatus.PASSED,
                message=None,
                details={"file": filename}
            )

            if not file_path.exists():
                check.status = CheckStatus.FAILED
                check.message = f"Required file missing: {filename}"
            elif not file_path.is_file():
                check.status = CheckStatus.FAILED
                check.message = f"Path is not a file: {filename}"

            self.checks.append(check)

    def _check_skill_md_frontmatter(self) -> None:
        """Check SKILL.md has valid YAML frontmatter."""
        check = VerificationCheck(
            name="skill_md_frontmatter",
            description="SKILL.md has valid YAML frontmatter",
            severity=CheckSeverity.CRITICAL,
            status=CheckStatus.PASSED,
            message=None,
            details=None
        )

        skill_md = self.install_path / "SKILL.md"
        if not skill_md.exists():
            check.status = CheckStatus.SKIPPED
            check.message = "SKILL.md not found"
            self.checks.append(check)
            return

        try:
            content = skill_md.read_text()

            # Check for frontmatter delimiters
            if not content.startswith("---"):
                check.status = CheckStatus.FAILED
                check.message = "Missing frontmatter delimiter (---)"
                self.checks.append(check)
                return

            # Extract frontmatter
            parts = content.split("---", 2)
            if len(parts) < 3:
                check.status = CheckStatus.FAILED
                check.message = "Invalid frontmatter structure"
                self.checks.append(check)
                return

            frontmatter = parts[1].strip()

            # Parse YAML
            data = yaml.safe_load(frontmatter)

            # Check required fields
            if not data:
                check.status = CheckStatus.FAILED
                check.message = "Empty frontmatter"
            elif "name" not in data:
                check.status = CheckStatus.FAILED
                check.message = "Missing required field: name"
            elif "description" not in data:
                check.status = CheckStatus.FAILED
                check.message = "Missing required field: description"
            else:
                check.details = {"name": data["name"], "description": data["description"][:50]}

        except yaml.YAMLError as e:
            check.status = CheckStatus.FAILED
            check.message = f"Invalid YAML: {e}"
        except Exception as e:
            check.status = CheckStatus.FAILED
            check.message = f"Error reading file: {e}"

        self.checks.append(check)

    def _check_file_permissions(self) -> None:
        """Check files are readable."""
        check = VerificationCheck(
            name="file_permissions",
            description="All files are readable",
            severity=CheckSeverity.CRITICAL,
            status=CheckStatus.PASSED,
            message=None,
            details={"unreadable": []}
        )

        unreadable = []
        for file in self.install_path.rglob("*"):
            if file.is_file():
                try:
                    file.read_bytes()
                except PermissionError:
                    unreadable.append(str(file.relative_to(self.install_path)))

        if unreadable:
            check.status = CheckStatus.FAILED
            check.message = f"{len(unreadable)} file(s) not readable"
            check.details = {"unreadable": unreadable}

        self.checks.append(check)

    def _check_content_validity(self) -> None:
        """Check files have valid content."""
        check = VerificationCheck(
            name="content_validity",
            description="Files have valid content",
            severity=CheckSeverity.ERROR,
            status=CheckStatus.PASSED,
            message=None,
            details={"empty_files": [], "invalid_files": []}
        )

        empty = []
        invalid = []

        for file in self.install_path.rglob("*.md"):
            try:
                content = file.read_text()
                rel_path = str(file.relative_to(self.install_path))

                if not content.strip():
                    empty.append(rel_path)
                elif len(content) < 10:
                    invalid.append({"file": rel_path, "reason": "Content too short"})

            except Exception as e:
                invalid.append({"file": str(file.name), "reason": str(e)})

        if empty or invalid:
            check.status = CheckStatus.FAILED
            check.message = f"{len(empty)} empty, {len(invalid)} invalid files"
            check.details = {"empty_files": empty, "invalid_files": invalid}

        self.checks.append(check)

    def _check_encoding(self) -> None:
        """Check files use valid UTF-8 encoding."""
        check = VerificationCheck(
            name="file_encoding",
            description="Files use UTF-8 encoding",
            severity=CheckSeverity.ERROR,
            status=CheckStatus.PASSED,
            message=None,
            details={"invalid_encoding": []}
        )

        invalid = []
        for file in self.install_path.rglob("*"):
            if file.is_file() and file.suffix in (".md", ".txt", ".yaml", ".yml"):
                try:
                    file.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    invalid.append(str(file.relative_to(self.install_path)))

        if invalid:
            check.status = CheckStatus.FAILED
            check.message = f"{len(invalid)} file(s) with encoding issues"
            check.details = {"invalid_encoding": invalid}

        self.checks.append(check)

    def _check_cross_references(self) -> None:
        """Check internal links resolve."""
        check = VerificationCheck(
            name="cross_references",
            description="Internal links resolve correctly",
            severity=CheckSeverity.WARNING,
            status=CheckStatus.PASSED,
            message=None,
            details={"broken_links": []}
        )

        broken = []
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

        for file in self.install_path.rglob("*.md"):
            try:
                content = file.read_text()
                for match in link_pattern.finditer(content):
                    link_text, link_target = match.groups()

                    # Skip external links
                    if link_target.startswith(("http://", "https://", "#")):
                        continue

                    # Check if target exists
                    target_path = file.parent / link_target
                    if not target_path.exists():
                        broken.append({
                            "source": str(file.relative_to(self.install_path)),
                            "target": link_target
                        })

            except Exception:
                pass

        if broken:
            check.status = CheckStatus.FAILED
            check.message = f"{len(broken)} broken link(s)"
            check.details = {"broken_links": broken}

        self.checks.append(check)

    def _check_token_budget(self) -> None:
        """Check token budget compliance."""
        check = VerificationCheck(
            name="token_budget",
            description="Within token budget limits",
            severity=CheckSeverity.WARNING,
            status=CheckStatus.PASSED,
            message=None,
            details={}
        )

        skill_md = self.install_path / "SKILL.md"
        refs_dir = self.install_path / "references"

        skill_tokens = 0
        refs_tokens = 0

        if skill_md.exists():
            content = skill_md.read_text()
            skill_tokens = len(content) // 4  # Approximate

        if refs_dir.exists():
            for file in refs_dir.rglob("*.md"):
                content = file.read_text()
                refs_tokens += len(content) // 4

        check.details = {
            "skill_md_tokens": skill_tokens,
            "references_tokens": refs_tokens,
            "skill_md_limit": 5000,
            "references_limit": 10000
        }

        if skill_tokens > 5000:
            check.status = CheckStatus.FAILED
            check.message = f"SKILL.md exceeds 5000 tokens ({skill_tokens})"
        elif refs_tokens > 10000:
            check.status = CheckStatus.FAILED
            check.message = f"References exceed 10000 tokens ({refs_tokens})"

        self.checks.append(check)

    def _check_naming_conventions(self) -> None:
        """Check naming conventions."""
        check = VerificationCheck(
            name="naming_conventions",
            description="Follows naming conventions",
            severity=CheckSeverity.WARNING,
            status=CheckStatus.PASSED,
            message=None,
            details={}
        )

        issues = []

        # Check skill name
        name_pattern = re.compile(r'^[a-z][a-z0-9-]*$')
        if not name_pattern.match(self.skill_name):
            issues.append(f"Skill name '{self.skill_name}' should be hyphen-case")

        if len(self.skill_name) > 64:
            issues.append(f"Skill name exceeds 64 characters")

        # Check file names
        for file in self.install_path.rglob("*"):
            if file.is_file():
                filename = file.name
                if " " in filename:
                    issues.append(f"File '{filename}' contains spaces")
                if any(c.isupper() for c in filename):
                    issues.append(f"File '{filename}' should be lowercase")

        if issues:
            check.status = CheckStatus.FAILED
            check.message = f"{len(issues)} naming issue(s)"
            check.details = {"issues": issues}

        self.checks.append(check)
```

## Result Formatter

```python
class VerificationResultFormatter:
    """Format verification results for display."""

    def format(self, result: VerificationResult) -> str:
        """Format verification result."""
        lines = []

        # Header
        status_icon = "✓" if result.passed else "✗"
        status_text = "PASSED" if result.passed else "FAILED"

        lines.append("")
        lines.append("═" * 60)
        lines.append(f"  {status_icon} INSTALLATION VERIFICATION: {status_text}")
        lines.append("═" * 60)
        lines.append("")

        # Summary
        lines.append(f"  Skill: {result.skill_name}")
        lines.append(f"  Path:  {result.install_path}")
        lines.append("")

        # Check results
        for check in result.checks:
            icon = self._status_icon(check.status)
            severity = check.severity.value.upper()
            lines.append(f"  {icon} [{severity}] {check.description}")
            if check.message:
                lines.append(f"       {check.message}")

        lines.append("")

        # Summary counts
        lines.append("─" * 60)
        passed = sum(1 for c in result.checks if c.status == CheckStatus.PASSED)
        total = len(result.checks)
        lines.append(f"  Checks: {passed}/{total} passed")

        if result.critical_failures:
            lines.append(f"  ✗ {result.critical_failures} critical failure(s)")
        if result.errors:
            lines.append(f"  ✗ {result.errors} error(s)")
        if result.warnings:
            lines.append(f"  ⚠ {result.warnings} warning(s)")

        lines.append("═" * 60)
        lines.append("")

        return "\n".join(lines)

    def _status_icon(self, status: CheckStatus) -> str:
        """Get icon for status."""
        icons = {
            CheckStatus.PASSED: "✓",
            CheckStatus.FAILED: "✗",
            CheckStatus.SKIPPED: "○"
        }
        return icons.get(status, "?")
```

## Integration

```python
def verify_installation(install_path: Path) -> bool:
    """Verify skill installation and display results."""
    verifier = InstallationVerifier(install_path)
    result = verifier.verify()

    formatter = VerificationResultFormatter()
    print(formatter.format(result))

    return result.passed
```

## Display Format

```
═══════════════════════════════════════════════════════════
  ✓ INSTALLATION VERIFICATION: PASSED
═══════════════════════════════════════════════════════════

  Skill: api-doc-generator
  Path:  ~/.claude/skills/api-doc-generator

  ✓ [CRITICAL] Installation directory exists
  ✓ [CRITICAL] Required file exists: SKILL.md
  ✓ [CRITICAL] SKILL.md has valid YAML frontmatter
  ✓ [CRITICAL] All files are readable
  ✓ [ERROR] Files have valid content
  ✓ [ERROR] Files use UTF-8 encoding
  ✓ [WARNING] Internal links resolve correctly
  ✓ [WARNING] Within token budget limits
  ✓ [WARNING] Follows naming conventions

─────────────────────────────────────────────────────────
  Checks: 9/9 passed
═══════════════════════════════════════════════════════════
```
