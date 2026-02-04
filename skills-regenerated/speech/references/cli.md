# CLI Reference: text_to_speech.py

The bundled CLI at `scripts/text_to_speech.py` handles all speech generation.

## Commands

| Command | Purpose |
|---------|---------|
| `speak` | Generate a single audio file |
| `speak-batch` | Generate many files from a JSONL file |
| `list-voices` | Print supported voice names |

## Quick Start

Set a stable path to the CLI:
```bash
export TTS_GEN="scripts/text_to_speech.py"
```

Dry run (no API call, no key needed):
```bash
python "$TTS_GEN" speak --input "Test" --dry-run
```

Generate a clip:
```bash
python "$TTS_GEN" speak \
  --input "Today is a wonderful day to build something people love!" \
  --voice cedar \
  --instructions "Voice Affect: Warm and composed. Tone: upbeat." \
  --response-format mp3 \
  --out speech.mp3
```

## Defaults

| Flag | Default |
|------|---------|
| `--model` | `gpt-4o-mini-tts-2025-12-15` |
| `--voice` | `cedar` |
| `--response-format` | `mp3` |
| `--speed` | `1.0` |
| `--rpm` (batch) | `50` |
| `--attempts` | `3` |

## Common Flags

| Flag | Description |
|------|-------------|
| `--input` | Input text string |
| `--input-file` | Path to text file (alternative to `--input`) |
| `--instructions` | Voice direction string |
| `--instructions-file` | Path to instructions file |
| `--out` | Output file path (speak) |
| `--out-dir` | Output directory (speak-batch) |
| `--dry-run` | Print payload without calling API |
| `--force` | Overwrite existing output files |

## Batch Generation

Write a JSONL file with one job per line:
```bash
mkdir -p tmp/speech
cat > tmp/speech/jobs.jsonl << 'JSONL'
{"input":"Thank you for calling.","voice":"cedar","response_format":"mp3","out":"hold.mp3"}
{"input":"For sales, press 1.","voice":"marin","instructions":"Tone: clear.","response_format":"wav"}
JSONL

python "$TTS_GEN" speak-batch --input tmp/speech/jobs.jsonl --out-dir out --rpm 50
rm -f tmp/speech/jobs.jsonl
```

Per-job JSONL overrides: `model`, `voice`, `response_format`, `speed`, `instructions`, `out`.

## Guardrails

- Use the bundled CLI for all TTS work. Do not create one-off scripts.
- Never modify `scripts/text_to_speech.py`. Ask the user first if something is missing.
- Input text must be <= 4096 characters. Split longer text into chunks.
- RPM is capped at 50. The CLI enforces this.
- Treat JSONL files as temporary: write under `tmp/`, delete after the run.
