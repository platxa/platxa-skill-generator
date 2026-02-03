# Monaco Editor Options Reference

Complete reference for Monaco editor configuration options.

## Editor Behavior

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fontSize` | number | 14 | Font size in pixels |
| `fontFamily` | string | 'Consolas' | Font family name(s) |
| `fontLigatures` | boolean | false | Enable font ligatures |
| `tabSize` | number | 4 | Number of spaces per tab |
| `insertSpaces` | boolean | true | Use spaces instead of tabs |
| `lineHeight` | number | 0 | Line height (0 = auto) |

## Word Wrap

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `wordWrap` | string | 'off' | 'off', 'on', 'wordWrapColumn', 'bounded' |
| `wordWrapColumn` | number | 80 | Column for 'wordWrapColumn' mode |
| `wrappingIndent` | string | 'same' | 'none', 'same', 'indent', 'deepIndent' |

## Cursor & Line Numbers

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cursorStyle` | string | 'line' | 'line', 'block', 'underline' |
| `cursorBlinking` | string | 'blink' | 'blink', 'smooth', 'phase', 'solid' |
| `lineNumbers` | string | 'on' | 'on', 'off', 'relative', 'interval' |
| `glyphMargin` | boolean | true | Show glyph margin |

## Minimap & Scrollbar

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `minimap.enabled` | boolean | true | Show minimap |
| `minimap.side` | string | 'right' | 'right', 'left' |
| `minimap.renderCharacters` | boolean | true | Render actual characters |
| `scrollBeyondLastLine` | boolean | true | Allow scroll past last line |
| `smoothScrolling` | boolean | false | Smooth scroll animation |

## Suggestions

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `quickSuggestions` | boolean | true | Auto show suggestions |
| `suggestOnTriggerCharacters` | boolean | true | Suggest on trigger chars |
| `acceptSuggestionOnEnter` | string | 'on' | 'on', 'smart', 'off' |
| `tabCompletion` | string | 'off' | 'on', 'off', 'onlySnippets' |

## Rendering & Brackets

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `renderWhitespace` | string | 'selection' | 'none', 'selection', 'all' |
| `renderLineHighlight` | string | 'line' | 'none', 'gutter', 'line', 'all' |
| `bracketPairColorization.enabled` | boolean | true | Colorize bracket pairs |
| `matchBrackets` | string | 'always' | 'never', 'near', 'always' |
| `guides.indentation` | boolean | true | Show indentation guides |

## Folding & Performance

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `folding` | boolean | true | Enable code folding |
| `foldingStrategy` | string | 'auto' | 'auto', 'indentation' |
| `largeFileOptimizations` | boolean | true | Enable for large files |
| `maxTokenizationLineLength` | number | 20000 | Max line to tokenize |
| `stopRenderingLineAfter` | number | 10000 | Stop rendering after column |

## Accessibility & Read-Only

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `accessibilitySupport` | string | 'auto' | 'auto', 'on', 'off' |
| `ariaLabel` | string | 'Editor' | ARIA label |
| `readOnly` | boolean | false | Make editor read-only |

## Formatting

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `formatOnType` | boolean | false | Format on type |
| `formatOnPaste` | boolean | false | Format on paste |
| `autoIndent` | string | 'advanced' | 'none', 'keep', 'brackets', 'full' |
| `autoClosingBrackets` | string | 'languageDefined' | Auto close brackets |

## Recommended Configurations

### Python
```typescript
{ tabSize: 4, insertSpaces: true, wordWrap: 'off' }
```

### JavaScript/TypeScript
```typescript
{ tabSize: 2, formatOnPaste: true, bracketPairColorization: { enabled: true } }
```

### Markdown
```typescript
{ wordWrap: 'on', lineNumbers: 'off', minimap: { enabled: false } }
```
