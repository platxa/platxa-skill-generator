---
name: transcribe
description: >-
  Transcribe audio files to text with optional speaker diarization using OpenAI.
  Use when a user asks to transcribe speech from audio or video, extract text
  from recordings, or label speakers in interviews and meetings. Runs the
  bundled transcribe_diarize.py CLI with sensible defaults.
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
metadata:
  version: "1.0.0"
  author: platxa
  tags:
    - automation
    - transcription
    - audio
    - openai
  provenance:
    upstream_source: "transcribe"
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T12:46:27Z"
    generator_version: "1.0.0"
    intent_confidence: 0.8
---

# Audio Transcribe

Transcribe audio using OpenAI with optional speaker diarization. Prefer the bundled CLI for deterministic, repeatable runs.

## Overview

This skill automates audio-to-text transcription using OpenAI's transcription models. It wraps the bundled `transcribe_diarize.py` CLI to provide fast text transcription by default, with optional speaker diarization when the user needs to identify who said what.

**What it automates:**
- Single-file and batch audio transcription
- Speaker diarization with known-speaker identification
- Model and format selection based on user needs
- Output file management and directory organization

**Models available:**
- `gpt-4o-mini-transcribe` (default) -- fast, cost-efficient text transcription
- `gpt-4o-transcribe-diarize` -- transcription with speaker labels

## Triggers

Run this skill when the user asks to:
- Transcribe an audio or video file
- Extract text from a recording
- Label speakers in an interview or meeting
- Convert speech to text
- Get a transcript with speaker diarization

## Process

### Step 1: Collect Inputs

Gather from the user:
- **Audio file path(s)** -- one or more files (mp3, mp4, mpeg, mpga, m4a, wav, webm)
- **Response format** -- `text` (default), `json`, or `diarized_json`
- **Language hint** -- optional, for non-English audio (e.g., `es`, `fr`)
- **Known speaker references** -- optional, up to 4 speakers as `NAME=PATH` pairs

If the user doesn't specify details, use defaults: `gpt-4o-mini-transcribe` model with `text` response format.

### Step 2: Verify Environment

Check that `OPENAI_API_KEY` is set:

```bash
echo "${OPENAI_API_KEY:+API key is set}"
```

If missing, instruct the user to create one at https://platform.openai.com/api-keys and export it in their shell. **Never ask the user to paste the key in chat.**

Check that the `openai` SDK is installed. If missing:

```bash
uv pip install openai
```

### Step 3: Run Transcription

Locate the bundled CLI script relative to this skill:

```bash
SKILL_DIR="$(dirname "$(readlink -f "$0")")"
TRANSCRIBE_CLI="$SKILL_DIR/scripts/transcribe_diarize.py"
```

Run with appropriate options based on user needs.

**Fast text transcription (default):**
```bash
python3 "$TRANSCRIBE_CLI" path/to/audio.wav --out transcript.txt
```

**Diarized output with known speakers:**
```bash
python3 "$TRANSCRIBE_CLI" meeting.m4a \
  --model gpt-4o-transcribe-diarize \
  --response-format diarized_json \
  --known-speaker "Alice=refs/alice.wav" \
  --known-speaker "Bob=refs/bob.wav" \
  --out-dir output/transcribe/meeting
```

**Batch transcription:**
```bash
python3 "$TRANSCRIBE_CLI" file1.mp3 file2.mp3 file3.mp3 \
  --out-dir output/transcribe/batch
```

### Step 4: Validate Output

After transcription completes:
- Read the output file to confirm transcription quality
- If diarized, check that speaker labels are present and reasonable
- If quality is poor, iterate with a single targeted change (e.g., add language hint, switch model)

## Decision Rules

| Condition | Model | Format | Notes |
|-----------|-------|--------|-------|
| Default / fast transcription | `gpt-4o-mini-transcribe` | `text` | Cheapest, fastest |
| User wants speaker labels | `gpt-4o-transcribe-diarize` | `diarized_json` | Required for diarization |
| Structured output needed | `gpt-4o-mini-transcribe` | `json` | Timestamps included |
| Audio > 30 seconds | Any | Any | Keep `--chunking-strategy auto` (default) |
| Non-English audio | Any | Any | Add `--language <code>` |

**Constraints:**
- Prompting (`--prompt`) is **not supported** with `gpt-4o-transcribe-diarize`
- `diarized_json` format **requires** `gpt-4o-transcribe-diarize` model
- Max 4 known speaker references, each 2-10 seconds of audio
- Max file size: 25 MB per request

## Verification

### Success Indicators
- Output file created at expected path
- Transcript contains readable text matching the audio content
- Speaker labels present when diarization was requested
- No API errors in stderr

### Failure Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `OPENAI_API_KEY is not set` | Missing environment variable | User must export the key |
| `Audio file not found` | Wrong path | Verify file path exists |
| `Audio file exceeds 25MB` | File too large | Split audio or compress |
| `response-format must be one of...` | Invalid format | Use text, json, or diarized_json |
| `prompt is not supported with gpt-4o-transcribe-diarize` | Incompatible options | Remove --prompt flag |
| `diarized_json requires gpt-4o-transcribe-diarize` | Wrong model for format | Switch to diarize model |
| `openai SDK not installed` | Missing dependency | Run `uv pip install openai` |

## Examples

### Example 1: Quick Transcription

```
User: Transcribe this audio file: ~/recordings/interview.mp3
Assistant: I'll transcribe the audio file using the fast transcription model.

Running: python3 transcribe_diarize.py ~/recordings/interview.mp3 --out interview.transcript.txt

Wrote interview.transcript.txt
```

### Example 2: Meeting with Speaker Labels

```
User: Transcribe this meeting recording and identify who is speaking.
      The speakers are Alice and Bob. I have reference clips at refs/alice.wav and refs/bob.wav.
Assistant: I'll use the diarization model with your known speaker references.

Running: python3 transcribe_diarize.py meeting.m4a \
  --model gpt-4o-transcribe-diarize \
  --response-format diarized_json \
  --known-speaker "Alice=refs/alice.wav" \
  --known-speaker "Bob=refs/bob.wav" \
  --out-dir output/transcribe/meeting

Wrote output/transcribe/meeting/meeting.transcript.json
```

### Example 3: Dry Run

```
User: What would the API call look like for transcribing podcast.mp3?
Assistant: I'll do a dry run to show the payload without calling the API.

Running: python3 transcribe_diarize.py podcast.mp3 --dry-run

{
  "model": "gpt-4o-mini-transcribe",
  "response_format": "text",
  "chunking_strategy": "auto"
}
```

## Safety

### Idempotency

This automation is **not idempotent** -- re-running overwrites the output file at the same path. Use `--out-dir` with unique directory names to preserve previous runs.

### Reversibility

Source audio files are never modified. Only output transcript files are created or overwritten. Delete the output file to undo.

### Prerequisites

Before running, ensure:
- [ ] `OPENAI_API_KEY` is set in the environment
- [ ] `openai` Python package is installed
- [ ] Audio file exists and is under 25 MB
- [ ] Audio format is supported (mp3, mp4, mpeg, mpga, m4a, wav, webm)

## Reference Map

- `references/api.md` -- supported formats, limits, response formats, and known-speaker notes
- `references/workflows.md` -- common transcription workflows with copy-paste examples
- `scripts/transcribe_diarize.py` -- bundled Python CLI for transcription