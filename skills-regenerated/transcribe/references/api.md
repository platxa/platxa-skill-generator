# OpenAI Audio Transcription API Reference

## Supported Models

| Model | Purpose | Prompting | Diarization |
|-------|---------|-----------|-------------|
| `gpt-4o-mini-transcribe` | Fast text transcription | Supported | No |
| `gpt-4o-transcribe-diarize` | Transcription with speaker labels | **Not supported** | Yes |

## Input Formats

Supported audio formats: `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm`.

Maximum file size: **25 MB** per request.

## Response Formats

| Format | Model Compatibility | Output |
|--------|-------------------|--------|
| `text` | Both models | Plain text transcript |
| `json` | Both models | JSON with timestamps |
| `diarized_json` | `gpt-4o-transcribe-diarize` only | JSON with speaker labels and segment boundaries |

## Chunking Strategy

For audio longer than ~30 seconds, use `chunking_strategy: "auto"` to split into manageable chunks. This is the default in the bundled CLI.

## Known Speaker References

- Maximum: **4** known speakers per request
- Reference audio: **2-10 seconds** per speaker
- Passed via `extra_body` as `known_speaker_names` (list of names) and `known_speaker_references` (list of base64 data URLs)
- Only supported with `gpt-4o-transcribe-diarize` model

## API Endpoint

`POST /v1/audio/transcriptions` -- the only endpoint that supports diarization. The Realtime API does not support diarization.

## Rate Limits

Monitor `x-ratelimit-*` response headers. Implement exponential backoff with retry for HTTP 429 responses.
