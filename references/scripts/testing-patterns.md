# Script Testing Patterns

Patterns for testing skill scripts with sample inputs.

## Test Structure

```
skill-name/
├── scripts/
│   ├── generate.sh
│   └── validate.sh
└── tests/
    ├── fixtures/
    │   ├── input-simple.txt
    │   ├── input-complex.txt
    │   └── expected-output.md
    ├── test_generate.sh
    └── test_validate.sh
```

## Bash Testing Pattern

### Test Script Template

```bash
#!/bin/bash
# test_generate.sh - Tests for generate.sh
#
# Usage: test_generate.sh [--verbose]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Test utilities
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-}"

    ((TESTS_RUN++))

    if [[ "$expected" == "$actual" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
        return 1
    fi
}

assert_exit_code() {
    local expected="$1"
    local actual="$2"
    local message="${3:-Exit code check}"

    assert_equals "$expected" "$actual" "$message"
}

assert_file_exists() {
    local filepath="$1"
    local message="${2:-File exists: $filepath}"

    ((TESTS_RUN++))

    if [[ -f "$filepath" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        return 1
    fi
}

assert_output_contains() {
    local output="$1"
    local expected="$2"
    local message="${3:-Output contains expected text}"

    ((TESTS_RUN++))

    if echo "$output" | grep -q "$expected"; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo "  Expected to contain: $expected"
        return 1
    fi
}

# Setup and teardown
setup() {
    TEST_DIR=$(mktemp -d)
    export TEST_DIR
}

teardown() {
    rm -rf "$TEST_DIR"
}

# Test cases
test_help_flag() {
    echo "Test: --help flag"
    local output
    output=$("$PROJECT_DIR/scripts/generate.sh" --help 2>&1) || true
    assert_output_contains "$output" "Usage:" "Help shows usage"
    assert_output_contains "$output" "--help" "Help shows --help option"
}

test_simple_input() {
    echo "Test: Simple input processing"
    setup

    cp "$FIXTURES_DIR/input-simple.txt" "$TEST_DIR/"

    local output
    local exit_code=0
    output=$("$PROJECT_DIR/scripts/generate.sh" "$TEST_DIR/input-simple.txt" 2>&1) || exit_code=$?

    assert_exit_code 0 "$exit_code" "Exit code is 0"
    assert_output_contains "$output" "success" "Output indicates success"

    teardown
}

test_missing_input() {
    echo "Test: Missing input file"

    local exit_code=0
    "$PROJECT_DIR/scripts/generate.sh" "/nonexistent/file.txt" 2>/dev/null || exit_code=$?

    assert_equals 1 "$exit_code" "Exits with error for missing file"
}

test_dry_run() {
    echo "Test: Dry run mode"
    setup

    cp "$FIXTURES_DIR/input-simple.txt" "$TEST_DIR/"

    local output
    output=$("$PROJECT_DIR/scripts/generate.sh" --dry-run "$TEST_DIR/input-simple.txt" 2>&1)

    assert_output_contains "$output" "DRY RUN" "Shows dry run indicator"

    # Verify no files were created
    local file_count
    file_count=$(find "$TEST_DIR" -type f -name "*.md" | wc -l)
    assert_equals 0 "$file_count" "No output files created in dry run"

    teardown
}

# Run all tests
run_tests() {
    echo "Running tests for generate.sh"
    echo "=============================="
    echo ""

    test_help_flag
    test_simple_input
    test_missing_input
    test_dry_run

    echo ""
    echo "=============================="
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"

    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "${RED}$TESTS_FAILED test(s) failed${NC}"
        exit 1
    else
        echo -e "${GREEN}All tests passed${NC}"
        exit 0
    fi
}

run_tests
```

## Python Testing Pattern

### pytest Test Template

