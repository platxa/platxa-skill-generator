# Conventional Commits Reference

Quick reference for the Conventional Commits specification.

## Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

| Type | Purpose | SemVer | Example |
|------|---------|--------|---------|
| `feat` | New feature | MINOR | `feat: add user avatar upload` |
| `fix` | Bug fix | PATCH | `fix: resolve login timeout` |
| `docs` | Documentation | - | `docs: update API reference` |
| `style` | Formatting | - | `style: fix indentation` |
| `refactor` | Code change (no behavior change) | - | `refactor: extract validation logic` |
| `perf` | Performance | - | `perf: optimize image loading` |
| `test` | Tests | - | `test: add auth unit tests` |
| `build` | Build system | - | `build: update webpack config` |
| `ci` | CI config | - | `ci: add GitHub Actions` |
| `chore` | Maintenance | - | `chore: update dependencies` |

## Subject Line Rules

1. **Length**: Maximum 50 characters
2. **Mood**: Imperative ("Add" not "Added" or "Adds")
3. **Case**: Capitalize first letter
4. **Punctuation**: No period at end
5. **Completeness**: Should complete "If applied, this commit will..."

### Imperative Mood Examples

| Wrong | Correct |
|-------|---------|
| Added new feature | Add new feature |
| Fixes bug | Fix bug |
| Changed behavior | Change behavior |
| Updating docs | Update docs |

## Scope

Optional context about what part of codebase changed:

```
feat(auth): add OAuth2 support
fix(parser): handle empty arrays
docs(readme): update installation steps
```

Common scopes:
- Component/module name: `auth`, `api`, `ui`
- Layer: `model`, `view`, `controller`
- Feature area: `login`, `checkout`, `search`

## Body

- Separate from subject with blank line
- Wrap at 72 characters
- Explain **what** and **why**, not how
- Use bullet points for multiple items

```
feat(auth): add two-factor authentication

Add TOTP-based 2FA for enhanced account security.
Users can now enable 2FA from their security settings.

- Add QR code generation for authenticator apps
- Store encrypted TOTP secrets
- Add backup codes for account recovery
```

## Footer

### Issue References

```
Closes #123
Fixes #456
Resolves #789
```

### Breaking Changes

Two methods to indicate:

**Method 1: Exclamation mark**
```
feat(api)!: change response format
```

**Method 2: Footer**
```
feat(api): change response format

BREAKING CHANGE: Response now returns {data, meta}
instead of flat object. All clients must update.
```

### Multiple Footers

```
feat(auth): add SSO support

Implement SAML-based single sign-on for enterprise users.

Closes #123
Reviewed-by: Alice
Co-authored-by: Bob <bob@example.com>
```

## Breaking Changes

Breaking changes MUST be indicated when:
- Public API signature changes
- Required configuration changes
- Behavior changes that affect consumers
- Removal of features/endpoints

Breaking change commits bump MAJOR version (1.0.0 → 2.0.0).

## Examples

### Minimal

```
fix: correct typo in error message
```

### With Scope

```
feat(cart): add quantity selector
```

### With Body

```
refactor(utils): simplify date formatting

Replace moment.js with date-fns for smaller bundle size.
All date formatting functions now use the new library.
```

### With Footer

```
fix(api): handle null response gracefully

Closes #234
```

### Complete Example

```
feat(payments)!: migrate to Stripe API v2

Update payment processing to use Stripe's latest API.
This enables support for new payment methods and
improved error handling.

- Migrate customer creation flow
- Update webhook handlers
- Add support for Apple Pay and Google Pay

BREAKING CHANGE: Payment method tokens are no longer
compatible. Existing saved payment methods must be
re-authenticated by users.

Closes #456
Reviewed-by: Security Team
```

## Validation Regex

Pattern for validating commit messages:

```regex
^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\([a-z0-9-]+\))?!?: .{1,50}$
```

## Tools Integration

### commitlint

```json
{
  "extends": ["@commitlint/config-conventional"]
}
```

### commitizen

```json
{
  "config": {
    "commitizen": {
      "path": "cz-conventional-changelog"
    }
  }
}
```

### Pre-commit Hook

```yaml
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v3.0.0
  hooks:
    - id: conventional-pre-commit
      stages: [commit-msg]
```
