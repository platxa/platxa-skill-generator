# Reliability Principles for Training Jobs

Derived from real production failures. Follow these to achieve 95%+ job success rate.

## Principle 1: Verify Before Use

Never assume repos, datasets, or resources exist. Verify first.

```python
dataset_search({"query": "dataset-name", "author": "author-name", "limit": 5})
hub_repo_details(["author/dataset-name"], repo_type="dataset")
hub_repo_details(["org/model-name"], repo_type="model")
```

**Prevents**: Non-existent datasets, typos in names, old/moved repos.

## Principle 2: Reliability Over Performance

Default to what succeeds, not what's theoretically fastest.

- Use `optim="adamw_torch"` (always works) over experimental optimizers
- Avoid `torch_compile=True` (fails on T4/A10G GPUs)
- Use CMake (not make) for building tools
- Use `fp16=True` for stable mixed precision

## Principle 3: Atomic, Self-Contained Scripts

Scripts must work as complete units. Don't remove deps to "simplify."

```python
# /// script
# dependencies = [
#     "trl>=0.12.0", "peft>=0.7.0", "torch>=2.0.0",
#     "accelerate>=0.24.0", "huggingface_hub>=0.20.0",
#     "sentencepiece>=0.1.99", "protobuf>=3.20.0",
# ]
# ///
```

## Principle 4: Clear Error Context

Wrap subprocess calls with try/except. Show stdout/stderr on failure. Validate environment variables early with clear error messages.

## Principle 5: Test on Known-Good Inputs

Before production, test with: `trl-lib/Capybara` (dataset) + `Qwen/Qwen2.5-0.5B` (model).

## Pre-Flight Checklist

- [ ] Verified all repos/datasets exist
- [ ] Tested with known-good inputs if new code
- [ ] All dependencies in PEP 723 header
- [ ] Timeout > expected runtime + 30% buffer
- [ ] Hub push configured with HF_TOKEN
- [ ] Clear error handling included
