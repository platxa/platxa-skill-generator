---
name: platxa-testing
description: Automated testing patterns for Platxa platform using pytest, Vitest, and E2E frameworks. Run tests, generate fixtures, configure CI/CD pipelines.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - automation
    - testing
    - pytest
    - vitest
    - e2e
---

# Platxa Testing

Automation skill for testing patterns in the Platxa platform.

## Overview

| Framework | Language | Use Case |
|-----------|----------|----------|
| **pytest** | Python | Unit, integration, E2E tests |
| **Vitest** | TypeScript | Unit tests, async patterns |
| **Playwright** | TypeScript | Visual regression, browser E2E |
| **Kind** | Kubernetes | E2E cluster testing |

## Core Philosophy

**NO MOCKS OR SIMULATIONS** - All tests use real operations:
- Real file system operations (no mock filesystem)
- Actual script execution via subprocess
- Real Kubernetes clusters for E2E
- Real database transactions for Odoo tests

## Prerequisites

```bash
# Python testing
pip install pytest pytest-timeout tiktoken pyyaml

# TypeScript testing
pnpm add -D vitest @types/node

# E2E testing
brew install kind kubectl  # macOS
# or apt install kind kubectl  # Linux
```

## Pytest Patterns

### Configuration (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers -ra
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (service interactions)
    e2e: End-to-end tests (full lifecycle)
    slow: Tests that take > 30 seconds
timeout = 300
log_cli = true
log_cli_level = INFO
filterwarnings =
    ignore::DeprecationWarning
```

### Core Fixtures (conftest.py)

```python
import pytest
import tempfile
import subprocess
import os
from pathlib import Path
from typing import Generator, Callable

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Creates isolated temporary directory."""
    with tempfile.TemporaryDirectory(prefix="test_") as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def run_script(scripts_dir: Path) -> Callable[[str, Path], subprocess.CompletedProcess]:
    """Returns function to execute scripts."""
    def _run(script_name: str, target: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(scripts_dir / script_name), str(target)],
            capture_output=True, text=True,
            env={**os.environ, "TERM": "dumb"},
        )
    return _run
```

### Test Organization

```python
@pytest.mark.unit
class TestFeatureValidation:
    """Tests for feature validation logic."""

    def test_valid_input_passes(self, temp_dir):
        """Feature #1: Valid input is accepted."""
        test_file = temp_dir / "valid.txt"
        test_file.write_text("content")
        result = validate(test_file)
        assert result.success is True

    def test_invalid_input_fails(self, temp_dir):
        """Feature #2: Invalid input is rejected."""
        test_file = temp_dir / "invalid.txt"
        test_file.write_text("")
        result = validate(test_file)
        assert result.success is False
```

## Vitest Patterns

### Configuration

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage"
  }
}
```

### Test Structure

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

describe('FeatureName', () => {
  let testDir: string;

  beforeEach(() => {
    testDir = fs.mkdtempSync(path.join(os.tmpdir(), 'test-'));
  });

  afterEach(() => {
    fs.rmSync(testDir, { recursive: true, force: true });
  });

  it('handles valid input correctly', () => {
    fs.writeFileSync(path.join(testDir, 'input.json'), '{"key": "value"}');
    const result = processFile(path.join(testDir, 'input.json'));
    expect(result.success).toBe(true);
  });
});
```

## E2E Testing

### Kind Cluster Setup

```bash
#!/bin/bash
cat <<EOF | kind create cluster --name platxa-test --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080
        hostPort: 8080
        protocol: TCP
EOF
```

### Instance Lifecycle Test

```python
@pytest.mark.e2e
class TestInstanceLifecycle:
    """E2E tests for complete instance lifecycle."""

    def test_complete_lifecycle(self, test_instance):
        instance = create_instance("e2e-test")
        assert instance.status == "draft"

        instance.provision()
        assert instance.status == "active"
        assert namespace_exists(instance.namespace)

        instance.suspend()
        assert instance.status == "suspended"

        instance.resume()
        assert instance.status == "active"

        instance.delete()
        assert instance.status == "deleted"
```

### Playwright Visual Testing

```typescript
import { test, expect } from '@playwright/test';

