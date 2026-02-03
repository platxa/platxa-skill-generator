---
name: platxa-monaco-config
description: Monaco editor configuration guide for Platxa platform. Configure themes, keybindings, editor options, and optimize performance with ready-to-use presets.
allowed-tools:
  - Read
  - Glob
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - guide
    - monaco
    - editor
    - configuration
---

# Platxa Monaco Configuration

Guide for configuring Monaco editor in the Platxa platform with themes, keybindings, and optimized presets.

## Overview

This skill helps configure Monaco editor settings for the Platxa IDE:

| Category | What You Can Configure |
|----------|----------------------|
| **Editor Behavior** | Font size, tab size, word wrap, cursor style |
| **Visual Settings** | Minimap, scrollbars, line highlighting, bracket colors |
| **Themes** | Built-in themes, custom themes, token colors |
| **Keybindings** | Default keys, Vim mode, Emacs mode, custom bindings |
| **Performance** | Large file optimization, tokenization limits |
| **Accessibility** | Screen reader support, high contrast themes |

## Workflow

When configuring Monaco editor, follow this workflow:

### Step 1: Identify Configuration Need

Determine what you want to configure:
- **Editor behavior** → Use editor options (fontSize, tabSize, wordWrap)
- **Visual appearance** → Use themes and color customization
- **Keyboard shortcuts** → Use keybindings (default, Vim, Emacs)
- **Performance issues** → Use large file optimizations

### Step 2: Choose a Preset or Custom

- **Standard use case**: Apply a preset from Configuration Presets section
- **Custom needs**: Start with a preset, then override specific options

### Step 3: Apply Configuration

```typescript
// Option 1: At creation time
const editor = monaco.editor.create(container, { ...options });

// Option 2: Update existing editor
editor.updateOptions({ fontSize: 16, minimap: { enabled: false } });
```

### Step 4: Verify Changes

Test the configuration:
1. Check visual appearance matches expectations
2. Verify keybindings work correctly
3. Test performance with representative file sizes

## Quick Start

### Apply a Preset

Choose a preset based on your use case:

```typescript
import { defaultEditorOptions } from '@/features/editor/config/editorOptions';

// Use directly or spread and override
const options = {
  ...defaultEditorOptions,
  fontSize: 16,  // Override specific setting
};
```

### Change Theme

```typescript
import * as monaco from 'monaco-editor';

// Built-in themes
monaco.editor.setTheme('vs-dark');  // Dark theme
monaco.editor.setTheme('vs');       // Light theme
monaco.editor.setTheme('hc-black'); // High contrast
```

### Enable Vim Mode

```typescript
import { initVimMode } from 'monaco-vim';

const statusBar = document.getElementById('vim-status');
const vimMode = initVimMode(editor, statusBar);

// To disable: vimMode.dispose();
```

## Configuration Presets

### Default (Platxa)

Optimized for Python/JavaScript development in Platxa:

```typescript
const platxaDefault = {
  fontSize: 14,
  fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
  fontLigatures: true,
  tabSize: 2,
  insertSpaces: true,
  wordWrap: 'off',
  lineNumbers: 'on',
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  automaticLayout: true,
  bracketPairColorization: { enabled: true },
  cursorBlinking: 'smooth',
  cursorSmoothCaretAnimation: 'on',
  renderWhitespace: 'selection',
  accessibilitySupport: 'auto',
};
```

### Minimal

Distraction-free editing:

```typescript
const minimal = {
  fontSize: 16,
  lineNumbers: 'off',
  minimap: { enabled: false },
  scrollbar: { vertical: 'hidden', horizontal: 'hidden' },
  overviewRulerBorder: false,
  hideCursorInOverviewRuler: true,
  overviewRulerLanes: 0,
  renderLineHighlight: 'none',
  folding: false,
  glyphMargin: false,
  lineDecorationsWidth: 0,
  lineNumbersMinChars: 0,
};
```

### Large File

Performance optimized for files > 1MB:

