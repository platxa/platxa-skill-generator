---
name: render-deploy
description: >-
  Deploy applications to Render by analyzing codebases, generating render.yaml
  Blueprints, and creating services via MCP. Use when the user wants to deploy,
  host, publish, or set up their application on Render's cloud platform.
allowed-tools:
  - AskUserQuestion
  - Bash
  - Glob
  - Grep
  - Read
  - WebFetch
  - Write
metadata:
  version: "1.0.0"
  author: "platxa-skill-generator"
  tags:
    - automation
    - deployment
    - render
    - cloud
    - devops
  provenance:
    upstream_source: "render-deploy"
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T15:20:37Z"
    generator_version: "1.0.0"
    intent_confidence: 0.76
---

# Deploy to Render

Deploy applications to Render using Blueprint files or direct MCP service creation.

## Overview

This skill automates Render deployments for any Git-backed application. It analyzes the codebase to detect framework, runtime, build/start commands, and dependencies, then generates the appropriate deployment configuration.

**What it automates:**
- Codebase analysis (framework, package manager, runtime detection)
- Blueprint generation (`render.yaml` for Infrastructure-as-Code)
- Direct service creation via MCP tools (single-service deployments)
- Dashboard deeplink generation for one-click deployment
- Post-deploy verification and basic troubleshooting

**Time saved:** ~15-30 minutes per deployment setup

## Triggers

### When to Run

Activate when the user wants to:
- Deploy an application to Render
- Create a `render.yaml` Blueprint file
- Set up hosting for their project on Render
- Create databases, cron jobs, or other Render resources
- Troubleshoot a failed Render deployment

### Manual Invocation

```
/render-deploy [options]
```

| Option | Description |
|--------|-------------|
| --blueprint | Force Blueprint method |
| --direct | Force Direct Creation via MCP |
| --dry-run | Generate config without deploying |

## Process

### Step 1: Gather Requirements

Ask the user two questions to reduce friction:
1. **Source**: Git repo or prebuilt Docker image?
2. **Scope**: Full provisioning (app + database + workers) or app-only?

If deploying a Docker image without a Git repo, guide the user to the Render Dashboard (MCP cannot create image-backed services).

### Step 2: Choose Deployment Method

| Method | Best For | Requires |
|--------|----------|----------|
| **Blueprint** | Multi-service apps, IaC workflows, databases | Git repo with render.yaml |
| **Direct Creation** | Single services, quick prototypes | MCP tools configured |

**Decision rule** (apply automatically unless user specifies):

- **Direct Creation** when ALL true: single service, no workers/cron, no databases, simple env vars, and MCP tools are available
- **Blueprint** when ANY true: multiple services, databases needed, cron/workers, reproducible IaC desired, monorepo

Default to Blueprint if unclear.

### Step 3: Verify Prerequisites

Run checks in order:

```bash
# 1. Verify Git remote exists
git remote -v

# 2. Check MCP availability (for Direct Creation)
# Try: list_services()

# 3. Check Render CLI (for Blueprint validation)
render --version

# 4. Check authentication (CLI fallback)
render whoami -o json
```

If MCP is not configured, offer setup instructions for the user's AI tool (Claude Code, Cursor, Codex). See [references/direct-creation.md](references/direct-creation.md) for MCP setup details.

### Step 4: Analyze Codebase

Detect framework, runtime, package manager, build/start commands, environment variables, and database requirements. Use the detection rules in [references/codebase-analysis.md](references/codebase-analysis.md).

### Step 5A: Blueprint Path

1. **Generate render.yaml** following the specification in [references/blueprint-spec.md](references/blueprint-spec.md)
   - Default to `plan: free` unless user specifies otherwise
   - Mark secrets with `sync: false`
   - Use appropriate service types from [references/service-config.md](references/service-config.md)

2. **Validate** (if CLI available):
   ```bash
   render blueprints validate
   ```

3. **Commit and push**:
   ```bash
   git add render.yaml
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

4. **Generate deeplink** from the Git remote URL:
   ```bash
   git remote get-url origin
   ```
   Convert SSH to HTTPS if needed, then format:
   `https://dashboard.render.com/blueprint/new?repo=REPOSITORY_URL`

5. **Guide user** through Dashboard: OAuth, name Blueprint, fill secrets, click Apply.

### Step 5B: Direct Creation Path

1. **Create resources via MCP** using the commands in [references/direct-creation.md](references/direct-creation.md)
2. **Configure environment variables** after creation
3. Services with autoDeploy deploy automatically

### Step 6: Verify Deployment

Run post-deploy checks:
1. Confirm deploy status is `live`
2. Hit health endpoint and verify 200 response
3. Scan error logs for failure signatures
4. Verify env vars and port binding (0.0.0.0:$PORT)

See [references/operations.md](references/operations.md) for verification commands and error patterns.

## Verification

### Success Indicators

- Deploy status shows `live`
- Health endpoint returns 200
- No error-level log entries in recent logs
- All required env vars are set
- Service is accessible at its public URL

### Failure Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Port binding error | Not binding to 0.0.0.0:$PORT | Fix host/port in app code |
| Build timeout | Slow deps or wrong command | Use npm ci, remove unused deps |
| Missing env vars | Not declared in config | Add to render.yaml or via MCP |
| DB connection refused | Wrong connection string | Use fromDatabase for internal URLs |
| Health check timeout | No health endpoint | Add /health returning 200 |
| OOM (exit 137) | Exceeded memory limit | Reduce usage or upgrade plan |
| SPA 404 on routes | Missing rewrite rules | Add rewrite rule for SPA |

## Examples

### Example 1: Deploy Node.js API with PostgreSQL (Blueprint)

```
Prompt: Deploy my Express app to Render with a database

Response: [Analyzes package.json, detects Express + pg]
Multiple services detected (web + database) - using Blueprint method.
Generated render.yaml with web service and PostgreSQL.
Validated with render blueprints validate.
Committed and pushed render.yaml.
Blueprint deeplink: https://dashboard.render.com/blueprint/new?repo=...
Click the link, fill in secrets, and click Apply to deploy.
```

### Example 2: Quick Static Site Deploy (Direct Creation)

```
Prompt: Host my React app on Render

Response: [Detects single static site, MCP available]
Single service with no database - using Direct Creation.
Created static site via create_static_site MCP tool.
Build command: npm ci and npm run build
Publish path: ./build
Service deploying automatically. Checking status...
Deploy is live at https://my-frontend.onrender.com
```

### Example 3: Dry Run Preview

```
Prompt: /render-deploy --dry-run

Response: [Analyzes codebase without deploying]
Framework: FastAPI (Python)
Runtime: python
Build: pip install -r requirements.txt
Start: uvicorn main:app --host 0.0.0.0 --port $PORT
Method: Blueprint (database detected)
Preview of render.yaml generated. Review and approve to proceed.
```

## Safety

### Idempotency

Blueprint generation is idempotent: running the skill again overwrites render.yaml with the same content. Direct Creation is NOT idempotent: running it again creates duplicate services.

### Reversibility

- Blueprint: Delete render.yaml and remove services from Render Dashboard
- Direct Creation: Delete services from Render Dashboard or via MCP

### Prerequisites

Before running, ensure:
- [ ] Code is pushed to a Git remote (GitHub, GitLab, or Bitbucket)
- [ ] You have a Render account
- [ ] MCP tools are configured (for Direct Creation) or CLI is installed (for Blueprint validation)

### Network Access

When sandboxing blocks deployment network calls, rerun with `sandbox_permissions=require_escalated`. The deploy requires escalated network access for outbound requests to Render.