# Playwright CLI Command Reference

Complete command listing for `playwright-cli` invoked via the wrapper script.

Set the wrapper path once per session:

```bash
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PWCLI="$SKILL_DIR/../scripts/playwright_cli.sh"
```

## Page Lifecycle

```bash
"$PWCLI" open <url>                  # navigate to URL
"$PWCLI" open <url> --headed         # visible browser window
"$PWCLI" close                       # close current page
"$PWCLI" go-back                     # browser back button
"$PWCLI" go-forward                  # browser forward button
"$PWCLI" reload                      # refresh page
```

## Snapshot and Element Refs

```bash
"$PWCLI" snapshot                    # accessibility tree with refs (e1, e2, ...)
```

Refs are stable within a single snapshot. Re-snapshot after navigation, modal changes, or `ElementNotFound` errors.

## Click and Input

```bash
"$PWCLI" click <ref>                 # left-click element
"$PWCLI" dblclick <ref>              # double-click element
"$PWCLI" hover <ref>                 # hover over element
"$PWCLI" fill <ref> "<value>"        # set input value (clears first)
"$PWCLI" type "<text>"               # type into focused element
"$PWCLI" press <key>                 # press key: Enter, Tab, ArrowDown, Escape
"$PWCLI" select <ref> "<value>"      # select dropdown option by value
"$PWCLI" check <ref>                 # check a checkbox
"$PWCLI" uncheck <ref>               # uncheck a checkbox
"$PWCLI" upload <filepath>           # upload file via file chooser
"$PWCLI" drag <startRef> <endRef>    # drag from one element to another
```

## Keyboard

```bash
"$PWCLI" press Enter
"$PWCLI" press ArrowDown
"$PWCLI" press Escape
"$PWCLI" keydown Shift
"$PWCLI" keyup Shift
```

## Mouse (low-level)

```bash
"$PWCLI" mousemove <x> <y>          # move mouse to coordinates
"$PWCLI" mousedown                   # press left button
"$PWCLI" mousedown right             # press right button
"$PWCLI" mouseup                     # release left button
"$PWCLI" mouseup right               # release right button
"$PWCLI" mousewheel <deltaX> <deltaY>  # scroll
```

## Artifacts

```bash
"$PWCLI" screenshot                  # viewport screenshot (PNG)
"$PWCLI" screenshot <ref>            # element-specific screenshot
"$PWCLI" pdf                         # save page as PDF
```

## JavaScript Evaluation

```bash
"$PWCLI" eval "<expression>"         # evaluate JS in page context
"$PWCLI" eval "<function>" <ref>     # evaluate with element argument
"$PWCLI" run-code "<playwright-code>"  # run arbitrary Playwright API code
```

Examples:

```bash
"$PWCLI" eval "document.title"
"$PWCLI" eval "el => el.textContent" e5
"$PWCLI" eval "window.location.href"
```

## Tabs

```bash
"$PWCLI" tab-list                    # list all open tabs
"$PWCLI" tab-new                     # open blank tab
"$PWCLI" tab-new <url>               # open tab with URL
"$PWCLI" tab-select <index>          # switch to tab by index (0-based)
"$PWCLI" tab-close                   # close current tab
"$PWCLI" tab-close <index>           # close tab by index
```

## DevTools

```bash
"$PWCLI" console                     # all console messages
"$PWCLI" console warning             # warnings and errors only
"$PWCLI" console error               # errors only
"$PWCLI" network                     # list network requests
```

## Tracing

```bash
"$PWCLI" tracing-start               # begin recording trace
"$PWCLI" tracing-stop                # stop and save trace.zip
```

View traces at `trace.playwright.dev` for timeline, network, and DOM snapshots.

## Dialogs

```bash
"$PWCLI" dialog-accept               # accept alert/confirm
"$PWCLI" dialog-accept "<text>"      # accept prompt with input
"$PWCLI" dialog-dismiss              # dismiss dialog
```

## Window

```bash
"$PWCLI" resize <width> <height>     # resize browser window (e.g., 1920 1080)
```

## Sessions

Isolate browser contexts with named sessions:

```bash
"$PWCLI" --session <name> <command>  # run command in named session
```

Or set an environment variable:

```bash
export PLAYWRIGHT_CLI_SESSION=myapp
"$PWCLI" open https://myapp.example.com
```

Sessions maintain separate cookies, localStorage, and browsing history.

## Configuration

Place `playwright-cli.json` in the working directory:

```json
{
  "browser": {
    "launchOptions": {
      "headless": false,
      "args": ["--disable-gpu"]
    },
    "contextOptions": {
      "viewport": { "width": 1280, "height": 720 },
      "locale": "en-US"
    }
  }
}
```

Override with `--config /path/to/config.json`.
