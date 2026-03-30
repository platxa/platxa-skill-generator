# Composition Patterns

Three levels of skill composition, from strongest to weakest coupling.

## Decision Framework

```
Does this skill BREAK without the other?
  ├── Yes → depends-on
  └── No
       Does this skill BENEFIT from the other?
         ├── Yes → suggests
         └── No → No relationship (don't declare anything)
```

## Level 1: depends-on (Hard Dependency)

**When**: Skill will not work correctly without the dependency.

```yaml
depends-on:
  - platxa-logging  # Our scripts call logging setup from this skill
```

**Characteristics**:
- Checked at install time (warning if missing)
- Auto-installed from catalog when available
- Validated by `check-dependencies.sh`
- Cycle detection prevents A→B→A

**Examples**:
- A deployment skill that requires a specific logging format
- A validator that references rules from another skill's references

**Anti-pattern**: Don't use for "nice to have." If your skill works fine alone, use `suggests`.

## Level 2: suggests (Soft Recommendation)

**When**: Skill works alone but is better with companions.

```yaml
suggests:
  - platxa-testing    # Generate tests for the code we produce
  - platxa-monitoring # Add observability to generated services
```

**Characteristics**:
- Shown after installation as recommendations
- Never blocks installation
- Displayed in dependency graph (dashed edges)

**Examples**:
- Builder skills suggesting testing/logging/monitoring patterns
- Skills in the same domain (k8s-ops + k8s-scaling)
- Complementary concerns (auth + secrets management)

## Level 3: No Relationship

**When**: Skills are independent. Most skills fall here.

Don't declare relationships that don't exist. A test-generator skill doesn't need to suggest a commit-message skill just because they're both in the catalog.

## Catalog Relationships

Current catalog composition map:

| Skill | suggests |
|-------|----------|
| platxa-sidecar-builder | logging, error-handling, testing, yjs-server |
| platxa-frontend-builder | testing, monaco-config |
| platxa-k8s-scaling | k8s-ops, monitoring |
| platxa-monitoring | logging |
| platxa-jwt-auth | secrets-management |
| platxa-yjs-server | sidecar-builder |

No catalog skills use `depends-on` — they are all independently functional.

## Tools

| Command | Purpose |
|---------|---------|
| `check-dependencies.sh <dir>` | Verify depends-on satisfied |
| `detect-circular-deps.sh` | Find cycles in dependency graph |
| `skill-graph.sh` | Visualize graph in DOT format |
| `install-from-catalog.sh` | Auto-install deps + topological ordering |
