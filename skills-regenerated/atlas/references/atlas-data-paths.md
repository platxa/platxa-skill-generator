# Atlas Data Paths (macOS)

Atlas stores Chromium-style profile data under the application support directory.

## Directory Layout

```
~/Library/Application Support/com.openai.atlas/
  browser-data/
    host/
      Local State          (JSON — profile metadata, last_used profile)
      Default/             (default profile directory)
        History            (SQLite — urls table, visits table)
        Bookmarks          (JSON — Chromium bookmark format)
      Profile 1/           (additional profiles, if any)
        History
        Bookmarks
```

## Local State

Path: `~/Library/Application Support/com.openai.atlas/browser-data/host/Local State`

JSON file containing profile configuration. Key fields:

```json
{
  "profile": {
    "last_used": "Default",
    "profiles_order": ["Default"]
  }
}
```

The `profile.last_used` value determines which profile directory is active. If missing or invalid, the CLI falls back to `Default`.

## History Database

Path: `<profile>/History`

SQLite database with Chrome schema. Primary table:

```sql
CREATE TABLE urls (
  id INTEGER PRIMARY KEY,
  url TEXT NOT NULL,
  title TEXT,
  visit_count INTEGER DEFAULT 0,
  typed_count INTEGER DEFAULT 0,
  last_visit_time INTEGER NOT NULL,
  hidden INTEGER DEFAULT 0
);
```

The `last_visit_time` column stores Chrome timestamps: microseconds since 1601-01-01 00:00:00 UTC. Conversion to Unix epoch:

```
unix_seconds = chrome_microseconds / 1_000_000 - 11_644_473_600
```

The CLI copies the History file to a temp directory before querying to avoid `SQLITE_BUSY` errors caused by the running Atlas process holding a write lock.

## Bookmarks File

Path: `<profile>/Bookmarks`

JSON file using Chromium's bookmark format:

```json
{
  "roots": {
    "bookmark_bar": { "children": [...], "name": "Bookmarks Bar", "type": "folder" },
    "other": { "children": [...], "name": "Other Bookmarks", "type": "folder" },
    "synced": { "children": [...], "name": "Synced Bookmarks", "type": "folder" }
  }
}
```

Each bookmark node has:
- `type`: `"url"` or `"folder"`
- `name`: display name
- `url`: target URL (only for `type: "url"`)
- `date_added`: Chrome timestamp (microseconds since 1601-01-01)
- `children`: nested nodes (only for `type: "folder"`)

## Beta Data Root

If the user runs the Atlas beta, data is stored under a separate bundle ID:

```
~/Library/Application Support/com.openai.atlas.beta/browser-data/host/
```

Same directory structure as the stable release. When history appears stale or empty, check both roots and use the one with the most recent `History` file modification time.

## AppleScript Dictionary

Atlas exposes a Safari-style AppleScript dictionary:

| Command | Scope | Description |
|---------|-------|-------------|
| `every window` | application | List all open windows |
| `id of w` | window | Unique window identifier |
| `every tab of w` | window | List tabs in a window |
| `active tab index of w` | window | 1-based index of the focused tab |
| `title of t` | tab | Page title |
| `URL of t` | tab | Current URL |
| `make new tab with properties {URL:"..."}` | window | Open new tab |
| `close tab <n>` | window | Close tab at index |
| `reload tab <n>` | window | Reload tab at index |
| `set active tab index of w to <n>` | window | Focus a tab |

All AppleScript commands are wrapped in `tell application "ChatGPT Atlas" ... end tell` blocks. The CLI detects the app name and verifies tab scripting support via a probe query (`get count of windows`).
