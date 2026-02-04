# Evaluation Frameworks

Two evaluation frameworks are supported: lighteval (HuggingFace) and inspect-ai (UK AI Safety Institute). Each has distinct strengths and usage patterns.

## lighteval

HuggingFace's evaluation library supporting Open LLM Leaderboard tasks.

**Backends:** vLLM (GPU, fastest), accelerate (GPU, HF Transformers), nanotron (distributed)

**Task format:** `suite|task|num_fewshot`
- `leaderboard|mmlu|5` -- MMLU 5-shot (Open LLM Leaderboard)
- `leaderboard|gsm8k|5` -- GSM8K math reasoning
- `leaderboard|arc_challenge|25` -- ARC-Challenge
- `lighteval|hellaswag|0` -- HellaSwag zero-shot
- `bigbench|abstract_narrative_understanding|0` -- BigBench tasks

**Full task list:** `https://github.com/huggingface/lighteval/blob/main/examples/tasks/all_tasks.txt`

**Key flags:**
- `--backend vllm` (default) or `--backend accelerate`
- `--use-chat-template` for instruction-tuned models only
- `--tasks` accepts comma-separated list for multiple benchmarks
- `--max-samples` to limit evaluation size during testing

## inspect-ai

UK AI Safety Institute's evaluation framework with strong support for complex reasoning tasks.

**Backends:** HF inference providers (API), vLLM (local GPU), HF Transformers (local)

**Tasks:** Standard string identifiers
- `mmlu`, `gsm8k`, `hellaswag`, `arc_challenge`
- `truthfulqa`, `winogrande`, `humaneval`

**Key flags:**
- `--model hf-inference-providers/model-id` for API-based evaluation
- `--sandbox local` for HF Jobs (no Docker available)
- `--limit N` to cap sample count
- `--tensor-parallel-size N` for multi-GPU with vLLM

## Comparison

| Feature | lighteval | inspect-ai |
|---------|-----------|------------|
| Task format | `suite\|task\|shots` | Simple string |
| Leaderboard tasks | Native support | Via inspect-evals |
| vLLM backend | Built-in | Via model prefix |
| API evaluation | No | Yes (inference providers) |
| Multi-GPU | Via accelerate | Via tensor parallelism |
| Custom tasks | Python task definitions | inspect Task objects |
| Best for | Open LLM Leaderboard | Safety/reasoning evals |

## When to Use Which

- **lighteval**: Reproducing Open LLM Leaderboard scores, standard benchmarks on custom models
- **inspect-ai with providers**: Evaluating models with API endpoints (no GPU needed)
- **inspect-ai with vLLM**: Complex evals requiring sandbox environments, safety benchmarks
