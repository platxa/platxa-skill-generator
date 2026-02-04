# Playwright Test Patterns

Usage patterns for the `web_game_playwright_client.js` test script.

## Script Invocation

```bash
node "$WEB_GAME_CLIENT" \
  --url <http-url>           \   # required: game URL
  --actions-file <path.json> \   # action burst file (mutually exclusive with --actions-json, --click)
  --actions-json '<json>'    \   # inline action JSON
  --click <x>,<y>            \   # single click at canvas coordinates
  --click-selector <css>     \   # click a DOM element before running actions (e.g., "#start-btn")
  --iterations <n>           \   # number of burst repetitions (default: 3)
  --pause-ms <ms>            \   # pause between iterations (default: 250)
  --headless <true|false>    \   # headless mode (default: true)
  --screenshot-dir <path>        # output directory (default: output/web-game)
```

At least one action source is required: `--actions-file`, `--actions-json`, or `--click`.

## Action Payload Format

Actions are a list of steps. Each step specifies buttons to hold, how many frames to advance, and optional mouse coordinates:

```json
{
  "steps": [
    { "buttons": ["left"], "frames": 6 },
    { "buttons": [], "frames": 4 },
    { "buttons": ["space"], "frames": 3 },
    { "buttons": ["left_mouse_button"], "frames": 2, "mouse_x": 120, "mouse_y": 80 }
  ]
}
```

### Button Names

| Button | Playwright Key |
|--------|---------------|
| `up` | ArrowUp |
| `down` | ArrowDown |
| `left` | ArrowLeft |
| `right` | ArrowRight |
| `enter` | Enter |
| `space` | Space |
| `a` | KeyA |
| `b` | KeyB |
| `left_mouse_button` | Mouse left click |
| `right_mouse_button` | Mouse right click |

Mouse coordinates (`mouse_x`, `mouse_y`) are relative to the canvas bounding box. If omitted, the click targets the canvas center.

## Virtual Time Shim

The script injects a virtual-time shim via `page.addInitScript` that intercepts:

- `window.setTimeout` -- wraps callback with pending-task tracking
- `window.setInterval` -- wraps callback with pending-task tracking
- `window.requestAnimationFrame` -- wraps callback with pending-task tracking
- `window.advanceTime(ms)` -- resolves after `ms` milliseconds of `requestAnimationFrame` steps

This lets the test script control time precisely. Each action step calls `window.advanceTime(1000/60)` per frame, advancing exactly one frame at 60 FPS.

## Output Artifacts

After each iteration, the script writes:

| File | Content |
|------|---------|
| `shot-{i}.png` | Canvas screenshot (tries toDataURL, element screenshot, then viewport clip) |
| `state-{i}.json` | Output of `window.render_game_to_text()` if the function exists |
| `errors-{i}.json` | Console errors (deduplicated). If any errors exist, the script halts |

## Canvas Capture Strategy

The script uses three fallback methods for capturing the canvas:

1. `canvas.toDataURL("image/png")` -- extracts raw pixel data as base64. Fastest but fails if canvas is cross-origin tainted or transparent.
2. `canvas.screenshot()` -- Playwright element screenshot. Works when toDataURL fails but may miss offscreen content.
3. `page.screenshot({ clip: bbox })` -- viewport clip at the canvas bounding box. Last resort; captures CSS backgrounds too.

If the canvas is fully transparent (all alpha=0), the script falls back to method 2 or 3 automatically.

## Debugging Tips

- Use `--headless false` to visually watch the test run in a real browser window
- Use `--pause-ms 1000` to slow down iterations for observation
- Use `--iterations 1` with specific `--actions-json` to isolate a single interaction
- Check `errors-{i}.json` for JavaScript exceptions; the script captures both `console.error` and `pageerror` events
- The script launches Chromium with `--use-gl=angle --use-angle=swiftshader` for consistent WebGL rendering in headless mode
