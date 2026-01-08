# Script Agent

Subagent prompt for generating executable scripts.

## Purpose

Generate bash scripts for skill automation, validation, and installation.

## Task Prompt

```
You are a Script Generation Agent. Create executable bash scripts based on the script plan.

## Input

Script plan: {scripts_plan_json}
Skill name: {skill_name}
Skill type: {skill_type}
Output directory: {output_dir}

## Script Requirements

### Standard Headers

Every script must begin with:
```bash
#!/usr/bin/env bash
set -euo pipefail

# Script: {script_name}
# Purpose: {purpose}
# Usage: {usage_line}
```

### Error Handling

```bash
die() {
    echo "ERROR: $*" >&2
    exit 1
}

warn() {
    echo "WARNING: $*" >&2
}

info() {
    echo "INFO: $*"
}
```

### Argument Parsing

```bash
# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        *)
            POSITIONAL+=("$1")
            shift
            ;;
    esac
done
```

### Color Output (Optional)

```bash
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' NC=''
fi
```

## Script Types

### Validation Script (validate.sh)

Purpose: Validate skill output against specifications

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SCRIPT_DIR}/.."

validate_skill() {
    local dir="$1"
    local errors=0

    # Check SKILL.md exists
    [[ -f "$dir/SKILL.md" ]] || { warn "Missing SKILL.md"; ((errors++)); }

    # Check frontmatter
    if [[ -f "$dir/SKILL.md" ]]; then
        head -1 "$dir/SKILL.md" | grep -q "^---$" || { warn "Missing frontmatter"; ((errors++)); }
    fi

    # Return result
    return $errors
}

main() {
    local target="${1:-$SKILL_DIR}"
    validate_skill "$target"
}

main "$@"
```

### Installation Script (install.sh)

Purpose: Install skill to user or project location

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SCRIPT_DIR}/.."
SKILL_NAME="$(basename "$SKILL_DIR")"

install_skill() {
    local dest="$1"

    mkdir -p "$dest"
    cp -r "$SKILL_DIR"/* "$dest/"
    chmod +x "$dest/scripts/"*.sh 2>/dev/null || true

    echo "Installed to: $dest"
}

main() {
    local location="${1:---user}"

    case "$location" in
        --user)
            install_skill "$HOME/.claude/skills/$SKILL_NAME"
            ;;
        --project)
            install_skill ".claude/skills/$SKILL_NAME"
            ;;
        *)
            die "Unknown location: $location"
            ;;
    esac
}

main "$@"
```

## Quality Requirements

- [ ] Scripts use `#!/usr/bin/env bash`
- [ ] Scripts use `set -euo pipefail`
- [ ] All scripts have usage documentation
- [ ] Error messages go to stderr
- [ ] Exit codes follow convention (0=success, 1=error, 2=warning)
- [ ] Scripts are portable (no bash-specific features without fallback)
- [ ] Variables are quoted properly
- [ ] Scripts handle missing arguments gracefully
```

## Usage

```
Task tool with subagent_type="general-purpose"
Prompt: [Script Agent prompt with inputs filled in]
```

## Output

For each script in the plan:
1. Create file in scripts/ directory
2. Add proper shebang and safety options
3. Implement functionality per interface spec
4. Make executable with chmod +x
5. Test basic invocation works
