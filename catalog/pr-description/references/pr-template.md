# PR Template Reference

Standard pull request template sections and formats.

## Standard Template

```markdown
## Summary
<!-- Brief description of what changed and why -->

## PR Type
- [ ] Bug fix
- [ ] Feature
- [ ] Refactoring
- [ ] Documentation
- [ ] Performance
- [ ] Configuration

## Related Issues
<!-- Link issues: Closes #123, Fixes #456, Relates to #789 -->

## Changes Made
### [Category]
- Change description

## Testing Instructions
### Environment Setup
1. Step to set up

### Test Scenarios
1. **Scenario**: [description]
   - Expected: [result]

## Screenshots
<!-- If UI changes, add before/after screenshots -->

## Breaking Changes
<!-- List any breaking changes and migration steps -->
None

## Checklist
- [ ] Code follows project style
- [ ] Self-reviewed changes
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CI passes
```

## Title Format

Follow conventional commits:

```
<type>(<scope>): <description>
```

### Types

| Type | Use For | Example |
|------|---------|---------|
| `feat` | New feature | `feat(auth): add SSO login` |
| `fix` | Bug fix | `fix(api): handle null response` |
| `docs` | Documentation | `docs: update API reference` |
| `style` | Formatting | `style: fix indentation` |
| `refactor` | Code restructure | `refactor(db): optimize queries` |
| `perf` | Performance | `perf: cache API responses` |
| `test` | Tests | `test: add auth unit tests` |
| `build` | Build changes | `build: update webpack` |
| `ci` | CI config | `ci: add GitHub Actions` |
| `chore` | Maintenance | `chore: update deps` |

### Breaking Changes

Add `!` before colon:
```
feat(api)!: change response format
```

## Git Commands for Analysis

### Branch Comparison

```bash
# Commits on branch
git log main..HEAD --oneline

# Files changed
git diff main..HEAD --name-status

# Statistics
git diff main..HEAD --stat

# Full diff
git diff main..HEAD
```

### File Status Codes

| Code | Meaning |
|------|---------|
| A | Added |
| M | Modified |
| D | Deleted |
| R | Renamed |
| C | Copied |

### Extract Issue References

```bash
# Find issue numbers in commits
git log main..HEAD --format="%B" | grep -oE '#[0-9]+'
```

## File Categorization

### Source Code
- `src/**/*`
- `lib/**/*`
- `app/**/*`
- `pkg/**/*`

### Tests
- `test/**/*`
- `tests/**/*`
- `__tests__/**/*`
- `*.test.*`
- `*.spec.*`
- `*_test.*`

### Documentation
- `docs/**/*`
- `*.md`
- `README*`
- `CHANGELOG*`

### Configuration
- `*.json`
- `*.yaml`
- `*.yml`
- `*.toml`
- `.*rc`
- `*.config.*`

### CI/CD
- `.github/**/*`
- `.gitlab-ci.yml`
- `Dockerfile*`
- `docker-compose*`
- `Jenkinsfile`

### Styles
- `*.css`
- `*.scss`
- `*.less`
- `*.styled.*`

## Issue Linking Syntax

### GitHub
```markdown
Closes #123
Fixes #456
Resolves #789
Relates to #101
```

### Jira
```markdown
Fixes PROJ-123
Relates to PROJ-456
```

### Multiple Issues
```markdown
Closes #123, #456
Fixes #789
```

## Breaking Change Documentation

### Format

```markdown
## Breaking Changes

**What Changed:**
- Old behavior description
- New behavior description

**Migration Steps:**
1. Update X to Y
2. Change config from A to B
3. Run migration script

**Rollback:**
If issues occur, revert with:
git revert <commit-hash>
```

### Example

```markdown
## Breaking Changes

**API Response Format Changed**

Previous:
```json
{"token": "abc123"}
```

New:
```json
{"accessToken": "abc123", "refreshToken": "xyz789"}
```

**Migration:**
1. Update token storage to save both tokens
2. Implement token refresh logic
3. Update logout to invalidate refresh token
```
