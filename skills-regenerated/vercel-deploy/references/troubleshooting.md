# Vercel Deploy Troubleshooting

Common deployment failures and resolution steps for the claimable-preview deploy flow.

## Network and Sandbox Errors

### Sandbox Blocks Outbound Requests

**Symptom**: `curl` fails with connection refused, timeout, or DNS resolution error.

**Cause**: The execution environment's sandbox prevents outbound HTTPS to `codex-deploy-skills.vercel.sh`.

**Fix**: Rerun with escalated permissions:
```
sandbox_permissions=require_escalated
```

### curl: Connection Timed Out

**Symptom**: Deploy hangs for 30-60 seconds then fails.

**Cause**: Firewall or proxy blocking port 443.

**Fix**:
1. Verify connectivity: `curl -I https://codex-deploy-skills.vercel.sh`
2. Check proxy settings: `echo $HTTP_PROXY $HTTPS_PROXY`
3. If behind a corporate proxy, set `HTTPS_PROXY` before running deploy

## Packaging Errors

### Tarball Too Large

**Symptom**: Upload fails or times out.

**Cause**: Project directory contains large binaries, media files, or untracked build artifacts.

**Fix**:
1. Check tarball size: `du -h /tmp/*/project.tgz`
2. Add large files to `.gitignore` (the script excludes `node_modules` and `.git` but not other large directories)
3. Pre-build and deploy only the output directory

### Permission Denied During Packaging

**Symptom**: `tar: Cannot open: Permission denied`

**Cause**: Files or directories lack read permissions.

**Fix**:
```bash
chmod -R u+r /path/to/project
```

## Framework Detection Issues

### Wrong Framework Detected

**Symptom**: Build fails because Vercel applies wrong build settings.

**Cause**: Multiple framework dependencies in `package.json`. The script checks frameworks in priority order -- the first match wins.

**Fix**:
1. Check which framework the script detects:
   ```bash
   bash -x scripts/deploy.sh . 2>&1 | grep "Detected framework"
   ```
2. If incorrect, create a `vercel.json` with explicit settings:
   ```json
   { "framework": "vite", "buildCommand": "npm run build", "outputDirectory": "dist" }
   ```

### No Framework Detected (null)

**Symptom**: Vercel treats the project as static files, no build step runs.

**Cause**: `package.json` missing or no recognized framework dependency.

**Fix**:
- For projects that need a build step, ensure the correct framework is in `dependencies` or `devDependencies`
- For static sites, `null` framework is correct -- Vercel serves files directly

## Build Failures on Vercel

### Build Command Failed

**Symptom**: Deployment succeeds (tarball uploaded) but the preview URL shows an error page.

**Cause**: The build step runs on Vercel's infrastructure after upload. If `npm run build` fails, the deployment fails.

**Fix**:
1. Run the build locally first to catch errors:
   ```bash
   npm install && npm run build
   ```
2. Check for environment variables required at build time that are not set in Vercel
3. Verify Node.js version compatibility (Vercel defaults to Node.js 20.x)

### Missing Dependencies

**Symptom**: `MODULE_NOT_FOUND` errors during build.

**Cause**: Dependencies listed in `devDependencies` that are needed at build time, or missing peer dependencies.

**Fix**:
- Move build-time dependencies from `devDependencies` to `dependencies`
- Or set `NPM_FLAGS=--include=dev` in Vercel environment variables

## Response Parsing Errors

### Empty Preview URL

**Symptom**: Script reports `Error: Could not extract preview URL from response`

**Cause**: The deployment endpoint returned an unexpected response format.

**Fix**:
1. Check the raw response by running deploy with `set -x`:
   ```bash
   bash -x scripts/deploy.sh .
   ```
2. Look for rate limiting (HTTP 429) or server errors (HTTP 5xx)
3. Retry after a brief wait

### Error Field in Response

**Symptom**: Script exits with an error message from the server.

**Cause**: The deployment endpoint rejected the request.

**Common error messages**:
| Message | Cause | Fix |
|---------|-------|-----|
| `file too large` | Tarball exceeds size limit | Reduce project size, exclude large assets |
| `invalid framework` | Unrecognized framework value | Use a supported framework or set to `null` |
| `rate limited` | Too many deployments | Wait 60 seconds and retry |

## Static HTML Issues

### Page Serves 404 at Root

**Symptom**: Visiting the preview URL returns 404.

**Cause**: No `index.html` at the root of the deployed files.

**Fix**: The deploy script auto-renames single HTML files to `index.html`. If you have multiple HTML files, ensure one is named `index.html` before deploying.

### Assets Not Loading (Relative Paths)

**Symptom**: CSS/JS/images return 404 on the preview URL.

**Cause**: Asset paths use relative references that break under the Vercel URL structure.

**Fix**: Use root-relative paths (`/style.css`) instead of relative paths (`style.css` or `./style.css`).
