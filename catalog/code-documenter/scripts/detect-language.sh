#!/usr/bin/env bash
#
# detect-language.sh - Detect primary language and documentation style
#
# Usage: ./detect-language.sh [directory]
#
# Scans a directory to determine:
# - Primary programming language(s)
# - Existing documentation conventions
# - Recommended docstring style
#

set -euo pipefail

DIR="${1:-.}"

# Count files by extension
declare -A file_counts
declare -A doc_styles

echo "Scanning: $DIR"
echo ""

# Count Python files and detect style
py_count=$(find "$DIR" -name "*.py" -type f 2>/dev/null | wc -l)
if [[ $py_count -gt 0 ]]; then
    file_counts[python]=$py_count

    # Detect docstring style by counting matches
    # shellcheck disable=SC2126  # grep|wc is clearer for counting matches across files
    google_count=$(grep -r 'Args:' "$DIR" --include="*.py" 2>/dev/null | wc -l || echo 0)
    # shellcheck disable=SC2126
    numpy_count=$(grep -r 'Parameters' "$DIR" --include="*.py" 2>/dev/null | grep -v 'Args:' | wc -l || echo 0)
    # shellcheck disable=SC2126
    sphinx_count=$(grep -r ':param' "$DIR" --include="*.py" 2>/dev/null | wc -l || echo 0)

    if [[ $google_count -ge $numpy_count && $google_count -ge $sphinx_count ]]; then
        doc_styles[python]="google"
    elif [[ $numpy_count -ge $sphinx_count ]]; then
        doc_styles[python]="numpy"
    else
        doc_styles[python]="sphinx"
    fi
fi

# Count TypeScript/JavaScript files
ts_count=$(find "$DIR" -name "*.ts" -o -name "*.tsx" -type f 2>/dev/null | wc -l)
js_count=$(find "$DIR" -name "*.js" -o -name "*.jsx" -type f 2>/dev/null | wc -l)
if [[ $((ts_count + js_count)) -gt 0 ]]; then
    file_counts[typescript]=$((ts_count + js_count))

    # Detect JSDoc vs TSDoc
    tsdoc_count=$(grep -r '@packageDocumentation\|@remarks' "$DIR" --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l || echo 0)
    jsdoc_count=$(grep -r '@param\|@returns' "$DIR" --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | wc -l || echo 0)

    # Prefer TSDoc if TSDoc-specific markers found and dominant, otherwise JSDoc
    if [[ $tsdoc_count -gt 0 && $tsdoc_count -ge $jsdoc_count ]]; then
        doc_styles[typescript]="tsdoc"
    else
        doc_styles[typescript]="jsdoc"
    fi
fi

# Count Java files
java_count=$(find "$DIR" -name "*.java" -type f 2>/dev/null | wc -l)
if [[ $java_count -gt 0 ]]; then
    file_counts[java]=$java_count
    doc_styles[java]="javadoc"
fi

# Count Go files
go_count=$(find "$DIR" -name "*.go" -type f 2>/dev/null | wc -l)
if [[ $go_count -gt 0 ]]; then
    file_counts[go]=$go_count
    doc_styles[go]="godoc"
fi

# Count Rust files
rs_count=$(find "$DIR" -name "*.rs" -type f 2>/dev/null | wc -l)
if [[ $rs_count -gt 0 ]]; then
    file_counts[rust]=$rs_count
    doc_styles[rust]="rustdoc"
fi

# Output results
echo "=== Language Detection Results ==="
echo ""

if [[ ${#file_counts[@]} -eq 0 ]]; then
    echo "No supported source files found."
    exit 0
fi

echo "Files by language:"
for lang in "${!file_counts[@]}"; do
    echo "  $lang: ${file_counts[$lang]} files"
done

echo ""
echo "Detected documentation styles:"
for lang in "${!doc_styles[@]}"; do
    echo "  $lang: ${doc_styles[$lang]}"
done

# Determine primary language
max_count=0
primary=""
for lang in "${!file_counts[@]}"; do
    if [[ ${file_counts[$lang]} -gt $max_count ]]; then
        max_count=${file_counts[$lang]}
        primary=$lang
    fi
done

echo ""
echo "Primary language: $primary"
echo "Recommended style: ${doc_styles[$primary]}"
