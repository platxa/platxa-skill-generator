# Wrangler CLI Reference

Command reference for `npx wrangler` used during Cloudflare deployment workflows.

## Authentication

```bash
npx wrangler login              # OAuth via browser
npx wrangler whoami             # Show logged-in account and user
npx wrangler logout             # Clear stored credentials
```

Set `CLOUDFLARE_API_TOKEN` env var for non-interactive auth (CI/CD or headless).

## Worker Deployment

```bash
npx wrangler deploy                       # Deploy Worker to production
npx wrangler deploy --env staging         # Deploy to named environment
npx wrangler deploy --minify              # Minify before deploying
npx wrangler deploy --dry-run             # Validate without deploying
npx wrangler deploy --keep-vars           # Preserve existing env vars
npx wrangler rollback                     # Roll back to previous version
npx wrangler versions list                # List recent deployments
```

## Pages Deployment

```bash
npx wrangler pages project create <name> --production-branch main
npx wrangler pages deploy ./dist                          # Upload build output
npx wrangler pages deploy ./dist --project-name my-site   # Specify project
npx wrangler pages deploy ./dist --branch feature-x       # Preview branch deploy
npx wrangler pages project list                           # List all Pages projects
npx wrangler pages deployment list --project-name my-site # List deployments
```

## Local Development

```bash
npx wrangler dev                          # Start local dev server (port 8787)
npx wrangler dev --port 3000              # Custom port
npx wrangler dev --remote                 # Dev against remote resources
npx wrangler pages dev ./dist             # Pages local dev
npx wrangler pages dev ./dist --port 3000 # Pages on custom port
```

## D1 Database

```bash
npx wrangler d1 create <name>                                 # Create database
npx wrangler d1 list                                          # List all databases
npx wrangler d1 execute <name> --command "SQL statement"       # Run SQL
npx wrangler d1 execute <name> --file schema.sql               # Run SQL file
npx wrangler d1 execute <name> --command "SQL" --remote        # Run against remote
npx wrangler d1 export <name> --output backup.sql              # Export data
npx wrangler d1 time-travel restore <name> --timestamp <ts>    # Point-in-time restore
```

## KV Store

```bash
npx wrangler kv namespace create <BINDING>          # Create namespace
npx wrangler kv namespace list                      # List all namespaces
npx wrangler kv key put --binding <BINDING> <key> <value>  # Write key
npx wrangler kv key get --binding <BINDING> <key>          # Read key
npx wrangler kv key list --binding <BINDING>               # List keys
npx wrangler kv bulk put --binding <BINDING> data.json     # Bulk write
```

## R2 Object Storage

```bash
npx wrangler r2 bucket create <name>        # Create bucket
npx wrangler r2 bucket list                 # List buckets
npx wrangler r2 object put <bucket>/<key> --file ./data.bin  # Upload object
npx wrangler r2 object get <bucket>/<key>                    # Download object
npx wrangler r2 object list <bucket>                         # List objects
```

## Secrets Management

```bash
npx wrangler secret put <NAME>              # Set secret (prompts for value)
npx wrangler secret list                    # List secret names
npx wrangler secret delete <NAME>           # Remove secret
npx wrangler secret bulk .env               # Bulk import from file
```

## Tail and Logs

```bash
npx wrangler tail                           # Stream live logs from Worker
npx wrangler tail --format json             # JSON log output
npx wrangler tail --status error            # Filter to errors only
npx wrangler tail --ip self                 # Filter to your requests
```

## Project Scaffolding

```bash
npm create cloudflare@latest                # Interactive project creator (C3)
npm create cloudflare@latest my-app -- --type worker     # Worker template
npm create cloudflare@latest my-app -- --type pages      # Pages template
npm create cloudflare@latest my-app -- --framework astro # Framework starter
```

## Useful Flags

| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON output |
| `--env <name>` | Target a named environment |
| `--config <path>` | Use alternate config file |
| `--compatibility-date <date>` | Override compatibility date |
