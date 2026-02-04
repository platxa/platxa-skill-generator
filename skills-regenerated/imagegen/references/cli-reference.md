# CLI Reference (`scripts/image_gen.py`)

Command catalog for the bundled image generation CLI.

## Commands

- `generate`: Create new images from a text prompt
- `edit`: Edit an existing image (inpainting, background replacement, object removal)
- `generate-batch`: Run many jobs from a JSONL file concurrently

## Quick Start

Set the CLI path:
```bash
IMAGE_GEN="<skill-directory>/scripts/image_gen.py"
```

Dry-run (no API call, no network required):
```bash
python3 "$IMAGE_GEN" generate --prompt "Test" --dry-run
```

Generate (requires `OPENAI_API_KEY`):
```bash
python3 "$IMAGE_GEN" generate --prompt "A cozy alpine cabin at dawn" --size 1024x1024
```

With `uv` (no install needed):
```bash
uv run --with openai python3 "$IMAGE_GEN" generate --prompt "A cozy alpine cabin at dawn"
```

## Guardrails

- Always use `python3 "$IMAGE_GEN" ...` for generations/edits/batch
- Do **not** create one-off scripts unless the user explicitly asks
- **Never modify** `scripts/image_gen.py`

## Shared Flags (all commands)

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `gpt-image-1.5` | Image model |
| `--prompt` | (required) | Text prompt |
| `--prompt-file` | - | Read prompt from file (mutually exclusive with `--prompt`) |
| `--n` | `1` | Number of images (1-10) |
| `--size` | `1024x1024` | `1024x1024`, `1536x1024`, `1024x1536`, or `auto` |
| `--quality` | `auto` | `low`, `medium`, `high`, or `auto` |
| `--background` | API default | `transparent`, `opaque`, or `auto` |
| `--output-format` | `png` | `png`, `jpeg`, `webp` |
| `--output-compression` | - | 0-100 (jpeg/webp only) |
| `--moderation` | `auto` | `auto` or `low` |
| `--out` | `output.png` | Output file path |
| `--out-dir` | - | Output directory |
| `--force` | false | Overwrite existing files |
| `--dry-run` | false | Print request JSON, skip API call |
| `--augment` / `--no-augment` | `--augment` | Enable/disable prompt augmentation |
| `--downscale-max-dim` | - | Generate additional downscaled copy |
| `--downscale-suffix` | `-web` | Suffix for downscaled file |

## Prompt Augmentation Flags

| Flag | Description |
|------|-------------|
| `--use-case` | Taxonomy slug (e.g., `product-mockup`) |
| `--scene` | Scene/background description |
| `--subject` | Main subject |
| `--style` | Style/medium |
| `--composition` | Composition/framing |
| `--lighting` | Lighting/mood |
| `--palette` | Color palette |
| `--materials` | Materials/textures |
| `--text` | Verbatim text to render |
| `--constraints` | Must-keep constraints |
| `--negative` | Must-avoid constraints |

## Edit-Specific Flags

| Flag | Description |
|------|-------------|
| `--image` | Input image path(s) (can repeat for multi-image) |
| `--mask` | Mask PNG path (alpha channel required) |
| `--input-fidelity` | `low` (default) or `high` (strict edits) |

## Batch-Specific Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | (required) | Path to JSONL file |
| `--out-dir` | (required) | Output directory |
| `--concurrency` | `5` | Parallel jobs (1-25) |
| `--max-attempts` | `3` | Retry attempts per job |
| `--fail-fast` | false | Stop on first failure |

## JSONL Format (batch)

One JSON object per line:
```json
{"prompt": "A sunset over mountains", "size": "1536x1024", "quality": "high"}
{"prompt": "A forest stream", "constraints": "no watermark"}
```

Supported per-job overrides: `size`, `quality`, `background`, `output_format`, `n`, `out`, and all augmentation fields.

## Common Recipes

Generate with augmentation:
```bash
python3 "$IMAGE_GEN" generate \
  --prompt "A minimal hero image of a ceramic coffee mug" \
  --use-case "product-mockup" \
  --style "clean product photography" \
  --composition "centered product, generous negative space" \
  --constraints "no logos, no text"
```

Generate + downscale for web:
```bash
uv run --with openai --with pillow python3 "$IMAGE_GEN" generate \
  --prompt "A cozy alpine cabin at dawn" \
  --size 1024x1024 \
  --downscale-max-dim 512
```

Edit with mask:
```bash
python3 "$IMAGE_GEN" edit --image input.png --mask mask.png \
  --prompt "Replace the background with a warm sunset" \
  --quality high --input-fidelity high
```

Batch (concurrent):
```bash
python3 "$IMAGE_GEN" generate-batch \
  --input prompts.jsonl --out-dir output/ --concurrency 5
```

## Notes

- Transparent backgrounds require `--output-format png` or `webp`
- `--n` generates variants of one prompt; batch is for different prompts
- Masks must be PNG with alpha channel, matching input dimensions
- Input images and masks must be under 50MB
- Supported sizes: `1024x1024`, `1536x1024`, `1024x1536`, `auto`
- Downscaling requires Pillow (`uv pip install pillow`)
