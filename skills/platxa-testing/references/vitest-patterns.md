# Vitest Patterns Reference

TypeScript testing patterns for Platxa using Vitest.

## Configuration

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.test.ts', 'tests/**/*.test.ts'],
    exclude: ['node_modules', 'dist'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.d.ts', '**/*.test.ts'],
    },
    testTimeout: 30000,
    hookTimeout: 30000,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### package.json Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:watch": "vitest --watch",
    "test:ui": "vitest --ui"
  }
}
```

## Test Structure

### Basic Test File

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

describe('FeatureName', () => {
  let testDir: string;

  beforeEach(() => {
    testDir = fs.mkdtempSync(path.join(os.tmpdir(), 'test-'));
  });

  afterEach(() => {
    fs.rmSync(testDir, { recursive: true, force: true });
  });

  it('handles valid input correctly', () => {
    // Test implementation
  });
});
```

### Async Testing

```typescript
describe('AsyncOperations', () => {
  it('waits for promise resolution', async () => {
    const result = await fetchData();
    expect(result).toBeDefined();
  });

  it('handles rejection correctly', async () => {
    await expect(failingOperation()).rejects.toThrow('Expected error');
  });

  it('uses fake timers for delays', async () => {
    vi.useFakeTimers();
    const promise = delayedOperation(1000);
    vi.advanceTimersByTime(1000);
    await expect(promise).resolves.toBe('done');
    vi.useRealTimers();
  });
});
```

## File System Testing

### Real File Operations

```typescript
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

describe('FileOperations', () => {
  let testDir: string;

  beforeEach(() => {
    testDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fileops-'));
  });

  afterEach(() => {
    fs.rmSync(testDir, { recursive: true, force: true });
  });

  it('reads JSON file correctly', async () => {
    const filePath = path.join(testDir, 'data.json');
    fs.writeFileSync(filePath, '{"key": "value"}');

    const result = await readJsonFile(filePath);

    expect(result).toEqual({ key: 'value' });
  });

  it('creates nested directories', () => {
    const nestedPath = path.join(testDir, 'a', 'b', 'c');

    createDirectoryTree(nestedPath);

    expect(fs.existsSync(nestedPath)).toBe(true);
  });
});
```

## Mocking (When Necessary)

### Function Mocks

```typescript
import { vi, describe, it, expect } from 'vitest';

describe('WithMocks', () => {
  it('mocks external API call', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ data: 'test' }),
    });

    global.fetch = mockFetch;

    const result = await fetchExternalData();

    expect(mockFetch).toHaveBeenCalledWith('https://api.example.com/data');
    expect(result.data).toBe('test');
  });
});
```

### Module Mocks

```typescript
vi.mock('./database', () => ({
  connect: vi.fn().mockResolvedValue({ connected: true }),
  query: vi.fn().mockResolvedValue([]),
}));

import { connect, query } from './database';

describe('DatabaseModule', () => {
  it('uses mocked database', async () => {
    const conn = await connect();
    expect(conn.connected).toBe(true);
  });
});
```

## Subprocess Testing

```typescript
import { execSync, spawn } from 'child_process';

describe('SubprocessExecution', () => {
  it('runs shell command synchronously', () => {
    const result = execSync('echo "hello"', { encoding: 'utf-8' });
    expect(result.trim()).toBe('hello');
  });

  it('runs long-running process', async () => {
    const child = spawn('node', ['script.js']);

    const output = await new Promise<string>((resolve) => {
      let data = '';
      child.stdout.on('data', (chunk) => { data += chunk; });
      child.on('close', () => resolve(data));
    });

    expect(output).toContain('expected output');
  });
});
```

## Snapshot Testing

```typescript
describe('SnapshotTests', () => {
  it('matches object snapshot', () => {
    const result = generateConfig();
    expect(result).toMatchSnapshot();
  });

  it('matches inline snapshot', () => {
    const result = formatOutput('test');
    expect(result).toMatchInlineSnapshot(`"formatted: test"`);
  });
});
```

## Test Utilities

### Custom Matchers

```typescript
expect.extend({
  toBeValidJSON(received: string) {
    try {
      JSON.parse(received);
      return { pass: true, message: () => 'Valid JSON' };
    } catch {
      return { pass: false, message: () => `Invalid JSON: ${received}` };
    }
  },
});

// Usage
expect('{"valid": true}').toBeValidJSON();
```

### Test Helpers

```typescript
// tests/helpers.ts
export function createTempFile(dir: string, name: string, content: string): string {
  const filePath = path.join(dir, name);
  fs.writeFileSync(filePath, content);
  return filePath;
}

export function waitFor(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
```

## CI Integration

```yaml
# GitHub Actions
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install
      - run: pnpm test:coverage
      - uses: codecov/codecov-action@v3
```