test('button matches snapshot', async ({ page }) => {
  await page.goto('/components/button');
  await expect(page.locator('button')).toHaveScreenshot('button.png', {
    maxDiffPixels: 100, threshold: 0.2, animations: 'disabled'
  });
});
```

## Workflow

### Step 1: Identify Test Type

| Scenario | Framework | Markers |
|----------|-----------|---------|
| Business logic | pytest | `@pytest.mark.unit` |
| API integration | pytest | `@pytest.mark.integration` |
| Full lifecycle | pytest + Kind | `@pytest.mark.e2e` |
| TypeScript utils | vitest | describe/it |
| Visual regression | Playwright | test() |

### Step 2: Create Test Structure

```bash
# Python project
tests/
├── conftest.py          # Shared fixtures
├── test_feature_a.py    # Feature tests
└── test_feature_b.py

# TypeScript project
src/utils/__tests__/feature.test.ts
tests/e2e/visual.spec.ts
```

### Step 3: Write Tests

1. Create fixtures for isolation
2. Organize tests by feature in classes
3. Add docstrings with feature numbers
4. Use markers for categorization
5. Verify cleanup in afterEach/teardown

### Step 4: Run Tests

```bash
# pytest
pytest tests/ -v                    # All tests
pytest tests/ -m unit               # Unit only
pytest tests/ -m "not slow"         # Skip slow

# vitest
pnpm test                           # Watch mode
pnpm test:run                       # Single run
```

## CI/CD Integration

```yaml
name: Tests
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest pytest-timeout
      - run: pytest tests/ -m "unit" -v

  e2e-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: helm/kind-action@v1
      - run: pytest tests/ -m "e2e" -v --timeout=600
```

## Examples

### Example 1: Pytest Unit Test

**User**: "Write tests for a validation function"

```python
@pytest.mark.unit
class TestValidation:
    def test_valid_yaml_passes(self, temp_dir):
        """Feature #1: Valid YAML files are accepted."""
        yaml_file = temp_dir / "valid.yaml"
        yaml_file.write_text("name: test\nversion: 1.0")
        result = validate_yaml(yaml_file)
        assert result.valid is True

    def test_invalid_yaml_fails(self, temp_dir):
        """Feature #2: Invalid YAML files are rejected."""
        yaml_file = temp_dir / "invalid.yaml"
        yaml_file.write_text("name: test\n  bad indent")
        result = validate_yaml(yaml_file)
        assert result.valid is False
```

### Example 2: Vitest Async Test

**User**: "Test async file operations"

```typescript
describe('fileOps', () => {
  let testDir: string;

  beforeEach(() => {
    testDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fileops-'));
  });

  afterEach(() => {
    fs.rmSync(testDir, { recursive: true, force: true });
  });

  it('reads JSON file correctly', async () => {
    fs.writeFileSync(path.join(testDir, 'data.json'), '{"key": "value"}');
    const result = await readJsonFile(path.join(testDir, 'data.json'));
    expect(result).toEqual({ key: 'value' });
  });
});
```

### Example 3: E2E Kind Cluster Test

**User**: "Test Kubernetes deployment"

```python
@pytest.mark.e2e
class TestKubernetesDeployment:
    @classmethod
    def setup_class(cls):
        config.load_kube_config(context="kind-platxa-test")
        cls.apps_v1 = client.AppsV1Api()

    def test_deployment_creates_pods(self):
        deploy = self.apps_v1.read_namespaced_deployment("my-app", "default")
        assert deploy.spec.replicas == 2
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Tests hang | Missing timeout | Add `timeout = 300` in pytest.ini |
| Flaky tests | Shared state | Use temp directories, cleanup |
| Import errors | Missing conftest | Add `__init__.py` to tests/ |
| K8s connection | Wrong context | `kubectl config use-context` |
| Permission denied | Script not executable | `chmod +x scripts/*.sh` |

## Output Checklist

After writing tests:

- [ ] Test file follows naming convention (test_*.py, *.test.ts)
- [ ] Tests use real operations (no mocks)
- [ ] Fixtures provide proper isolation
- [ ] Markers categorize test types
- [ ] Docstrings explain test purpose
- [ ] Cleanup handles all created resources
- [ ] CI/CD pipeline runs tests
- [ ] Tests pass locally before push

## Related Resources

See `references/` for detailed patterns: pytest-patterns.md, vitest-patterns.md, e2e-patterns.md
