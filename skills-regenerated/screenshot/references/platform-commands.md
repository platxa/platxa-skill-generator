# Platform-Specific Screenshot Commands

Native OS commands for screenshot capture when the Python helper is unavailable.

## macOS (`screencapture`)

Built-in on all macOS versions. Requires Screen Recording permission for window-level captures.

```bash
# Full screen to file (silent, no shutter sound)
screencapture -x output/screen.png

# Pixel region
screencapture -x -R100,200,800,600 output/region.png

# Specific window by CGWindowID
screencapture -x -l12345 output/window.png

# Interactive selection (crosshair cursor)
screencapture -x -i output/selection.png

# Specific display (1-indexed)
screencapture -x -D2 output/display2.png

# JPEG format at 80% quality
screencapture -x -tjpg output/screen.jpg
```

**Default screenshot location** is read from:

```bash
defaults read com.apple.screencapture location
```

Falls back to `~/Desktop` if unset.

**Permission check** uses the bundled Swift helper `macos_permissions.swift`, which queries the Screen Recording entitlement via `CGPreflightScreenCaptureAccess()` and optionally requests it with `CGRequestScreenCaptureAccess()`.

## Linux

Three tools supported in priority order. The Python helper auto-selects the first available.

### scrot (recommended)

```bash
# Install
sudo apt install scrot          # Debian/Ubuntu
sudo dnf install scrot          # Fedora
sudo pacman -S scrot            # Arch

# Full screen
scrot output/screen.png

# Active/focused window
scrot -u output/window.png

# Pixel region (x,y,w,h)
scrot -a 100,200,800,600 output/region.png

# Delay 3 seconds before capture
scrot -d 3 output/delayed.png
```

### gnome-screenshot

```bash
# Install (GNOME-based desktops)
sudo apt install gnome-screenshot

# Full screen
gnome-screenshot -f output/screen.png

# Active window
gnome-screenshot -w -f output/window.png

# With 3-second delay
gnome-screenshot -d 3 -f output/delayed.png
```

Does not support pixel-region capture natively.

### ImageMagick import

```bash
# Install
sudo apt install imagemagick

# Full screen (root window)
import -window root output/screen.png

# Specific window by X11 ID
import -window 0x12345 output/window.png

# Crop region from root (WxH+X+Y)
import -window root -crop 800x600+100+200 output/region.png
```

**Active window via xdotool:**

```bash
sudo apt install xdotool
import -window "$(xdotool getactivewindow)" output/active.png
```

### Tool availability check

```bash
command -v scrot && echo "scrot available"
command -v gnome-screenshot && echo "gnome-screenshot available"
command -v import && echo "ImageMagick available"
```

## Windows (PowerShell)

Uses .NET `System.Drawing` and `System.Windows.Forms` assemblies. No additional installation needed on Windows 10+.

```powershell
# Full screen
powershell -ExecutionPolicy Bypass -File take_screenshot.ps1

# To temp directory
powershell -ExecutionPolicy Bypass -File take_screenshot.ps1 -Mode temp

# Explicit path
powershell -ExecutionPolicy Bypass -File take_screenshot.ps1 -Path "C:\Temp\screen.png"

# Pixel region
powershell -ExecutionPolicy Bypass -File take_screenshot.ps1 -Region 100,200,800,600

# Active window (user must focus it first)
powershell -ExecutionPolicy Bypass -File take_screenshot.ps1 -ActiveWindow

# Specific window handle (HWND)
powershell -ExecutionPolicy Bypass -File take_screenshot.ps1 -WindowHandle 123456
```

## Image Format Notes

| Format | Flag | Use Case |
|--------|------|----------|
| PNG | `--format png` (default) | Lossless, best for UI screenshots |
| JPEG | `--format jpg` | Smaller files, acceptable for photos |
| TIFF | `--format tiff` | macOS only, high fidelity |

The Python helper defaults to PNG. Pass `--format jpg` for smaller file sizes when pixel accuracy is not critical.
