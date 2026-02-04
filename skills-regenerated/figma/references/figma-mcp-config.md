# Figma MCP Server Configuration

Setup and configuration for the Figma MCP server across different IDE and CLI environments.

## Claude Code Configuration

Add to `.claude/settings.json` or the project's MCP configuration:

```json
{
  "mcpServers": {
    "figma": {
      "url": "https://mcp.figma.com/mcp",
      "headers": {
        "Authorization": "Bearer ${FIGMA_OAUTH_TOKEN}",
        "X-Figma-Region": "us-east-1"
      }
    }
  }
}
```

## Codex / OpenAI Configuration

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.figma]
url = "https://mcp.figma.com/mcp"
bearer_token_env_var = "FIGMA_OAUTH_TOKEN"
http_headers = { "X-Figma-Region" = "us-east-1" }
```

Enable the RMCP client at the top level of `config.toml`:

```toml
[features]
rmcp_client = true
```

## Environment Variable Setup

Set the OAuth token for the current shell:

```bash
export FIGMA_OAUTH_TOKEN="figd_your-token-here"
```

Persist across sessions by adding the export to your shell profile:

```bash
echo 'export FIGMA_OAUTH_TOKEN="figd_your-token-here"' >> ~/.bashrc
source ~/.bashrc
```

Verify the token is set before launching the IDE/CLI:

```bash
echo $FIGMA_OAUTH_TOKEN  # must print a non-empty token
```

## Server Options

| Option | Default | Description |
|--------|---------|-------------|
| `url` | `https://mcp.figma.com/mcp` | Remote MCP endpoint |
| `bearer_token_env_var` | `FIGMA_OAUTH_TOKEN` | Env var holding the OAuth token |
| `X-Figma-Region` | `us-east-1` | Figma region header (match your org's region) |
| `startup_timeout_sec` | `10` | Time to wait for server connection |
| `tool_timeout_sec` | `60` | Time to wait for individual tool responses |

## Verification Checklist

1. Confirm `FIGMA_OAUTH_TOKEN` is set: `echo $FIGMA_OAUTH_TOKEN`
2. Add the MCP config snippet to your IDE/CLI settings
3. Restart the IDE or CLI after updating config and env vars
4. Run a test call: ask the agent to list Figma tools or call `whoami`
5. Verify the response includes your Figma email and plan type

## Troubleshooting

**Token not picked up**: Export `FIGMA_OAUTH_TOKEN` in the same shell that launches the IDE. Tokens in separate terminal sessions are not inherited.

**OAuth 401 errors**: Verify the token is valid and not expired. Tokens copied from Figma should not include surrounding quotes. Regenerate the token from Figma Settings > Personal Access Tokens.

**Region mismatch**: Keep `X-Figma-Region` consistent between config and requests. Check your org's Figma admin panel for the correct region identifier.

**Connection timeout**: Increase `startup_timeout_sec` to 30 if your network is slow. The remote server at `mcp.figma.com` requires HTTPS.

**RMCP client not enabled**: For Codex/OpenAI configs using streamable HTTP, set `rmcp_client = true` (or `experimental_use_rmcp_client = true` on older builds) in the `[features]` section.
