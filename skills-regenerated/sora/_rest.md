## Examples

### Single Shot

```
User: Generate a product teaser of a matte black camera

Assistant runs:
uv run --with openai python scripts/sora.py create-and-poll \
  --prompt "A matte black camera on a pedestal" \
  --use-case "product teaser" \
  --camera "85mm, slow orbit" \
  --lighting "soft key, subtle rim" \
  --constraints "no logos, no text" \
  --size 1280x720 --seconds 4 \
  --download --out camera-teaser.mp4
```

### Remix

```
User: Same shot but teal/sand/rust palette with warmer backlight

Assistant runs:
uv run --with openai python scripts/sora.py remix \
  --id video_abc123 \
  --prompt "Same shot, switch palette to teal/sand/rust" \
  --constraints "keep subject and camera unchanged"
```

### Batch

```
User: Generate 3 product shots with different angles

Assistant writes tmp/sora/batch.jsonl then runs:
uv run --with openai python scripts/sora.py create-batch \
  --input tmp/sora/batch.jsonl --out-dir out/ --concurrency 3
```

## Output Checklist

- [ ] Video file downloaded and accessible locally
- [ ] Correct model, size, and duration used
- [ ] No content policy violations (guardrails respected)
- [ ] Intermediate files cleaned up (prompt.txt, temp JSONL)
- [ ] Asset copied to persistent storage (URLs expire in ~1 hour)

## Reference Map

- **`references/cli.md`**: CLI commands, flags, recipes for `scripts/sora.py`
- **`references/video-api.md`**: API knobs (models, sizes, duration, status)
- **`references/prompting.md`**: prompt structure, camera language, iteration
- **`references/templates.md`**: cinematic shot and social ad prompt templates
- **`references/sample-prompts.md`**: copy-paste prompt recipes by asset type
- **`references/troubleshooting.md`**: common errors, fixes, sandbox workarounds
