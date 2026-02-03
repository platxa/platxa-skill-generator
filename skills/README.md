# Claude Code Skills Registry

> A curated, quality-verified collection of production-ready skills for Claude Code CLI.
>
> **Maintained by**: [Platxa](https://platxa.com) | **License**: MIT | **Compatible with**: `npx skills`

**37 skills** across **13 categories** — 21 local, 16 external

---

## Quick Install

```bash
# Clone the repository
git clone https://github.com/platxa/platxa-skill-generator.git
cd platxa-skill-generator

# Install a single skill
./scripts/install-from-catalog.sh <skill-name>

# Install to project instead of user directory
./scripts/install-from-catalog.sh <skill-name> --project

# Install all essential skills (tier 1)
./scripts/install-from-catalog.sh --all --tier 1

# List all available skills
./scripts/install-from-catalog.sh --list
```

---

## Skills Index

| Skill | Trust | Description | Category | Tier | Tokens | Source | Install |
|-------|-------|-------------|----------|------|--------|--------|---------|
| [platxa-error-handling](skills/platxa-error-handling/SKILL.md) | ![trust](badges/platxa-error-handling.svg) | Guide for structured error handling across Platxa stack. Covers error types, ... | backend | Internal | 7,013 | Platxa | `./scripts/install-from-catalog.sh platxa-error-handling` |
| [platxa-sidecar-builder](skills/platxa-sidecar-builder/SKILL.md) | ![trust](badges/platxa-sidecar-builder.svg) | Build Node.js sidecar services for real-time code editing platforms. Covers f... | backend | Internal | 7,475 | Platxa | `./scripts/install-from-catalog.sh platxa-sidecar-builder` |
| [platxa-yjs-server](skills/platxa-yjs-server/SKILL.md) | ![trust](badges/platxa-yjs-server.svg) | Yjs WebSocket server implementation guide for real-time collaboration. Config... | backend | Internal | 5,407 | Platxa | `./scripts/install-from-catalog.sh platxa-yjs-server` |
| [code-documenter](skills/code-documenter/SKILL.md) | ![trust](badges/code-documenter.svg) | Automatically generates and improves code documentation across Python, JavaSc... | devtools | Internal | 3,605 | Platxa | `./scripts/install-from-catalog.sh code-documenter` |
| [platxa-frontend-builder](skills/platxa-frontend-builder/SKILL.md) | ![trust](badges/platxa-frontend-builder.svg) | Generate production-ready React/Next.js components for Platxa platform. Creat... | frontend | Internal | 7,468 | Platxa | `./scripts/install-from-catalog.sh platxa-frontend-builder` |
| [platxa-monaco-config](skills/platxa-monaco-config/SKILL.md) | ![trust](badges/platxa-monaco-config.svg) | Monaco editor configuration guide for Platxa platform. Configure themes, keyb... | frontend | Internal | 5,873 | Platxa | `./scripts/install-from-catalog.sh platxa-monaco-config` |
| [platxa-preview-service](skills/platxa-preview-service/SKILL.md) | ![trust](badges/platxa-preview-service.svg) | Live preview service for Odoo themes with real-time token updates, SCSS compi... | frontend | Internal | 1,764 | Platxa | `./scripts/install-from-catalog.sh platxa-preview-service` |
| [platxa-token-sync](skills/platxa-token-sync/SKILL.md) | ![trust](badges/platxa-token-sync.svg) | Transform Brand Kit design tokens (OKLCH colors, spacing, typography) into Od... | frontend | Internal | 6,793 | Platxa | `./scripts/install-from-catalog.sh platxa-token-sync` |
| [commit-message](skills/commit-message/SKILL.md) | ![trust](badges/commit-message.svg) | Generate conventional commit messages by analyzing staged git changes. Detect... | git | Internal | 2,475 | Platxa | `./scripts/install-from-catalog.sh commit-message` |
| [pr-description](skills/pr-description/SKILL.md) | ![trust](badges/pr-description.svg) | Generate comprehensive pull request descriptions by analyzing git commits and... | git | Internal | 2,467 | Platxa | `./scripts/install-from-catalog.sh pr-description` |
| [platxa-k8s-ops](skills/platxa-k8s-ops/SKILL.md) | ![trust](badges/platxa-k8s-ops.svg) | Kubernetes operations automation for Platxa platform. Debug instances, manage... | infrastructure | Internal | 6,064 | Platxa | `./scripts/install-from-catalog.sh platxa-k8s-ops` |
| [platxa-k8s-scaling](skills/platxa-k8s-scaling/SKILL.md) | ![trust](badges/platxa-k8s-scaling.svg) | Kubernetes scaling patterns for Platxa platform. Configure scale-to-zero with... | infrastructure | Internal | 5,551 | Platxa | `./scripts/install-from-catalog.sh platxa-k8s-scaling` |
| [platxa-logging](skills/platxa-logging/SKILL.md) | ![trust](badges/platxa-logging.svg) | Structured logging and correlation ID patterns for Platxa services. Covers Py... | observability | Internal | 6,683 | Platxa | `./scripts/install-from-catalog.sh platxa-logging` |
| [platxa-monitoring](skills/platxa-monitoring/SKILL.md) | ![trust](badges/platxa-monitoring.svg) | Observability guide for Platxa platform using Prometheus metrics and Loki log... | observability | Internal | 6,739 | Platxa | `./scripts/install-from-catalog.sh platxa-monitoring` |
| [platxa-odoo-blog](skills/platxa-odoo-blog/SKILL.md) | ![trust](badges/platxa-odoo-blog.svg) | Generate Odoo blog templates with post layouts, category pages, author profil... | odoo | Internal | 2,953 | Platxa | `./scripts/install-from-catalog.sh platxa-odoo-blog` |
| [platxa-odoo-form](skills/platxa-odoo-form/SKILL.md) | ![trust](badges/platxa-odoo-form.svg) | Generate Odoo website forms with CRM lead integration, field validation, cond... | odoo | Internal | 4,342 | Platxa | `./scripts/install-from-catalog.sh platxa-odoo-form` |
| [platxa-odoo-page](skills/platxa-odoo-page/SKILL.md) | ![trust](badges/platxa-odoo-page.svg) | Generate complete Odoo website pages (About, Contact, Services, Team, FAQ, Pr... | odoo | Internal | 6,834 | Platxa | `./scripts/install-from-catalog.sh platxa-odoo-page` |
| [platxa-jwt-auth](skills/platxa-jwt-auth/SKILL.md) | ![trust](badges/platxa-jwt-auth.svg) | Generate RS256 JWT authentication with JWKS endpoint for Platxa services. Cre... | security | Internal | 6,318 | Platxa | `./scripts/install-from-catalog.sh platxa-jwt-auth` |
| [platxa-secrets-management](skills/platxa-secrets-management/SKILL.md) | ![trust](badges/platxa-secrets-management.svg) | Fernet encryption, Kubernetes secrets, and secure token patterns for Platxa s... | security | Internal | 6,971 | Platxa | `./scripts/install-from-catalog.sh platxa-secrets-management` |
| [platxa-testing](skills/platxa-testing/SKILL.md) | ![trust](badges/platxa-testing.svg) | Automated testing patterns for Platxa platform using pytest, Vitest, and E2E ... | testing | Internal | 6,090 | Platxa | `./scripts/install-from-catalog.sh platxa-testing` |
| [test-generator](skills/test-generator/SKILL.md) | ![trust](badges/test-generator.svg) | Generate unit tests for existing code across Python, JavaScript/TypeScript, J... | testing | Internal | 3,392 | Platxa | `./scripts/install-from-catalog.sh test-generator` |
| [systematic-debugging](skills/systematic-debugging/SKILL.md) | ![trust](badges/systematic-debugging.svg) | Use when encountering any bug, test failure, or unexpected behavior, before p... | debugging | Essential | 2,330 | Obra | `./scripts/install-from-catalog.sh systematic-debugging` |
| [frontend-design](skills/frontend-design/SKILL.md) | ![trust](badges/frontend-design.svg) | Create distinctive, production-grade frontend interfaces with high design qua... | design | Essential | 1,084 | Anthropic | `./scripts/install-from-catalog.sh frontend-design` |
| [mcp-builder](skills/mcp-builder/SKILL.md) | ![trust](badges/mcp-builder.svg) | Guide for creating high-quality MCP (Model Context Protocol) servers that ena... | devtools | Essential | 1,922 | Anthropic | `./scripts/install-from-catalog.sh mcp-builder` |
| [react-best-practices](skills/react-best-practices/SKILL.md) | ![trust](badges/react-best-practices.svg) | React and Next.js performance optimization guidelines from Vercel Engineering... | frontend | Essential | 1,488 | Vercel | `./scripts/install-from-catalog.sh react-best-practices` |
| [web-artifacts-builder](skills/web-artifacts-builder/SKILL.md) | ![trust](badges/web-artifacts-builder.svg) | Suite of tools for creating elaborate, multi-component claude.ai HTML artifac... | frontend | Essential | 702 | Anthropic | `./scripts/install-from-catalog.sh web-artifacts-builder` |
| [test-driven-development](skills/test-driven-development/SKILL.md) | ![trust](badges/test-driven-development.svg) | Use when implementing any feature or bugfix, before writing implementation code | testing | Essential | 2,420 | Obra | `./scripts/install-from-catalog.sh test-driven-development` |
| [webapp-testing](skills/webapp-testing/SKILL.md) | ![trust](badges/webapp-testing.svg) | Toolkit for interacting with and testing local web applications using Playwri... | testing | Essential | 881 | Anthropic | `./scripts/install-from-catalog.sh webapp-testing` |
| [executing-plans](skills/executing-plans/SKILL.md) | ![trust](badges/executing-plans.svg) | Use when you have a written implementation plan to execute in a separate sess... | workflow | Essential | 562 | Obra | `./scripts/install-from-catalog.sh executing-plans` |
| [verification-before-completion](skills/verification-before-completion/SKILL.md) | ![trust](badges/verification-before-completion.svg) | Use when about to claim work is complete, fixed, or passing, before committin... | workflow | Essential | 987 | Obra | `./scripts/install-from-catalog.sh verification-before-completion` |
| [writing-plans](skills/writing-plans/SKILL.md) | ![trust](badges/writing-plans.svg) | Use when you have a spec or requirements for a multi-step task, before touchi... | workflow | Essential | 795 | Obra | `./scripts/install-from-catalog.sh writing-plans` |
| [web-design-guidelines](skills/web-design-guidelines/SKILL.md) | ![trust](badges/web-design-guidelines.svg) | Review UI code for Web Interface Guidelines compliance. Use when asked to "re... | design | Useful | 268 | Vercel | `./scripts/install-from-catalog.sh web-design-guidelines` |
| [react-native-skills](skills/react-native-skills/SKILL.md) | ![trust](badges/react-native-skills.svg) | React Native and Expo best practices for building performant mobile apps. Use... | mobile | Useful | 1,041 | Vercel | `./scripts/install-from-catalog.sh react-native-skills` |
| [brainstorming](skills/brainstorming/SKILL.md) | ![trust](badges/brainstorming.svg) | You MUST use this before any creative work - creating features, building comp... | workflow | Useful | 522 | Obra | `./scripts/install-from-catalog.sh brainstorming` |
| [dispatching-parallel-agents](skills/dispatching-parallel-agents/SKILL.md) | ![trust](badges/dispatching-parallel-agents.svg) | Use when facing 2+ independent tasks that can be worked on without shared sta... | workflow | Useful | 1,405 | Obra | `./scripts/install-from-catalog.sh dispatching-parallel-agents` |
| [subagent-driven-development](skills/subagent-driven-development/SKILL.md) | ![trust](badges/subagent-driven-development.svg) | Use when executing implementation plans with independent tasks in the current... | workflow | Useful | 2,269 | Obra | `./scripts/install-from-catalog.sh subagent-driven-development` |
| [using-superpowers](skills/using-superpowers/SKILL.md) | ![trust](badges/using-superpowers.svg) | Use when starting any conversation - establishes how to find and use skills, ... | workflow | Experimental | 925 | Obra | `./scripts/install-from-catalog.sh using-superpowers` |

---

## Categories

| Category | Skills | Description |
|----------|--------|-------------|
| backend | 3 | Server-side services and APIs |
| debugging | 1 | Bug diagnosis and resolution |
| design | 2 | UI/UX design and frontend aesthetics |
| devtools | 2 | Developer productivity tools |
| frontend | 6 | Client-side components and UI |
| git | 2 | Git workflow automation |
| infrastructure | 2 | Kubernetes and cloud operations |
| mobile | 1 | Mobile app development |
| observability | 2 | Logging, monitoring, and tracing |
| odoo | 3 | Odoo ERP platform development |
| security | 2 | Authentication, encryption, secrets |
| testing | 4 | Test generation and automation |
| workflow | 7 | Agent workflow and orchestration |

---

## Skill Tiers

| Tier | Label | Description | Count |
|------|-------|-------------|-------|
| 0 | Internal | Platxa internal skills (local only) | 21 |
| 1 | Essential | Essential, high-quality skills | 10 |
| 2 | Useful | Useful, recommended skills | 5 |
| 3 | Experimental | Experimental or niche skills | 1 |

Install by tier: `./scripts/install-from-catalog.sh --all --tier 1`

---

## Installation Methods

### Method 1: Install Script (Recommended)

```bash
./scripts/install-from-catalog.sh <skill-name> [--user|--project]
```

| Flag | Description |
|------|-------------|
| `--user` | Install to `~/.claude/skills/` (default) |
| `--project` | Install to `.claude/skills/` |
| `--list` | List all available skills |
| `--all` | Install all skills |
| `--force` | Overwrite existing without prompting |
| `--tier N` | Only install skills with tier <= N |
| `--category X` | Only install skills matching category X |

### Method 2: Manual Copy

```bash
cp -r skills/<skill-name> ~/.claude/skills/
```

### Method 3: Symbolic Link (Development)

```bash
ln -s $(pwd)/skills/<skill-name> ~/.claude/skills/<skill-name>
```

---

## Quality Standards

All skills meet these requirements:

| Requirement | Threshold |
|-------------|-----------|
| SKILL.md exists | Required |
| Valid YAML frontmatter | Required |
| Name (hyphen-case) | <= 64 chars |
| Description | <= 1,024 chars |
| Token budget (SKILL.md) | <= 5,000 recommended |
| Token budget (total) | <= 15,000 recommended |
| All validations pass | Required |

```bash
# Validate a skill
./scripts/validate-all.sh skills/<skill-name>

# Check token count
python3 scripts/count-tokens.py skills/<skill-name>
```

---

## External vs Local Skills

- **Local** (21 skills): Created and maintained in this repo. Never overwritten by sync.
- **External** (16 skills): Synced from upstream repos (Anthropic, Vercel, Obra).

```bash
# Sync external skills from upstream
./scripts/sync-catalog.sh sync

# List sources
./scripts/sync-catalog.sh list-external
./scripts/sync-catalog.sh list-local
```

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full PR-based submission guide.

```bash
# Quick validation before submitting
./scripts/validate-all.sh skills/my-skill-name
python3 scripts/count-tokens.py skills/my-skill-name
python3 scripts/check-duplicates.py skills/my-skill-name
```

---

## License

MIT License - See [LICENSE](../LICENSE) for details.

---

*Auto-generated from registry data. 37 skills across 13 categories.*
