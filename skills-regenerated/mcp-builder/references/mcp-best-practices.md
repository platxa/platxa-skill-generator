# MCP Server Best Practices

## Server Naming

- **Python**: `{service}_mcp` -- `slack_mcp`, `github_mcp`, `jira_mcp`
- **TypeScript**: `{service}-mcp-server` -- `slack-mcp-server`, `github-mcp-server`
- Names must be general, descriptive of the service, and without version numbers

## Tool Naming

- snake_case with service prefix: `slack_send_message`, `github_create_issue`
- Action-oriented verbs: get, list, search, create, update, delete
- Avoid generic names that conflict with other servers

## Tool Annotations

| Annotation        | Type    | Default | Meaning                                   |
|-------------------|---------|---------|-------------------------------------------|
| `readOnlyHint`    | boolean | false   | Tool does not modify its environment       |
| `destructiveHint` | boolean | true    | Tool may perform destructive updates       |
| `idempotentHint`  | boolean | false   | Repeated calls have no additional effect   |
| `openWorldHint`   | boolean | true    | Tool interacts with external entities      |

Annotations are hints, not security guarantees. Set them accurately to help clients make informed decisions.

## Tool Descriptions

- Must narrowly and unambiguously describe functionality
- Include parameter descriptions with types and constraints
- Document return schema with field names and types
- List error cases and suggested remediation
- Add usage examples showing when to use and when not to use the tool

## Response Formats

Support both formats via a `response_format` parameter:

**Markdown** (default for human readability):
- Headers, lists, formatting for clarity
- Human-readable timestamps (`2024-01-15 10:30 UTC` not epoch)
- Display names with IDs: `@john.doe (U123456)`
- Omit verbose metadata

**JSON** (for programmatic processing):
- Complete structured data with all fields
- Consistent field names and types
- Suitable for downstream composition

## Pagination

- Always respect `limit` parameter
- Return `has_more`, `next_offset` or `next_cursor`, `total_count`
- Default to 20-50 items per page
- Never load all results into memory

```json
{
  "total": 150,
  "count": 20,
  "offset": 0,
  "items": [],
  "has_more": true,
  "next_offset": 20
}
```

## Transport Selection

**Streamable HTTP** -- remote servers, multi-client, cloud deployment:
- Bidirectional over HTTP
- Supports multiple simultaneous clients
- Use stateless JSON mode (`enableJsonResponse: true`, `sessionIdGenerator: undefined`) for simpler scaling

**stdio** -- local tools, desktop apps, single-user:
- Standard input/output communication
- No network configuration needed
- Server runs as subprocess of client
- Never write to stdout (use stderr for logging)

Avoid SSE transport -- deprecated in favour of streamable HTTP.

## Security

**Authentication:**
- Store API keys in environment variables, never in code
- Validate on startup, fail fast with clear error
- For OAuth 2.1: validate access tokens per request, accept only tokens for your server

**Input validation:**
- Sanitise file paths against directory traversal
- Validate URLs and external identifiers
- Check parameter sizes and ranges
- Use schema validation (Zod/Pydantic) for all inputs

**DNS rebinding protection** (local streamable HTTP):
- Bind to `127.0.0.1` not `0.0.0.0`
- Validate `Origin` header on all connections

## Error Handling

- Use standard JSON-RPC error codes
- Report tool errors in result objects, not protocol-level errors
- Provide specific, actionable messages with next steps
- Never expose internal implementation details
- Clean up resources on errors

```typescript
return {
  isError: true,
  content: [{
    type: "text",
    text: `Error: Rate limit exceeded. Wait 30s or reduce limit parameter.`
  }]
};
```