```python
#!/usr/bin/env python3
"""Tests for generate.py script."""

import subprocess
import tempfile
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
SCRIPT_PATH = PROJECT_DIR / "scripts" / "generate.py"


class TestHelpFlag:
    """Tests for --help flag."""

    def test_help_shows_usage(self):
        """--help should show usage information."""
        result = subprocess.run(
            ["python3", str(SCRIPT_PATH), "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()

    def test_help_shows_options(self):
        """--help should list all options."""
        result = subprocess.run(
            ["python3", str(SCRIPT_PATH), "--help"],
            capture_output=True,
            text=True
        )
        assert "--verbose" in result.stdout
        assert "--dry-run" in result.stdout


class TestSimpleInput:
    """Tests for simple input processing."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def simple_input(self, temp_dir):
        """Create simple input file."""
        input_file = temp_dir / "input.txt"
        input_file.write_text("Sample input content")
        return input_file

    def test_processes_simple_input(self, simple_input, temp_dir):
        """Should process simple input successfully."""
        output_file = temp_dir / "output.md"

        result = subprocess.run(
            [
                "python3", str(SCRIPT_PATH),
                str(simple_input),
                "-o", str(output_file)
            ],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert output_file.exists()

    def test_output_content(self, simple_input, temp_dir):
        """Output should contain expected content."""
        output_file = temp_dir / "output.md"

        subprocess.run(
            [
                "python3", str(SCRIPT_PATH),
                str(simple_input),
                "-o", str(output_file)
            ],
            capture_output=True
        )

        content = output_file.read_text()
        assert "Sample" in content or len(content) > 0


class TestErrorHandling:
    """Tests for error handling."""

    def test_missing_file_error(self):
        """Should exit with error for missing input file."""
        result = subprocess.run(
            ["python3", str(SCRIPT_PATH), "/nonexistent/file.txt"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_invalid_option_error(self):
        """Should exit with error for invalid option."""
        result = subprocess.run(
            ["python3", str(SCRIPT_PATH), "--invalid-option"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0


class TestDryRun:
    """Tests for --dry-run mode."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_dry_run_no_files_created(self, temp_dir):
        """--dry-run should not create output files."""
        input_file = temp_dir / "input.txt"
        input_file.write_text("test content")
        output_file = temp_dir / "output.md"

        subprocess.run(
            [
                "python3", str(SCRIPT_PATH),
                "--dry-run",
                str(input_file),
                "-o", str(output_file)
            ],
            capture_output=True
        )

        assert not output_file.exists()

    def test_dry_run_shows_preview(self, temp_dir):
        """--dry-run should show what would be done."""
        input_file = temp_dir / "input.txt"
        input_file.write_text("test content")

        result = subprocess.run(
            [
                "python3", str(SCRIPT_PATH),
                "--dry-run",
                str(input_file)
            ],
            capture_output=True,
            text=True
        )

        assert "dry run" in result.stdout.lower() or "would" in result.stdout.lower()
```

## Test Fixtures

### fixtures/input-simple.txt

```
Simple input for testing.
Contains basic content.
```

### fixtures/input-complex.txt

```yaml
# Complex input with multiple sections
name: test-skill
type: builder

sections:
  - name: overview
    content: |
      This is a test overview.
  - name: workflow
    content: |
      Step 1: Do this
      Step 2: Do that
```

### fixtures/expected-output.md

```markdown
# Test Output

Generated from input-simple.txt

## Content

Simple input for testing.
Contains basic content.
```

## Running Tests

### Bash

```bash
# Run all tests
./tests/test_generate.sh

# Run with verbose output
./tests/test_generate.sh --verbose

# Run specific test (if supported)
./tests/test_generate.sh test_simple_input
```

### Python

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_generate.py

# Run specific test
pytest tests/test_generate.py::TestSimpleInput::test_processes_simple_input
```

## CI Integration

```yaml
# .github/workflows/test-scripts.yml
name: Test Scripts

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Test bash scripts
        run: |
          chmod +x scripts/*.sh tests/*.sh
          ./tests/test_generate.sh

      - name: Test python scripts
        run: |
          pip install pytest
          pytest tests/ -v
```
