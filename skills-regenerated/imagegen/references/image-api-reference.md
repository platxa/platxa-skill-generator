# Image API Quick Reference

## Endpoints

| Endpoint | SDK Method | Use |
|----------|-----------|-----|
| `POST /v1/images/generations` | `client.images.generate(...)` | Create new images |
| `POST /v1/images/edits` | `client.images.edit(...)` | Edit existing images |

## Models

| Model | Notes |
|-------|-------|
| `gpt-image-1.5` | Default. Best quality and text rendering |
| `gpt-image-1-mini` | Faster, lower cost. Use when user requests cheaper/faster |

## Core Parameters (generate + edit)

| Parameter | Values | Default | Notes |
|-----------|--------|---------|-------|
| `prompt` | text | (required) | Text description |
| `model` | model name | `gpt-image-1.5` | Image model |
| `n` | 1-10 | 1 | Number of images |
| `size` | `1024x1024`, `1536x1024`, `1024x1536`, `auto` | `1024x1024` | Output dimensions |
| `quality` | `low`, `medium`, `high`, `auto` | `auto` | Quality level |
| `background` | `transparent`, `opaque`, `auto` | `auto` | Requires png/webp for transparent |
| `output_format` | `png`, `jpeg`, `webp` | `png` | Image format |
| `output_compression` | 0-100 | - | jpeg/webp only |
| `moderation` | `auto`, `low` | `auto` | Content moderation level |

## Edit-Specific Parameters

| Parameter | Values | Default | Notes |
|-----------|--------|---------|-------|
| `image` | file(s) | (required) | Input image(s). First is primary |
| `mask` | file | optional | PNG with alpha channel, same dimensions as input |
| `input_fidelity` | `low`, `high` | `low` | Use `high` for strict edits (identity lock, layout lock) |

## Output Format

Response contains `data[]` array with `b64_json` per image (base64-encoded image data).

## Limits

- Input images and masks: max 50MB each
- Mask must match input image dimensions
- Masking is prompt-guided; exact shapes are not guaranteed
- Large sizes + high quality = higher latency and cost

## Quality vs Latency Guide

| Scenario | Quality | Input Fidelity |
|----------|---------|----------------|
| Fast iteration / drafts | `low` | - |
| General use | `auto` | - |
| Text-heavy / detail-critical | `high` | - |
| Strict edits (identity, layout lock) | `high` | `high` |
| Compositing with precise placement | - | `high` |
