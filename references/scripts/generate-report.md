# Generate Report Script

Shell script to generate comprehensive JSON validation report.

## Script: generate-report.sh

```bash
#!/bin/bash
# generate-report.sh - Generate comprehensive skill validation report
#
# Usage: generate-report.sh <skill-path> [options]
#
# Options:
#   --output <file>  Write report to file (default: stdout)
#   --format <fmt>   Output format: json, markdown, text (default: json)
#   --full           Include all details (verbose mode)

set -e

# Parse arguments
SKILL_PATH=""
OUTPUT_FILE=""
FORMAT="json"
FULL_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --output|-o)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --format|-f)
            FORMAT="$2"
            shift 2
            ;;
        --full)
            FULL_MODE=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            SKILL_PATH="$1"
            shift
            ;;
    esac
done

# Validate
if [ -z "$SKILL_PATH" ]; then
    echo "Usage: generate-report.sh <skill-path> [options]"
    exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
    echo "Error: Directory not found: $SKILL_PATH"
    exit 1
fi

SKILL_PATH=$(cd "$SKILL_PATH" && pwd)
SKILL_NAME=$(basename "$SKILL_PATH")
TIMESTAMP=$(date -Iseconds)

# Collect data
collect_metadata() {
    local skill_md="$SKILL_PATH/SKILL.md"

    if [ ! -f "$skill_md" ]; then
        echo "{}"
        return
    fi

    # Extract frontmatter
    local name=$(sed -n '/^---$/,/^---$/p' "$skill_md" | grep "^name:" | sed 's/name:\s*//')
    local desc=$(sed -n '/^---$/,/^---$/p' "$skill_md" | grep "^description:" | sed 's/description:\s*//')
    local version=$(sed -n '/^---$/,/^---$/p' "$skill_md" | grep "^version:" | sed 's/version:\s*//' || echo "1.0.0")

    cat << EOF
{
    "name": "$name",
    "description": "$desc",
    "version": "$version"
}
EOF
}

collect_files() {
    local files=()
    local total_size=0
    local total_tokens=0

    while IFS= read -r -d '' file; do
        local rel_path="${file#$SKILL_PATH/}"
        local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)
        local tokens=$((size / 4))

        total_size=$((total_size + size))
        total_tokens=$((total_tokens + tokens))

        files+=("\"$rel_path\": {\"size\": $size, \"tokens\": $tokens}")
    done < <(find "$SKILL_PATH" -type f -print0)

    echo "{"
    echo "  \"count\": ${#files[@]},"
    echo "  \"total_size\": $total_size,"
    echo "  \"total_tokens\": $total_tokens,"
    echo "  \"files\": {"

    local first=true
    for f in "${files[@]}"; do
        [ "$first" = true ] && first=false || echo ","
        echo -n "    $f"
    done

    echo ""
    echo "  }"
    echo "}"
}

collect_structure() {
    local has_skill_md=false
    local has_references=false
    local has_scripts=false
    local ref_count=0
    local script_count=0

    [ -f "$SKILL_PATH/SKILL.md" ] && has_skill_md=true
    [ -d "$SKILL_PATH/references" ] && has_references=true && ref_count=$(find "$SKILL_PATH/references" -name "*.md" | wc -l)
    [ -d "$SKILL_PATH/scripts" ] && has_scripts=true && script_count=$(find "$SKILL_PATH/scripts" -name "*.sh" | wc -l)

    cat << EOF
{
    "has_skill_md": $has_skill_md,
    "has_references": $has_references,
    "has_scripts": $has_scripts,
    "reference_count": $ref_count,
    "script_count": $script_count
}
EOF
}

run_lint_checks() {
    local errors=0
    local warnings=0
    local checks=()

    # Check SKILL.md exists
    if [ -f "$SKILL_PATH/SKILL.md" ]; then
        checks+=('{"name": "skill_md_exists", "status": "passed"}')
    else
        checks+=('{"name": "skill_md_exists", "status": "failed", "message": "SKILL.md not found"}')
        ((errors++))
    fi

    # Check frontmatter
    if [ -f "$SKILL_PATH/SKILL.md" ]; then
        if head -n 1 "$SKILL_PATH/SKILL.md" | grep -q "^---$"; then
            checks+=('{"name": "frontmatter_present", "status": "passed"}')
        else
            checks+=('{"name": "frontmatter_present", "status": "failed", "message": "Missing frontmatter"}')
            ((errors++))
        fi
    fi

    # Check name field
    if [ -f "$SKILL_PATH/SKILL.md" ]; then
        if sed -n '/^---$/,/^---$/p' "$SKILL_PATH/SKILL.md" | grep -q "^name:"; then
            checks+=('{"name": "name_field", "status": "passed"}')
        else
            checks+=('{"name": "name_field", "status": "failed", "message": "Missing name field"}')
            ((errors++))
        fi
    fi

    # Check description field
    if [ -f "$SKILL_PATH/SKILL.md" ]; then
        if sed -n '/^---$/,/^---$/p' "$SKILL_PATH/SKILL.md" | grep -q "^description:"; then
            checks+=('{"name": "description_field", "status": "passed"}')
        else
            checks+=('{"name": "description_field", "status": "failed", "message": "Missing description field"}')
            ((errors++))
        fi
    fi

    # Check for trailing whitespace
    if find "$SKILL_PATH" -name "*.md" -exec grep -l '\s$' {} \; 2>/dev/null | grep -q .; then
        checks+=('{"name": "no_trailing_whitespace", "status": "warning", "message": "Trailing whitespace found"}')
        ((warnings++))
    else
        checks+=('{"name": "no_trailing_whitespace", "status": "passed"}')
    fi

    # Check for tabs
    if find "$SKILL_PATH" -name "*.md" -exec grep -l $'\t' {} \; 2>/dev/null | grep -q .; then
        checks+=('{"name": "no_tabs", "status": "warning", "message": "Tab characters found"}')
        ((warnings++))
    else
        checks+=('{"name": "no_tabs", "status": "passed"}')
    fi

    echo "{"
    echo "  \"errors\": $errors,"
    echo "  \"warnings\": $warnings,"
    echo "  \"checks\": ["

    local first=true
    for c in "${checks[@]}"; do
        [ "$first" = true ] && first=false || echo ","
        echo -n "    $c"
    done

    echo ""
    echo "  ]"
    echo "}"
}

check_links() {
    local total=0
    local broken=0
    local broken_links=()

    while IFS= read -r -d '' file; do
        local rel_file="${file#$SKILL_PATH/}"
        local file_dir=$(dirname "$file")

        while IFS= read -r line; do
            local target=$(echo "$line" | sed -n 's/.*](\([^)#]*\)).*/\1/p')
            [ -z "$target" ] && continue
            [[ "$target" =~ ^https?:// ]] && continue
            [[ "$target" =~ ^mailto: ]] && continue

            ((total++))

            local full_path="$file_dir/$target"
            if [ ! -e "$full_path" ]; then
                ((broken++))
                broken_links+=("{\"file\": \"$rel_file\", \"link\": \"$target\"}")
            fi
        done < <(grep -o '\[.*\]([^)]*)'  "$file" 2>/dev/null || true)
    done < <(find "$SKILL_PATH" -name "*.md" -type f -print0)

    echo "{"
    echo "  \"total\": $total,"
    echo "  \"valid\": $((total - broken)),"
    echo "  \"broken\": $broken,"
    echo "  \"broken_links\": ["

    local first=true
    for l in "${broken_links[@]}"; do
        [ "$first" = true ] && first=false || echo ","
        echo -n "    $l"
    done

    echo ""
    echo "  ]"
    echo "}"
}

calculate_quality() {
    local score=10.0
    local lint=$(run_lint_checks)
    local links=$(check_links)

    local lint_errors=$(echo "$lint" | grep '"errors":' | grep -o '[0-9]*')
    local lint_warnings=$(echo "$lint" | grep '"warnings":' | grep -o '[0-9]*')
    local broken_links=$(echo "$links" | grep '"broken":' | grep -o '[0-9]*')

    # Deduct points
    score=$(echo "$score - ($lint_errors * 1.0)" | bc)
    score=$(echo "$score - ($lint_warnings * 0.25)" | bc)
    score=$(echo "$score - ($broken_links * 0.5)" | bc)

    # Clamp to 0-10
    score=$(echo "if ($score < 0) 0 else if ($score > 10) 10 else $score" | bc)

    local passed="false"
    [ $(echo "$score >= 7.0" | bc) -eq 1 ] && passed="true"

    cat << EOF
{
    "score": $score,
    "passed": $passed,
    "threshold": 7.0
}
EOF
}

# Generate report
generate_json_report() {
    cat << EOF
{
  "report": {
    "skill": "$SKILL_NAME",
    "path": "$SKILL_PATH",
    "generated_at": "$TIMESTAMP",
    "generator": "generate-report.sh"
  },
  "metadata": $(collect_metadata),
  "structure": $(collect_structure),
  "files": $(collect_files),
  "lint": $(run_lint_checks),
  "links": $(check_links),
  "quality": $(calculate_quality)
}
EOF
}

generate_markdown_report() {
    local quality=$(calculate_quality)
    local score=$(echo "$quality" | grep '"score":' | grep -o '[0-9.]*')
    local lint=$(run_lint_checks)
    local errors=$(echo "$lint" | grep '"errors":' | grep -o '[0-9]*')
    local warnings=$(echo "$lint" | grep '"warnings":' | grep -o '[0-9]*')

    cat << EOF
# Skill Validation Report

**Skill:** $SKILL_NAME
**Generated:** $TIMESTAMP

## Quality Score

**Score: $score/10**

| Metric | Value |
|--------|-------|
| Lint Errors | $errors |
| Lint Warnings | $warnings |

## Structure

$(collect_structure | grep -E '"(has_|count)"' | sed 's/[",]//g' | sed 's/:/|/g' | awk -F'|' '{print "| " $1 " | " $2 " |"}')

## Files

$(find "$SKILL_PATH" -type f | sed "s|$SKILL_PATH/||" | sort | sed 's/^/- /')

---
*Generated by generate-report.sh*
EOF
}

generate_text_report() {
    local quality=$(calculate_quality)
    local score=$(echo "$quality" | grep '"score":' | grep -o '[0-9.]*')

    echo "═══════════════════════════════════════════════════════════"
    echo "  SKILL VALIDATION REPORT"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  Skill: $SKILL_NAME"
    echo "  Score: $score/10"
    echo "  Time:  $TIMESTAMP"
    echo ""
    echo "───────────────────────────────────────────────────────────"
    echo ""
    run_lint_checks | grep -E '"(name|status|message)"' | sed 's/[",{}]//g' | sed 's/^/  /'
    echo ""
    echo "═══════════════════════════════════════════════════════════"
}

# Output
case "$FORMAT" in
    json)
        REPORT=$(generate_json_report)
        ;;
    markdown|md)
        REPORT=$(generate_markdown_report)
        ;;
    text|txt)
        REPORT=$(generate_text_report)
        ;;
    *)
        echo "Unknown format: $FORMAT"
        exit 1
        ;;
esac

if [ -n "$OUTPUT_FILE" ]; then
    echo "$REPORT" > "$OUTPUT_FILE"
    echo "Report written to: $OUTPUT_FILE"
else
    echo "$REPORT"
fi
```

## Usage

```bash
# JSON report to stdout
./generate-report.sh ~/.claude/skills/my-skill/

# Save to file
./generate-report.sh ~/.claude/skills/my-skill/ --output report.json

# Markdown format
./generate-report.sh ~/.claude/skills/my-skill/ --format markdown

# Text format
./generate-report.sh ~/.claude/skills/my-skill/ --format text
```

## Report Structure

```json
{
  "report": {
    "skill": "my-skill",
    "path": "/path/to/skill",
    "generated_at": "2024-01-15T14:30:00+00:00"
  },
  "metadata": {
    "name": "my-skill",
    "description": "Skill description",
    "version": "1.0.0"
  },
  "structure": {
    "has_skill_md": true,
    "has_references": true,
    "reference_count": 3
  },
  "files": {
    "count": 5,
    "total_size": 12800,
    "total_tokens": 3200
  },
  "lint": {
    "errors": 0,
    "warnings": 2,
    "checks": [...]
  },
  "links": {
    "total": 8,
    "valid": 7,
    "broken": 1
  },
  "quality": {
    "score": 8.5,
    "passed": true,
    "threshold": 7.0
  }
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Report generated successfully |
| 1 | Error generating report |
