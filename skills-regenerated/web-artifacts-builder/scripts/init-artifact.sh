#!/usr/bin/env bash
# init-artifact.sh - Scaffold a React + Vite + Tailwind + shadcn/ui project
#
# Usage: bash scripts/init-artifact.sh <project-name>
#
# Creates a fully configured project ready for artifact development.

set -euo pipefail

if [[ -z "${1:-}" ]]; then
    echo "Usage: $(basename "$0") <project-name>" >&2
    exit 1
fi

PROJECT_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)

if [[ "$NODE_VERSION" -lt 18 ]]; then
    echo "Error: Node.js 18+ required (current: $(node -v))" >&2
    exit 1
fi

if [[ "$NODE_VERSION" -ge 20 ]]; then
    VITE_VERSION="latest"
else
    VITE_VERSION="5.4.11"
fi

if [[ "${OSTYPE:-}" == darwin* ]]; then
    SED_CMD=(sed -i '')
else
    SED_CMD=(sed -i)
fi

if ! command -v pnpm &>/dev/null; then
    echo "Installing pnpm..."
    npm install -g pnpm
fi

echo "Creating React + Vite project: $PROJECT_NAME"
pnpm create vite "$PROJECT_NAME" --template react-ts
cd "$PROJECT_NAME"

"${SED_CMD[@]}" '/<link rel="icon".*vite\.svg/d' index.html
"${SED_CMD[@]}" "s/<title>.*<\\/title>/<title>${PROJECT_NAME}<\\/title>/" index.html

echo "Installing base dependencies..."
pnpm install

if [[ "$NODE_VERSION" -lt 20 ]]; then
    pnpm add -D "vite@${VITE_VERSION}"
fi

echo "Installing Tailwind CSS..."
pnpm install -D tailwindcss@3.4.1 postcss autoprefixer @types/node tailwindcss-animate
pnpm install class-variance-authority clsx tailwind-merge lucide-react next-themes

echo "Configuring path aliases..."
node -e "
var fs = require('fs');
var cfg = JSON.parse(fs.readFileSync('tsconfig.json', 'utf8'));
cfg.compilerOptions = cfg.compilerOptions || {};
cfg.compilerOptions.baseUrl = '.';
cfg.compilerOptions.paths = { '@/*': ['./src/*'] };
fs.writeFileSync('tsconfig.json', JSON.stringify(cfg, null, 2));
"

echo "Installing shadcn/ui dependencies..."
pnpm install \
    @radix-ui/react-accordion @radix-ui/react-aspect-ratio @radix-ui/react-avatar \
    @radix-ui/react-checkbox @radix-ui/react-collapsible @radix-ui/react-context-menu \
    @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-hover-card \
    @radix-ui/react-label @radix-ui/react-menubar @radix-ui/react-navigation-menu \
    @radix-ui/react-popover @radix-ui/react-progress @radix-ui/react-radio-group \
    @radix-ui/react-scroll-area @radix-ui/react-select @radix-ui/react-separator \
    @radix-ui/react-slider @radix-ui/react-slot @radix-ui/react-switch \
    @radix-ui/react-tabs @radix-ui/react-toast @radix-ui/react-toggle \
    @radix-ui/react-toggle-group @radix-ui/react-tooltip

pnpm install sonner cmdk vaul embla-carousel-react react-day-picker \
    react-resizable-panels date-fns react-hook-form @hookform/resolvers zod

COMPONENTS_TARBALL="$SCRIPT_DIR/shadcn-components.tar.gz"
if [[ -f "$COMPONENTS_TARBALL" ]]; then
    echo "Extracting shadcn/ui components from tarball..."
    tar -xzf "$COMPONENTS_TARBALL" -C src/
else
    echo "Note: shadcn-components.tar.gz not found."
    echo "  Install components manually: npx shadcn@latest init && npx shadcn@latest add --all"
fi

echo ""
echo "Project ready: $PROJECT_NAME"
echo "  cd $PROJECT_NAME && pnpm dev"
