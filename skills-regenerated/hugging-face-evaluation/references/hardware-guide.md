# Hardware Selection Guide

GPU hardware selection for running evaluations on Hugging Face Jobs.

## Hardware Flavors

| Flavor | GPU | VRAM | vCPU | RAM | Cost/hr |
|--------|-----|------|------|-----|---------|
| `cpu-basic` | None | -- | 2 | 16GB | ~$0.10 |
| `t4-small` | 1x T4 | 16GB | 4 | 15GB | ~$0.75 |
| `t4-medium` | 1x T4 | 16GB | 8 | 30GB | ~$1.50 |
| `l4x1` | 1x L4 | 24GB | 8 | 30GB | ~$2.00 |
| `a10g-small` | 1x A10G | 24GB | 4 | 15GB | ~$2.50 |
| `a10g-large` | 4x A10G | 96GB | 12 | 142GB | ~$5.00 |
| `a100-large` | 2x A100 | 160GB | 24 | 200GB | ~$10-20 |

## Selection by Model Size

| Model Parameters | Minimum VRAM | Recommended Flavor |
|-----------------|-------------|-------------------|
| < 1B | 4GB | `cpu-basic` (slow) or `t4-small` |
| 1-3B | 8GB | `t4-small` |
| 3-7B | 16GB | `a10g-small` |
| 7-13B | 24GB | `a10g-small` (quantized) or `a10g-large` |
| 13-34B | 48-96GB | `a10g-large` with tensor parallelism |
| 34-70B | 160GB+ | `a100-large` with tensor parallelism |

## VRAM Estimation

Approximate VRAM for inference (fp16):
- **Formula:** `parameters_in_billions * 2 GB` (fp16) + overhead
- 7B model: ~14GB + 2GB overhead = 16GB minimum
- 13B model: ~26GB + 4GB overhead = 30GB minimum
- 70B model: ~140GB + 10GB overhead = 150GB minimum

## Cost Optimization

- Use `cpu-basic` for API-based evaluations (inspect-ai with inference providers)
- Use `--limit N` during testing before full evaluation runs
- Quantized models (AWQ, GPTQ) reduce VRAM by ~50% but may affect scores
- Time estimation: ~1-5 samples/second on GPU (varies by model and task)
- Add 30% buffer to timeout estimates

## Multi-GPU Configuration

For models requiring tensor parallelism:
```bash
# lighteval: automatic with a10g-large/a100-large
# inspect-ai: explicit flag
uv run scripts/inspect_vllm_uv.py --tensor-parallel-size 4 --model large-model
```

`--tensor-parallel-size` must match the number of available GPUs in the selected flavor.
