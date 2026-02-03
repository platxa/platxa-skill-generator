# Monaco Keybindings Reference

Guide for keybindings, Vim mode, and Emacs mode in Monaco editor.

## Default Keybindings

### Edit Operations

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Undo | Ctrl+Z | Cmd+Z |
| Redo | Ctrl+Shift+Z | Cmd+Shift+Z |
| Cut/Copy/Paste | Ctrl+X/C/V | Cmd+X/C/V |
| Delete Line | Ctrl+Shift+K | Cmd+Shift+K |
| Move Line Up/Down | Alt+Up/Down | Opt+Up/Down |
| Toggle Comment | Ctrl+/ | Cmd+/ |

### Selection

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Select All | Ctrl+A | Cmd+A |
| Select Word | Ctrl+D | Cmd+D |
| Select All Occurrences | Ctrl+Shift+L | Cmd+Shift+L |
| Add Cursor Above/Below | Ctrl+Alt+Up/Down | Cmd+Opt+Up/Down |

### Find & Navigation

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Find | Ctrl+F | Cmd+F |
| Replace | Ctrl+H | Cmd+H |
| Go to Line | Ctrl+G | Ctrl+G |
| Command Palette | F1 / Ctrl+Shift+P | F1 / Cmd+Shift+P |
| Fold/Unfold | Ctrl+Shift+[/] | Cmd+Opt+[/] |

### Code Actions

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Format Document | Alt+Shift+F | Opt+Shift+F |
| Quick Fix | Ctrl+. | Cmd+. |
| Trigger Suggest | Ctrl+Space | Ctrl+Space |

## Vim Mode

### Installation & Setup

```bash
pnpm add monaco-vim
```

```typescript
import { initVimMode } from 'monaco-vim';

const statusBar = document.getElementById('vim-status');
const vimMode = initVimMode(editor, statusBar);

// Dispose: vimMode.dispose();
```

### Supported Commands

**Normal Mode**: `h j k l w b e 0 $ ^ gg G` | `d y p c x r s` | `dd yy cc` | `iw aw i" a"`

**Insert Mode**: Enter with `i I a A o O`, exit with `Esc`

**Visual Mode**: Enter with `v V Ctrl+v`, use `d y c > < =`

**Command Mode**: `:s/old/new/g` supported, `:w :q` not supported

## Emacs Mode

### Installation & Setup

```bash
pnpm add monaco-emacs
```

```typescript
import { EmacsExtension } from 'monaco-emacs';
const emacsMode = new EmacsExtension(editor);
// Dispose: emacsMode.dispose();
```

### Key Bindings

| Movement | Editing |
|----------|---------|
| `Ctrl+F/B` - Forward/Back char | `Ctrl+D` - Delete char |
| `Ctrl+N/P` - Next/Prev line | `Ctrl+K` - Kill line |
| `Alt+F/B` - Forward/Back word | `Ctrl+Y` - Yank |
| `Ctrl+A/E` - Begin/End line | `Ctrl+W` - Kill region |

## Custom Keybindings

### Adding Actions

```typescript
editor.addAction({
  id: 'my-action',
  label: 'My Custom Action',
  keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyK],
  run: (editor) => { console.log('Triggered'); }
});
```

### Chord Keybindings

```typescript
// Ctrl+K Ctrl+C style
keybindings: [
  monaco.KeyMod.chord(
    monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyK,
    monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC
  )
]
```

### Key Modifiers

```typescript
monaco.KeyMod.CtrlCmd  // Ctrl (Win/Linux), Cmd (Mac)
monaco.KeyMod.Shift
monaco.KeyMod.Alt
monaco.KeyCode.KeyA    // A-Z
monaco.KeyCode.F1      // F1-F12
```

## Context Conditions

```typescript
editor.addAction({
  id: 'python-only',
  keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyI],
  precondition: 'editorLangId == python',
  run: (editor) => { /* ... */ }
});
```

**Contexts**: `editorTextFocus`, `editorHasSelection`, `editorReadonly`, `editorLangId == <lang>`
