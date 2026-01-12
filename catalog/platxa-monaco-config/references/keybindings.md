# Monaco Keybindings Reference

Guide for keybindings, Vim mode, and Emacs mode in Monaco editor.

## Default Keybindings

### File Operations

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Save | Ctrl+S | Cmd+S |
| Save All | Ctrl+K S | Cmd+K S |
| Close Editor | Ctrl+W | Cmd+W |

### Edit Operations

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Undo | Ctrl+Z | Cmd+Z |
| Redo | Ctrl+Shift+Z / Ctrl+Y | Cmd+Shift+Z |
| Cut | Ctrl+X | Cmd+X |
| Copy | Ctrl+C | Cmd+C |
| Paste | Ctrl+V | Cmd+V |
| Delete Line | Ctrl+Shift+K | Cmd+Shift+K |
| Duplicate Line | Alt+Shift+Down | Opt+Shift+Down |
| Move Line Up | Alt+Up | Opt+Up |
| Move Line Down | Alt+Down | Opt+Down |
| Toggle Comment | Ctrl+/ | Cmd+/ |
| Block Comment | Alt+Shift+A | Opt+Shift+A |

### Selection

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Select All | Ctrl+A | Cmd+A |
| Select Line | Ctrl+L | Cmd+L |
| Select Word | Ctrl+D | Cmd+D |
| Select All Occurrences | Ctrl+Shift+L | Cmd+Shift+L |
| Expand Selection | Alt+Shift+Right | Opt+Shift+Right |
| Shrink Selection | Alt+Shift+Left | Opt+Shift+Left |
| Column Selection | Shift+Alt+Drag | Shift+Opt+Drag |
| Add Cursor Above | Ctrl+Alt+Up | Cmd+Opt+Up |
| Add Cursor Below | Ctrl+Alt+Down | Cmd+Opt+Down |

### Find & Replace

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Find | Ctrl+F | Cmd+F |
| Replace | Ctrl+H | Cmd+H |
| Find Next | F3 / Ctrl+G | Cmd+G |
| Find Previous | Shift+F3 | Cmd+Shift+G |
| Find in Selection | Alt+L | Cmd+L |

### Navigation

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Go to Line | Ctrl+G | Ctrl+G |
| Go to Start | Ctrl+Home | Cmd+Home |
| Go to End | Ctrl+End | Cmd+End |
| Go to Bracket | Ctrl+Shift+\ | Cmd+Shift+\ |
| Fold | Ctrl+Shift+[ | Cmd+Opt+[ |
| Unfold | Ctrl+Shift+] | Cmd+Opt+] |
| Command Palette | F1 / Ctrl+Shift+P | F1 / Cmd+Shift+P |

### Code Actions

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Format Document | Alt+Shift+F | Opt+Shift+F |
| Format Selection | Ctrl+K Ctrl+F | Cmd+K Cmd+F |
| Quick Fix | Ctrl+. | Cmd+. |
| Trigger Suggest | Ctrl+Space | Ctrl+Space |
| Parameter Hints | Ctrl+Shift+Space | Cmd+Shift+Space |

## Vim Mode

### Installation

```bash
pnpm add monaco-vim
```

### Setup

```typescript
import { initVimMode } from 'monaco-vim';

// Create status bar for mode display
const statusBar = document.createElement('div');
statusBar.className = 'vim-status-bar';
container.appendChild(statusBar);

// Initialize
const vimMode = initVimMode(editor, statusBar);

// Dispose when done
vimMode.dispose();
```

### Supported Vim Commands

**Normal Mode**:
- Movement: `h j k l w b e 0 $ ^ gg G`
- Editing: `d y p c x r s`
- Operators: `dd yy cc`
- Text objects: `iw aw i" a" i( a( i{ a{`
- Jumps: `% * # n N`
- Marks: `m' ``

**Insert Mode**:
- Enter: `i I a A o O`
- Exit: `Esc`

**Visual Mode**:
- Enter: `v V Ctrl+v`
- Operations: `d y c > < =`

**Command Mode (Limited)**:
- `:w` - Not supported (use Ctrl+S)
- `:q` - Not supported
- `:s/old/new/g` - Supported
- `:noh` - Clear search highlight

### Vim Mode Styling

```css
.vim-status-bar {
  height: 24px;
  padding: 4px 8px;
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: monospace;
  font-size: 12px;
}

