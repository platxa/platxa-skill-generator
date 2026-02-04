# Figma Implementation Rules

Rules for translating Figma MCP output into production code. Apply these after fetching design context and screenshots.

## Code Translation Rules

### React + Tailwind Output Adaptation

The MCP server defaults to React + Tailwind output. Treat this as a design representation, not final code.

1. **Replace Tailwind utilities** with project design-system tokens:
   - `bg-indigo-500` -> `bg-primary` or `var(--color-primary-500)`
   - `p-4` -> `var(--spacing-md)` or the project's spacing scale
   - `text-lg font-semibold` -> project typography class (`heading-md`)

2. **Reuse existing components** from the project's component library:
   - Check `get_code_connect_map` for registered components first
   - Buttons, inputs, selects, modals, cards -> use project versions
   - Icon wrappers -> use the project's icon system, not raw SVGs

3. **Preserve project patterns**:
   - Follow existing routing conventions (Next.js App Router, Vue Router, SvelteKit)
   - Use the project's state management (Zustand, Pinia, Redux, Context)
   - Match existing data-fetching patterns (SWR, TanStack Query, server actions)

### Framework-Specific Prompts

Override the default React + Tailwind scaffold by specifying your target framework:

| Framework | Prompt Directive |
|-----------|-----------------|
| Vue 3 + Composition API | `"generate in Vue 3 with <script setup>"` |
| Svelte 5 | `"generate in Svelte with runes"` |
| Angular | `"generate as Angular standalone component"` |
| Plain HTML/CSS | `"generate in plain HTML + CSS, no framework"` |
| iOS SwiftUI | `"generate for iOS SwiftUI"` |
| React Native | `"generate for React Native with StyleSheet"` |

## Asset Handling Rules

### Localhost Sources

When the MCP server returns a `localhost` URL for an image or SVG asset:

- Use the URL directly as `src` or `href` -- the server hosts it during the session
- Do **not** replace it with a placeholder (`placeholder.png`, `#`)
- Do **not** download and re-host unless the asset needs to persist beyond the session

### Icon Packages

- Do **not** import new icon packages (`lucide-react`, `heroicons`, `@mdi/js`)
- All icons should come from the Figma payload via the MCP server
- If an icon is missing from the payload, ask the user to check the Figma file

### Image Optimization

For production builds after the MCP session:

1. Download assets from localhost URLs to `public/assets/` or the project's asset directory
2. Convert PNGs to WebP where supported: `cwebp input.png -o output.webp`
3. Optimize SVGs: `svgo input.svg -o output.svg`
4. Update `src` references to point to the persisted file paths

## Design Token Mapping

### Color Tokens

Map Figma color variables to project CSS custom properties:

```css
/* Figma variable -> Project token */
Primary/500  -> var(--color-primary-500)   /* #6366F1 */
Primary/600  -> var(--color-primary-600)   /* #4F46E5 */
Gray/100     -> var(--color-gray-100)      /* #F3F4F6 */
Gray/900     -> var(--color-gray-900)      /* #111827 */
```

### Spacing Tokens

```css
/* Figma spacing -> Project token */
4px   -> var(--spacing-xs)     /* 0.25rem */
8px   -> var(--spacing-sm)     /* 0.5rem  */
16px  -> var(--spacing-md)     /* 1rem    */
24px  -> var(--spacing-lg)     /* 1.5rem  */
32px  -> var(--spacing-xl)     /* 2rem    */
```

### Typography Scale

```css
/* Figma text style -> Project class */
Heading/XL    -> .heading-xl    /* 2.25rem/700 */
Heading/LG    -> .heading-lg    /* 1.875rem/700 */
Body/Base     -> .body-base     /* 1rem/400 */
Body/SM       -> .body-sm       /* 0.875rem/400 */
Caption       -> .caption       /* 0.75rem/400 */
```

## Visual Parity Validation

After implementation, verify against the Figma screenshot:

1. **Layout**: Elements positioned correctly relative to each other
2. **Spacing**: Padding and margins match the design within 2px tolerance
3. **Colors**: Background, text, and border colors match token values
4. **Typography**: Font family, size, weight, and line height match the design
5. **Borders**: Border radius, width, and color match
6. **Shadows**: Box shadows match Figma's elevation/shadow styles
7. **Responsive**: If the Figma file includes responsive variants, verify breakpoints

When conflicts arise between the Figma design and the project's design system, prefer design-system tokens and adjust spacing or sizes minimally to match the visual intent.
