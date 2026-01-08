# Documentation Quality Checklist

Validation criteria for code documentation quality assessment.

## Required Elements

### All Languages

- [ ] **Summary line present**: First line describes the purpose
- [ ] **Summary is concise**: One sentence, starts with verb
- [ ] **Parameters documented**: All input parameters have descriptions
- [ ] **Return value documented**: What the function returns
- [ ] **No placeholders**: No TODO, TBD, FIXME, or "..." in docs

### Language-Specific

#### Python
- [ ] Docstring format consistent (Google/NumPy/Sphinx throughout)
- [ ] Type hints present OR types in docstring
- [ ] `Raises` section for functions that raise exceptions
- [ ] Triple quotes used correctly (`"""`)

#### TypeScript/JavaScript
- [ ] JSDoc/TSDoc format used for exports
- [ ] `@param` tags have type and description
- [ ] `@returns` describes return value
- [ ] `@throws` documents thrown errors

#### Java
- [ ] All public methods have Javadoc
- [ ] `@param` for each parameter
- [ ] `@return` for non-void methods
- [ ] `@throws` for checked exceptions

#### Go
- [ ] Comment starts with function name
- [ ] Comment is complete sentence
- [ ] Examples use tab indentation

#### Rust
- [ ] `///` doc comments for public items
- [ ] `//!` for module-level docs
- [ ] `# Errors` section for Result returns
- [ ] `# Panics` section if function can panic

---

## Quality Levels

### Level 1: Minimal (Score 1-3)
- Some items have docstrings
- Basic parameter listing
- No examples

### Level 2: Adequate (Score 4-6)
- Most public items documented
- Parameters have types and descriptions
- Return values documented
- No placeholder content

### Level 3: Good (Score 7-8)
- All public items documented
- Consistent style throughout
- Exceptions documented
- Usage context provided

### Level 4: Excellent (Score 9-10)
- Complete coverage
- Rich examples
- Edge cases documented
- Cross-references included
- Self-documenting code structure

---

## Common Issues

### Content Problems

| Issue | Example | Fix |
|-------|---------|-----|
| Too brief | `"""Gets data."""` | Describe what data and how |
| Too verbose | 50 lines for simple getter | Summarize, be concise |
| Obvious | `"""Returns the name."""` | Only doc if non-trivial |
| Stale | Docs don't match code | Update after changes |
| Placeholder | `TODO: document this` | Write actual docs |

### Format Problems

| Issue | Example | Fix |
|-------|---------|-----|
| Wrong style | Mixing Google and NumPy | Standardize on one |
| Missing sections | No Args/Returns | Add required sections |
| Incorrect order | Returns before Args | Follow style guide order |
| Bad indentation | Misaligned params | Consistent spacing |

### Completeness Problems

| Issue | Example | Fix |
|-------|---------|-----|
| Missing params | 3 params, 2 documented | Document all params |
| No return doc | Returns complex object | Describe return structure |
| Silent exceptions | Raises but not documented | Add Raises section |
| No examples | Complex function, no demo | Add usage example |

---

## Scoring Rubric

| Category | Weight | Criteria |
|----------|--------|----------|
| Coverage | 30% | Percentage of public items documented |
| Completeness | 25% | All sections present (params, returns, etc.) |
| Accuracy | 20% | Docs match actual behavior |
| Style | 15% | Consistent format throughout |
| Examples | 10% | Working examples for complex items |

### Calculation

```
Score = (Coverage × 0.30) + (Completeness × 0.25) +
        (Accuracy × 0.20) + (Style × 0.15) + (Examples × 0.10)
```

### Thresholds

- **Pass**: Score >= 7.0
- **Needs Work**: Score 5.0-6.9
- **Fail**: Score < 5.0

---

## Pre-Commit Checks

Automated validation to run before commits:

### Python (pydocstyle)
```bash
pydocstyle --convention=google src/
```

### TypeScript (eslint-plugin-jsdoc)
```json
{
  "plugins": ["jsdoc"],
  "rules": {
    "jsdoc/require-description": "warn",
    "jsdoc/require-param": "error",
    "jsdoc/require-returns": "error"
  }
}
```

### Java (Checkstyle)
```xml
<module name="JavadocMethod">
  <property name="scope" value="public"/>
</module>
```

### Go (golint)
```bash
golint ./...
```

### Rust (rustdoc)
```bash
RUSTDOCFLAGS="-D warnings" cargo doc
```
