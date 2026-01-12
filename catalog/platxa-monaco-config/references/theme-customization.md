# Monaco Theme Customization

Guide for creating and customizing Monaco editor themes.

## Built-in Themes

| Theme | Description |
|-------|-------------|
| `vs` | Light theme (VS Code default) |
| `vs-dark` | Dark theme (VS Code default) |
| `hc-black` | High contrast dark (accessibility) |
| `hc-light` | High contrast light (accessibility) |

## Theme Structure

```typescript
interface ThemeData {
  base: 'vs' | 'vs-dark' | 'hc-black' | 'hc-light';
  inherit: boolean;
  rules: Array<{ token: string; foreground?: string; fontStyle?: string }>;
  colors: Record<string, string>;
}
```

## Defining Custom Themes

```typescript
monaco.editor.defineTheme('myTheme', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
    { token: 'keyword', foreground: 'C586C0' },
    { token: 'string', foreground: 'CE9178' },
  ],
  colors: { 'editor.background': '#1E1E1E' }
});

monaco.editor.setTheme('myTheme');
```

## Token Scopes

### Basic Tokens

| Token | Description |
|-------|-------------|
| `comment` | Comments |
| `keyword` | Language keywords (`if`, `for`, `class`) |
| `string` | String literals |
| `number` | Numeric literals |
| `operator` | Operators (`+`, `=`, `&&`) |
| `type` | Type names |
| `function` | Function names |
| `variable` | Variable names |

### Language-Specific

```typescript
{ token: 'keyword.python', foreground: 'FF79C6' }
{ token: 'tag', foreground: 'E06C75' }  // HTML
{ token: 'attribute.name', foreground: 'D19A66' }
```

## Editor Colors

### Core Colors

| Key | Description |
|-----|-------------|
| `editor.background` | Editor background |
| `editor.foreground` | Default text color |
| `editorCursor.foreground` | Cursor color |
| `editor.lineHighlightBackground` | Current line |
| `editor.selectionBackground` | Selection |
| `editorLineNumber.foreground` | Line numbers |

### Brackets & Matching

| Key | Description |
|-----|-------------|
| `editorBracketMatch.background` | Matching bracket |
| `editorBracketHighlight.foreground1` | Bracket pair color 1 |
| `editorBracketHighlight.foreground2` | Bracket pair color 2 |

## Example Theme

```typescript
monaco.editor.defineTheme('one-dark', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '5C6370', fontStyle: 'italic' },
    { token: 'keyword', foreground: 'C678DD' },
    { token: 'string', foreground: '98C379' },
    { token: 'number', foreground: 'D19A66' },
    { token: 'type', foreground: 'E5C07B' },
    { token: 'function', foreground: '61AFEF' },
    { token: 'variable', foreground: 'E06C75' },
  ],
  colors: {
    'editor.background': '#282C34',
    'editor.foreground': '#ABB2BF',
    'editor.lineHighlightBackground': '#2C313A',
    'editor.selectionBackground': '#3E4451',
    'editorCursor.foreground': '#528BFF',
    'editorLineNumber.foreground': '#4B5263',
  }
});
```

## Dynamic Theme Switching

```typescript
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

function updateTheme() {
  monaco.editor.setTheme(prefersDark.matches ? 'vs-dark' : 'vs');
}

prefersDark.addEventListener('change', updateTheme);
updateTheme();
```

## Validation Rules

1. Foreground colors: 6-char hex without `#` (e.g., `6A9955`)
2. Editor colors: Include `#` (e.g., `#1E1E1E`)
3. Font styles: `italic`, `bold`, `underline`, or space-separated combinations
