# TypeScript MCP Server Implementation

## Project Structure

```
{service}-mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts          # McpServer init, transport, main
│   ├── types.ts           # Interfaces and type definitions
│   ├── constants.ts       # API_BASE_URL, CHARACTER_LIMIT
│   ├── tools/             # Tool implementations by domain
│   ├── services/          # API clients, shared utilities
│   └── schemas/           # Zod validation schemas
└── dist/                  # Compiled output (entry: dist/index.js)
```

## Key Imports

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
```

Use `registerTool`, `registerResource`, `registerPrompt` exclusively. The older `server.tool()` and `server.setRequestHandler(ListToolsRequestSchema, ...)` APIs are deprecated.

## Zod Schemas

```typescript
const SearchInput = z.object({
  query: z.string()
    .min(2, "Query must be at least 2 characters")
    .max(200)
    .describe("Search string to match against names/emails"),
  limit: z.number().int().min(1).max(100).default(20)
    .describe("Maximum results to return"),
  offset: z.number().int().min(0).default(0)
    .describe("Number of results to skip for pagination"),
  response_format: z.nativeEnum(ResponseFormat).default(ResponseFormat.MARKDOWN)
    .describe("Output format: markdown or json"),
}).strict();

type SearchInput = z.infer<typeof SearchInput>;
```

Always call `.strict()` to reject unknown fields. Use `.describe()` on every field -- LLMs read these descriptions.

## Tool Registration

```typescript
server.registerTool(
  "service_search_items",
  {
    title: "Search Items",
    description: `Search items by keyword, returning paginated results.

Args:
  - query (string): Search term (2-200 chars)
  - limit (number): Max results, 1-100, default 20
  - offset (number): Skip N results, default 0

Returns JSON:
  { total, count, offset, items: [{ id, name, ... }], has_more, next_offset }

Errors:
  - "Rate limit exceeded" on 429
  - "Not found" on 404`,
    inputSchema: SearchInput,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true,
    },
  },
  async (params: SearchInput) => {
    const data = await makeApiRequest<SearchResponse>("items/search", "GET", undefined, {
      q: params.query, limit: params.limit, offset: params.offset,
    });
    const output = formatSearchResponse(data, params);
    return {
      content: [{ type: "text", text: formatAsText(output, params.response_format) }],
      structuredContent: output,
    };
  }
);
```

## Shared Utilities

```typescript
const CHARACTER_LIMIT = 25000;

async function makeApiRequest<T>(
  endpoint: string, method = "GET", data?: unknown, params?: Record<string, unknown>
): Promise<T> {
  const response = await axios({
    method, url: `${API_BASE_URL}/${endpoint}`,
    data, params, timeout: 30000,
    headers: { "Content-Type": "application/json", Accept: "application/json" },
  });
  return response.data;
}

function handleApiError(error: unknown): string {
  if (error instanceof AxiosError && error.response) {
    const status = error.response.status;
    if (status === 404) return "Error: Resource not found. Check the ID.";
    if (status === 403) return "Error: Permission denied.";
    if (status === 429) return "Error: Rate limit exceeded. Wait before retrying.";
    return `Error: API request failed (${status}).`;
  }
  if (error instanceof AxiosError && error.code === "ECONNABORTED") {
    return "Error: Request timed out. Try again.";
  }
  return `Error: ${error instanceof Error ? error.message : String(error)}`;
}
```

## Transport Setup

```typescript
// stdio (local)
async function runStdio() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP server running via stdio");
}

// Streamable HTTP (remote, stateless)
async function runHTTP() {
  const app = express();
  app.use(express.json());
  app.post("/mcp", async (req, res) => {
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true,
    });
    res.on("close", () => transport.close());
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  });
  app.listen(parseInt(process.env.PORT || "3000"));
}

const mode = process.env.TRANSPORT || "stdio";
(mode === "http" ? runHTTP() : runStdio()).catch(err => {
  console.error("Server error:", err);
  process.exit(1);
});
```

## Package Configuration

**package.json:**

```json
{
  "name": "{service}-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "clean": "rm -rf dist"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.6.1",
    "axios": "^1.7.9",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@types/node": "^22.10.0",
    "tsx": "^4.19.2",
    "typescript": "^5.7.2"
  }
}
```

**tsconfig.json:**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Quality Checklist

- [ ] `npm run build` succeeds without errors
- [ ] All tools registered with `registerTool` (not `server.tool()`)
- [ ] Zod schemas use `.strict()` and `.describe()` on every field
- [ ] No `any` types -- use `unknown` or proper interfaces
- [ ] All async functions have explicit `Promise<T>` return types
- [ ] `structuredContent` returned alongside `text` content
- [ ] Error handling uses `AxiosError` type guard
- [ ] `CHARACTER_LIMIT` enforced on large responses
