# Verification Command Reference

Language-specific commands for pre-completion verification. Each entry shows the command, what it proves, and how to confirm success.

## Python

| Command | Proves | Success |
|---------|--------|---------|
| `pytest tests/ -v` | Tests pass | 0 failed, exit 0 |
| `pyright .` | Types clean | 0 errors |
| `ruff check .` | Lint clean | exit 0, no output |
| `ruff format --check .` | Format correct | exit 0 |
| `python -m py_compile file.py` | Syntax valid | exit 0, no output |

## TypeScript / JavaScript

| Command | Proves | Success |
|---------|--------|---------|
| `pnpm typecheck` / `npx tsc --noEmit` | Types clean | 0 errors, exit 0 |
| `pnpm test` / `npx vitest run` | Tests pass | 0 failed, exit 0 |
| `pnpm build` / `npx next build` | Build works | exit 0 |
| `pnpm lint:fix` / `npx eslint .` | Lint clean | 0 errors, exit 0 |

## Go

| Command | Proves | Success |
|---------|--------|---------|
| `go test ./...` | Tests pass | "ok" per package, exit 0 |
| `go test -v ./...` | Tests pass (verbose) | PASS per test, exit 0 |
| `go build ./...` | Build works | exit 0, no output |
| `go vet ./...` | Static analysis clean | exit 0, no output |

## Rust

| Command | Proves | Success |
|---------|--------|---------|
| `cargo test` | Tests pass | "test result: ok", exit 0 |
| `cargo build` | Build works | "Finished", exit 0 |
| `cargo clippy -- -D warnings` | Lint clean | exit 0 |

## Shell / Bash

| Command | Proves | Success |
|---------|--------|---------|
| `shellcheck script.sh` | Script valid | exit 0, no output |
| `bash -n script.sh` | Syntax valid | exit 0, no output |

## Git / VCS

| Command | Proves | Use For |
|---------|--------|---------|
| `git status` | Working tree state | Pre-commit check |
| `git diff HEAD` | Actual changes | Agent delegation verification |
| `git diff --stat` | Change summary | Quick scope check |
| `git log -1 --format=%H` | Latest commit | Verify commit happened |

## Exit Code Reference

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Claim allowed (after reading output) |
| 1 | Failure | Report actual errors, do not claim success |
| 2 | Warnings/partial | Report warnings, conditional pass only |
| 127 | Command not found | Tool not installed, cannot verify |

## Verification Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| Running linter, claiming build passes | Different tools check different things |
| Running one test file, claiming "all tests pass" | Partial suite ≠ full suite |
| Checking exit code only, not reading output | Exit 0 with warnings is not clean |
| Using cached/previous results | Only current session evidence counts |
| Trusting IDE squiggles | IDE checks ≠ CLI verification |
