---
name: pr-description
description: Generate comprehensive pull request descriptions by analyzing git commits and diff. Creates structured summaries with changes breakdown, testing instructions, and related issues following team PR templates.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - Write
metadata:
  version: "1.0.0"
  tags:
    - builder
    - git
    - workflow
---

# PR Description Generator

Generate comprehensive pull request descriptions from git history.

## Overview

This skill creates well-structured PR descriptions by analyzing your branch's commits and diff against the base branch. It categorizes changes, extracts related issues, detects breaking changes, and formats everything according to your team's PR template.

**What it creates:**
- Formatted PR title following conventional commits
- Summary of what changed and why
- Categorized list of modifications
- Testing instructions
- Related issue links

## Workflow

### Step 1: Analyze Branch

I'll examine your branch compared to the base:

```bash
# Get commit history
git log main..HEAD --oneline

# Get file changes
git diff main..HEAD --name-status

# Get statistics
git diff main..HEAD --stat
```

### Step 2: Categorize Changes

Group modified files by type:

| Category | Patterns | Label |
|----------|----------|-------|
| Source | `src/`, `lib/`, `app/` | Implementation |
| Tests | `test/`, `*.test.*`, `*.spec.*` | Testing |
| Docs | `docs/`, `*.md`, `README` | Documentation |
| Config | `*.json`, `*.yaml`, `.*rc` | Configuration |
| CI/CD | `.github/`, `Dockerfile` | Infrastructure |
| Styles | `*.css`, `*.scss` | Styling |

### Step 3: Extract Information

From commits and diff, I identify:
- **PR Type**: feat, fix, refactor, docs, etc.
- **Scope**: Primary area affected
- **Breaking Changes**: API changes, removed features
- **Related Issues**: #123, JIRA-456 references
- **Authors**: Contributors to credit

### Step 4: Generate Description

Create structured PR description:

```markdown
## Summary
[What changed and why]

## Changes
### [Category]
- Change 1
- Change 2

## Testing
[How to verify]

## Related Issues
Closes #123
```

### Step 5: Apply Template

If `.github/pull_request_template.md` exists, I'll fill in its sections. Otherwise, I use the standard format.

## Examples

### Example 1: Feature PR

```
User: Generate a PR description for this branch
Assistant: Analyzing branch against main...

Commits found: 5
Files changed: 8
Lines: +245, -32

## Generated PR Description:

**Title:** feat(auth): add OAuth2 login with Google

## Summary
Add Google OAuth2 authentication as an alternative login method.
Users can now sign in with their Google account, reducing friction
for new user registration.

## PR Type
- [x] Feature
- [ ] Bug fix
- [ ] Refactoring

## Changes

### Backend
- `src/auth/oauth.ts` - OAuth2 client implementation
- `src/auth/routes.ts` - New `/auth/google` endpoint
- `src/config/oauth.ts` - Google OAuth configuration

### Frontend
- `src/components/LoginButton.tsx` - Google sign-in button
- `src/pages/Login.tsx` - OAuth callback handling

### Configuration
- `.env.example` - Added GOOGLE_CLIENT_ID, GOOGLE_SECRET

## Testing Instructions
1. Set up Google OAuth credentials in `.env`
2. Start the dev server: `npm run dev`
3. Click "Sign in with Google" on login page
4. Verify redirect and token exchange
5. Check user session is created

## Related Issues
Closes #42
Relates to #38

## Checklist
- [x] Tests added
- [x] Documentation updated
- [ ] Ready for review
```

### Example 2: Bug Fix PR

```
User: Generate PR description
Assistant: Analyzing branch...

Commits: 2
Files: 3
Lines: +12, -8

**Title:** fix(api): handle null response in user fetch

## Summary
Fix crash when API returns null for deleted users.
Previously, accessing properties on null response
caused runtime errors.

## PR Type
- [ ] Feature
- [x] Bug fix
- [ ] Refactoring

## Changes

### Source
- `src/services/user.ts` - Add null check before access

### Tests
- `tests/user.test.ts` - Add test for null response case

## Root Cause
API returns `null` instead of 404 for deleted users.
Code assumed response was always an object.

## Testing Instructions
1. Delete a user via admin panel
2. Try to fetch deleted user's profile
3. Verify graceful error message instead of crash

## Related Issues
Fixes #89
```

### Example 3: Breaking Change PR

```
User: Generate PR description - this has breaking changes
Assistant: Analyzing branch...

**Title:** feat(api)!: redesign authentication response

## Summary
Restructure authentication API response format to include
refresh tokens and standardize error codes.

## PR Type
- [x] Feature (Breaking Change)

## Breaking Changes

**Previous Response:**
```json
{"token": "xxx", "user": {...}}
```

**New Response:**
```json
{"accessToken": "xxx", "refreshToken": "yyy", "user": {...}}
```

## Migration Guide
1. Update token storage to handle both tokens
2. Implement refresh token rotation
3. Update error handling for new error codes

See `docs/migration-v2.md` for detailed guide.

## Related Issues
Closes #156
BREAKING CHANGE: Authentication response format changed
```

## Configuration

### PR Template Detection

I'll check these locations for templates:
1. `.github/pull_request_template.md`
2. `.github/PULL_REQUEST_TEMPLATE.md`
3. `docs/pull_request_template.md`
4. `pull_request_template.md`

### Base Branch Detection

Default comparison branch (in order):
1. `main`
2. `master`
3. `develop`
4. Current tracking branch

Override with: "Compare against `release/v2`"

## Output Checklist

Before finalizing PR description:

- [ ] Title follows conventional commit format
- [ ] Summary explains what and why
- [ ] All changed files categorized
- [ ] Testing instructions are specific
- [ ] Related issues linked
- [ ] Breaking changes documented
- [ ] Migration guide included (if breaking)
- [ ] Checklist items relevant to changes
