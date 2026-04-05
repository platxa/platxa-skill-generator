# Skill Packs Pattern

Group related skills for selective enablement. Anthropic recommends evaluating if you have
more than 20-50 skills enabled simultaneously — packs help organize and manage large catalogs.

## Why Packs?

- Too many skills enabled simultaneously causes large context and degraded responses
- Users need related skills together but don't want to install them individually
- Packs provide a curated experience for specific domains

## Pack Definition

A pack is a JSON file listing related skills with metadata:

```json
{
  "name": "platxa-k8s-pack",
  "description": "Kubernetes operations, scaling, and monitoring for Platxa platform",
  "skills": [
    "platxa-k8s-ops",
    "platxa-k8s-scaling",
    "platxa-monitoring"
  ],
  "optional": [
    "platxa-logging"
  ]
}
```

## Pack Categories

| Pack | Skills | Use Case |
|------|--------|----------|
| Infrastructure | k8s-ops, k8s-scaling, monitoring, logging | Platform ops |
| Security | jwt-auth, secrets-management | Auth and secrets |
| Frontend | frontend-builder, monaco-config, testing | UI development |
| Backend | sidecar-builder, error-handling, yjs-server | Service development |
| Quality | code-review, testing, code-documenter | Code quality |

## Installation

```bash
# Install all skills in a pack
./scripts/install-from-catalog.sh --pack platxa-k8s-pack

# List available packs
./scripts/install-from-catalog.sh --list-packs

# Install pack with optional skills
./scripts/install-from-catalog.sh --pack platxa-k8s-pack --include-optional
```

## Guidelines

- Keep packs to 3-5 core skills (plus optional extras)
- Document what the pack enables as a combined capability
- Use `suggests` relationships between skills within a pack
- Consider context budget: total tokens across all pack skills should be reasonable
