# Cross-Language Security Best Practices

Condensed security checklist covering Python (FastAPI/Django/Flask), JavaScript/TypeScript (Express/Next.js/React/Vue), and Go backends. Organized by vulnerability category with framework-specific guidance.

## Safety Constraints

- MUST NOT output, log, or commit secrets (API keys, passwords, tokens, signing keys)
- MUST NOT weaken security as a fix (disabling auth, permissive CORS, skipping validation)
- MUST cite file paths and code snippets as evidence for findings
- MUST note "verify at runtime" when infrastructure protections may exist

## Secure Baseline (All Frameworks)

| Area | Requirement |
|------|-------------|
| Debug | Disabled in production; no stack traces to clients |
| Auth | Explicit enforcement on all routes via middleware |
| CORS | Disabled unless needed; strict allowlist when enabled |
| Cookies | `HttpOnly`, `SameSite=Lax` minimum; `Secure` only over HTTPS |
| CSRF | Token-based when using cookie authentication |
| Secrets | From environment or vault only; never in source |
| Dependencies | Pinned versions; regular vulnerability scanning |
| Rate limiting | On auth endpoints and public APIs |
| IDs | Use UUID4 or random hex for public resource identifiers, not auto-increment |

## Authentication and Authorization

- Auth MUST be enforced via middleware/dependencies, not per-handler opt-in
- Passwords MUST use bcrypt/argon2/scrypt with appropriate cost
- JWTs MUST validate signature, expiry, issuer, and audience
- Resource ownership MUST be verified on every state-changing request
- Session tokens MUST be regenerated after privilege escalation

## Injection Prevention

### SQL Injection
- Use parameterized queries or ORM exclusively
- Never concatenate user input into query strings
- Python: `cursor.execute("SELECT * FROM t WHERE id = %s", (id,))`
- Go: `db.Query("SELECT * FROM t WHERE id = $1", id)`

### Command Injection
- Avoid `os.system()`, `eval()`, `exec()`, `child_process.exec()`
- Python: `subprocess.run(["cmd", arg], shell=False)`
- Node.js: `execFile("cmd", [arg])` instead of `exec("cmd " + arg)`
- Go: `exec.Command("cmd", arg)` -- never through shell

### Template Injection (SSTI)
- Never pass user input as template source
- Use auto-escaping in all template engines

### Path Traversal
- Validate and canonicalize all file paths
- Reject `..` sequences
- Resolve to absolute path and verify within allowed directory

### Unsafe Deserialization
- Never unpickle or unserialize untrusted data
- Python: avoid `pickle.load()`, use `yaml.safe_load()` not `yaml.load()`
- Use JSON for data interchange

## XSS Prevention

- React JSX auto-escapes by default; never use `dangerouslySetInnerHTML` with user input
- Vue templates auto-escape; avoid `v-html` with untrusted data
- Jinja2: use `{{ var | e }}` or enable auto-escaping globally
- Sanitize rich content with DOMPurify (browser) or bleach (Python)
- Set `Content-Security-Policy` header to restrict inline scripts

## CSRF Protection

- Required when cookies carry auth (session cookies)
- Not needed for pure header-token APIs (Bearer tokens in Authorization header)
- Django: `{% csrf_token %}` in forms + middleware
- FastAPI: implement explicitly if using cookie-based sessions
- Express: `csurf` or `csrf-csrf` middleware
- Next.js: verify `Origin` header on Server Actions

## File Upload Security

- Validate MIME type AND magic bytes (not just file extension)
- Store outside web root with random generated filenames
- Enforce server-side size limits
- Scan for malware on sensitive systems
- Never execute uploaded files

## Secrets Management

- Load from environment variables (`os.environ`, `process.env`, `os.Getenv`)
- Never hardcode in source, config files, or Docker images
- Rotate compromised secrets immediately
- Exclude `.env` and credential files in `.gitignore`

## Framework-Specific Hardening

### Python -- FastAPI
- Disable OpenAPI docs in production: `docs_url=None, redoc_url=None`
- Use `Depends()` for auth enforcement on all routes
- Validate request bodies with Pydantic models (type coercion + validation)

### Python -- Django
- `DEBUG = False` in production
- `ALLOWED_HOSTS` explicitly set
- `SECRET_KEY` loaded from environment
- `SECURE_BROWSER_XSS_FILTER = True`
- `X_FRAME_OPTIONS = "DENY"`

### Python -- Flask
- `app.secret_key` from environment, never hardcoded
- Never `app.run(debug=True)` in production
- Use `flask-talisman` for security headers

### JavaScript -- Express
- Use `helmet()` middleware for security headers
- Set `trust proxy` correctly behind reverse proxies
- Use `express-rate-limit` on auth endpoints

### JavaScript -- Next.js
- Server Actions: validate all input server-side
- Never trust client-side data
- Use `next/headers` for CSRF verification

### JavaScript -- React/Vue
- JSX and Vue templates auto-escape; avoid raw HTML injection APIs
- Sanitize with DOMPurify when rich HTML is required
- Never store tokens in localStorage; use httpOnly cookies

### Go
- Use `html/template` (auto-escapes) not `text/template` for HTML
- Set timeouts on `http.Server`: `ReadTimeout`, `WriteTimeout`, `IdleTimeout`
- Use `crypto/rand` not `math/rand` for security-sensitive values
- SQL: `db.Query(query, args...)` with placeholders, never `fmt.Sprintf`

## TLS and Cookie Guidance

- Do not flag missing TLS in development environments
- `Secure` cookie flag breaks non-HTTPS environments; use env-based toggle
- Avoid recommending HSTS without discussing permanent browser caching risks
- Provide `SECURE_COOKIES=true/false` environment variable pattern

## Audit Finding Format

```
[SEC-NNN] Severity: CRITICAL|HIGH|MEDIUM|LOW
Category: Injection|Auth|XSS|CSRF|Secrets|Config|Upload
File: path/to/file.py:42
Finding: Description of vulnerability
Evidence: `code_snippet()`
Impact: What an attacker could achieve
Fix: Remediation with code
```

## Quick Scan Patterns

| Pattern | Language | Risk |
|---------|----------|------|
| `eval(`, `exec(` | Python/JS | Command injection |
| `os.system(` | Python | Command injection |
| `subprocess.*shell=True` | Python | Command injection |
| `child_process.exec(` | JS/TS | Command injection |
| `dangerouslySetInnerHTML` | React | XSS |
| `v-html` | Vue | XSS |
| `innerHTML` | JS/TS | XSS |
| `pickle.load` | Python | Deserialization |
| `yaml.load(` (no SafeLoader) | Python | Deserialization |
| `fmt.Sprintf` in SQL | Go | SQL injection |
| String concat in `execute()` | Python | SQL injection |
| `DEBUG = True` | Python | Misconfiguration |
| `chmod 777` | Shell | Misconfiguration |
| Hardcoded password strings | Any | Secrets exposure |
