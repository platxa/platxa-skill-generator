# JWT Token Claims Reference

Standard and Platxa-specific claims for RS256 tokens.

## Standard Claims (RFC 7519)

| Claim | Type | Description |
|-------|------|-------------|
| `iss` | string | Issuer (e.g., `https://platxa.com`) |
| `sub` | string | Subject (user/service identifier) |
| `aud` | string | Audience (intended recipient) |
| `exp` | number | Expiration time (Unix timestamp) |
| `nbf` | number | Not before (Unix timestamp) |
| `iat` | number | Issued at (Unix timestamp) |
| `jti` | string | JWT ID (unique identifier) |

## Access Token Claims

For user authentication to Platform API:

```json
{
  "iss": "https://platxa.com",
  "sub": "12345",
  "aud": "platxa-api",
  "exp": 1699574400,
  "nbf": 1699570800,
  "iat": 1699570800,
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "type": "access",
  "user_id": 12345,
  "partner_id": 67890,
  "instance_ids": [1, 2, 3],
  "roles": ["user", "developer"]
}
```

| Claim | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"access"` |
| `user_id` | int | Odoo user ID |
| `partner_id` | int | Odoo partner ID |
| `instance_ids` | int[] | Accessible instance IDs |
| `roles` | string[] | User roles |

## Editor Token Claims

For Sidecar/IDE communication:

```json
{
  "iss": "https://platxa.com",
  "sub": "editor:abc123xy",
  "aud": "sidecar-abc123xy",
  "exp": 1699599600,
  "nbf": 1699570800,
  "iat": 1699570800,
  "jti": "550e8400-e29b-41d4-a716-446655440001",
  "type": "editor",
  "instance_name": "abc123xy",
  "user_id": 12345,
  "permissions": ["read", "write", "deploy"]
}
```

| Claim | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"editor"` |
| `instance_name` | string | Target instance |
| `user_id` | int | Acting user ID |
| `permissions` | string[] | `read`, `write`, `deploy` |

## Service Token Claims

For service-to-service authentication:

```json
{
  "iss": "https://platxa.com",
  "sub": "service:ai-engine",
  "aud": "platxa-internal",
  "exp": 1699571100,
  "nbf": 1699570800,
  "iat": 1699570800,
  "jti": "550e8400-e29b-41d4-a716-446655440002",
  "type": "service",
  "service_name": "ai-engine",
  "allowed_endpoints": [
    "/instances/*/files/*",
    "/instances/*/deploy"
  ]
}
```

| Claim | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"service"` |
| `service_name` | string | Calling service |
| `allowed_endpoints` | string[] | Permitted API patterns |

## Claim Validation Rules

```python
def validate_claims(payload: dict, expected_type: str):
    """Validate token claims."""
    # Required for all tokens
    assert payload.get("iss") == EXPECTED_ISSUER
    assert payload.get("type") == expected_type
    assert payload.get("jti")  # For revocation

    # Type-specific validation
    if expected_type == "access":
        assert payload.get("user_id")
        assert payload.get("instance_ids")

    elif expected_type == "editor":
        assert payload.get("instance_name")
        assert payload.get("permissions")

    elif expected_type == "service":
        assert payload.get("service_name")
        assert payload.get("allowed_endpoints")
```

## Audience Values

| Audience | Used For |
|----------|----------|
| `platxa-api` | Platform API access |
| `sidecar-{name}` | Specific instance Sidecar |
| `platxa-internal` | Internal service calls |
| `validator-service` | Validation requests |
