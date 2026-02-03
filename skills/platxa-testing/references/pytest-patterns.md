# Pytest Patterns Reference

Configuration and fixture patterns for pytest in Platxa.

## Configuration Files

### pytest.ini

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
minversion = 7.0
timeout = 300
log_cli = true
log_cli_level = INFO
console_output_style = progress
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers -ra"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests (> 30s)",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

## Fixture Patterns

### Temporary Directory

```python
@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Creates isolated temporary directory with automatic cleanup."""
    with tempfile.TemporaryDirectory(prefix="test_") as tmpdir:
        yield Path(tmpdir)
```

### Script Runner

```python
@pytest.fixture
def run_script(scripts_dir: Path) -> Callable[[str, Path], subprocess.CompletedProcess]:
    """Execute shell scripts with captured output."""
    def _run(script_name: str, target: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(scripts_dir / script_name), str(target)],
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},  # Disable colors
        )
    return _run
```

### File Factory

```python
@pytest.fixture
def create_file() -> Callable[[Path, str, str], Path]:
    """Factory for creating test files."""
    def _create(directory: Path, name: str, content: str) -> Path:
        file_path = directory / name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path
    return _create
```

### Executable Script Creator

```python
@pytest.fixture
def create_script() -> Callable[[Path, str, str], Path]:
    """Create executable shell script."""
    def _create(directory: Path, name: str, content: str) -> Path:
        script = directory / name
        script.write_text(content)
        script.chmod(0o755)
        return script
    return _create
```

## Test Organization

### Class-Based Grouping

```python
@pytest.mark.unit
class TestFeatureValidation:
    """Tests for feature validation logic."""

    def test_valid_case(self, temp_dir):
        """Feature #1: Valid input accepted."""
        pass

    def test_invalid_case(self, temp_dir):
        """Feature #2: Invalid input rejected."""
        pass
```

### Parametric Testing

```python
@pytest.mark.parametrize("input,expected", [
    ("valid", True),
    ("invalid", False),
    ("edge", True),
])
def test_validation(input, expected):
    result = validate(input)
    assert result == expected
```

## Subprocess Testing

### Basic Execution

```python
result = subprocess.run(
    [str(script_path), str(arg)],
    capture_output=True,
    text=True,
    env={**os.environ, "TERM": "dumb"},
)
assert result.returncode == 0
assert "SUCCESS" in result.stdout
```

### JSON Output Validation

```python
result = subprocess.run(
    [script, "--json", str(target)],
    capture_output=True,
    text=True,
)
data = json.loads(result.stdout)
assert data["passed"] is True
assert "tokens" in data
```

## Odoo TransactionCase

### Base Setup

```python
from odoo.tests import TransactionCase, tagged

@tagged('unit', 'post_install', '-at_install')
class TestInstanceModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_partner = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test@example.com',
        })

    def test_create_instance(self):
        instance = self.env['instance.instance'].create({
            'display_name': 'Test Instance',
            'partner_id': self.test_partner.id,
        })
        self.assertEqual(instance.status, 'draft')
```

## Marker Usage

```bash
# Run specific markers
pytest tests/ -m unit
pytest tests/ -m "integration and not slow"
pytest tests/ -m "not e2e"

# Run with timeout
pytest tests/ --timeout=60 -m unit
```
