#!/usr/bin/env bash
#
# check-coverage.sh - Report documentation coverage
#
# Usage: ./check-coverage.sh [directory] [language]
#
# Analyzes source files to determine documentation coverage:
# - Total public functions/methods
# - Number with documentation
# - Coverage percentage
#

set -euo pipefail

DIR="${1:-.}"
LANG="${2:-auto}"

echo "Documentation Coverage Report"
echo "============================="
echo ""
echo "Directory: $DIR"
echo ""

# Python coverage check
check_python() {
    local dir="$1"
    local total=0
    local documented=0

    while IFS= read -r file; do
        # Count function definitions (excluding private)
        funcs=$(grep -c "^def [^_]" "$file" 2>/dev/null || echo 0)
        total=$((total + funcs))

        # Count documented functions (def followed by docstring within 2 lines)
        docs=$(grep -A2 "^def [^_]" "$file" 2>/dev/null | grep -c '"""' || echo 0)
        documented=$((documented + docs / 2))  # Divide by 2 since docstrings have opening and closing

        # Count class definitions
        classes=$(grep -c "^class [^_]" "$file" 2>/dev/null || echo 0)
        total=$((total + classes))

        class_docs=$(grep -A2 "^class [^_]" "$file" 2>/dev/null | grep -c '"""' || echo 0)
        documented=$((documented + class_docs / 2))
    done < <(find "$dir" -name "*.py" -type f 2>/dev/null)

    echo "Python:"
    echo "  Public items: $total"
    echo "  Documented: $documented"
    if [[ $total -gt 0 ]]; then
        coverage=$((documented * 100 / total))
        echo "  Coverage: ${coverage}%"
    else
        echo "  Coverage: N/A (no public items)"
    fi
}

# TypeScript/JavaScript coverage check
check_typescript() {
    local dir="$1"
    local total=0
    local documented=0

    while IFS= read -r file; do
        # Count exported functions
        exports=$(grep -c "^export " "$file" 2>/dev/null || echo 0)
        total=$((total + exports))

        # Count JSDoc comments before exports
        docs=$(grep -B3 "^export " "$file" 2>/dev/null | grep -c "\\*/" || echo 0)
        documented=$((documented + docs))
    done < <(find "$dir" \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -type f 2>/dev/null)

    echo "TypeScript/JavaScript:"
    echo "  Exported items: $total"
    echo "  Documented: $documented"
    if [[ $total -gt 0 ]]; then
        coverage=$((documented * 100 / total))
        echo "  Coverage: ${coverage}%"
    else
        echo "  Coverage: N/A (no exports)"
    fi
}

# Java coverage check
check_java() {
    local dir="$1"
    local total=0
    local documented=0

    while IFS= read -r file; do
        # Count public methods
        methods=$(grep -c "public .*(.*)" "$file" 2>/dev/null || echo 0)
        total=$((total + methods))

        # Count Javadoc comments
        docs=$(grep -c "/\\*\\*" "$file" 2>/dev/null || echo 0)
        documented=$((documented + docs))
    done < <(find "$dir" -name "*.java" -type f 2>/dev/null)

    echo "Java:"
    echo "  Public methods: $total"
    echo "  Javadoc blocks: $documented"
    if [[ $total -gt 0 ]]; then
        coverage=$((documented * 100 / total))
        echo "  Coverage: ${coverage}%"
    else
        echo "  Coverage: N/A (no public methods)"
    fi
}

# Go coverage check
check_go() {
    local dir="$1"
    local total=0
    local documented=0

    while IFS= read -r file; do
        # Count exported functions (start with capital letter)
        exports=$(grep -c "^func [A-Z]" "$file" 2>/dev/null || echo 0)
        total=$((total + exports))

        # Count comments before exported functions
        docs=$(grep -B1 "^func [A-Z]" "$file" 2>/dev/null | grep -c "^//" || echo 0)
        documented=$((documented + docs))
    done < <(find "$dir" -name "*.go" -type f 2>/dev/null)

    echo "Go:"
    echo "  Exported functions: $total"
    echo "  Documented: $documented"
    if [[ $total -gt 0 ]]; then
        coverage=$((documented * 100 / total))
        echo "  Coverage: ${coverage}%"
    else
        echo "  Coverage: N/A (no exports)"
    fi
}

# Rust coverage check
check_rust() {
    local dir="$1"
    local total=0
    local documented=0

    while IFS= read -r file; do
        # Count public functions
        exports=$(grep -c "^pub fn" "$file" 2>/dev/null || echo 0)
        total=$((total + exports))

        # Count doc comments
        docs=$(grep -c "^///" "$file" 2>/dev/null || echo 0)
        # Rough estimate: assume each doc block has ~3 lines
        documented=$((docs / 3))
    done < <(find "$dir" -name "*.rs" -type f 2>/dev/null)

    echo "Rust:"
    echo "  Public items: $total"
    echo "  Doc comments (est.): $documented"
    if [[ $total -gt 0 ]]; then
        coverage=$((documented * 100 / total))
        echo "  Coverage: ~${coverage}%"
    else
        echo "  Coverage: N/A (no public items)"
    fi
}

# Run checks based on language
case "$LANG" in
    python)
        check_python "$DIR"
        ;;
    typescript|javascript)
        check_typescript "$DIR"
        ;;
    java)
        check_java "$DIR"
        ;;
    go)
        check_go "$DIR"
        ;;
    rust)
        check_rust "$DIR"
        ;;
    auto|*)
        # Check all languages present
        [[ $(find "$DIR" -name "*.py" -type f 2>/dev/null | head -1) ]] && check_python "$DIR" && echo ""
        [[ $(find "$DIR" \( -name "*.ts" -o -name "*.tsx" \) -type f 2>/dev/null | head -1) ]] && check_typescript "$DIR" && echo ""
        [[ $(find "$DIR" -name "*.java" -type f 2>/dev/null | head -1) ]] && check_java "$DIR" && echo ""
        [[ $(find "$DIR" -name "*.go" -type f 2>/dev/null | head -1) ]] && check_go "$DIR" && echo ""
        [[ $(find "$DIR" -name "*.rs" -type f 2>/dev/null | head -1) ]] && check_rust "$DIR"
        ;;
esac

echo ""
echo "Note: Coverage estimates are approximate. Manual review recommended."
