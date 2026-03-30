#!/usr/bin/env bash
set -euo pipefail

# Scan files for hardcoded secrets, API keys, and tokens.
# Usage: detect-secrets.sh <file-or-directory>
# Exit code: 0 = clean, 1 = secrets found, 2 = usage error

readonly TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
    echo "Usage: detect-secrets.sh <file-or-directory>"
    exit 2
fi

if [[ ! -e "$TARGET" ]]; then
    echo "Error: $TARGET does not exist"
    exit 2
fi

FOUND=0

# Collect files to scan
if [[ -d "$TARGET" ]]; then
    FILES=$(find "$TARGET" -type f \( \
        -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" \
        -o -name "*.go" -o -name "*.java" -o -name "*.rs" -o -name "*.rb" \
        -o -name "*.php" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" \
        -o -name "*.toml" -o -name "*.cfg" -o -name "*.ini" -o -name "*.env" \
    \) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/vendor/*" \
       ! -path "*/__pycache__/*" ! -path "*/dist/*" ! -path "*/build/*")
else
    FILES="$TARGET"
fi

if [[ -z "$FILES" ]]; then
    echo "No files to scan"
    exit 0
fi

echo "Scanning for hardcoded secrets..."
echo "================================="

# Pattern 1: Generic API keys and tokens
while IFS= read -r file; do
    while IFS= read -r match; do
        echo "[SECRET] $file: $match"
        FOUND=$((FOUND + 1))
    done < <(grep -nE '(api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token|secret[_-]?key)\s*[=:]\s*["\x27][A-Za-z0-9+/=_-]{8,}' "$file" 2>/dev/null || true)
done <<< "$FILES"

# Pattern 2: AWS keys
while IFS= read -r file; do
    while IFS= read -r match; do
        echo "[AWS] $file: $match"
        FOUND=$((FOUND + 1))
    done < <(grep -nE '(AKIA[A-Z0-9]{16}|aws[_-]?secret[_-]?access[_-]?key\s*[=:])' "$file" 2>/dev/null || true)
done <<< "$FILES"

# Pattern 3: Private keys
while IFS= read -r file; do
    while IFS= read -r match; do
        echo "[KEY] $file: $match"
        FOUND=$((FOUND + 1))
    done < <(grep -nE 'BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY' "$file" 2>/dev/null || true)
done <<< "$FILES"

# Pattern 4: Connection strings with passwords
while IFS= read -r file; do
    while IFS= read -r match; do
        echo "[CONN] $file: $match"
        FOUND=$((FOUND + 1))
    done < <(grep -nE '(postgres|mysql|mongodb|redis)://[^:]+:[^@]+@' "$file" 2>/dev/null || true)
done <<< "$FILES"

# Pattern 5: JWT tokens (eyJ prefix)
while IFS= read -r file; do
    while IFS= read -r match; do
        echo "[JWT] $file: $match"
        FOUND=$((FOUND + 1))
    done < <(grep -nE 'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.' "$file" 2>/dev/null || true)
done <<< "$FILES"

# Pattern 6: Password assignments
while IFS= read -r file; do
    while IFS= read -r match; do
        echo "[PASS] $file: $match"
        FOUND=$((FOUND + 1))
    done < <(grep -nEi 'password\s*[=:]\s*["\x27][^"\x27]{4,}' "$file" 2>/dev/null | grep -vi '(env|environ|getenv|os\.get|process\.env|config\.|placeholder|example|changeme|xxx)' || true)
done <<< "$FILES"

echo "================================="
if [[ "$FOUND" -gt 0 ]]; then
    echo "FOUND $FOUND potential secret(s)"
    exit 1
else
    echo "No secrets detected"
    exit 0
fi
