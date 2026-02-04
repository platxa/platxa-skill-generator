# Sensitivity Patterns Reference

Default and extended file sensitivity patterns for security ownership classification.

## Built-in Patterns

These patterns are applied by default when no `--sensitive-config` is provided:

| Pattern | Tag | Weight | Matches |
|---------|-----|--------|---------|
| `**/auth/**` | auth | 1.0 | Authentication modules |
| `**/oauth/**` | auth | 1.0 | OAuth implementations |
| `**/rbac/**` | auth | 1.0 | Role-based access control |
| `**/session/**` | auth | 1.0 | Session management |
| `**/token/**` | auth | 1.0 | Token handling |
| `**/iam/**` | auth | 1.0 | Identity and access management |
| `**/sso/**` | auth | 1.0 | Single sign-on |
| `**/crypto/**` | crypto | 1.0 | Cryptographic operations |
| `**/tls/**` | crypto | 1.0 | TLS implementations |
| `**/ssl/**` | crypto | 1.0 | SSL implementations |
| `**/secrets/**` | secrets | 1.0 | Secret storage |
| `**/keys/**` | secrets | 1.0 | Key material |
| `**/*.pem` | secrets | 1.0 | PEM certificates |
| `**/*.key` | secrets | 1.0 | Key files |
| `**/*.p12` | secrets | 1.0 | PKCS#12 keystores |
| `**/*.pfx` | secrets | 1.0 | PFX certificates |

## Extended Patterns

Add these to a custom CSV for broader security coverage:

### PII and Compliance

```csv
**/pii/**,pii,1.0
**/gdpr/**,compliance,1.0
**/hipaa/**,compliance,1.0
**/privacy/**,pii,0.8
**/personal/**,pii,0.8
```

### Infrastructure as Code

```csv
**/terraform/**,infrastructure,1.0
**/cloudformation/**,infrastructure,1.0
**/ansible/**,infrastructure,0.8
**/helm/**,infrastructure,0.8
**/k8s/**,infrastructure,0.8
**/kubernetes/**,infrastructure,0.8
**/*.tf,infrastructure,1.0
**/Dockerfile,infrastructure,0.5
```

### Payment and Financial

```csv
**/payment/**,payment,1.0
**/billing/**,payment,0.8
**/stripe/**,payment,1.0
**/checkout/**,payment,0.8
```

## Custom CSV Format

```
# pattern,tag,weight
# Lines starting with # are comments
# pattern: glob pattern (** for recursive match)
# tag: category label (used in summary.json and queries)
# weight: float 0.0-1.0 (contribution to sensitivity_score)
```

Use with: `--sensitive-config path/to/custom-rules.csv`

## Tag Interpretation

| Tag | Security Risk | Recommended Bus Factor |
|-----|--------------|----------------------|
| auth | Unauthorized access if compromised | >= 3 |
| crypto | Data exposure if weakened | >= 3 |
| secrets | Credential leak if mishandled | >= 2 |
| pii | Privacy violation and regulatory fines | >= 3 |
| infrastructure | Full system compromise if misconfigured | >= 2 |
| payment | Financial loss and PCI compliance risk | >= 3 |
| compliance | Regulatory penalties | >= 2 |
