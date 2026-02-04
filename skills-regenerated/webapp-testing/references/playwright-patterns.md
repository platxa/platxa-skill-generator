# Playwright Patterns for Web Application Testing

Selector strategies, wait conditions, and common validation recipes using the `playwright` Python sync API.

## Selector Strategy Priority

Use selectors in this order of reliability:

1. **ARIA role + name**: `page.get_by_role("button", name="Submit")` -- most resilient to markup changes
2. **Test ID**: `page.get_by_test_id("login-form")` -- requires `data-testid` attributes
3. **Text content**: `page.get_by_text("Welcome back")` -- good for headings and labels
4. **CSS selector**: `page.locator("nav > ul > li.active")` -- flexible but brittle to DOM restructuring
5. **XPath**: `page.locator("xpath=//div[@class='card']")` -- last resort

## Wait Conditions

```python
# Wait for network activity to settle (SPAs, lazy loading)
page.wait_for_load_state("networkidle")

# Wait for a specific element to appear
page.locator("#dashboard").wait_for(state="visible", timeout=10000)

# Wait for a specific element to disappear (loading spinner)
page.locator(".spinner").wait_for(state="hidden", timeout=15000)

# Wait for a URL pattern after navigation
page.wait_for_url("**/dashboard**", timeout=10000)

# Wait for a network response
with page.expect_response("**/api/users") as resp_info:
    page.click("button#load-users")
response = resp_info.value
assert response.status == 200
```

## Console Capture Pattern

```python
console_messages = {"error": [], "warning": [], "info": []}

def on_console(msg):
    level = msg.type
    if level in console_messages:
        console_messages[level].append(msg.text)

page.on("console", on_console)
page.goto(url)
page.wait_for_load_state("networkidle")

# Check results
assert len(console_messages["error"]) == 0, (
    f"Console errors: {console_messages['error']}"
)
```

## Network Request Auditing

```python
failed_requests = []

def on_response(response):
    if response.status >= 400:
        failed_requests.append({
            "url": response.url,
            "status": response.status,
            "method": response.request.method,
        })

page.on("response", on_response)
page.goto(url, wait_until="networkidle")

for req in failed_requests:
    print(f"  {req['method']} {req['url']} -> {req['status']}")
assert len(failed_requests) == 0, f"{len(failed_requests)} failed request(s)"
```

## Viewport Resize and Overflow Detection

```python
BREAKPOINTS = [
    (375, 812, "mobile"),
    (768, 1024, "tablet"),
    (1280, 720, "laptop"),
    (1920, 1080, "desktop"),
]

for width, height, label in BREAKPOINTS:
    page.set_viewport_size({"width": width, "height": height})
    page.wait_for_timeout(300)
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    if scroll_width > width:
        print(f"FAIL: {label} overflow ({scroll_width}px > {width}px)")
    page.screenshot(path=f"/tmp/responsive-{label}.png")
```

## Form Interaction Recipes

```python
# Text input
page.fill("#email", "test@example.com")

# Password field
page.fill("input[type='password']", "SecureP@ss42")

# Select dropdown (by visible text)
page.select_option("#country", label="United States")

# Checkbox
page.check("#agree-terms")

# Radio button
page.click("input[name='plan'][value='pro']")

# File upload
page.set_input_files("#avatar", "/tmp/test-image.png")

# Submit and verify redirect
page.click("button[type='submit']")
page.wait_for_url("**/success**", timeout=10000)
```

## Screenshot as Evidence

```python
import os

output_dir = "/tmp/webapp-test"
os.makedirs(output_dir, exist_ok=True)

# Full-page screenshot
page.screenshot(path=f"{output_dir}/full-page.png", full_page=True)

# Element screenshot
page.locator("#error-banner").screenshot(path=f"{output_dir}/error-banner.png")

# Clip a region
page.screenshot(path=f"{output_dir}/header.png", clip={"x": 0, "y": 0, "width": 1920, "height": 80})
```

## Handling Authentication

```python
# Login once, save storage state
context = browser.new_context()
page = context.new_page()
page.goto("http://localhost:5173/login")
page.fill("#email", "admin@test.io")
page.fill("#password", "password123")
page.click("button[type='submit']")
page.wait_for_url("**/dashboard**")
context.storage_state(path="/tmp/auth-state.json")
context.close()

# Reuse in subsequent checks
authed_context = browser.new_context(storage_state="/tmp/auth-state.json")
authed_page = authed_context.new_page()
authed_page.goto("http://localhost:5173/settings")  # already logged in
```
