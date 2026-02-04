# Python MCP Server Implementation

## Key Imports

```python
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
import httpx, json
```

## Server Initialisation

```python
mcp = FastMCP("service_mcp")
```

Name format: `{service}_mcp` (lowercase, underscores). Examples: `github_mcp`, `slack_mcp`.

## Pydantic Input Models

```python
class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

class SearchInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    query: str = Field(..., min_length=2, max_length=200,
                       description="Search term to match against names/emails")
    limit: int = Field(default=20, ge=1, le=100,
                       description="Maximum results to return")
    offset: int = Field(default=0, ge=0,
                        description="Number of results to skip")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: markdown or json",
    )

    @field_validator("query")
    @classmethod
    def strip_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()
```

Use `ConfigDict(extra="forbid")` to reject unknown fields. Use `Field()` with constraints and descriptions on every parameter.

## Tool Registration

```python
@mcp.tool(
    name="service_search_items",
    annotations={
        "title": "Search Items",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def service_search_items(params: SearchInput) -> str:
    """Search items by keyword, returning paginated results.

    Args:
        params: Validated input with query, limit, offset, response_format.

    Returns:
        JSON string: { total, count, offset, items: [...], has_more, next_offset }
    """
    try:
        data = await _api_request("items/search", params={
            "q": params.query, "limit": params.limit, "offset": params.offset,
        })
        return _format_response(data, params.response_format)
    except Exception as e:
        return _handle_error(e)
```

## Shared Utilities

```python
async def _api_request(
    endpoint: str, method: str = "GET", **kwargs: Any
) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(method, f"{API_BASE_URL}/{endpoint}", **kwargs)
        resp.raise_for_status()
        return resp.json()

def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 404:
            return "Error: Resource not found. Check the ID."
        if status == 403:
            return "Error: Permission denied."
        if status == 429:
            return "Error: Rate limit exceeded. Wait before retrying."
        return f"Error: API request failed ({status})."
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Try again."
    return f"Error: {type(e).__name__}: {e}"
```

## Context Injection

FastMCP injects a `Context` parameter for logging, progress, and user interaction:

```python
@mcp.tool()
async def long_operation(query: str, ctx: Context) -> str:
    """Operation with progress reporting."""
    await ctx.report_progress(0.1, "Starting search...")
    results = await _api_request("search", params={"q": query})
    await ctx.report_progress(0.8, "Formatting results...")
    return json.dumps(results, indent=2)
```

Context capabilities: `report_progress`, `log_info`, `log_error`, `log_debug`, `elicit` (request user input), `read_resource`, `fastmcp.name`.

## Resource Registration

```python
@mcp.resource("config://settings/{key}")
async def get_setting(key: str) -> str:
    """Expose configuration as MCP resources."""
    settings = await load_settings()
    return json.dumps(settings.get(key, {}))
```

Use resources for static or template-based data. Use tools for operations with validation and business logic.

## Lifespan Management

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    db = await connect_database()
    yield {"db": db}
    await db.close()

mcp = FastMCP("service_mcp", lifespan=app_lifespan)

@mcp.tool()
async def query_db(sql: str, ctx: Context) -> str:
    db = ctx.request_context.lifespan_state["db"]
    return json.dumps(await db.query(sql))
```

## Transport

```python
# stdio (default, local)
if __name__ == "__main__":
    mcp.run()

# Streamable HTTP (remote)
if __name__ == "__main__":
    mcp.run(transport="streamable_http", port=8000)
```

## Quality Checklist

- [ ] Server name: `{service}_mcp`
- [ ] All tools use `@mcp.tool(name=..., annotations={...})`
- [ ] Pydantic models with `extra="forbid"`, `Field()` constraints and descriptions
- [ ] `field_validator` with `@classmethod` (Pydantic v2)
- [ ] Comprehensive docstrings with Args, Returns, Errors sections
- [ ] All network calls use `async with httpx.AsyncClient()`
- [ ] Type hints on every function signature
- [ ] Error handler maps status codes to actionable messages
- [ ] Constants defined at module level in UPPER_CASE