```typescript
const largeFile = {
  minimap: { enabled: false },
  folding: false,
  wordWrap: 'off',
  renderWhitespace: 'none',
  renderControlCharacters: false,
  quickSuggestions: false,
  suggestOnTriggerCharacters: false,
  maxTokenizationLineLength: 5000,
  stopRenderingLineAfter: 5000,
  largeFileOptimizations: true,
};
```

### Read-Only

For code viewing and diffs:

```typescript
const readOnly = {
  readOnly: true,
  cursorStyle: 'block',
  cursorBlinking: 'solid',
  renderLineHighlight: 'none',
  matchBrackets: 'never',
  selectionHighlight: false,
  occurrencesHighlight: 'off',
};
```

### Accessibility

Screen reader optimized:

```typescript
const accessibility = {
  accessibilitySupport: 'on',
  ariaLabel: 'Code editor - press F1 for accessibility help',
  screenReaderAnnounceInlineSuggestion: true,
  accessibilityPageSize: 20,
  cursorWidth: 3,
  fontSize: 16,
  lineHeight: 1.8,
};
```

### Diff Editor

Side-by-side comparison:

```typescript
const diffEditor = {
  renderSideBySide: true,
  enableSplitViewResizing: true,
  renderOverviewRuler: true,
  ignoreTrimWhitespace: true,
  renderIndicators: true,
  originalEditable: false,
};
```

## Examples

### Example 1: Configure Distraction-Free Mode

**User**: "I want a minimal editor without distractions"

**Response**:

Apply the minimal preset to remove visual clutter:

```typescript
const editor = monaco.editor.create(container, {
  value: content,
  language: 'python',
  theme: 'vs-dark',
  // Minimal preset
  fontSize: 16,
  lineNumbers: 'off',
  minimap: { enabled: false },
  scrollbar: { vertical: 'hidden', horizontal: 'hidden' },
  overviewRulerBorder: false,
  renderLineHighlight: 'none',
  folding: false,
  glyphMargin: false,
  lineDecorationsWidth: 0,
});
```

Toggle back to normal mode by updating options:
```typescript
editor.updateOptions({ lineNumbers: 'on', minimap: { enabled: true } });
```

### Example 2: Enable Vim Keybindings

**User**: "Enable Vim keybindings in Monaco"

**Response**:

1. Install monaco-vim:
```bash
pnpm add monaco-vim
```

2. Initialize after editor creation:
```typescript
import { initVimMode, VimMode } from 'monaco-vim';

// Create status bar element for Vim mode display
const statusBar = document.createElement('div');
statusBar.id = 'vim-status';
container.appendChild(statusBar);

// Initialize Vim mode
const vimMode = initVimMode(editor, statusBar);

// To disable Vim mode
function toggleVim(enabled: boolean) {
  if (enabled) {
    vimMode = initVimMode(editor, statusBar);
  } else {
    vimMode?.dispose();
  }
}
```

Supported Vim commands: Most normal mode, insert mode, visual mode commands. Ex commands are limited.

### Example 3: Create Custom Theme

**User**: "Create a dark theme with purple keywords"

**Response**:

Define and register custom theme:

```typescript
monaco.editor.defineTheme('platxa-purple', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '#6A9955', fontStyle: 'italic' },
    { token: 'keyword', foreground: '#C792EA' },  // Purple keywords
    { token: 'string', foreground: '#C3E88D' },
    { token: 'number', foreground: '#F78C6C' },
    { token: 'type', foreground: '#FFCB6B' },
    { token: 'function', foreground: '#82AAFF' },
    { token: 'variable', foreground: '#89DDFF' },
    { token: 'operator', foreground: '#89DDFF' },
  ],
  colors: {
    'editor.background': '#0F111A',
    'editor.foreground': '#A6ACCD',
    'editor.lineHighlightBackground': '#1A1C25',
    'editor.selectionBackground': '#717CB450',
    'editorCursor.foreground': '#FFCC00',
    'editorLineNumber.foreground': '#3B3F51',
    'editorLineNumber.activeForeground': '#A6ACCD',
  },
});

// Apply theme
monaco.editor.setTheme('platxa-purple');
```

