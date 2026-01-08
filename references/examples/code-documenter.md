# Example Skill: Code Documenter

A complete skill example demonstrating references and scripts usage.

## Skill Overview

| Property | Value |
|----------|-------|
| Name | `code-documenter` |
| Type | Builder |
| Complexity | Medium |
| Files | 5 |

## File Structure

```
code-documenter/
├── SKILL.md
├── references/
│   ├── doc-styles.md
│   └── language-patterns.md
└── scripts/
    └── extract-signatures.sh
```

## SKILL.md

```markdown
---
name: code-documenter
description: Generate comprehensive documentation for code files and functions
version: 1.0.0
author: Skill Generator
tags: [builder, documentation, code]
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Code Documenter

Generate comprehensive documentation for your code files, functions, and modules.

## What This Skill Does

- Analyzes code structure and patterns
- Generates docstrings and comments
- Creates README sections
- Produces API documentation

## How to Use

1. Specify the target file or directory
2. Choose documentation style
3. Review and refine output

```
/code-documenter path/to/file.py
```

## Documentation Styles

| Style | Best For | Format |
|-------|----------|--------|
| Docstring | Functions/classes | Inline comments |
| README | Modules/packages | Markdown file |
| API | Libraries | Structured reference |
| Inline | Complex logic | Code comments |

See [Documentation Styles](references/doc-styles.md) for details.

## Workflow

### Step 1: Analysis

I'll read the target code and identify:
- Functions and their signatures
- Classes and methods
- Module structure
- Dependencies

### Step 2: Pattern Detection

Using language-specific patterns to understand:
- Parameter types and purposes
- Return values
- Side effects
- Usage patterns

See [Language Patterns](references/language-patterns.md) for supported languages.

### Step 3: Generation

Generate documentation including:
- Purpose description
- Parameter documentation
- Return value explanation
- Usage examples
- Error handling notes

### Step 4: Review

Present documentation for your review:
- Verify accuracy
- Add domain context
- Refine wording

## Examples

### Example 1: Python Function

**Input:**
```python
def calculate_discount(price, percentage, max_discount=None):
    discount = price * (percentage / 100)
    if max_discount and discount > max_discount:
        discount = max_discount
    return price - discount
```

**Generated Documentation:**
```python
def calculate_discount(price: float, percentage: float, max_discount: float | None = None) -> float:
    """Calculate discounted price with optional maximum discount cap.

    Applies a percentage-based discount to a price, optionally capping
    the discount at a maximum value.

    Args:
        price: Original price before discount.
        percentage: Discount percentage (0-100).
        max_discount: Optional maximum discount amount. If the calculated
            discount exceeds this, the max is used instead.

    Returns:
        The final price after applying the discount.

    Examples:
        >>> calculate_discount(100, 20)
        80.0
        >>> calculate_discount(100, 50, max_discount=30)
        70.0
    """
    discount = price * (percentage / 100)
    if max_discount and discount > max_discount:
        discount = max_discount
    return price - discount
```

### Example 2: JavaScript Class

**Input:**
```javascript
class UserManager {
    constructor(database) {
        this.db = database;
        this.cache = new Map();
    }

    async getUser(id) {
        if (this.cache.has(id)) {
            return this.cache.get(id);
        }
        const user = await this.db.findUser(id);
        this.cache.set(id, user);
        return user;
    }
}
```

**Generated Documentation:**
```javascript
/**
 * Manages user data with caching support.
 *
 * Provides cached access to user records, reducing database queries
 * for frequently accessed users.
 *
 * @example
 * const manager = new UserManager(database);
 * const user = await manager.getUser('user-123');
 */
class UserManager {
    /**
     * Creates a new UserManager instance.
     * @param {Database} database - Database connection for user queries.
     */
    constructor(database) {
        this.db = database;
        this.cache = new Map();
    }

    /**
     * Retrieves a user by ID, using cache when available.
     *
     * @param {string} id - Unique user identifier.
     * @returns {Promise<User>} The user object.
     * @throws {NotFoundError} If user doesn't exist.
     */
    async getUser(id) {
        if (this.cache.has(id)) {
            return this.cache.get(id);
        }
        const user = await this.db.findUser(id);
        this.cache.set(id, user);
        return user;
    }
}
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--style` | `docstring` | Documentation style |
| `--lang` | auto-detect | Target language |
| `--examples` | `true` | Include usage examples |
| `--types` | `true` | Include type annotations |

## See Also

- [Documentation Styles](references/doc-styles.md)
- [Language Patterns](references/language-patterns.md)
```

## references/doc-styles.md

```markdown
# Documentation Styles

## Docstring Style

### Python (Google Style)
```python
def function(arg1, arg2):
    """Short description.

    Longer description if needed.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.

    Returns:
        Description of return value.

    Raises:
        ErrorType: When this error occurs.
    """
```

### JavaScript (JSDoc)
```javascript
/**
 * Short description.
 *
 * @param {Type} arg1 - Description.
 * @param {Type} arg2 - Description.
 * @returns {Type} Description.
 * @throws {ErrorType} Description.
 */
```

## README Style

```markdown
# Module Name

Brief description.

## Installation

## Usage

## API Reference

## Examples
```

## API Style

```markdown
## function_name

**Signature:** `function_name(arg1, arg2) -> ReturnType`

**Description:** What it does.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|

**Returns:** Description

**Example:**
```
```

## references/language-patterns.md

```markdown
# Language Patterns

## Python

### Function Detection
- `def function_name(args):`
- `async def function_name(args):`

### Class Detection
- `class ClassName:`
- `class ClassName(Parent):`

### Type Hints
- `arg: Type`
- `-> ReturnType`

## JavaScript/TypeScript

### Function Detection
- `function name(args) {`
- `const name = (args) => {`
- `async function name(args) {`

### Class Detection
- `class ClassName {`
- `class ClassName extends Parent {`

## Go

### Function Detection
- `func name(args) returnType {`
- `func (r Receiver) name(args) returnType {`

### Struct Detection
- `type Name struct {`
```

## scripts/extract-signatures.sh

```bash
#!/bin/bash
# Extract function signatures from source files

FILE="$1"
LANG="${2:-auto}"

# Auto-detect language
if [ "$LANG" = "auto" ]; then
    case "$FILE" in
        *.py) LANG="python" ;;
        *.js|*.ts) LANG="javascript" ;;
        *.go) LANG="go" ;;
        *) LANG="unknown" ;;
    esac
fi

case "$LANG" in
    python)
        grep -n "^\s*def \|^\s*async def \|^\s*class " "$FILE"
        ;;
    javascript)
        grep -n "function \|const.*= .*=> \|class " "$FILE"
        ;;
    go)
        grep -n "^func \|^type.*struct" "$FILE"
        ;;
    *)
        echo "Unknown language: $LANG"
        exit 1
        ;;
esac
```

## Token Analysis

| File | Tokens |
|------|--------|
| SKILL.md | 1,842 |
| references/doc-styles.md | 856 |
| references/language-patterns.md | 412 |
| scripts/extract-signatures.sh | 124 |
| **Total** | **3,234** |

## Key Takeaways

1. **References expand capability**: Detailed patterns in separate files
2. **Scripts automate tasks**: Shell scripts for code extraction
3. **Examples are essential**: Real before/after demonstrations
4. **Structure matches purpose**: Builder skills need more detail
