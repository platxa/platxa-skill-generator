# Cross-Language Security Best Practices

Condensed security checklist covering Python (FastAPI/Django/Flask), JavaScript/TypeScript (Express/Next.js/React/Vue), and Go backends. For full framework-specific rules, see the upstream skill at https://github.com/openai/skills.

## Safety Constraints (MUST FOLLOW)

- MUST NOT output, log, or commit secrets (API keys, passwords, tokens, signing keys)
- MUST NOT "fix" security by disabling protections (weakening auth, permissive CORS, skipping validation)
- MUST provide evidence-based findings: cite file paths and code snippets
- MUST treat uncertainty honestly: if protection may exist in infrastructure, note "verify at runtime"
- CORS is NOT an auth mechanism. CSRF applies only when browsers auto-attach cookies.

## Operating Modes

1. **Generation mode** (default): Write secure-by-default code. Follow every MUST rule.
2. **Passive review** (always on): Flag critical violations in touched/nearby code.
3. **Active audit** (on request): Systematic scan with structured findings output.

## Secure Baseline (ALL Frameworks)

| Area | Requirement |
|------|-------------|
| TLS | HTTPS enforced; HSTS header present |
| Debug | Disabled in production; no stack traces to clients |
| Auth | Explicit, consistent enforcement on all routes |
| CORS | Disabled unless needed; strict allowlist when enabled |
| Cookies | `Secure`, `HttpOnly`, `SameSite=Lax/Strict` |
| CSRF | Token-based protection when using cookie auth |
| Secrets | From environment/vault only; never hardcoded |
| Dependencies | Pinned versions; regular vulnerability scanning |
| Rate limiting | Applied to auth endpoints and public APIs |

## Critical Rules by Category

### Authentication & Authorization
- Auth MUST be enforced via middleware/dependencies (not per-handler opt-in)
- Passwords MUST use bcrypt/argon2/scrypt with appropriate cost
- JWTs MUST validate signature, expiry, issuer, and audience
- Broken access control: verify resource ownership on every request

### Injection Prevention
- **SQL**: Use parameterized queries/ORM exclusively. Never string-concatenate user input.
- **Command**: Avoid `os.system()`, `eval()`, `exec()`, `child_process.exec()`. Use `subprocess.run(["cmd", arg], shell=False)` or `execFile()`.
- **Template (SSTI)**: Never pass user input as template source. Use auto-escaping.
- **Path traversal**: Validate and canonicalize file paths. Reject `..` sequences.
- **Deserialization**: Never unpickle/unserialize untrusted data. Use JSON.

### XSS Prevention
- Use framework auto-escaping (React JSX, Vue templates, Jinja2 `|e`)
- Avoid `dangerouslySetInnerHTML`, `v-html`, `innerHTML`, `{!! $var !!}`
- Sanitize HTML with DOMPurify/bleach when rich content is required
- Set `Content-Security-Policy` header

### CSRF Protection
- Required when cookies carry auth (session cookies)
- Not needed for pure header-token APIs (Bearer tokens)
- Django: `{% csrf_token %}` + middleware. FastAPI: explicit if using cookies.
- Express: `csurf` or `csrf-csrf`. Next.js: verify `Origin` header.

### File Upload Security
- Validate MIME type AND file content (magic bytes), not just extension
- Store outside web root. Generate random filenames.
- Enforce size limits. Scan for malware on sensitive systems.

### Secrets Management
- MUST use environment variables or secret managers
- MUST NOT hardcode in source, config files, or Docker images
- MUST rotate compromised secrets immediately

## Framework-Specific Notes

### Python (FastAPI/Django/Flask)
- FastAPI: Disable OpenAPI docs in production (`docs_url=None, redoc_url=None`)
- Django: `DEBUG=False`, `ALLOWED_HOSTS` set, `SECRET_KEY` from env
- Flask: `app.secret_key` from env, never `app.run(debug=True)` in prod

### JavaScript/TypeScript (Express/Next.js)
- Express: Use `helmet()` middleware for security headers
- Next.js: Server Actions validate input server-side; don't trust client data
- React: JSX auto-escapes. Never use `dangerouslySetInnerHTML` with user input.
- Vue: Template syntax auto-escapes. Avoid `v-html` with untrusted data.

### Go
- Use `html/template` (auto-escapes) not `text/template` for HTML
- `net/http`: Set timeouts on server and client. Use `crypto/rand` not `math/rand`.
- SQL: Use `db.Query(query, args...)` with placeholders. Never `fmt.Sprintf`.

## Audit Finding Format

```
[RULE-ID] Severity: CRITICAL|HIGH|MEDIUM|LOW
File: path/to/file.py:42
Finding: Description of the vulnerability
Evidence: `code snippet showing the issue`
Fix: Recommended remediation
```

## Scanning Heuristics

Search for these patterns to find vulnerabilities quickly:
- `eval(`, `exec(`, `os.system(`, `subprocess.*shell=True` — command injection
- `innerHTML`, `v-html`, `dangerouslySetInnerHTML` — XSS
- String concatenation in SQL queries — SQL injection
- `pickle.load`, `yaml.load(` without `Loader` — unsafe deserialization
- `chmod 777`, hardcoded passwords, `DEBUG=True` — misconfigurations
- Missing auth decorators/middleware on state-changing routes
