# Netlify CLI Commands Reference

Quick reference for `npx netlify` commands used during deployment workflows.

## Authentication

```bash
npx netlify login          # OAuth via browser
npx netlify status         # Show logged-in user and linked site
npx netlify logout         # Clear stored credentials
```

Set `NETLIFY_AUTH_TOKEN` env var for non-interactive auth (CI/CD or headless environments).

## Site Management

```bash
npx netlify link                              # Interactive site picker
npx netlify link --git-remote-url <url>       # Link by Git remote
npx netlify init                              # Create new site + link
npx netlify unlink                            # Disconnect local project
npx netlify open                              # Open dashboard in browser
npx netlify open:site                         # Open production URL
```

## Deployment

```bash
npx netlify deploy                            # Preview/draft deploy
npx netlify deploy --prod                     # Production deploy
npx netlify deploy --dir=dist                 # Override publish directory
npx netlify deploy --message="v1.0.0"         # Attach deploy note
npx netlify deploy --prod --dir=build --message="hotfix"
```

## Environment Variables

```bash
npx netlify env:list                          # Show all env vars
npx netlify env:set KEY value                 # Set variable
npx netlify env:get KEY                       # Read variable
npx netlify env:import .env                   # Bulk import from file
```

## Build and Dev

```bash
npx netlify build                             # Run build locally
npx netlify build --dry                       # Show build settings without running
npx netlify dev                               # Local dev server with Netlify features
npx netlify dev --port 8888                   # Dev server on custom port
```

## Serverless Functions

```bash
npx netlify functions:list                    # List deployed functions
npx netlify functions:invoke <name>           # Invoke function locally
npx netlify functions:create <name>           # Scaffold new function
npx netlify logs                              # Stream function logs
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Authentication failure |
| 3 | Site not found |
| 4 | Build failed |

## Useful Flags

| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON output |
| `--silent` | Suppress all output |
| `--debug` | Verbose debug logging |
| `--force` | Skip confirmation prompts |
