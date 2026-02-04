# Audio Speech API Reference

## Endpoint

- Create speech: `POST /v1/audio/speech`

## Models

| Model | Instructions Support |
|-------|---------------------|
| `gpt-4o-mini-tts-2025-12-15` (default) | Yes |
| `gpt-4o-mini-tts` | Yes |
| `tts-1` | No |
| `tts-1-hd` | No |

## Core Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Speech model (required) |
| `input` | string | Text to synthesize, max 4096 characters (required) |
| `voice` | string | Built-in voice name (required) |
| `instructions` | string | Style directions (GPT-4o mini TTS only) |
| `response_format` | string | `mp3`, `opus`, `aac`, `flac`, `wav`, or `pcm` |
| `speed` | float | 0.25 to 4.0 |

## Built-in Voices

`alloy`, `ash`, `ballad`, `cedar`, `coral`, `echo`, `fable`, `marin`, `nova`, `onyx`, `sage`, `shimmer`, `verse`

## Output Format Notes

- Default format: `mp3`
- `pcm`: Raw 24 kHz 16-bit little-endian samples (no header)
- `wav`: Includes header (better for quick playback and IVR)

## Compliance

Provide a clear disclosure that the voice is AI-generated.
