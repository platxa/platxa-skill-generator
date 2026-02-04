# Security Controls and Asset Categories

Lightweight checklist for consistent threat model outputs. Prefer concrete, system-specific items over generic text.

## Asset Categories

Select only categories that apply to the target repository:

| Category | Examples | Security Objective |
|----------|----------|--------------------|
| User data | PII, content, uploads, form submissions | Confidentiality, Integrity |
| Authentication artifacts | Passwords, tokens, sessions, cookies, OAuth state | Confidentiality, Integrity |
| Authorization state | Roles, policies, ACLs, permission matrices | Integrity |
| Secrets and keys | API keys, signing keys, encryption keys, certificates | Confidentiality |
| Configuration | Feature flags, environment variables, deployment configs | Integrity, Availability |
| Models and weights | ML model files, training data, inference configs | Integrity, Confidentiality |
| Source code and build artifacts | Compiled binaries, container images, release packages | Integrity |
| Audit logs and telemetry | Access logs, error traces, metrics, alert configs | Integrity, Availability |
| Availability-critical resources | Queues, caches, rate limit state, compute budgets | Availability |
| Tenant isolation boundaries | Namespace metadata, tenant IDs, routing rules | Confidentiality, Integrity |

## Security Control Categories

### Identity and Access

- AuthN mechanisms (OAuth2, SAML, OIDC, API keys, mTLS)
- AuthZ enforcement (RBAC, ABAC, policy engines)
- Session handling (token rotation, expiry, revocation)
- Key rotation schedules and secret management (Vault, KMS, SOPS)

### Input Protection

- Schema validation at API boundaries (JSON Schema, protobuf, OpenAPI)
- Parsing hardening (safe YAML/XML/JSON loaders, size limits)
- Upload scanning (file type validation, antivirus, size caps)
- Sandboxing for untrusted content (iframe sandbox, WebAssembly, seccomp)

### Network Safeguards

- TLS 1.2+ enforcement on all external and inter-service connections
- Network policies (Kubernetes NetworkPolicy, security groups, firewall rules)
- WAF rules (OWASP CRS, custom rules for application-specific patterns)
- Rate limiting per endpoint, per user, with burst caps
- DoS protection (connection limits, request timeouts, circuit breakers)

### Data Protection

- Encryption at rest (database-level, file-level, field-level)
- Encryption in transit (TLS, mTLS between services)
- Tokenization and redaction for sensitive fields
- Data retention and deletion policies

### Isolation

- Process sandboxing (seccomp, AppArmor, SELinux profiles)
- Container boundaries (non-root, read-only filesystem, dropped capabilities)
- Tenant isolation (database-per-tenant, row-level security, namespace separation)
- Privilege boundaries (least privilege, service accounts, role separation)

### Observability

- Audit logging for security-relevant actions (auth events, data access, config changes)
- Alerting on anomalous patterns (failed auth spikes, unusual data access)
- Tamper resistance for log storage (append-only, separate write permissions)
- Metrics for security SLIs (auth failure rate, request latency p99, error rate)

### Supply Chain

- Dependency pinning (lockfiles, hash verification)
- SBOMs and vulnerability scanning (Trivy, Snyk, Dependabot)
- Provenance and signing (Sigstore, cosign for container images)
- CI pipeline hardening (least privilege runners, no secrets in logs)

## Mitigation Phrasing Patterns

Use specific language that maps controls to locations:

```
Enforce schema validation at {boundary} for {payload} before {component}.
Require authZ check for {action} on {resource} in {service}.
Isolate {parser/component} in a sandbox with {resource limits}.
Rate limit {endpoint} by {key} with burst cap of {N} requests per {interval}.
Encrypt {data} at rest using {key management} and rotate keys every {interval}.
Add audit logging for {action} in {component} with {alert threshold}.
Pin {dependency} to {version} with hash verification in {lockfile}.
```

## Evidence Anchor Patterns

When documenting controls or gaps, always cite repo evidence:

```
Existing control: JWT validation in src/auth/middleware.py:L28 (verify_exp=True, verify_aud=True)
Gap: No rate limiting on POST /api/upload (routes/upload.py:L15, no middleware applied)
Recommended: Add rate_limit(100, per="minute") decorator at routes/upload.py:L15
```
