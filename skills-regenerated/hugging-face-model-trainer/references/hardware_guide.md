# Hardware Selection Guide

## GPU Options

| Flavor | GPU | VRAM | Use Case | Cost/hr |
|--------|-----|------|----------|---------|
| `t4-small` | T4 | 16GB | <1B models, demos | ~$0.50-1 |
| `t4-medium` | T4 | 16GB | 1-3B dev | ~$1-2 |
| `l4x1` | L4 | 24GB | 3-7B efficient | ~$2-3 |
| `l4x4` | 4x L4 | 96GB | Multi-GPU | ~$8-12 |
| `a10g-small` | A10G | 24GB | 3-7B production | ~$3-4 |
| `a10g-large` | A10G | 24GB | 7-13B | ~$4-6 |
| `a10g-largex2` | 2x A10G | 48GB | Large multi-GPU | ~$8-12 |
| `a10g-largex4` | 4x A10G | 96GB | Very large | ~$16-24 |
| `a100-large` | A100 | 40GB | 13B+, fast | ~$8-12 |

CPU flavors (`cpu-basic`, `cpu-upgrade`) for testing/validation only.

## By Model Size

| Size | Hardware | Batch Size | Time (10K examples) |
|------|----------|-----------|-------------------|
| <1B | `t4-small` | 4-8 | 1-2h |
| 1-3B | `t4-medium`/`a10g-small` | 2-4 | 2-4h |
| 3-7B | `a10g-small`/`a10g-large` | 1-2 (LoRA: 4-8) | 4-8h |
| 7-13B | `a10g-large`/`a100-large` | 1 (LoRA: 2-4) | 6-12h |
| 13B+ | `a100-large` (LoRA only) | 1-2 with LoRA | 8-24h |

## Memory Estimation

- **Full fine-tuning**: ~(params in B) x 20 GB
- **LoRA fine-tuning**: ~(params in B) x 4 GB

## Memory Optimization Order

1. Use LoRA/PEFT: `peft_config=LoraConfig(r=16, lora_alpha=32)`
2. Reduce batch: `per_device_train_batch_size=1`
3. Increase accumulation: `gradient_accumulation_steps=8`
4. Enable checkpointing: `gradient_checkpointing=True`
5. Mixed precision: `bf16=True`
6. Upgrade GPU: t4 -> a10g -> a100

## Multi-GPU

TRL/Accelerate handles distribution automatically. No code changes needed.
Use `a10g-largex2`/`a10g-largex4`/`l4x4` flavors.
Effective batch = `per_device_train_batch_size` x `num_gpus` x `gradient_accumulation_steps`.

## Quick Reference

```python
HARDWARE_MAP = {
    "<1B":   "t4-small",
    "1-3B":  "a10g-small",
    "3-7B":  "a10g-large",
    "7-13B": "a10g-large (LoRA) or a100-large",
    ">13B":  "a100-large (LoRA required)"
}
```
