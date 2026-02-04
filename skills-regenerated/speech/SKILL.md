---
name: speech
description: "Automates text-to-speech generation via the OpenAI Audio API. Runs the bundled CLI (scripts/text_to_speech.py) to produce narration, voiceover, IVR prompts, accessibility reads, and batch audio from text input. Requires OPENAI_API_KEY. Custom voice creation is out of scope."
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
metadata:
  version: "1.0.0"
  author: "platxa-skill-generator"
  tags:
    - automation
    - speech
    - tts
    - audio
    - openai
  provenance:
    upstream_source: "speech"
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T15:20:34Z"
    generator_version: "1.0.0"
    intent_confidence: 0.88
---

# Speech Generation

Automate spoken audio generation for narration, product demos, IVR prompts, accessibility reads, and batch speech jobs using the OpenAI Audio API and the bundled CLI.

## Overview

This skill automates text-to-speech generation for developers and content creators. It runs the bundled CLI (`scripts/text_to_speech.py`) whenever the user needs spoken audio generated from text input.

**What it automates:**
- Single clip generation from text with voice direction
- Batch generation of multiple audio files from JSONL input
- Instruction augmentation from user intent into structured voice directions
- Dependency installation and environment setup

**Time saved:** ~5-15 minutes per clip (manual API calls, parameter tuning, file management)

## Triggers

### When to Run

This automation should run when:
- User asks to generate speech, narration, voiceover, or audio from text
- User needs batch audio generation for multiple prompts
- User asks about text-to-speech, TTS, or the OpenAI Audio API
- User wants accessibility reads or IVR phone prompts

### Decision Tree

- Multiple lines, prompts, or many outputs requested --> **batch mode**
- Single text or one clip --> **single mode**

## Process

### Step 1: Collect Inputs

Gather from the user before generating:
- **Text**: The exact words to speak (verbatim, do not paraphrase)
- **Voice**: Preferred voice (default: `cedar`; brighter: `marin`)
- **Style**: Delivery style, tone, pacing preferences
- **Format**: Output format (`mp3`, `wav`, `opus`, `aac`, `flac`, `pcm`)
- **Constraints**: Speed, pronunciation needs, emphasis points

If the user provides only text, proceed with defaults. Ask only when a critical detail is ambiguous and blocks success.

### Step 2: Check Environment

Verify prerequisites before making API calls:

1. **OPENAI_API_KEY** must be set. If missing, guide the user:
   - Create a key at https://platform.openai.com/api-keys
   - Set it as an environment variable
   - Never ask the user to paste the key in chat
2. **openai package** must be installed:
   ```
   uv pip install openai
   ```
   If `uv` is unavailable: `python3 -m pip install openai`

### Step 3: Augment Instructions

Convert user direction into a structured voice spec. Only make implicit details explicit; do not invent new requirements.

Include only relevant lines from this template:
```
Voice Affect: <overall character and texture>
Tone: <attitude, formality, warmth>
Pacing: <slow, steady, brisk>
Emotion: <key emotions to convey>
Pronunciation: <words to enunciate or emphasize>
Pauses: <where to add intentional pauses>
Emphasis: <key words or phrases to stress>
Delivery: <cadence or rhythm notes>
```

**Rules:**
- Keep it to 4-8 short lines; avoid conflicting guidance
- Do not rewrite the input text
- If the user says "narration for a demo", you may add implied constraints (clear pacing, friendly tone)
- Do not introduce a persona, accent, or emotional style the user did not request

### Step 4: Run the CLI

Use the bundled CLI for all generation. Never create one-off scripts.

**Single clip:**
```bash
python scripts/text_to_speech.py speak \
  --input "Your text here" \
  --voice cedar \
  --instructions "Voice Affect: Warm and composed. Tone: Friendly." \
  --response-format mp3 \
  --out output.mp3
```

**Batch (JSONL):**
```bash
mkdir -p tmp/speech
# Write JSONL with one job per line
python scripts/text_to_speech.py speak-batch \
  --input tmp/speech/jobs.jsonl \
  --out-dir out \
  --rpm 50
# Delete the JSONL when done
rm -f tmp/speech/jobs.jsonl
```

**Dry run (no API call, no key needed):**
```bash
python scripts/text_to_speech.py speak --input "Test" --dry-run
```

### Step 5: Validate Output

For important clips, check:
- Intelligibility and clarity
- Pacing matches intent
- Pronunciation of names, acronyms, and numbers
- Adherence to user constraints

### Step 6: Iterate if Needed

Make one targeted change per iteration:
- Change voice, speed, or instructions (not all at once)
- Repeat invariant constraints to reduce drift (e.g., "keep pacing steady")
- Re-validate after each change

### Step 7: Deliver

Save final outputs and report:
- Output file path(s)
- Final text, instructions, and CLI flags used
- Voice and format used

## Defaults and Rules

