## Description

<!-- Brief description of what this PR does -->

## PR Type

- [ ] New skill submission
- [ ] Skill improvement/fix
- [ ] Documentation
- [ ] Infrastructure/CI
- [ ] Other

## For New Skills

<!-- Complete this section if adding a new skill to the catalog -->

### Skill Details

- **Name**: <!-- e.g., code-documenter -->
- **Type**: <!-- Builder / Guide / Automation / Analyzer / Validator -->
- **Category**: <!-- Code Quality / Git Workflow / Testing / Documentation / DevOps -->

### Checklist

- [ ] SKILL.md has valid YAML frontmatter
- [ ] Name is hyphen-case and <= 64 characters
- [ ] Description is <= 1024 characters
- [ ] `./scripts/validate-all.sh skills/<skill-name>` passes
- [ ] Token budget within limits (`python3 scripts/count-tokens.py skills/<skill-name>`)
- [ ] No placeholder content (TODO, TBD, etc.)
- [ ] Examples show realistic usage
- [ ] Tested on real projects
- [ ] Updated `skills/README.md` with new skill entry

### Testing

<!-- Describe how you tested this skill -->

1.
2.
3.

## For Other Changes

### What Changed

<!-- List the changes made -->

-
-

### Testing

<!-- How was this tested? -->

---

## Screenshots

<!-- If applicable, add screenshots -->
