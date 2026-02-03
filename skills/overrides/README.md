# Catalog Overrides

Override files for upstream skills synced via `sync-catalog.sh`. Overrides are applied automatically during sync without modifying upstream content directly.

## Override Types

### File Overrides

Place files in `overrides/<skill-name>/` to replace or add files in the synced skill directory. Any file except `patch.yaml` is copied into the skill directory after sync.

```
overrides/
  frontend-design/
    references/extra-guide.md    # Added to skill's references/
```

### Section Injection (patch.yaml)

Use `patch.yaml` to inject missing sections into a skill's `SKILL.md`. Sections are only added if the `## Heading` does not already exist in the file.

**Format:**

```yaml
# patch.yaml
sections:
  Overview: |
    Description of what the skill does.

  Workflow: |
    1. Step one
    2. Step two

  Examples: |
    ```
    Example usage here
    ```

  Output Checklist: |
    - [ ] Checklist item
```

**Rules:**

- Keys are section headings (injected as `## Heading`)
- Values are the section body (YAML block scalar `|`)
- Existing sections are never overwritten
- Sections are appended at the end of SKILL.md

### When to Use Overrides

- Bring upstream skills up to strict validation profile (add missing Overview, Workflow, Examples, Output Checklist)
- Add company-specific references or scripts
- Patch upstream content without forking

## Existing Overrides

| Skill | Override | Purpose |
|-------|----------|---------|
| `frontend-design` | `patch.yaml` | Adds Overview, Workflow, Examples, Output Checklist for strict profile |
