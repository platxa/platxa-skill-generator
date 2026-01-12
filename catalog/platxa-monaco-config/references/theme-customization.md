# Monaco Theme Customization

Guide for creating and customizing Monaco editor themes.

## Built-in Themes

| Theme | Description |
|-------|-------------|
| `vs` | Light theme (VS Code default light) |
| `vs-dark` | Dark theme (VS Code default dark) |
| `hc-black` | High contrast dark (accessibility) |
| `hc-light` | High contrast light (accessibility) |

## Theme Structure

```typescript
interface ThemeData {
  base: 'vs' | 'vs-dark' | 'hc-black' | 'hc-light';
  inherit: boolean;
  rules: TokenRule[];
  colors: Record<string, string>;
}

interface TokenRule {
  token: string;           // Token scope
  foreground?: string;     // Hex color (without #)
  background?: string;     // Hex color (without #)
  fontStyle?: string;      // 'italic', 'bold', 'underline', 'strikethrough'
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
  colors: {
    'editor.background': '#1E1E1E',
  }
});

// Apply theme
monaco.editor.setTheme('myTheme');
```

## Token Scopes

### Basic Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `comment` | Comments | `// comment`, `/* block */` |
| `keyword` | Language keywords | `if`, `for`, `class` |
| `string` | String literals | `"hello"`, `'world'` |
| `number` | Numeric literals | `42`, `3.14` |
| `regexp` | Regular expressions | `/pattern/` |
| `operator` | Operators | `+`, `=`, `&&` |
| `delimiter` | Delimiters | `()`, `{}`, `[]` |
| `identifier` | Identifiers | Variable names |

### Semantic Tokens

| Token | Description |
|-------|-------------|
| `type` | Type names |
| `type.identifier` | Type identifiers |
| `function` | Function names |
| `function.declaration` | Function declarations |
| `variable` | Variable names |
| `variable.readonly` | Constants |
| `parameter` | Function parameters |
| `property` | Object properties |
| `class` | Class names |
| `interface` | Interface names |
| `namespace` | Namespace names |
| `enum` | Enum names |
| `enumMember` | Enum members |

### Language-Specific Tokens

```typescript
// Python
{ token: 'keyword.python', foreground: 'FF79C6' }
{ token: 'string.python', foreground: 'F1FA8C' }

// JavaScript
{ token: 'keyword.js', foreground: 'FF79C6' }
{ token: 'string.js', foreground: 'F1FA8C' }

// HTML
{ token: 'tag', foreground: 'E06C75' }
{ token: 'attribute.name', foreground: 'D19A66' }
{ token: 'attribute.value', foreground: '98C379' }
```

## Editor Colors

### Editor Background & Foreground

| Key | Description |
|-----|-------------|
| `editor.background` | Editor background |
| `editor.foreground` | Default text color |
| `editorCursor.foreground` | Cursor color |
| `editorCursor.background` | Cursor background (block cursor) |

### Line Highlighting

| Key | Description |
|-----|-------------|
| `editor.lineHighlightBackground` | Current line background |
| `editor.lineHighlightBorder` | Current line border |
| `editorLineNumber.foreground` | Line number color |
| `editorLineNumber.activeForeground` | Active line number |

### Selection

| Key | Description |
|-----|-------------|
| `editor.selectionBackground` | Selection background |
| `editor.selectionForeground` | Selection text color |
| `editor.inactiveSelectionBackground` | Unfocused selection |
| `editor.selectionHighlightBackground` | Match selection highlight |

### Find & Replace

| Key | Description |
|-----|-------------|
| `editor.findMatchBackground` | Current match |
| `editor.findMatchHighlightBackground` | Other matches |
| `editor.findRangeHighlightBackground` | Range highlight |

### Brackets

| Key | Description |
|-----|-------------|
| `editorBracketMatch.background` | Matching bracket background |
| `editorBracketMatch.border` | Matching bracket border |
| `editorBracketHighlight.foreground1` | Bracket pair color 1 |
| `editorBracketHighlight.foreground2` | Bracket pair color 2 |
| `editorBracketHighlight.foreground3` | Bracket pair color 3 |

### Gutter & Minimap

| Key | Description |
|-----|-------------|
| `editorGutter.background` | Gutter background |
| `editorGutter.modifiedBackground` | Modified line indicator |
| `editorGutter.addedBackground` | Added line indicator |
| `editorGutter.deletedBackground` | Deleted line indicator |
| `minimap.background` | Minimap background |
| `minimapSlider.background` | Minimap slider |

## Example Themes

### Material Darker

```typescript
monaco.editor.defineTheme('material-darker', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '545454', fontStyle: 'italic' },
    { token: 'keyword', foreground: 'C792EA' },
    { token: 'string', foreground: 'C3E88D' },
    { token: 'number', foreground: 'F78C6C' },
    { token: 'type', foreground: 'FFCB6B' },
    { token: 'function', foreground: '82AAFF' },
    { token: 'variable', foreground: 'EEFFFF' },
    { token: 'operator', foreground: '89DDFF' },
  ],
  colors: {
    'editor.background': '#212121',
    'editor.foreground': '#EEFFFF',
    'editor.lineHighlightBackground': '#1A1A1A',
    'editor.selectionBackground': '#61616150',
    'editorCursor.foreground': '#FFCC00',
    'editorLineNumber.foreground': '#424242',
  }
});
```

### Solarized Dark

```typescript
monaco.editor.defineTheme('solarized-dark', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '586E75', fontStyle: 'italic' },
    { token: 'keyword', foreground: '859900' },
    { token: 'string', foreground: '2AA198' },
    { token: 'number', foreground: 'D33682' },
    { token: 'type', foreground: 'B58900' },
    { token: 'function', foreground: '268BD2' },
    { token: 'variable', foreground: '839496' },
  ],
  colors: {
    'editor.background': '#002B36',
    'editor.foreground': '#839496',
    'editor.lineHighlightBackground': '#073642',
    'editor.selectionBackground': '#274642',
    'editorCursor.foreground': '#D30102',
    'editorLineNumber.foreground': '#586E75',
  }
});
```

### One Dark Pro

```typescript
monaco.editor.defineTheme('one-dark-pro', {
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
    { token: 'constant', foreground: 'D19A66' },
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
// Detect system preference
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

function updateTheme() {
  monaco.editor.setTheme(prefersDark.matches ? 'vs-dark' : 'vs');
}

prefersDark.addEventListener('change', updateTheme);
updateTheme();
```

## Theme Validation

Before registering, validate your theme:

1. All foreground colors should be 6-char hex (no #)
2. All color keys should start with valid prefix (editor., editorCursor., etc.)
3. Font styles must be: 'italic', 'bold', 'underline', or combinations with space
