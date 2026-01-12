# Monaco Editor Options Reference

Complete reference for Monaco editor configuration options.

## Editor Behavior

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fontSize` | number | 14 | Font size in pixels |
| `fontFamily` | string | 'Consolas' | Font family name(s) |
| `fontWeight` | string | 'normal' | Font weight (normal, bold, 100-900) |
| `fontLigatures` | boolean | false | Enable font ligatures |
| `lineHeight` | number | 0 | Line height (0 = computed from fontSize) |
| `letterSpacing` | number | 0 | Letter spacing in pixels |
| `tabSize` | number | 4 | Number of spaces per tab |
| `insertSpaces` | boolean | true | Use spaces instead of tabs |
| `detectIndentation` | boolean | true | Auto-detect indentation |
| `trimAutoWhitespace` | boolean | true | Remove trailing whitespace |

## Word Wrap

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `wordWrap` | string | 'off' | 'off', 'on', 'wordWrapColumn', 'bounded' |
| `wordWrapColumn` | number | 80 | Column for 'wordWrapColumn' mode |
| `wordWrapMinified` | boolean | true | Force wrap for minified files |
| `wrappingIndent` | string | 'same' | 'none', 'same', 'indent', 'deepIndent' |
| `wrappingStrategy` | string | 'simple' | 'simple', 'advanced' |

## Cursor

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cursorStyle` | string | 'line' | 'line', 'block', 'underline', 'line-thin', 'block-outline', 'underline-thin' |
| `cursorBlinking` | string | 'blink' | 'blink', 'smooth', 'phase', 'expand', 'solid' |
| `cursorSmoothCaretAnimation` | string | 'off' | 'off', 'explicit', 'on' |
| `cursorWidth` | number | 0 | Cursor width (0 = default) |

## Line Numbers

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `lineNumbers` | string | 'on' | 'on', 'off', 'relative', 'interval' |
| `lineNumbersMinChars` | number | 5 | Min characters for line number gutter |
| `lineDecorationsWidth` | number | 10 | Width of line decorations gutter |
| `glyphMargin` | boolean | true | Show glyph margin (breakpoints) |

## Minimap

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `minimap.enabled` | boolean | true | Show minimap |
| `minimap.side` | string | 'right' | 'right', 'left' |
| `minimap.showSlider` | string | 'mouseover' | 'always', 'mouseover' |
| `minimap.renderCharacters` | boolean | true | Render actual characters |
| `minimap.maxColumn` | number | 120 | Max columns to render |
| `minimap.scale` | number | 1 | Minimap scale (1-3) |

## Scrollbar

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `scrollbar.vertical` | string | 'auto' | 'auto', 'visible', 'hidden' |
| `scrollbar.horizontal` | string | 'auto' | 'auto', 'visible', 'hidden' |
| `scrollbar.verticalScrollbarSize` | number | 14 | Vertical scrollbar width |
| `scrollbar.horizontalScrollbarSize` | number | 12 | Horizontal scrollbar height |
| `scrollbar.useShadows` | boolean | true | Show shadows on scroll |
| `scrollBeyondLastLine` | boolean | true | Allow scroll past last line |
| `smoothScrolling` | boolean | false | Smooth scroll animation |

## Suggestions & IntelliSense

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `quickSuggestions` | boolean/object | true | Auto show suggestions |
| `quickSuggestions.other` | boolean | true | Suggestions in code |
| `quickSuggestions.comments` | boolean | false | Suggestions in comments |
| `quickSuggestions.strings` | boolean | false | Suggestions in strings |
| `suggestOnTriggerCharacters` | boolean | true | Suggest on trigger chars |
| `acceptSuggestionOnEnter` | string | 'on' | 'on', 'smart', 'off' |
| `snippetSuggestions` | string | 'inline' | 'top', 'bottom', 'inline', 'none' |
| `tabCompletion` | string | 'off' | 'on', 'off', 'onlySnippets' |
| `suggest.showWords` | boolean | true | Show word suggestions |
| `suggest.localityBonus` | boolean | false | Boost nearby suggestions |

