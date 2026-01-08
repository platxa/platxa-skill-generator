# Test Patterns Reference

Quick reference for test generation patterns across languages.

## AAA Pattern (Arrange-Act-Assert)

The universal structure for unit tests:

```
Arrange: Set up test data and dependencies
Act:     Execute the code under test
Assert:  Verify the expected outcome
```

### Python (pytest)

```python
def test_user_creation():
    # Arrange
    user_data = {"name": "Alice", "email": "alice@example.com"}

    # Act
    user = create_user(user_data)

    # Assert
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
```

### TypeScript (Jest)

```typescript
it('creates user with correct data', () => {
  // Arrange
  const userData = { name: 'Alice', email: 'alice@example.com' };

  // Act
  const user = createUser(userData);

  // Assert
  expect(user.name).toBe('Alice');
  expect(user.email).toBe('alice@example.com');
});
```

### Go (testing)

```go
func TestCreateUser(t *testing.T) {
    // Arrange
    userData := UserData{Name: "Alice", Email: "alice@example.com"}

    // Act
    user := CreateUser(userData)

    // Assert
    if user.Name != "Alice" {
        t.Errorf("expected Alice, got %s", user.Name)
    }
}
```

## Parameterized Tests

### Python (pytest)

```python
@pytest.mark.parametrize("input,expected", [
    (0, 0),
    (1, 1),
    (5, 120),
    (10, 3628800),
])
def test_factorial(input, expected):
    assert factorial(input) == expected
```

### TypeScript (Jest)

```typescript
describe.each([
  [0, 0],
  [1, 1],
  [5, 120],
  [10, 3628800],
])('factorial(%i)', (input, expected) => {
  it(`returns ${expected}`, () => {
    expect(factorial(input)).toBe(expected);
  });
});
```

### Go (Table-Driven)

```go
func TestFactorial(t *testing.T) {
    tests := []struct {
        input    int
        expected int
    }{
        {0, 0},
        {1, 1},
        {5, 120},
        {10, 3628800},
    }

    for _, tt := range tests {
        t.Run(fmt.Sprintf("factorial(%d)", tt.input), func(t *testing.T) {
            if got := Factorial(tt.input); got != tt.expected {
                t.Errorf("got %d, want %d", got, tt.expected)
            }
        })
    }
}
```

## Exception Testing

### Python

```python
def test_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        validate_percentage(-1)
    assert "must be positive" in str(exc_info.value)
```

### TypeScript

```typescript
it('throws error for invalid input', () => {
  expect(() => validatePercentage(-1)).toThrow('must be positive');
});
```

### Go

```go
func TestValidatePercentage_Error(t *testing.T) {
    _, err := ValidatePercentage(-1)
    if err == nil {
        t.Error("expected error, got nil")
    }
}
```

## Mocking Dependencies

### Python (unittest.mock)

```python
from unittest.mock import Mock, patch

def test_service_calls_repository():
    # Arrange
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = User(id=1, name="Alice")
    service = UserService(mock_repo)

    # Act
    user = service.get_user(1)

    # Assert
    mock_repo.find_by_id.assert_called_once_with(1)
    assert user.name == "Alice"
```

### TypeScript (Jest)

```typescript
jest.mock('./repository');

it('calls repository with correct id', () => {
  // Arrange
  const mockRepo = Repository as jest.Mocked<typeof Repository>;
  mockRepo.findById.mockResolvedValue({ id: 1, name: 'Alice' });

  // Act
  const user = await service.getUser(1);

  // Assert
  expect(mockRepo.findById).toHaveBeenCalledWith(1);
  expect(user.name).toBe('Alice');
});
```

## Boundary Value Testing

For any range `[min, max]`, test these points:

| Point | Value | Purpose |
|-------|-------|---------|
| Below min | `min - 1` | Should fail/error |
| At min | `min` | Should pass |
| Above min | `min + 1` | Should pass |
| Nominal | `(min + max) / 2` | Should pass |
| Below max | `max - 1` | Should pass |
| At max | `max` | Should pass |
| Above max | `max + 1` | Should fail/error |

### Example: Percentage (0-100)

```python
@pytest.mark.parametrize("value,is_valid", [
    (-1, False),   # Below min
    (0, True),     # At min
    (1, True),     # Above min
    (50, True),    # Nominal
    (99, True),    # Below max
    (100, True),   # At max
    (101, False),  # Above max
])
def test_percentage_boundaries(value, is_valid):
    if is_valid:
        assert validate_percentage(value) == value
    else:
        with pytest.raises(ValueError):
            validate_percentage(value)
```

## Test Naming Conventions

### Pattern 1: test_method_scenario_expected

```python
test_calculate_discount_zero_percentage_returns_original_price
test_calculate_discount_negative_percentage_raises_error
```

### Pattern 2: Given-When-Then

```python
test_given_valid_email_when_validating_then_returns_true
```

### Pattern 3: Should statements

```typescript
it('should return true for valid email')
it('should throw error for empty input')
```

## Fixtures and Setup

### Python (pytest fixtures)

```python
@pytest.fixture
def sample_user():
    return User(id=1, name="Alice", email="alice@example.com")

@pytest.fixture
def mock_database():
    return Mock(spec=Database)

def test_save_user(mock_database, sample_user):
    service = UserService(mock_database)
    service.save(sample_user)
    mock_database.insert.assert_called_once()
```

### TypeScript (beforeEach)

```typescript
describe('UserService', () => {
  let service: UserService;
  let mockDb: jest.Mocked<Database>;

  beforeEach(() => {
    mockDb = createMockDatabase();
    service = new UserService(mockDb);
  });

  it('saves user to database', () => {
    service.save(sampleUser);
    expect(mockDb.insert).toHaveBeenCalled();
  });
});
```

## Common Edge Cases Checklist

| Type | Edge Cases to Test |
|------|-------------------|
| Strings | Empty `""`, whitespace `"  "`, very long, special chars |
| Numbers | `0`, negative, `MAX_INT`, `MIN_INT`, `NaN`, `Infinity` |
| Arrays | Empty `[]`, single item, many items, duplicates |
| Objects | Empty `{}`, null, undefined, missing keys |
| Dates | Min date, max date, leap years, timezones |
| Booleans | Both `true` and `false` paths |
