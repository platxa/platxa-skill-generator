# YAML Metadata for Paper Linking

## Model Card Frontmatter

When linking a paper to a model, the README.md must contain YAML frontmatter with proper metadata. The Hub uses this to extract arXiv IDs and create automatic tags.

### Minimal Model Card

```yaml
---
language:
  - en
license: apache-2.0
tags:
  - text-generation
  - transformers
library_name: transformers
---

# Model Name

Based on [Our Paper](https://arxiv.org/abs/2301.12345).
```

The Hub extracts `2301.12345` from the arXiv URL and adds `arxiv:2301.12345` as a tag.

### Model Card with Citation

```yaml
---
language:
  - en
license: apache-2.0
tags:
  - text-generation
  - transformers
  - llm
library_name: transformers
---

# Model Name

This model implements the approach described in [Paper Title](https://arxiv.org/abs/2301.12345).

## Citation

If you use this model, please cite:

```bibtex
@article{doe2023paper,
  title={Paper Title},
  author={Doe, Jane and Smith, John},
  journal={arXiv preprint arXiv:2301.12345},
  year={2023}
}
```
```

### Multi-Paper Model Card

Link multiple papers by including multiple arXiv URLs:

```yaml
---
language:
  - en
license: mit
tags:
  - text-classification
  - bert
---

# Model Name

Built on [BERT](https://arxiv.org/abs/1810.04805) and
fine-tuned with techniques from [LoRA](https://arxiv.org/abs/2106.09685).
```

Both papers generate separate tags: `arxiv:1810.04805` and `arxiv:2106.09685`.

## Dataset Card Frontmatter

### Standard Dataset Card

```yaml
---
language:
  - en
license: cc-by-4.0
task_categories:
  - text-generation
  - question-answering
size_categories:
  - 10K<n<100K
---

# Dataset Name

Dataset introduced in [Our Paper](https://arxiv.org/abs/2301.12345).

See the [paper page](https://huggingface.co/papers/2301.12345) for details.
```

## Tag Format

The Hub generates tags in the format `arxiv:PAPER_ID`:

| arXiv URL | Generated Tag |
|-----------|--------------|
| `https://arxiv.org/abs/2301.12345` | `arxiv:2301.12345` |
| `https://arxiv.org/abs/2106.09685` | `arxiv:2106.09685` |
| `https://arxiv.org/pdf/2301.12345` | `arxiv:2301.12345` |

Tags are clickable -- clicking them navigates to the Paper Page showing all linked artifacts.

## Frontmatter Fields Reference

| Field | Required | Example |
|-------|----------|---------|
| `language` | Recommended | `["en"]` |
| `license` | Recommended | `apache-2.0`, `mit`, `cc-by-4.0` |
| `tags` | Optional | `["text-generation", "llm"]` |
| `library_name` | Optional | `transformers`, `diffusers` |
| `task_categories` | Datasets only | `["text-generation"]` |
| `size_categories` | Datasets only | `["10K<n<100K"]` |
