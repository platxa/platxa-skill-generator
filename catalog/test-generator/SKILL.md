---
name: test-generator
description: Generate unit tests for existing code across Python, JavaScript/TypeScript, Java, Go, and Rust. Creates comprehensive test cases covering happy paths, edge cases, and error handling using appropriate testing frameworks.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
metadata:
  version: "1.0.0"
  tags:
    - builder
    - testing
    - developer-tools
---

# Test Generator

Generate comprehensive unit tests for existing code.

## Overview

This skill creates production-ready unit tests by analyzing your code, detecting the appropriate testing framework, and generating test cases that cover happy paths, boundary values, edge cases, and error handling. Tests follow the AAA (Arrange-Act-Assert) pattern and language-specific best practices.

**What it creates:**
- Test files matching project conventions
- Parameterized tests for multiple scenarios
- Mock setups for dependencies
- Coverage-focused test cases

## Framework Detection

| Language | Framework | Test File Pattern |
|----------|-----------|-------------------|
| Python | pytest | `test_*.py` or `*_test.py` |
| TypeScript/JS | Jest/Vitest | `*.test.ts` or `*.spec.ts` |
| Java | JUnit 5 | `*Test.java` |
| Go | testing | `*_test.go` |
| Rust | built-in | `#[cfg(test)]` module |

## Workflow

### Step 1: Analyze Source Code

I'll read the target file and identify:
- Functions/methods to test
- Parameter types and constraints
- Return types and possible values
- Dependencies that need mocking
- Existing test patterns in the project

### Step 2: Detect Testing Framework

Check for existing test configuration:
- `pytest.ini`, `pyproject.toml` (Python)
- `jest.config.js`, `vitest.config.ts` (JS/TS)
- `pom.xml` with JUnit (Java)
- Go module with `_test.go` files
- Rust `Cargo.toml` with test configuration

### Step 3: Generate Test Cases

For each function, I generate tests covering:

**Happy Path**
- Normal expected inputs
- Primary success scenarios

**Boundary Values**
- Minimum/maximum valid inputs
- Empty collections, zero values
- String length limits

**Edge Cases**
- Null/None/undefined inputs
- Empty strings, empty arrays
- Negative numbers (when unexpected)

**Error Handling**
- Invalid input types
- Out-of-range values
- Expected exceptions

### Step 4: Structure Tests (AAA Pattern)

Each test follows Arrange-Act-Assert:

```python
def test_calculate_discount_valid_percentage():
    # Arrange
    price = 100.0
    percentage = 20

    # Act
    result = calculate_discount(price, percentage)

    # Assert
    assert result == 80.0
```

### Step 5: Write Test File

Create the test file following project conventions:
- Place in appropriate test directory
- Use consistent naming
- Include necessary imports
- Add fixture setup if needed

## Examples

### Example 1: Python Function

**Source:** `src/utils/calculator.py`
```python
def calculate_discount(price: float, percentage: int) -> float:
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be 0-100")
    return price * (1 - percentage / 100)
```

**Generated:** `tests/test_calculator.py`
```python
import pytest
from src.utils.calculator import calculate_discount


class TestCalculateDiscount:
    """Tests for calculate_discount function."""

    # Happy path tests
    def test_applies_discount_correctly(self):
        assert calculate_discount(100.0, 20) == 80.0

    def test_zero_discount_returns_original(self):
        assert calculate_discount(100.0, 0) == 100.0

    def test_full_discount_returns_zero(self):
        assert calculate_discount(100.0, 100) == 0.0

    # Boundary value tests
    @pytest.mark.parametrize("price,percentage,expected", [
        (100.0, 0, 100.0),    # Min boundary
        (100.0, 100, 0.0),    # Max boundary
        (100.0, 1, 99.0),     # Just above min
        (100.0, 99, 1.0),     # Just below max
    ])
    def test_boundary_values(self, price, percentage, expected):
        assert calculate_discount(price, percentage) == expected

    # Error handling tests
    def test_negative_percentage_raises_error(self):
        with pytest.raises(ValueError):
            calculate_discount(100.0, -1)

    def test_percentage_over_100_raises_error(self):
        with pytest.raises(ValueError):
            calculate_discount(100.0, 101)
```

### Example 2: TypeScript Function

**Source:** `src/utils/validator.ts`
```typescript
export function isValidEmail(email: string): boolean {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}
```

**Generated:** `src/utils/validator.test.ts`
```typescript
import { isValidEmail } from './validator';

describe('isValidEmail', () => {
  // Happy path
  it('returns true for valid email', () => {
    expect(isValidEmail('user@example.com')).toBe(true);
  });

  // Valid variations
  it.each([
    ['simple@example.com'],
    ['user.name@domain.org'],
    ['user+tag@example.co.uk'],
  ])('returns true for %s', (email) => {
    expect(isValidEmail(email)).toBe(true);
  });

  // Invalid cases
  it.each([
    [''],
    ['invalid'],
    ['@example.com'],
    ['user@'],
    ['user@.com'],
    ['user name@example.com'],
  ])('returns false for invalid email: %s', (email) => {
    expect(isValidEmail(email)).toBe(false);
  });
});
```

### Example 3: Go Function

**Source:** `pkg/math/operations.go`
```go
func Divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}
```

**Generated:** `pkg/math/operations_test.go`
```go
func TestDivide(t *testing.T) {
    tests := []struct {
        name    string
        a, b    float64
        want    float64
        wantErr bool
    }{
        {"positive numbers", 10, 2, 5, false},
        {"negative dividend", -10, 2, -5, false},
        {"negative divisor", 10, -2, -5, false},
        {"division by zero", 10, 0, 0, true},
        {"zero dividend", 0, 5, 0, false},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Divide(tt.a, tt.b)
            if (err != nil) != tt.wantErr {
                t.Errorf("error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if got != tt.want {
                t.Errorf("got %v, want %v", got, tt.want)
            }
        })
    }
}
```

## Test Case Categories

| Category | What to Test | Example |
|----------|--------------|---------|
| Happy Path | Normal valid inputs | `add(2, 3)` returns `5` |
| Boundaries | Min/max valid values | `0`, `100` for percentage |
| Edge Cases | Unusual but valid | Empty string, single item |
| Null/None | Missing values | `None`, `null`, `undefined` |
| Type Errors | Wrong input types | String where number expected |
| Exceptions | Error conditions | Division by zero |

## Output Checklist

Before finalizing generated tests:

- [ ] Tests follow AAA pattern
- [ ] Naming convention matches project
- [ ] Happy path covered
- [ ] Boundary values tested
- [ ] Edge cases included
- [ ] Error handling verified
- [ ] Mocks properly configured
- [ ] Tests are deterministic
- [ ] No hardcoded paths or secrets
- [ ] Tests can run independently