| Parameter | Default | Notes |
|-----------|---------|-------|
| Model | `gpt-4o-mini-tts-2025-12-15` | Only change if user requests |
| Voice | `cedar` | Use `marin` for brighter tone |
| Format | `mp3` | Use `wav` for video sync or IVR |
| Speed | `1.0` | Range: 0.25-4.0 |
| RPM cap | `50` | Maximum 50 requests/minute |
| Input limit | 4096 chars | Split longer text into chunks |

**Hard rules:**
- Built-in voices only. Custom voices are out of scope.
- `instructions` only work with GPT-4o mini TTS models, not `tts-1` or `tts-1-hd`.
- Always require `OPENAI_API_KEY` before live API calls.
- Disclose to end users that the voice is AI-generated.
- Use the OpenAI Python SDK; do not use raw HTTP.
- Never modify `scripts/text_to_speech.py`. If something is missing, ask the user first.
- Prefer the bundled CLI over writing new one-off scripts.

## Use-Case Quick Reference

| Use Case | Voice | Format | Speed | Reference |
|----------|-------|--------|-------|-----------|
| Narration / explainer | `cedar` | `mp3` | `1.0` | `references/use-case-defaults.md` |
| Product demo / voiceover | `cedar` or `marin` | `wav` / `mp3` | `1.0` | `references/use-case-defaults.md` |
| IVR / phone prompts | `cedar` or `marin` | `wav` | `0.9-1.0` | `references/use-case-defaults.md` |
| Accessibility reads | `cedar` | `mp3` / `wav` | `0.95-1.0` | `references/use-case-defaults.md` |

## Verification

### Success Indicators

- Audio file exists at the specified output path
- File size is non-zero and format matches the requested format
- Playback sounds intelligible with correct pacing and voice

### Failure Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `OPENAI_API_KEY is not set` | Missing API key | Guide user to set the environment variable |
| `Input text exceeds 4096 characters` | Text too long | Split into smaller chunks |
| `openai SDK not installed` | Missing dependency | Run `uv pip install openai` |
| `Output already exists` | File conflict | Use `--force` to overwrite |
| Rate limit (429) | Too many requests | CLI retries automatically with backoff |
| Network error | No connectivity | Check network; see `references/codex-network.md` |

## Examples

### Example 1: Single Narration Clip

```
User: Generate a narration for "Welcome to the demo. Today we'll show how it works."
Assistant: I'll generate a narration clip with warm, friendly delivery.

Running:
python scripts/text_to_speech.py speak \
  --input "Welcome to the demo. Today we'll show how it works." \
  --voice cedar \
  --instructions "Voice Affect: Warm and composed. Tone: Friendly and confident. Pacing: Steady and moderate. Emphasis: Stress 'demo' and 'show'." \
  --response-format mp3 \
  --out demo-narration.mp3

Done. Wrote demo-narration.mp3
Voice: cedar | Format: mp3 | Speed: 1.0
```

### Example 2: Batch IVR Prompts

```
User: Generate IVR prompts for our phone system: "Thank you for calling. Please hold." and "For sales, press 1. For support, press 2."
Assistant: I'll create both prompts as a batch job with IVR-appropriate settings.

Writing JSONL to tmp/speech/jobs.jsonl and running batch:
python scripts/text_to_speech.py speak-batch \
  --input tmp/speech/jobs.jsonl \
  --out-dir out \
  --rpm 50

Done. Generated 2 files in out/
Cleaning up tmp/speech/jobs.jsonl
```

### Example 3: Dry Run

```
User: Preview what the CLI would do for "Hello world" without calling the API.
Assistant: Running dry-run (no API call, no key needed):
python scripts/text_to_speech.py speak --input "Hello world" --dry-run

Output:
{
  "input": "Hello world",
  "model": "gpt-4o-mini-tts-2025-12-15",
  "response_format": "mp3",
  "voice": "cedar"
}
Would write speech.mp3
```

## Safety

### Idempotency

This automation is idempotent with `--force`: re-running with the same inputs produces an equivalent output file. Without `--force`, it refuses to overwrite existing files.

### Reversibility

Generated audio files can be deleted. No destructive changes are made to existing files. The CLI never modifies source files.

### Prerequisites

Before running, ensure:
- [ ] `OPENAI_API_KEY` is set as an environment variable
- [ ] `openai` Python package is installed
- [ ] Network access is available for API calls (see `references/codex-network.md` for sandbox environments)

## File and Directory Conventions

- Temporary files: `tmp/speech/` (delete JSONL batches after use)
- Final outputs: `output/speech/` or user-specified path via `--out` / `--out-dir`
- Keep filenames stable and descriptive

## Reference Map

- **`references/audio-api.md`**: API endpoint, parameters, voice list, format options
- **`references/cli.md`**: CLI commands, flags, recipes, guardrails
- **`references/voice-directions.md`**: Instruction template, best practices, example direction blocks
- **`references/use-case-defaults.md`**: Per-use-case defaults for narration, voiceover, IVR, accessibility
- **`references/codex-network.md`**: Sandbox and network approval troubleshooting
