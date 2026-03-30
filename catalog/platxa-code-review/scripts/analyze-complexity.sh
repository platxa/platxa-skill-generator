#!/usr/bin/env bash
set -euo pipefail

# Analyze code complexity: function count, length, nesting depth.
# Usage: analyze-complexity.sh <file-or-directory>
# Exit code: 0 = clean, 1 = issues found, 2 = usage error

readonly TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
    echo "Usage: analyze-complexity.sh <file-or-directory>"
    exit 2
fi

if [[ ! -e "$TARGET" ]]; then
    echo "Error: $TARGET does not exist"
    exit 2
fi

WARNINGS=0
ERRORS=0

# Collect source files
if [[ -d "$TARGET" ]]; then
    FILES=$(find "$TARGET" -type f \( \
        -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" \
        -o -name "*.go" -o -name "*.java" -o -name "*.rs" \
    \) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/vendor/*" \
       ! -path "*/__pycache__/*" ! -path "*/dist/*" ! -path "*/build/*" \
       ! -path "*/*.test.*" ! -path "*/*.spec.*" ! -path "*/test_*")
else
    FILES="$TARGET"
fi

if [[ -z "$FILES" ]]; then
    echo "No source files to analyze"
    exit 0
fi

echo "Complexity Analysis Report"
echo "=========================="
echo ""

TOTAL_FILES=0
TOTAL_LINES=0
TOTAL_FUNCTIONS=0
LONG_FUNCTIONS=0
DEEP_NESTING=0
LONG_FILES=0

while IFS= read -r file; do
    [[ -f "$file" ]] || continue
    TOTAL_FILES=$((TOTAL_FILES + 1))

    LINES=$(wc -l < "$file")
    TOTAL_LINES=$((TOTAL_LINES + LINES))

    # Check file length
    if [[ "$LINES" -gt 500 ]]; then
        echo "[ERROR] $file: $LINES lines (max 500)"
        LONG_FILES=$((LONG_FILES + 1))
        ERRORS=$((ERRORS + 1))
    elif [[ "$LINES" -gt 300 ]]; then
        echo "[WARN]  $file: $LINES lines (target <300)"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Count functions and check length
    # Python: def keyword
    if [[ "$file" == *.py ]]; then
        CURRENT_FUNC=""
        CURRENT_START=0
        LINE_NUM=0

        while IFS= read -r line; do
            LINE_NUM=$((LINE_NUM + 1))
            if [[ "$line" =~ ^[[:space:]]*def[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*) ]]; then
                # Save previous function
                if [[ -n "$CURRENT_FUNC" ]]; then
                    FUNC_LEN=$((LINE_NUM - CURRENT_START))
                    TOTAL_FUNCTIONS=$((TOTAL_FUNCTIONS + 1))
                    if [[ "$FUNC_LEN" -gt 50 ]]; then
                        echo "[ERROR] $file:$CURRENT_START: $CURRENT_FUNC() is $FUNC_LEN lines (max 50)"
                        LONG_FUNCTIONS=$((LONG_FUNCTIONS + 1))
                        ERRORS=$((ERRORS + 1))
                    elif [[ "$FUNC_LEN" -gt 25 ]]; then
                        echo "[WARN]  $file:$CURRENT_START: $CURRENT_FUNC() is $FUNC_LEN lines (target <25)"
                        WARNINGS=$((WARNINGS + 1))
                    fi
                fi
                CURRENT_FUNC="${BASH_REMATCH[1]}"
                CURRENT_START=$LINE_NUM
            fi
        done < "$file"

        # Handle last function
        if [[ -n "$CURRENT_FUNC" ]]; then
            FUNC_LEN=$((LINE_NUM - CURRENT_START + 1))
            TOTAL_FUNCTIONS=$((TOTAL_FUNCTIONS + 1))
            if [[ "$FUNC_LEN" -gt 50 ]]; then
                echo "[ERROR] $file:$CURRENT_START: $CURRENT_FUNC() is $FUNC_LEN lines (max 50)"
                LONG_FUNCTIONS=$((LONG_FUNCTIONS + 1))
                ERRORS=$((ERRORS + 1))
            elif [[ "$FUNC_LEN" -gt 25 ]]; then
                echo "[WARN]  $file:$CURRENT_START: $CURRENT_FUNC() is $FUNC_LEN lines (target <25)"
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
    fi

    # JavaScript/TypeScript: function keyword, arrow functions, method definitions
    if [[ "$file" == *.js || "$file" == *.ts || "$file" == *.tsx ]]; then
        FUNC_COUNT=$(grep -cE '(function\s+\w+|=>\s*\{|^\s*(async\s+)?[a-zA-Z]+\s*\([^)]*\)\s*\{)' "$file" 2>/dev/null || echo 0)
        TOTAL_FUNCTIONS=$((TOTAL_FUNCTIONS + FUNC_COUNT))
    fi

    # Go: func keyword
    if [[ "$file" == *.go ]]; then
        FUNC_COUNT=$(grep -cE '^func\s+' "$file" 2>/dev/null || echo 0)
        TOTAL_FUNCTIONS=$((TOTAL_FUNCTIONS + FUNC_COUNT))
    fi

    # Check nesting depth (language-agnostic: count indentation)
    MAX_DEPTH=0
    LINE_NUM=0
    while IFS= read -r line; do
        LINE_NUM=$((LINE_NUM + 1))
        # Count leading spaces/tabs
        STRIPPED="${line#"${line%%[! ]*}"}"
        INDENT=$(( (${#line} - ${#STRIPPED}) / 4 ))

        # Also count tabs
        STRIPPED_TAB="${line#"${line%%[!	]*}"}"
        INDENT_TAB=$(( ${#line} - ${#STRIPPED_TAB} ))
        DEPTH=$((INDENT > INDENT_TAB ? INDENT : INDENT_TAB))

        if [[ "$DEPTH" -gt "$MAX_DEPTH" ]]; then
            MAX_DEPTH=$DEPTH
        fi
    done < "$file"

    if [[ "$MAX_DEPTH" -gt 5 ]]; then
        echo "[ERROR] $file: max nesting depth $MAX_DEPTH (max 4)"
        DEEP_NESTING=$((DEEP_NESTING + 1))
        ERRORS=$((ERRORS + 1))
    elif [[ "$MAX_DEPTH" -gt 3 ]]; then
        echo "[WARN]  $file: max nesting depth $MAX_DEPTH (target <4)"
        WARNINGS=$((WARNINGS + 1))
    fi

done <<< "$FILES"

echo ""
echo "Summary"
echo "-------"
echo "Files analyzed:    $TOTAL_FILES"
echo "Total lines:       $TOTAL_LINES"
echo "Functions found:   $TOTAL_FUNCTIONS"
echo "Long functions:    $LONG_FUNCTIONS"
echo "Deep nesting:      $DEEP_NESTING"
echo "Long files:        $LONG_FILES"
echo "Warnings:          $WARNINGS"
echo "Errors:            $ERRORS"
echo ""

if [[ "$ERRORS" -gt 0 ]]; then
    echo "STATUS: ISSUES FOUND"
    exit 1
else
    echo "STATUS: CLEAN"
    exit 0
fi
