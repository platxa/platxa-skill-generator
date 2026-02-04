# Playwright CLI Workflow Patterns

Step-by-step recipes for common browser automation scenarios.

Assume `PWCLI` is set to the wrapper script path and `pwcli` is an alias for `"$PWCLI"`.

## Standard Interaction Loop

Every workflow follows this pattern:

```bash
pwcli open <url>
pwcli snapshot          # always snapshot first
pwcli <action> <ref>    # use refs from snapshot
pwcli snapshot          # refresh refs after DOM changes
```

## Form Submission

```bash
pwcli open https://app.example.com/register --headed
pwcli snapshot
pwcli fill e1 "Jane Doe"
pwcli fill e2 "jane@company.io"
pwcli fill e3 "SecureP@ss99"
pwcli select e4 "enterprise"      # plan dropdown
pwcli check e5                    # accept terms checkbox
pwcli click e6                    # submit button
pwcli snapshot                    # verify success state
pwcli screenshot                  # capture confirmation
```

## Data Extraction

### Extract page title and metadata

```bash
pwcli open https://example.com
pwcli eval "document.title"
pwcli eval "document.querySelector('meta[name=description]')?.content"
```

### Extract table data as JSON

```bash
pwcli open https://example.com/pricing
pwcli snapshot
pwcli eval "JSON.stringify([...document.querySelectorAll('table tbody tr')].map(row => ({name: row.cells[0]?.textContent?.trim(), price: row.cells[1]?.textContent?.trim()})))"
```

### Extract all links from a page

```bash
pwcli eval "JSON.stringify([...document.querySelectorAll('a[href]')].map(a => ({text: a.textContent.trim(), href: a.href})))"
```

## Authentication Flow

```bash
pwcli open https://app.example.com/login
pwcli snapshot
pwcli fill e1 "admin@company.io"
pwcli fill e2 "AdminPass!2024"
pwcli click e3                    # login button
pwcli snapshot                    # should show dashboard
pwcli eval "document.cookie"      # verify session cookie set
```

## Multi-Step Navigation

```bash
pwcli open https://shop.example.com
pwcli snapshot
pwcli click e12                   # navigate to category
pwcli snapshot                    # new page, new refs
pwcli click e5                    # select product
pwcli snapshot
pwcli click e8                    # add to cart
pwcli snapshot
pwcli screenshot                  # verify cart state
```

## Debugging with Console and Network

### Check for JavaScript errors

```bash
pwcli open https://staging.example.com --headed
pwcli snapshot
pwcli click e15                   # trigger problematic action
pwcli console error               # show JS errors
```

### Inspect network failures

```bash
pwcli open https://api-frontend.example.com
pwcli snapshot
pwcli click e4                    # trigger API call
pwcli network                     # inspect request/response status codes
```

### Full trace capture

```bash
pwcli open https://buggy-app.example.com --headed
pwcli tracing-start
pwcli snapshot
pwcli click e3
pwcli fill e7 "test input"
pwcli click e9
pwcli console warning             # capture warnings during flow
pwcli tracing-stop                # saves trace.zip
```

Upload `trace.zip` to `trace.playwright.dev` for visual timeline analysis including DOM snapshots, network waterfall, and console logs.

## Multi-Tab Workflows

### Compare two pages side-by-side

```bash
pwcli open https://v1.example.com
pwcli snapshot
pwcli eval "document.title"       # capture v1 title
pwcli tab-new https://v2.example.com
pwcli snapshot
pwcli eval "document.title"       # capture v2 title
pwcli tab-select 0                # back to v1
pwcli snapshot                    # re-snapshot after tab switch
```

### Copy data between tabs

```bash
pwcli open https://source.example.com
pwcli snapshot
pwcli eval "document.querySelector('#data-field').textContent"
# store the result, then:
pwcli tab-new https://dest.example.com/form
pwcli snapshot
pwcli fill e1 "<extracted-value>"
pwcli click e2
```

## Session Isolation

Run parallel workflows without cookie or state interference:

```bash
pwcli --session user1 open https://app.example.com/login
pwcli --session user1 snapshot
pwcli --session user1 fill e1 "user1@test.io"

pwcli --session user2 open https://app.example.com/login
pwcli --session user2 snapshot
pwcli --session user2 fill e1 "user2@test.io"
```

## Responsive Testing

```bash
pwcli open https://example.com --headed
pwcli resize 375 812             # iPhone 12 viewport
pwcli snapshot
pwcli screenshot                 # mobile view
pwcli resize 1920 1080           # desktop viewport
pwcli snapshot
pwcli screenshot                 # desktop view
```

## Dialog Handling

```bash
pwcli open https://app.example.com
pwcli snapshot
pwcli click e5                   # triggers confirm dialog
pwcli dialog-accept              # accept the dialog
pwcli snapshot                   # continue after dialog
```

For prompt dialogs with text input:

```bash
pwcli click e8                   # triggers prompt dialog
pwcli dialog-accept "my input"   # accept with value
```

## Troubleshooting Checklist

| Symptom | Fix |
|---------|-----|
| `ElementNotFound` error | Run `pwcli snapshot` and use fresh refs |
| Page looks wrong in headless | Add `--headed` and `pwcli resize 1280 720` |
| Cookies lost between commands | Use `--session <name>` for persistent context |
| `npx` command not found | Install Node.js >= 18 with npm |
| Trace file not generated | Ensure `tracing-start` was called before `tracing-stop` |
| Slow first command | npx downloads `@playwright/mcp` on first run; subsequent calls are cached |
