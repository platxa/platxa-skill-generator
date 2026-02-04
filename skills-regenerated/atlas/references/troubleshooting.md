# Troubleshooting Atlas CLI

Common issues and resolutions when using the Atlas CLI on macOS.

## Permission Errors

### Error: AppleScript failed: -1743

**Cause:** macOS Automation permission not granted for your terminal.

**Fix:**
1. Open System Settings > Privacy & Security > Automation
2. Find your terminal app (Terminal, iTerm2, Warp, VS Code, etc.)
3. Enable the toggle for "ChatGPT Atlas"
4. Restart your terminal session

If the toggle does not appear, trigger it by running any Atlas AppleScript command once. macOS will show a permission dialog on the first attempt.

### Error: osascript is not available on PATH

**Cause:** Not running on macOS, or `osascript` was removed from PATH.

**Fix:** This skill requires macOS. On Linux or Windows, AppleScript is not available. Verify with:

```bash
which osascript
# Expected: /usr/bin/osascript
```

## App Detection

### Error: Could not find ChatGPT Atlas

**Cause:** The Atlas app bundle is not installed in a standard location.

**Fix:** Install ChatGPT Atlas and ensure the `.app` bundle exists at one of:
- `/Applications/ChatGPT Atlas.app`
- `~/Applications/ChatGPT Atlas.app`

If installed elsewhere, create a symlink:

```bash
ln -s "/path/to/ChatGPT Atlas.app" "/Applications/ChatGPT Atlas.app"
```

### Error: does not appear to expose window/tab scripting

**Cause:** The installed version of Atlas does not support the expected AppleScript commands.

**Fix:** Update Atlas to the latest version. Older builds may lack the Safari-style AppleScript dictionary that the CLI depends on.

## History and Bookmarks

### Empty History Results

**Causes:**
1. Atlas has not been used for browsing yet
2. The CLI is reading the wrong profile directory
3. The History file is locked by another process

**Diagnostic steps:**

```bash
# Check if History file exists and has data
ls -la ~/Library/Application\ Support/com.openai.atlas/browser-data/host/Default/History

# Check file size (should be > 0)
stat -f%z ~/Library/Application\ Support/com.openai.atlas/browser-data/host/Default/History

# Check beta installation
ls -la ~/Library/Application\ Support/com.openai.atlas.beta/browser-data/host/Default/History
```

If the beta root has a newer History file, the user is running the Atlas beta. Update the data path in `atlas_common.py` or ask the user which installation they use.

### Error: SQLite database not found

**Cause:** The profile directory or History file does not exist.

**Fix:** Launch Atlas and visit at least one page to initialize the profile data. The History database is created on first use.

### Error: Local State file not found

**Cause:** Atlas has never been launched, or the data directory was moved.

**Fix:** Launch Atlas at least once. The Local State file is created during first run at:

```
~/Library/Application Support/com.openai.atlas/browser-data/host/Local State
```

### Stale History Data

The CLI copies the History SQLite database to a temporary directory before querying. This avoids `SQLITE_BUSY` errors but means results reflect the state at copy time. If Atlas is actively being used, re-run the query for fresh data.

## Tab Operations

### Tab Index Out of Range

**Cause:** The tab was closed between listing and operating on it.

**Fix:** Re-list tabs with `tabs` to get current `window_id` and `tab_index` values, then retry the operation.

### Window Not Found

**Cause:** The window was closed after listing tabs.

**Fix:** Re-list tabs. Window IDs are assigned by macOS and change when windows are closed and reopened.
