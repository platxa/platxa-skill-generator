---
name: sora
description: "Generate, remix, poll, list, download, and delete Sora videos via the OpenAI Video API using the bundled CLI (scripts/sora.py). Handles single shots, batch runs, prompt augmentation, and asset downloads. Requires OPENAI_API_KEY."
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
  - WebFetch
  - WebSearch
metadata:
  version: "1.0.0"
  author: "platxa"
  tags:
    - builder
    - video
    - media
    - sora
    - openai
  provenance:
    upstream_source: "sora"
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T16:00:00Z"
    generator_version: "1.0.0"
    intent_confidence: 0.88
---

# Sora Video Generation

Create and manage short video clips (product demos, marketing spots, cinematic shots, UI mocks) using the OpenAI Sora Video API and the bundled CLI.

## Overview

This skill wraps the OpenAI Video API through `scripts/sora.py`, a Python CLI that handles job creation, polling, downloading, remixing, and batch runs. It defaults to the `sora-2` model with structured prompt augmentation so every generation starts from a production-oriented spec.

**What it creates:**
- Video clips (mp4) in 4, 8, or 12 second durations
- Thumbnails (webp) and spritesheets (jpg)
- Remixed variants of existing videos

**Key features:**
- Structured prompt augmentation with CLI flags (`--use-case`, `--camera`, `--lighting`)
- Batch generation from JSONL manifests
- Dry-run mode for preflight without API calls
- Automatic polling and asset download

## When to Use

- Generate a new video clip from a text prompt
- Remix an existing video by ID
- Poll status, list jobs, or download assets (video/thumbnail/spritesheet)
- Batch-create many prompts or variants

## Decision Tree

| Situation | Action |
|-----------|--------|
| User has a **video ID** and wants a change | `remix` |
| User has a **video ID** and wants status/assets | `status` / `poll` / `download` |
| User needs many prompts or variants | `create-batch` |
| Two versions with a small tweak | `create` base, then `remix` |
| Otherwise | `create` or `create-and-poll` |

## Workflow

### Step 1: Determine Intent

Classify the request as create, remix, status/download, or batch using the decision tree.

### Step 2: Collect Inputs

Gather from the user:
- **Prompt** (required): what to generate
- **Model**: `sora-2` (default) or `sora-2-pro` (higher fidelity)
- **Size**: `1280x720` (default), see `references/video-api.md` for all sizes
- **Duration**: `"4"` (default), `"8"`, or `"12"` seconds (string enum)
- **Input reference image** (optional): jpg/png/webp matching target size

### Step 3: Build the Prompt

Prefer CLI augmentation flags over pre-writing a structured prompt:

```bash
uv run --with openai python "$SORA_CLI" create \
  --prompt "A matte black camera on a pedestal" \
  --use-case "product teaser" \
  --camera "85mm, slow orbit" \
  --lighting "soft key, subtle rim" \
  --constraints "no logos, no text"
```

If you already produced a structured prompt file, pass `--no-augment` to skip re-wrapping.

### Step 4: Execute via CLI

Run `scripts/sora.py` with the collected parameters. For long prompts, use `--prompt-file` to avoid shell-escaping issues. See `references/cli.md` for the full command catalog.

### Step 5: Poll and Download

For async jobs, poll until complete or use `create-and-poll`:

```bash
uv run --with openai python "$SORA_CLI" create-and-poll \
  --prompt "Close-up of steaming coffee on a wooden table" \
  --size 1280x720 --seconds 8 \
  --download --variant video --out coffee.mp4
```

### Step 6: Cleanup

Remove intermediate files (prompt.txt, temp JSONL). If the sandbox blocks `rm`, skip cleanup or truncate without surfacing an error.

## Authentication

`OPENAI_API_KEY` must be set for live API calls.

If the key is missing:
1. Direct the user to create a key at https://platform.openai.com/api-keys
2. Ask them to set `OPENAI_API_KEY` as an environment variable
3. Offer to guide through setup for their OS/shell
4. Never ask the user to paste the full key in chat

## Prompt Augmentation

Reformat prompts into a structured spec. Only make implicit details explicit; do not invent new creative elements.

Template (include only relevant lines):
```
Use case: <clip destination>
Primary request: <user prompt>
Scene/background: <location, time of day, atmosphere>
Subject: <main subject>
Action: <single clear action>
Camera: <shot type, angle, motion>
Lighting/mood: <lighting + mood>
Color palette: <3-5 color anchors>
Style/format: <film/animation/format cues>
Timing/beats: <counts or beats>
Audio: <ambient cue / music / voiceover>
Text (verbatim): "<exact text>"
Constraints: <must keep/must avoid>
Avoid: <negative constraints>
```

Augmentation rules:
- Keep it short; add only details the user implied or provided
- For remixes, list invariants explicitly ("same shot, change only X")
- If a critical detail is missing and blocks success, ask; otherwise proceed
- Pair `--prompt-file` with `--no-augment` for pre-structured prompts

## Defaults and Rules

| Parameter | Default | Notes |
|-----------|---------|-------|
| Model | `sora-2` | Use `sora-2-pro` for higher fidelity |
| Size | `1280x720` | See `references/video-api.md` for supported sizes |
| Seconds | `"4"` | String enum: `"4"`, `"8"`, `"12"` |
| Variant | `video` | Also: `thumbnail`, `spritesheet` |
| Poll interval | `10s` | Adjustable via `--poll-interval` |

- Set size and seconds via API params; prose will not change them
- Use the OpenAI Python SDK via `uv run --with openai`
- If uv cache permissions fail, set `UV_CACHE_DIR=/tmp/uv-cache`
- Input reference images must be jpg/png/webp matching target size
- Download URLs expire after ~1 hour; copy assets to your own storage
- Never modify `scripts/sora.py` unless the user asks

## API Limitations

- Models limited to `sora-2` and `sora-2-pro`
- Organization-verified account required for API access
- Duration limited to 4/8/12 seconds via the `seconds` string param
- Video creation is async; poll for completion before downloading
- Rate limits apply by usage tier
- Content restrictions enforced by the API (see Guardrails)

## Guardrails

- Only content suitable for audiences under 18
- No copyrighted characters or copyrighted music
- No real people (including public figures)
- Input images with human faces are rejected

## Prompting Tips

- One main action + one camera move per shot
- Use counts or beats for timing ("two steps, pause, turn")
- Keep text short and lock off the camera for on-screen text
- Add an avoid line when artifacts appear (flicker, jitter, fast motion)
- Shorter prompts are more creative; longer prompts give more control
- State invariants explicitly for remixes
- Iterate with a single change per follow-up

## Examples

### Single Shot

```
User: Generate a product teaser of a matte black camera