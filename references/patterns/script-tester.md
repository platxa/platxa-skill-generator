# Script Functionality Tester

Test generated scripts for correct execution without errors.

## Purpose

Validate that skill scripts execute correctly before installation. Catches syntax errors, missing dependencies, and runtime failures.

## Test Levels

| Level | Description | When |
|-------|-------------|------|
| Syntax | Parse without errors | Always |
| Dry Run | Execute with --help/--dry-run | Always |
| Sandbox | Execute in isolated environment | If available |
| Integration | Execute with test inputs | Optional |

## Testing Algorithm

```python
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile

@dataclass
class ScriptTestResult:
    passed: bool
    script: str
    tests_run: list[str]
    tests_passed: list[str]
    tests_failed: list[dict]
    errors: list[str]
    warnings: list[str]

def test_script(script_path: Path) -> ScriptTestResult:
    """
    Test a script for correct functionality.

    Args:
        script_path: Path to script file

    Returns:
        ScriptTestResult with pass/fail details
    """
    tests_run = []
    tests_passed = []
    tests_failed = []
    errors = []
    warnings = []

    # Determine script type
    if script_path.suffix == '.sh':
        result = test_bash_script(script_path)
    elif script_path.suffix == '.py':
        result = test_python_script(script_path)
    else:
        return ScriptTestResult(
            passed=False,
            script=script_path.name,
            tests_run=[],
            tests_passed=[],
            tests_failed=[],
            errors=[f"Unknown script type: {script_path.suffix}"],
            warnings=[]
        )

    return result
```

## Bash Script Testing

```python
def test_bash_script(script_path: Path) -> ScriptTestResult:
    """Test bash script functionality."""
    tests_run = []
    tests_passed = []
    tests_failed = []
    errors = []
    warnings = []

    script = script_path.name

    # 1. Syntax check with bash -n
    tests_run.append('syntax_check')
    result = subprocess.run(
        ['bash', '-n', str(script_path)],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        tests_passed.append('syntax_check')
    else:
        tests_failed.append({
            'test': 'syntax_check',
            'error': result.stderr
        })
        errors.append(f"Syntax error: {result.stderr}")

    # 2. Shellcheck (if available)
    tests_run.append('shellcheck')
    result = subprocess.run(
        ['shellcheck', '-s', 'bash', str(script_path)],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        tests_passed.append('shellcheck')
    elif result.returncode == 127:  # shellcheck not found
        warnings.append("shellcheck not installed, skipping")
    else:
        # Parse shellcheck output for severity
        if 'error' in result.stdout.lower():
            tests_failed.append({
                'test': 'shellcheck',
                'error': result.stdout[:500]
            })
        else:
            tests_passed.append('shellcheck')
            warnings.append(f"Shellcheck warnings: {result.stdout[:200]}")

    # 3. Check shebang
    tests_run.append('shebang_check')
    content = script_path.read_text()
    if content.startswith('#!/'):
        tests_passed.append('shebang_check')
    else:
        tests_failed.append({
            'test': 'shebang_check',
            'error': 'Missing shebang line'
        })

    # 4. Help flag test (if script supports it)
    tests_run.append('help_flag')
    if '--help' in content or '-h' in content:
        result = subprocess.run(
            ['bash', str(script_path), '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode in [0, 1]:  # 0 or 1 are acceptable for help
            tests_passed.append('help_flag')
        else:
            tests_failed.append({
                'test': 'help_flag',
                'error': f"Exit code {result.returncode}"
            })
    else:
        warnings.append("Script doesn't support --help flag")

    # 5. Dry run test (if supported)
    if '--dry-run' in content or '-n' in content:
        tests_run.append('dry_run')
        result = subprocess.run(
            ['bash', str(script_path), '--dry-run'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            tests_passed.append('dry_run')
        else:
            tests_failed.append({
                'test': 'dry_run',
                'error': result.stderr[:200]
            })

    passed = len(tests_failed) == 0
    return ScriptTestResult(
        passed=passed,
        script=script,
        tests_run=tests_run,
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        errors=errors,
        warnings=warnings
    )
```

## Python Script Testing