## Rendering

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `renderWhitespace` | string | 'selection' | 'none', 'boundary', 'selection', 'trailing', 'all' |
| `renderControlCharacters` | boolean | true | Render control characters |
| `renderLineHighlight` | string | 'line' | 'none', 'gutter', 'line', 'all' |
| `renderLineHighlightOnlyWhenFocus` | boolean | false | Highlight only when focused |
| `fontFamily` | string | system | Editor font family |

## Brackets

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bracketPairColorization.enabled` | boolean | true | Colorize bracket pairs |
| `bracketPairColorization.independentColorPoolPerBracketType` | boolean | false | Separate colors per type |
| `matchBrackets` | string | 'always' | 'never', 'near', 'always' |
| `guides.bracketPairs` | boolean/string | false | Show bracket guides |
| `guides.indentation` | boolean | true | Show indentation guides |

## Folding

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `folding` | boolean | true | Enable code folding |
| `foldingStrategy` | string | 'auto' | 'auto', 'indentation' |
| `foldingHighlight` | boolean | true | Highlight folding regions |
| `showFoldingControls` | string | 'mouseover' | 'always', 'never', 'mouseover' |
| `unfoldOnClickAfterEndOfLine` | boolean | false | Click after line unfolds |

## Performance

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `largeFileOptimizations` | boolean | true | Enable for large files |
| `maxTokenizationLineLength` | number | 20000 | Max line length to tokenize |
| `stopRenderingLineAfter` | number | 10000 | Stop rendering after column |
| `disableLayerHinting` | boolean | false | Disable compositor hints |
| `disableMonospaceOptimizations` | boolean | false | Disable mono optimizations |

## Accessibility

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `accessibilitySupport` | string | 'auto' | 'auto', 'on', 'off' |
| `ariaLabel` | string | 'Editor content' | ARIA label for screen readers |
| `accessibilityPageSize` | number | 10 | Lines per screen reader page |
| `screenReaderAnnounceInlineSuggestion` | boolean | true | Announce suggestions |

## Read-Only

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `readOnly` | boolean | false | Make editor read-only |
| `readOnlyMessage` | object | undefined | Message for read-only tooltip |
| `domReadOnly` | boolean | false | Use DOM contenteditable=false |

## Selection

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `selectionHighlight` | boolean | true | Highlight selection matches |
| `occurrencesHighlight` | string | 'singleFile' | Highlight word occurrences |
| `roundedSelection` | boolean | true | Rounded selection corners |
| `columnSelection` | boolean | false | Enable column selection |
| `multiCursorModifier` | string | 'alt' | 'ctrlCmd', 'alt' |

## Formatting

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `formatOnType` | boolean | false | Format on type |
| `formatOnPaste` | boolean | false | Format on paste |
| `autoIndent` | string | 'advanced' | 'none', 'keep', 'brackets', 'advanced', 'full' |
| `autoClosingBrackets` | string | 'languageDefined' | 'always', 'languageDefined', 'beforeWhitespace', 'never' |
| `autoClosingQuotes` | string | 'languageDefined' | Same as brackets |
| `autoSurround` | string | 'languageDefined' | 'languageDefined', 'quotes', 'brackets', 'never' |

## Recommended Configurations

### Python Development
```typescript
{
  tabSize: 4,
  insertSpaces: true,
  rulers: [79, 120],
  wordWrap: 'off',
  formatOnType: false,
}
```

### JavaScript/TypeScript
```typescript
{
  tabSize: 2,
  insertSpaces: true,
  formatOnPaste: true,
  bracketPairColorization: { enabled: true },
}
```

### JSON Editing
```typescript
{
  tabSize: 2,
  formatOnPaste: true,
  folding: true,
  foldingStrategy: 'auto',
}
```

### Markdown
```typescript
{
  wordWrap: 'on',
  lineNumbers: 'off',
  minimap: { enabled: false },
  quickSuggestions: false,
}
```
