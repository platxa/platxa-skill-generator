# GGUF Conversion Guide

Convert trained models to GGUF format for llama.cpp, Ollama, LM Studio, and other local inference tools.

## What is GGUF

- Optimized format for CPU/GPU inference with llama.cpp
- Supports quantization (4-bit, 5-bit, 8-bit) to reduce model size
- Compatible with: Ollama, LM Studio, Jan, GPT4All, llama.cpp

## Critical Success Factors

1. **Install build tools FIRST**: `apt-get install build-essential cmake`
2. **Use CMake** (not make) for building the quantize tool
3. **Include ALL dependencies** in PEP 723 (especially `sentencepiece`, `protobuf`)
4. **Verify repos exist** before submitting: `hub_repo_details([MODEL], repo_type="model")`

## Quick Conversion

```python
hf_jobs("uv", {
    "script": "<use scripts/convert_to_gguf.py content>",
    "flavor": "a10g-large",
    "timeout": "45m",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"},
    "env": {
        "ADAPTER_MODEL": "username/my-finetuned-model",
        "BASE_MODEL": "Qwen/Qwen2.5-0.5B",
        "OUTPUT_REPO": "username/my-model-gguf"
    }
})
```

## Conversion Process

1. Load base model + LoRA adapter, merge them
2. Install build tools (gcc, cmake)
3. Clone llama.cpp, install Python deps
4. Convert to FP16 GGUF via `convert_hf_to_gguf.py`
5. Build quantize tool with CMake
6. Create Q4_K_M, Q5_K_M, Q8_0 quantizations
7. Upload all versions + README to Hub

## Quantization Options

| Format | Size | Quality | Use Case |
|--------|------|---------|----------|
| Q4_K_M | ~300MB | Good | **Recommended** balance |
| Q5_K_M | ~350MB | Better | Higher quality |
| Q8_0 | ~500MB | Very High | Near-original |
| F16 | ~1GB | Original | Full precision |

## Hardware and Time

- <1B model: ~15-25 min on A10G
- 1-7B model: ~30-45 min on A10G
- 7B+ model: ~45-60 min on A10G

## Usage

### Ollama
```bash
huggingface-cli download user/model-gguf model-q4_k_m.gguf
echo "FROM ./model-q4_k_m.gguf" > Modelfile
ollama create my-model -f Modelfile
ollama run my-model
```

### llama.cpp
```bash
./llama-cli -m model-q4_k_m.gguf -p "Your prompt"
./llama-cli -m model-q4_k_m.gguf -ngl 32 -p "Your prompt"  # GPU acceleration
```

Complete script: `scripts/convert_to_gguf.py`
