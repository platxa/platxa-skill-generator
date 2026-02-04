# Frontend Testing Checklist

Organized by category. Use this checklist to determine which validation rules to run for a given application.

## Page Load

- [ ] Page returns HTTP 200 within timeout
- [ ] `document.title` is non-empty
- [ ] No redirect loops (final URL matches expected)
- [ ] Favicon loads without 404
- [ ] Meta viewport tag present (`<meta name="viewport" ...>`)

## Console Health

- [ ] Zero `console.error` messages during load
- [ ] Zero uncaught promise rejections
- [ ] No deprecation warnings from core frameworks
- [ ] No Content Security Policy (CSP) violations

## DOM Structure

- [ ] Primary heading (`h1`) present and visible
- [ ] Navigation element (`nav`) present
- [ ] Main content area rendered (`main` or `#app` or `#root`)
- [ ] Footer present (if expected by layout)
- [ ] No empty containers where content is expected

## Forms

- [ ] All `input` elements have associated `label` or `aria-label`
- [ ] Required fields are marked with `required` attribute or visual indicator
- [ ] Submit button is present and enabled
- [ ] Form submission changes page state (redirect, success message, or DOM update)
- [ ] Invalid input shows validation error message
- [ ] Form does not submit when required fields are empty

## Network Requests

- [ ] All XHR/Fetch requests return 2xx status
- [ ] No mixed-content warnings (HTTP resources on HTTPS page)
- [ ] API responses parse without JSON errors
- [ ] No CORS errors in the console
- [ ] Static assets (CSS, JS, images) load without 404

## Responsive Layout

- [ ] No horizontal overflow at 375px width (mobile)
- [ ] No horizontal overflow at 768px width (tablet)
- [ ] Navigation collapses or transforms on mobile breakpoints
- [ ] Text remains readable (font-size >= 14px on mobile)
- [ ] Touch targets are at least 44x44px on mobile

## Accessibility Basics

- [ ] All images have `alt` attributes
- [ ] Focus order follows visual layout (Tab key navigation)
- [ ] Interactive elements are keyboard-accessible
- [ ] Color contrast meets WCAG AA (4.5:1 for normal text)
- [ ] ARIA roles are used correctly (no `role="button"` on `div` without keyboard handler)

## Performance Indicators

- [ ] Largest Contentful Paint (LCP) < 2.5 seconds
- [ ] No render-blocking scripts in `<head>` without `defer` or `async`
- [ ] Images use modern formats (WebP/AVIF) or are reasonably compressed
- [ ] Total page weight < 3 MB for initial load

## Security Surface

- [ ] No inline `onclick` handlers with user data
- [ ] No `eval()` or `innerHTML` with untrusted input visible in source
- [ ] Cookies set with `HttpOnly` and `Secure` flags (when over HTTPS)
- [ ] No sensitive data in URL query parameters
