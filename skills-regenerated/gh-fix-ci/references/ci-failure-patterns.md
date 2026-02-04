# CI Failure Patterns

Common GitHub Actions failure patterns and their typical fixes.

## Build Failures

### Missing Dependencies

```
error: Cannot find module 'lodash'
ModuleNotFoundError: No module named 'requests'
could not resolve dependency: npm ERR! peer dep missing
```

**Fix**: Add missing package to `package.json`, `requirements.txt`, or lock file. Check if the dependency was removed from a lock file update.

### Syntax / Type Errors

```
SyntaxError: Unexpected token '}'
error TS2339: Property 'foo' does not exist on type 'Bar'
error[E0308]: mismatched types
```

**Fix**: Check the PR diff for the file and line reported. Correct the syntax or type annotation.

### Build Tool Version Mismatch

```
Error: The engine "node" is incompatible with this module
rustup: toolchain 'nightly-2025-01-01' is not installed
```

**Fix**: Update `.node-version`, `rust-toolchain.toml`, or CI workflow `setup-*` action version.

## Test Failures

### Assertion Errors

```
AssertionError: expected 200 got 401
FAIL: test_create_user (tests.test_api.UserTestCase)
assert result == expected, f"Got {result}"
```

**Fix**: Check if the PR changed the behavior the test expects. Update the test or fix the implementation.

### Flaky Tests

Symptoms: intermittent failures, passes on retry, timing-dependent.

```
TimeoutError: Waited 30s for element
ConnectionResetError: [Errno 104] Connection reset by peer
```

**Fix**: Add retry logic, increase timeouts, or use `pytest-rerunfailures`. For CI-specific flakiness, check runner resource limits.

### Missing Fixtures / Setup

```
fixture 'db_session' not found
SetUpError: Database not initialized
FileNotFoundError: test_data/sample.json
```

**Fix**: Ensure test fixtures are committed and CI setup steps create required resources.

## Lint Failures

### Style Violations

```
E501 line too long (120 > 88 characters)
W503 line break before binary operator
C0301: Line too long (src/handler.py:42)
```

**Fix**: Run the formatter locally (`ruff format`, `prettier`, `gofmt`) and commit.

### Import Order

```
I001 [*] Import block is un-sorted or un-formatted
isort: imports are not sorted
```

**Fix**: Run `isort .` or `ruff check --fix` locally.

## Infrastructure Failures

### Runner Out of Disk

```
No space left on device
ENOSPC: no space left on device, write
```

**Fix**: Add cleanup steps in workflow, reduce artifact sizes, or use larger runners.

### Network Issues

```
Could not resolve host: registry.npmjs.org
ConnectionError: HTTPSConnectionPool host='pypi.org'
```

**Fix**: Usually transient. Retry the workflow. If persistent, check GitHub status page.

### Secret / Permission Issues

```
Error: Resource not accessible by integration
fatal: could not read Username for 'https://github.com'
Error: secret DEPLOY_KEY is not defined
```

**Fix**: Check repository Settings > Secrets. Ensure the workflow has correct `permissions:` block. For GITHUB_TOKEN, verify the `permissions` key in the workflow YAML.

## Timeout Failures

```
The job exceeded the maximum execution time of 360 minutes
Error: The operation was canceled.
```

**Fix**: Profile slow steps, parallelize tests, add caching for dependencies, or increase `timeout-minutes` in the workflow.

## Log Marker Reference

Markers the inspection script scans for (in reverse order):

| Marker | Typical Source |
|--------|---------------|
| `error` | General errors across all languages |
| `fail` / `failed` | Test frameworks, build tools |
| `traceback` | Python stack traces |
| `exception` | Java, Python, JavaScript |
| `assert` | Test assertion failures |
| `panic` | Go, Rust panics |
| `fatal` | Git, build tools, runtime crashes |
| `timeout` | CI runners, test frameworks |
| `segmentation fault` | C/C++ crashes |