.vim-status-bar.normal {
  background: #007acc;
}

.vim-status-bar.insert {
  background: #4ec9b0;
}

.vim-status-bar.visual {
  background: #c586c0;
}
```

## Emacs Mode

### Installation

```bash
pnpm add monaco-emacs
```

### Setup

```typescript
import { EmacsExtension } from 'monaco-emacs';

// Initialize
const emacsMode = new EmacsExtension(editor);

// Dispose when done
emacsMode.dispose();
```

### Supported Emacs Keybindings

**Movement**:
- `Ctrl+F` - Forward char
- `Ctrl+B` - Backward char
- `Ctrl+N` - Next line
- `Ctrl+P` - Previous line
- `Alt+F` - Forward word
- `Alt+B` - Backward word
- `Ctrl+A` - Beginning of line
- `Ctrl+E` - End of line

**Editing**:
- `Ctrl+D` - Delete char
- `Alt+D` - Delete word
- `Ctrl+K` - Kill line
- `Ctrl+Y` - Yank (paste)
- `Ctrl+W` - Kill region
- `Alt+W` - Copy region

**Selection**:
- `Ctrl+Space` - Set mark
- `Ctrl+X Ctrl+X` - Exchange point and mark

## Custom Keybindings

### Adding Actions

```typescript
editor.addAction({
  id: 'my-action',
  label: 'My Custom Action',
  keybindings: [
    monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyK,
  ],
  precondition: null,
  keybindingContext: null,
  contextMenuGroupId: 'navigation',
  contextMenuOrder: 1.5,
  run: (editor) => {
    console.log('Action triggered');
  }
});
```

### Chord Keybindings

```typescript
// Ctrl+K Ctrl+C style chords
editor.addAction({
  id: 'chord-action',
  label: 'Chord Action',
  keybindings: [
    monaco.KeyMod.chord(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyK,
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC
    )
  ],
  run: (editor) => { /* ... */ }
});
```

### Key Modifiers

```typescript
// Available modifiers
monaco.KeyMod.CtrlCmd  // Ctrl (Win/Linux), Cmd (Mac)
monaco.KeyMod.Shift
monaco.KeyMod.Alt
monaco.KeyMod.WinCtrl  // Ctrl on Mac, Win on Windows

// Key codes
monaco.KeyCode.KeyA    // A-Z
monaco.KeyCode.Digit0  // 0-9
monaco.KeyCode.F1      // F1-F12
monaco.KeyCode.Enter
monaco.KeyCode.Escape
monaco.KeyCode.Space
monaco.KeyCode.Tab
```

### Removing Default Keybindings

```typescript
// Remove by rebinding to null action
editor.addCommand(
  monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyK,
  () => {}, // Empty handler
  ''        // Empty context
);
```

## Context Conditions

Keybindings can be conditional:

```typescript
editor.addAction({
  id: 'conditional-action',
  label: 'Only in Python',
  keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyI],
  precondition: 'editorLangId == python',
  run: (editor) => { /* ... */ }
});
```

**Available Contexts**:
- `editorTextFocus` - Editor has focus
- `editorHasSelection` - Text is selected
- `editorReadonly` - Editor is read-only
- `editorLangId == <language>` - Specific language
- `findWidgetVisible` - Find widget open

## Toggling Keybinding Modes

```typescript
let vimMode: VimMode | null = null;
let emacsMode: EmacsExtension | null = null;

function setKeybindingMode(mode: 'default' | 'vim' | 'emacs') {
  // Cleanup existing
  vimMode?.dispose();
  emacsMode?.dispose();
  vimMode = null;
  emacsMode = null;

  // Initialize new mode
  switch (mode) {
    case 'vim':
      vimMode = initVimMode(editor, statusBar);
      break;
    case 'emacs':
      emacsMode = new EmacsExtension(editor);
      break;
    case 'default':
      // Nothing to initialize
      break;
  }
}
```
