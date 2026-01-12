# JWKS Format Reference

JSON Web Key Set structure for RS256 public keys.

## JWKS Response Format

Endpoint: `/.well-known/jwks.json`

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "a1b2c3d4e5f6g7h8",
      "n": "0vx7agoebGcQSuuPiLJXZptN9...",
      "e": "AQAB"
    },
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "i9j0k1l2m3n4o5p6",
      "n": "ofgWCuLjybRlzo0tZWJjNiuS...",
      "e": "AQAB"
    }
  ]
}
```

## JWK Fields

| Field | Value | Description |
|-------|-------|-------------|
| `kty` | `"RSA"` | Key type |
| `use` | `"sig"` | Usage (signature) |
| `alg` | `"RS256"` | Algorithm |
| `kid` | string | Key ID (matches token header) |
| `n` | base64url | RSA modulus |
| `e` | base64url | RSA exponent |

## Converting RSA to JWK

```python
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import base64

def rsa_to_jwk(public_key: RSAPublicKey, kid: str) -> dict:
    """Convert RSA public key to JWK format."""
    numbers = public_key.public_numbers()

    def int_to_base64url(n: int, length: int) -> str:
        """Convert integer to base64url without padding."""
        data = n.to_bytes(length, byteorder='big')
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

    return {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": kid,
        "n": int_to_base64url(numbers.n, 256),  # 2048-bit key
        "e": int_to_base64url(numbers.e, 3),
    }
```

## Client-Side Key Fetching

Using PyJWT with JWKS:

```python
import jwt
from jwt import PyJWKClient

# Initialize JWKS client (caches keys)
jwks_client = PyJWKClient("https://platxa.com/.well-known/jwks.json")

def verify_token(token: str) -> dict:
    """Verify token using JWKS endpoint."""
    # Get signing key from JWKS
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    # Decode and verify
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience="platxa-api",
        issuer="https://platxa.com"
    )
```

## Cache Headers

```python
from fastapi import Response

@app.get("/.well-known/jwks.json")
async def jwks(response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["Content-Type"] = "application/json"

    return {"keys": get_active_keys_as_jwk()}
```

## Multiple Keys (Rotation)

JWKS supports multiple keys for rotation:

```
Time 0:  [Key A (active)]
Time 1:  [Key A (expiring), Key B (active)]   <- Rotation
Time 2:  [Key B (active)]                      <- After grace period
```

All active keys appear in JWKS during grace period.

## Token Header with Key ID

Tokens include `kid` to identify signing key:

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "a1b2c3d4e5f6g7h8"
}
```

Verification process:
1. Extract `kid` from token header
2. Fetch JWKS from endpoint
3. Find matching key by `kid`
4. Verify signature with that key