### Example 4: Optimize for Large Files

**User**: "The editor is slow with large log files"

**Response**:

Large files (>1MB) need optimization to prevent UI freezing:

```typescript
function getEditorOptions(fileSize: number) {
  const isLargeFile = fileSize > 1_000_000; // 1MB threshold

  if (isLargeFile) {
    return {
      // Disable expensive features
      minimap: { enabled: false },
      folding: false,
      wordWrap: 'off',
      renderWhitespace: 'none',
      quickSuggestions: false,

      // Limit tokenization
      maxTokenizationLineLength: 5000,
      stopRenderingLineAfter: 5000,
      largeFileOptimizations: true,

      // Disable bracket matching
      matchBrackets: 'never',
      bracketPairColorization: { enabled: false },
    };
  }

  return defaultEditorOptions;
}
```

For files >10MB, consider streaming or pagination instead of loading entirely.

## Best Practices

### Font Configuration

```typescript
// Recommended programming fonts with ligature support
fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Source Code Pro', monospace",
fontLigatures: true,  // Enable => -> !== etc.
fontSize: 14,         // 14-16 for most displays
lineHeight: 1.6,      // Comfortable line spacing
```

### Performance Tips

1. **Disable minimap** for better performance on lower-end devices
2. **Use `automaticLayout: true`** for responsive containers
3. **Limit suggestions** if not needed: `quickSuggestions: false`
4. **Lazy load editor** with React.lazy() or dynamic imports

### Theme Selection

| Use Case | Recommended Theme |
|----------|------------------|
| Long coding sessions | Dark theme (`vs-dark`) |
| Bright environments | Light theme (`vs`) |
| Vision impairment | High contrast (`hc-black`, `hc-light`) |
| Presentations | Light with large font |

### Keybinding Modes

| Mode | Best For |
|------|----------|
| Default | New developers, VS Code users |
| Vim | Experienced Vim users, keyboard-centric workflow |
| Emacs | Emacs users |

## Troubleshooting

### Editor Not Rendering

**Symptom**: Blank container, no editor visible

**Fix**: Ensure container has explicit height:
```css
.editor-container {
  height: 500px;  /* Or use flex/grid with defined height */
  width: 100%;
}
```

### Fonts Not Loading

**Symptom**: Fallback font displaying instead of custom font

**Fix**: Ensure font is loaded before editor initialization:
```typescript
await document.fonts.load('14px "JetBrains Mono"');
monaco.editor.create(container, options);
```

### Theme Not Applying

**Symptom**: Theme registered but not visible

**Fix**: Register theme before creating editor, or call setTheme after:
```typescript
monaco.editor.defineTheme('myTheme', themeData);
monaco.editor.setTheme('myTheme');  // Must call after defineTheme
```

### Vim Mode Issues

**Symptom**: Some Vim commands not working

**Known Limitations**:
- Ex commands (`:w`, `:q`) not supported by default
- Macros have limited support
- Some plugins not available

### Slow Performance

**Symptom**: Lag when typing or scrolling

**Diagnostic Steps**:
1. Check file size (>1MB needs optimization)
2. Disable minimap: `minimap: { enabled: false }`
3. Reduce tokenization: `maxTokenizationLineLength: 5000`
4. Check for memory leaks: dispose unused editors

## Output Checklist

After configuring Monaco editor, verify:

- [ ] Editor renders correctly with specified dimensions
- [ ] Theme applies (check syntax highlighting colors)
- [ ] Font family and size display correctly
- [ ] Keybindings work (test Ctrl+F for find, Ctrl+/ for comment)
- [ ] If using Vim/Emacs mode, verify mode indicator and commands
- [ ] Performance acceptable (no lag on scroll/type)
- [ ] `automaticLayout: true` if container is resizable

## Related Resources

- **Code Generation**: Use `monaco-editor-integrator` package in platxa-agent-generator for scaffolding
- **Yjs Integration**: See `YjsProvider` and `useMonacoBinding` hooks for collaboration
- **Full Options Reference**: See `references/editor-options.md`
