#!/usr/bin/env bash
# bundle-artifact.sh - Bundle a React project into a single HTML artifact
#
# Usage: bash scripts/bundle-artifact.sh
#
# Must be run from the project root (where package.json and index.html live).
# Produces bundle.html with all JS/CSS inlined.

set -euo pipefail

echo "Bundling React app to single HTML artifact..."

if [[ ! -f "package.json" ]]; then
    echo "Error: No package.json found. Run from your project root." >&2
    exit 1
fi

if [[ ! -f "index.html" ]]; then
    echo "Error: No index.html found in project root." >&2
    exit 1
fi

echo "Installing bundling dependencies..."
pnpm add -D parcel @parcel/config-default parcel-resolver-tspaths html-inline

if [[ ! -f ".parcelrc" ]]; then
    echo "Creating Parcel configuration..."
    printf '{\n  "extends": "@parcel/config-default",\n  "resolvers": ["parcel-resolver-tspaths", "..."]\n}\n' > .parcelrc
fi

echo "Cleaning previous build..."
rm -rf dist bundle.html

echo "Building with Parcel..."
pnpm exec parcel build index.html --dist-dir dist --no-source-maps

echo "Inlining all assets into single HTML file..."
pnpm exec html-inline dist/index.html > bundle.html

FILE_SIZE=$(du -h bundle.html | cut -f1)

echo ""
echo "Bundle complete: bundle.html ($FILE_SIZE)"
echo "Open in browser to test, or share as a claude.ai artifact."