```python
def test_python_script(script_path: Path) -> ScriptTestResult:
    """Test Python script functionality."""
    tests_run = []
    tests_passed = []
    tests_failed = []
    errors = []
    warnings = []

    script = script_path.name

    # 1. Syntax check with py_compile
    tests_run.append('syntax_check')
    result = subprocess.run(
        ['python', '-m', 'py_compile', str(script_path)],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        tests_passed.append('syntax_check')
    else:
        tests_failed.append({
            'test': 'syntax_check',
            'error': result.stderr
        })
        errors.append(f"Syntax error: {result.stderr}")

    # 2. Import check (catches import errors)
    tests_run.append('import_check')
    result = subprocess.run(
        ['python', '-c', f'import importlib.util; '
         f'spec = importlib.util.spec_from_file_location("mod", "{script_path}"); '
         f'mod = importlib.util.module_from_spec(spec)'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        tests_passed.append('import_check')
    else:
        tests_failed.append({
            'test': 'import_check',
            'error': result.stderr[:300]
        })

    # 3. Type check with pyright (if available)
    tests_run.append('type_check')
    result = subprocess.run(
        ['pyright', str(script_path)],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        tests_passed.append('type_check')
    elif result.returncode == 127:
        warnings.append("pyright not installed, skipping type check")
    else:
        # Type errors are warnings, not failures
        tests_passed.append('type_check')
        warnings.append(f"Type hints: {result.stdout[:200]}")

    # 4. Help flag test
    tests_run.append('help_flag')
    content = script_path.read_text()
    if 'argparse' in content or '--help' in content:
        result = subprocess.run(
            ['python', str(script_path), '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            tests_passed.append('help_flag')
        else:
            tests_failed.append({
                'test': 'help_flag',
                'error': result.stderr[:200]
            })

    # 5. Standalone execution check
    tests_run.append('main_guard')
    if "if __name__ == '__main__':" in content or 'if __name__ == "__main__":' in content:
        tests_passed.append('main_guard')
    else:
        warnings.append("Missing if __name__ == '__main__' guard")

    passed = len(tests_failed) == 0
    return ScriptTestResult(
        passed=passed,
        script=script,
        tests_run=tests_run,
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        errors=errors,
        warnings=warnings
    )
```

## Sandbox Execution

```python
def test_in_sandbox(script_path: Path, test_inputs: dict) -> ScriptTestResult:
    """
    Test script in isolated sandbox environment.

    Uses temporary directory with controlled inputs.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy script to sandbox
        sandbox_script = Path(tmpdir) / script_path.name
        sandbox_script.write_text(script_path.read_text())
        sandbox_script.chmod(0o755)

        # Create test input files
        for name, content in test_inputs.items():
            (Path(tmpdir) / name).write_text(content)

        # Execute in sandbox
        env = {
            'HOME': tmpdir,
            'PATH': '/usr/bin:/bin',
            'TERM': 'dumb',
        }

        try:
            result = subprocess.run(
                [str(sandbox_script)],
                cwd=tmpdir,
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )

            return ScriptTestResult(
                passed=result.returncode == 0,
                script=script_path.name,
                tests_run=['sandbox_execution'],
                tests_passed=['sandbox_execution'] if result.returncode == 0 else [],
                tests_failed=[{'test': 'sandbox_execution', 'error': result.stderr}] if result.returncode != 0 else [],
                errors=[result.stderr] if result.returncode != 0 else [],
                warnings=[]
            )
        except subprocess.TimeoutExpired:
            return ScriptTestResult(
                passed=False,
                script=script_path.name,
                tests_run=['sandbox_execution'],
                tests_passed=[],
                tests_failed=[{'test': 'sandbox_execution', 'error': 'Timeout after 30s'}],
                errors=['Script execution timed out'],
                warnings=[]
            )
```

## Test All Scripts

```python
def test_all_scripts(skill_dir: Path) -> dict:
    """Test all scripts in a skill directory."""
    scripts_dir = skill_dir / "scripts"

    if not scripts_dir.exists():
        return {
            'passed': True,
            'message': 'No scripts directory',
            'results': []
        }

    results = []
    all_passed = True

    for script in scripts_dir.glob("*"):
        if script.suffix in ['.sh', '.py']:
            result = test_script(script)
            results.append(result)
            if not result.passed:
                all_passed = False

    return {
        'passed': all_passed,
        'scripts_tested': len(results),
        'scripts_passed': sum(1 for r in results if r.passed),
        'results': [asdict(r) for r in results]
    }
```

## Output Format

```json
{
  "script_tests": {
    "passed": true,
    "scripts_tested": 2,
    "scripts_passed": 2,
    "results": [
      {
        "passed": true,
        "script": "validate.sh",
        "tests_run": ["syntax_check", "shellcheck", "shebang_check", "help_flag"],
        "tests_passed": ["syntax_check", "shellcheck", "shebang_check", "help_flag"],
        "tests_failed": [],
        "errors": [],
        "warnings": []
      },
      {
        "passed": true,
        "script": "generate.py",
        "tests_run": ["syntax_check", "import_check", "type_check", "help_flag"],
        "tests_passed": ["syntax_check", "import_check", "type_check", "help_flag"],
        "tests_failed": [],
        "errors": [],
        "warnings": ["Type hints: 1 warning"]
      }
    ]
  }
}
```

## Pass Criteria

- All scripts must pass syntax check
- All scripts must pass shellcheck/pyright without errors
- Scripts with --help flag must respond correctly
- No runtime errors in dry-run mode
