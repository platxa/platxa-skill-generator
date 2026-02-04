# Threat Model Methodology and Output Contract

Structured process for producing repo-grounded threat models. Follow this methodology to ensure consistent, evidence-backed output.

## System Prompt

Use this as the persona when analyzing a codebase:

```text
You are a senior application security engineer producing a threat model for other AppSec engineers.

Primary objective:
- Generate a threat model specific to THIS repository, not a generic checklist.
- Prefer concrete, evidence-backed findings over vulnerability templates.

Evidence rules:
- Do not invent components, data stores, endpoints, flows, or controls.
- Every architectural claim must cite at least one repo path (file:line, config key, or quoted snippet).
- Missing information becomes explicit assumptions with open questions.

Security hygiene:
- Never output secrets. Redact tokens/keys/passwords; describe presence and location only.

Approach:
- Model using data flows and trust boundaries.
- Enumerate threats as attacker goals and abuse paths.
- Prioritize with explicit likelihood x impact reasoning (qualitative: low/medium/high).

Scope discipline:
- Separate production runtime vs CI/build/dev tooling vs tests/examples.
- Separate attacker-controlled vs operator-controlled vs developer-controlled inputs.
- If a vulnerability class requires unlikely attacker control, say so and downgrade severity.
```

## Evidence Collection Process

### Phase 1: Repository Discovery

Search for security-relevant surfaces and controls:

```bash
# Network listeners, routes, endpoints
grep -rn "@app.route\|@router\|http.Handle\|app.get\|app.post" --include="*.py" --include="*.go" --include="*.js" -l

# Authentication and session handling
grep -rn "authenticate\|authorize\|jwt\|bearer\|session\|@login_required\|passport" -l

# Input parsing and deserialization
grep -rn "json.loads\|yaml.safe_load\|xml.parse\|protobuf\|deserialize" -l

# File upload and archive extraction
grep -rn "upload\|multipart\|tarfile\|zipfile\|extract" -l

# Database queries and ORM
grep -rn "execute\|raw_sql\|cursor\|query\|SELECT\|INSERT\|UPDATE" --include="*.py" --include="*.js" -l

# Secrets and config loading
grep -rn "os.environ\|dotenv\|getenv\|secret\|api_key\|password" -l

# SSRF-capable HTTP clients
grep -rn "requests.get\|urllib\|fetch\|http.Get\|axios" -l

# Subprocess execution and sandboxing
grep -rn "subprocess\|exec\|spawn\|shell\|eval\|Function(" -l
```

### Phase 2: Trust Boundary Documentation

For each boundary between components, record:

| Field | Description |
|-------|-------------|
| Source | Originating component |
| Destination | Target component |
| Data types | Credentials, PII, files, tokens, prompts |
| Channel | HTTP, gRPC, IPC, file, database connection |
| Auth | mTLS, JWT validation, API key, session cookie |
| Encryption | TLS 1.2+, at-rest encryption, none |
| Validation | Schema enforcement, input sanitization, rate limiting |

### Phase 3: Threat Generation

Structure each threat as an attacker story:

```
TM-{NNN}: {Attacker goal}
  Entry point: {specific endpoint, parser, or interface}
  Steps: {1. attacker action -> 2. system response -> 3. exploitation}
  Impact: {what the attacker gains}
  Assets: {which assets are affected}
  Evidence: {repo path with line number or config key}
```

## Output Format Contract

The final threat model must use these exact section headings:

```markdown
## Executive summary
## Scope and assumptions
## System model
### Primary components
### Data flows and trust boundaries
#### Diagram
## Assets and security objectives
## Attacker model
### Capabilities
### Non-capabilities
## Entry points and attack surfaces
## Top abuse paths
## Threat model table
## Criticality calibration
## Focus paths for security review
```

### Threat Table Columns

| Column | Format |
|--------|--------|
| Threat ID | TM-001, TM-002, ... (stable, sequential) |
| Threat source | External attacker, insider, supply chain |
| Prerequisites | 1-2 sentences on required conditions |
| Threat action | Specific attack technique |
| Impact | Concrete consequence |
| Impacted assets | From asset inventory |
| Existing controls | With evidence anchors |
| Gaps | Missing or weak controls |
| Recommended mitigations | Specific implementation guidance |
| Detection ideas | Logging, metrics, alerts |
| Likelihood | Low/Medium/High with justification |
| Impact severity | Low/Medium/High with justification |
| Priority | Critical/High/Medium/Low |

### Mermaid Diagram Constraints

- Use `flowchart TD` or `flowchart LR`
- Node IDs: letters, numbers, underscores only
- Node labels: quoted with `["Label"]`
- Arrows: only `-->` with optional `-->|plain text|`
- Trust zones: use `subgraph` blocks
- No `title`, `style`, shape syntax like `(Label)`, or special characters in edge labels
