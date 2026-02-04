# Figma MCP Tool Catalog and Prompt Patterns

Complete reference for all Figma MCP tools with usage context, parameters, and prompt patterns.

## Core Design Tools

### get_design_context

**Context**: Figma Design, Figma Make
**Purpose**: Primary tool. Returns structured design data and generated code (default: React + Tailwind).
**Input**: Figma frame/layer URL with `node-id` parameter
**Output**: JSON with layer tree, styles, and code scaffold

The server extracts the `node-id` from the URL. Selection-based prompting works on desktop; the remote server requires a frame/layer link.

**Prompt patterns:**

```
"get the design context for https://figma.com/design/KEY/Name?node-id=42-100"
"generate my Figma selection in Vue"
"generate my Figma selection in plain HTML + CSS"
"generate my Figma selection for iOS SwiftUI"
"generate using components from src/components/ui"
"generate using components from src/ui and style with Tailwind"
```

### get_metadata

**Context**: Figma Design
**Purpose**: Sparse XML outline of layer IDs, names, types, positions, and sizes. Use before `get_design_context` on large nodes to avoid truncation.
**Input**: Figma URL with `node-id`
**Output**: XML outline with `<node id="..." name="..." type="..." x="..." y="..." width="..." height="...">`

Use when `get_design_context` returns truncated or overly large responses (100+ layers).

### get_screenshot

**Context**: Figma Design, FigJam
**Purpose**: PNG screenshot of the selected node variant. Use for visual fidelity checks.
**Input**: Figma URL with `node-id`
**Output**: PNG image data

Always capture a screenshot before starting implementation. Compare the final rendered output against this reference.

### get_variable_defs

**Context**: Figma Design
**Purpose**: Lists variables and styles (colors, spacing, typography) used in the selection.
**Input**: Figma URL with `node-id`
**Output**: JSON with variable names, values, and types

**Prompt patterns:**

```
"get the variables used in my Figma selection"
"what color and spacing variables are used in my Figma selection?"
"list the variable names and their values"
```

## FigJam Tools

### get_figjam

**Context**: FigJam only
**Purpose**: XML representation plus screenshots of FigJam boards (architecture diagrams, user flows, wireframes).
**Input**: FigJam URL
**Output**: XML structure + PNG screenshots

## Code Connect Tools

### get_code_connect_map

**Context**: Figma Design
**Purpose**: Returns existing mappings between Figma node IDs and code components.
**Output**: `{ "codeConnectSrc": "src/components/Button.tsx", "codeConnectName": "Button" }`

Check this before implementing a component to avoid duplicating existing work.

### add_code_connect_map

**Context**: Figma Design
**Purpose**: Registers a new mapping between a Figma node and a code component for future reuse.
**Input**: `nodeId`, `codeConnectSrc` (file path), `codeConnectName` (component name)

Register mappings after completing an implementation to build up the project's component library.

**Prompt patterns:**

```
"show the code connect map for this selection"
"map this node to src/components/ui/Button.tsx with name Button"
```

## Design System Tools

### create_design_system_rules

**Context**: No file context required
**Purpose**: Generates a rule file with design-to-code guidance tailored to your stack (framework, component library, token system).
**Output**: Markdown rule file

Save the output where the agent can read it. Useful for onboarding new team members to a project's Figma-to-code conventions.

## Alpha / Local-Only Tools

### get_strategy_for_mapping

**Context**: Local Dev Mode only (alpha)
**Purpose**: Figma-prompted tool that suggests a mapping strategy for connecting a node to a code component.

### send_get_strategy_response

**Context**: Local Dev Mode only (alpha)
**Purpose**: Sends the response back to Figma after `get_strategy_for_mapping`.

## Utility Tools

### whoami

**Context**: Remote server only
**Purpose**: Returns the authenticated Figma user identity including email, plan type, and seat types.
**Use**: Verify authentication is working correctly.

## Tool Selection Decision Tree

1. **Need structured code?** -> `get_design_context`
2. **Response too large?** -> `get_metadata` first, then `get_design_context` on children
3. **Need visual reference?** -> `get_screenshot`
4. **Need token values?** -> `get_variable_defs`
5. **Checking existing components?** -> `get_code_connect_map`
6. **Registering new component?** -> `add_code_connect_map`
7. **Working with FigJam?** -> `get_figjam`
8. **Setting up conventions?** -> `create_design_system_rules`
9. **Verifying auth?** -> `whoami`
