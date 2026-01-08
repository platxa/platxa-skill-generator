# Post-Install Test Runner

Run basic invocation tests after skill installation.

## Test Types

| Test | Purpose | Required |
|------|---------|----------|
| Load test | Skill loads without errors | Yes |
| Parse test | SKILL.md parses correctly | Yes |
| Reference test | References accessible | Yes |
| Invocation test | Basic command works | Optional |

## Test Model

```python
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from datetime import datetime

class TestType(Enum):
    LOAD = "load"
    PARSE = "parse"
    REFERENCE = "reference"
    INVOCATION = "invocation"

class TestResult(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class TestCase:
    name: str
    test_type: TestType
    description: str
    required: bool

@dataclass
class TestExecution:
    test_case: TestCase
    result: TestResult
    duration_ms: int
    message: str | None
    details: dict | None

@dataclass
class TestSuiteResult:
    skill_name: str
    install_path: Path
    passed: bool
    executions: list[TestExecution]
    total_tests: int
    passed_count: int
    failed_count: int
    skipped_count: int
    total_duration_ms: int
    timestamp: datetime
```

## Test Runner

```python
import time
import yaml
from pathlib import Path

class PostInstallTestRunner:
    """Run post-installation tests on skill."""

    def __init__(self, install_path: Path):
        self.install_path = install_path
        self.skill_name = install_path.name

    def run_all(self) -> TestSuiteResult:
        """Run all post-install tests."""
        start_time = time.time()
        executions = []

        # Define test suite
        tests = [
            TestCase("skill_loads", TestType.LOAD, "Skill directory loads", True),
            TestCase("skill_md_parses", TestType.PARSE, "SKILL.md parses correctly", True),
            TestCase("frontmatter_valid", TestType.PARSE, "Frontmatter is valid", True),
            TestCase("references_accessible", TestType.REFERENCE, "References are accessible", True),
            TestCase("no_syntax_errors", TestType.PARSE, "No syntax errors in content", True),
            TestCase("basic_invocation", TestType.INVOCATION, "Basic invocation works", False),
        ]

        # Run each test
        for test in tests:
            execution = self._run_test(test)
            executions.append(execution)

        # Calculate results
        total_duration = int((time.time() - start_time) * 1000)
        passed = sum(1 for e in executions if e.result == TestResult.PASSED)
        failed = sum(1 for e in executions if e.result == TestResult.FAILED)
        skipped = sum(1 for e in executions if e.result == TestResult.SKIPPED)

        # Check if all required tests passed
        all_passed = all(
            e.result == TestResult.PASSED
            for e in executions
            if e.test_case.required
        )

        return TestSuiteResult(
            skill_name=self.skill_name,
            install_path=self.install_path,
            passed=all_passed,
            executions=executions,
            total_tests=len(tests),
            passed_count=passed,
            failed_count=failed,
            skipped_count=skipped,
            total_duration_ms=total_duration,
            timestamp=datetime.now()
        )

    def _run_test(self, test: TestCase) -> TestExecution:
        """Run a single test."""
        start_time = time.time()

        try:
            # Dispatch to test method
            test_methods = {
                "skill_loads": self._test_skill_loads,
                "skill_md_parses": self._test_skill_md_parses,
                "frontmatter_valid": self._test_frontmatter_valid,
                "references_accessible": self._test_references_accessible,
                "no_syntax_errors": self._test_no_syntax_errors,
                "basic_invocation": self._test_basic_invocation,
            }

            method = test_methods.get(test.name)
            if method:
                result, message, details = method()
            else:
                result = TestResult.SKIPPED
                message = "Test not implemented"
                details = None

        except Exception as e:
            result = TestResult.ERROR
            message = str(e)
            details = {"exception": type(e).__name__}

        duration = int((time.time() - start_time) * 1000)

        return TestExecution(
            test_case=test,
            result=result,
            duration_ms=duration,
            message=message,
            details=details
        )

    def _test_skill_loads(self) -> tuple[TestResult, str | None, dict | None]:
        """Test that skill directory loads."""
        if not self.install_path.exists():
            return TestResult.FAILED, "Directory not found", None

        if not self.install_path.is_dir():
            return TestResult.FAILED, "Path is not a directory", None

        files = list(self.install_path.iterdir())
        return TestResult.PASSED, None, {"file_count": len(files)}

    def _test_skill_md_parses(self) -> tuple[TestResult, str | None, dict | None]:
        """Test that SKILL.md parses correctly."""
        skill_md = self.install_path / "SKILL.md"

        if not skill_md.exists():
            return TestResult.FAILED, "SKILL.md not found", None

        try:
            content = skill_md.read_text()
            if not content.strip():
                return TestResult.FAILED, "SKILL.md is empty", None

            return TestResult.PASSED, None, {"size": len(content)}

        except Exception as e:
            return TestResult.FAILED, f"Parse error: {e}", None

    def _test_frontmatter_valid(self) -> tuple[TestResult, str | None, dict | None]:
        """Test that frontmatter is valid YAML."""
        skill_md = self.install_path / "SKILL.md"

        if not skill_md.exists():
            return TestResult.SKIPPED, "SKILL.md not found", None

        content = skill_md.read_text()

        if not content.startswith("---"):
            return TestResult.FAILED, "Missing frontmatter", None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return TestResult.FAILED, "Invalid frontmatter structure", None

        try:
            data = yaml.safe_load(parts[1])
            if not data:
                return TestResult.FAILED, "Empty frontmatter", None

            required = ["name", "description"]
            missing = [f for f in required if f not in data]
            if missing:
                return TestResult.FAILED, f"Missing fields: {missing}", None

            return TestResult.PASSED, None, {"fields": list(data.keys())}

        except yaml.YAMLError as e:
            return TestResult.FAILED, f"YAML error: {e}", None

    def _test_references_accessible(self) -> tuple[TestResult, str | None, dict | None]:
        """Test that references directory is accessible."""
        refs_dir = self.install_path / "references"

        if not refs_dir.exists():
            # References are optional
            return TestResult.PASSED, "No references directory", {"has_refs": False}

        try:
            ref_files = list(refs_dir.rglob("*.md"))

            # Try to read each file
            for ref_file in ref_files:
                ref_file.read_text()

            return TestResult.PASSED, None, {
                "has_refs": True,
                "ref_count": len(ref_files)
            }

        except Exception as e:
            return TestResult.FAILED, f"Reference access error: {e}", None

    def _test_no_syntax_errors(self) -> tuple[TestResult, str | None, dict | None]:
        """Test for obvious syntax errors in content."""
        errors = []

        for md_file in self.install_path.rglob("*.md"):
            try:
                content = md_file.read_text()
                rel_path = md_file.relative_to(self.install_path)

                # Check for unclosed code blocks
                code_block_count = content.count("```")
                if code_block_count % 2 != 0:
                    errors.append(f"{rel_path}: Unclosed code block")

                # Check for malformed links
                import re
                malformed = re.findall(r'\[[^\]]*\]\([^)]*$', content, re.MULTILINE)
                if malformed:
                    errors.append(f"{rel_path}: Malformed link")

            except Exception as e:
                errors.append(f"{md_file.name}: {e}")

        if errors:
            return TestResult.FAILED, f"{len(errors)} syntax error(s)", {"errors": errors}

        return TestResult.PASSED, None, None

    def _test_basic_invocation(self) -> tuple[TestResult, str | None, dict | None]:
        """Test basic skill invocation simulation."""
        # This is a simulation - actual invocation would require Claude Code
        skill_md = self.install_path / "SKILL.md"

        if not skill_md.exists():
            return TestResult.SKIPPED, "Cannot test without SKILL.md", None

        try:
            content = skill_md.read_text()

            # Simulate parsing that Claude Code would do
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2]

                # Check minimum viable skill
                if frontmatter and "name" in frontmatter and len(body.strip()) > 0:
                    return TestResult.PASSED, "Invocation simulation passed", {
                        "skill_name": frontmatter["name"],
                        "body_length": len(body)
                    }

            return TestResult.FAILED, "Skill structure invalid", None

        except Exception as e:
            return TestResult.FAILED, f"Invocation test error: {e}", None
