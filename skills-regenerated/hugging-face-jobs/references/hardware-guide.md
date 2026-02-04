# Hardware Selection Guide

## Available Flavors

**CPU:**
- `cpu-basic` — Testing, lightweight tasks (~$0.03/15min)
- `cpu-upgrade` — Data processing, heavier CPU work (~$0.50/hr)

**Single GPU:**

| Flavor | GPU | VRAM | Best For | Est. Cost |
|--------|-----|------|----------|-----------|
| `t4-small` | T4 | 16GB | <1B models, demos | ~$1/hr |
| `t4-medium` | T4 | 16GB | 1-3B models | ~$1.50/hr |
| `l4x1` | L4 | 24GB | 3-7B efficient | ~$2.50/hr |
| `a10g-small` | A10G | 24GB | 3-7B production | ~$3.50/hr |
| `a10g-large` | A10G | 24GB | 7-13B models | ~$5/hr |
| `a100-large` | A100 | 40GB | 13B+ models | ~$10/hr |

**Multi-GPU:**
- `l4x4` — 4x L4, 96GB total VRAM
- `a10g-largex2` — 2x A10G, 48GB total VRAM
- `a10g-largex4` — 4x A10G, 96GB total VRAM

**TPU (JAX/Flax only):**
- `v5e-1x1`, `v5e-2x2`, `v5e-2x4`

## Selection by Model Size

| Model Parameters | Recommended Flavor | Notes |
|------------------|--------------------|-------|
| <1B | `t4-small` | 16GB VRAM sufficient |
| 1-3B | `t4-medium` or `a10g-small` | Quantized fits T4 |
| 3-7B | `a10g-small` or `a10g-large` | 24GB VRAM |
| 7-13B | `a10g-large` or `a100-large` | May need quantization on A10G |
| 13B+ | `a100-large` | 40GB VRAM for full precision |
| 30B+ | Multi-GPU (`a10g-largex4`) | Distributed inference required |

**Memory estimates:**
- Inference: ~2-4GB per billion parameters (FP16)
- Training (full): ~20GB per billion parameters
- Training (LoRA): ~4GB per billion parameters

## Selection by Workload

| Workload | Recommended | Rationale |
|----------|-------------|-----------|
| Quick test / debug | `cpu-basic` | Cheapest, verify logic first |
| Data processing (Pandas/Polars) | `cpu-upgrade` | CPU-bound, more RAM |
| Batch inference (small model) | `t4-small` | Cost-effective for small models |
| Batch inference (medium model) | `a10g-large` | Balance of cost and performance |
| Batch inference (large model) | `a100-large` | Required for 13B+ |
| Synthetic data generation | `a10g-small` | Good balance for generation |
| Experiments / prototyping | `a10g-small` | Versatile GPU option |

## Cost Optimization

1. **Start small** — Use `cpu-basic` or `t4-small` for initial testing
2. **Set tight timeouts** — Avoid idle GPU time (add 20-30% buffer, not more)
3. **Use checkpoints** — Save intermediate results for long jobs
4. **Right-size hardware** — Don't use A100 when T4 suffices
5. **Cost formula:** `Total Cost = Hours x $/hr`
