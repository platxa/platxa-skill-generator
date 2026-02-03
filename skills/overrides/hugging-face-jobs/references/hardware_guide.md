# Hardware Selection Guide

## Available Flavors

**CPU:** `cpu-basic` (testing), `cpu-upgrade` (data processing)

**GPU (Single):**
| Flavor | GPU | VRAM | Best For |
|--------|-----|------|----------|
| `t4-small` | T4 | 16GB | <1B models, demos |
| `t4-medium` | T4 | 16GB | 1-3B models |
| `l4x1` | L4 | 24GB | 3-7B efficient |
| `a10g-small` | A10G | 24GB | 3-7B production |
| `a10g-large` | A10G | 24GB | 7-13B models |
| `a100-large` | A100 | 40GB | 13B+ models |

**GPU (Multi):** `l4x4` (96GB), `a10g-largex2` (48GB), `a10g-largex4` (96GB)
**TPU:** `v5e-1x1`, `v5e-2x2`, `v5e-2x4` (JAX/Flax workloads)

## Selection by Workload

| Workload | Recommended | Budget Estimate |
|----------|-------------|-----------------|
| Testing | `cpu-basic` | ~$0.03/15min |
| Data processing | `cpu-upgrade` | ~$0.50/hr |
| Batch inference (small) | `t4-small` | ~$1/hr |
| Batch inference (medium) | `a10g-large` | ~$5/hr |
| Batch inference (large) | `a100-large` | ~$10/hr |
| Experiments | `a10g-small` | ~$3.50/hr |

## By Model Size

- **<1B params:** `t4-small` (16GB VRAM)
- **1-3B:** `t4-medium` or `a10g-small`
- **3-7B:** `a10g-small` or `a10g-large`
- **7-13B:** `a10g-large` or `a100-large`
- **13B+:** `a100-large` or multi-GPU

**Memory estimate:** Inference ~2-4GB per billion params. Training ~20GB (full) or ~4GB (LoRA) per billion.

## Cost Optimization

1. Start small (cpu-basic/t4-small) for testing
2. Set appropriate timeouts (avoid idle GPU time)
3. Use checkpoints for long jobs
4. Choose right hardware (don't over-provision)
5. `Total Cost = Hours × $/hr`