```

## Result Formatter

```python
class TestResultFormatter:
    """Format test results for display."""

    def format(self, result: TestSuiteResult) -> str:
        """Format test suite result."""
        lines = []

        # Header
        icon = "✓" if result.passed else "✗"
        status = "ALL TESTS PASSED" if result.passed else "TESTS FAILED"

        lines.append("")
        lines.append("═" * 60)
        lines.append(f"  {icon} POST-INSTALL TESTS: {status}")
        lines.append("═" * 60)
        lines.append("")

        # Test results
        for exec in result.executions:
            icon = self._result_icon(exec.result)
            required = "*" if exec.test_case.required else " "
            duration = f"({exec.duration_ms}ms)"

            lines.append(f"  {icon}{required} {exec.test_case.description} {duration}")
            if exec.message:
                lines.append(f"       {exec.message}")

        lines.append("")

        # Summary
        lines.append("─" * 60)
        lines.append(f"  Results: {result.passed_count} passed, "
                    f"{result.failed_count} failed, "
                    f"{result.skipped_count} skipped")
        lines.append(f"  Duration: {result.total_duration_ms}ms")
        lines.append("")
        lines.append("  * = required test")
        lines.append("═" * 60)
        lines.append("")

        return "\n".join(lines)

    def _result_icon(self, result: TestResult) -> str:
        """Get icon for result."""
        icons = {
            TestResult.PASSED: "✓",
            TestResult.FAILED: "✗",
            TestResult.SKIPPED: "○",
            TestResult.ERROR: "!",
        }
        return icons.get(result, "?")
```

## Quick Test Mode

```python
def quick_test(install_path: Path) -> bool:
    """Run quick test and return pass/fail."""
    runner = PostInstallTestRunner(install_path)
    result = runner.run_all()
    return result.passed

def verbose_test(install_path: Path) -> TestSuiteResult:
    """Run tests and display results."""
    runner = PostInstallTestRunner(install_path)
    result = runner.run_all()

    formatter = TestResultFormatter()
    print(formatter.format(result))

    return result
```

## Integration

```python
def run_post_install_tests(install_path: Path, verbose: bool = True) -> bool:
    """Run post-install tests after installation."""
    print()
    print("  Running post-install tests...")
    print()

    if verbose:
        result = verbose_test(install_path)
        return result.passed
    else:
        passed = quick_test(install_path)
        if passed:
            print("  ✓ All tests passed")
        else:
            print("  ✗ Some tests failed")
        return passed
```

## Display Format

```
═══════════════════════════════════════════════════════════
  ✓ POST-INSTALL TESTS: ALL TESTS PASSED
═══════════════════════════════════════════════════════════

  ✓* Skill directory loads (2ms)
  ✓* SKILL.md parses correctly (1ms)
  ✓* Frontmatter is valid (3ms)
  ✓* References are accessible (5ms)
  ✓* No syntax errors in content (4ms)
  ✓  Basic invocation works (2ms)

─────────────────────────────────────────────────────────
  Results: 6 passed, 0 failed, 0 skipped
  Duration: 17ms

  * = required test
═══════════════════════════════════════════════════════════
```
