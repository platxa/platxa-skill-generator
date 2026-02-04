---
name: hugging-face-paper-publisher
description: Guide for publishing and managing research papers on Hugging Face Hub. Covers paper indexing from arXiv, linking papers to models and datasets via YAML metadata, claiming authorship, managing paper visibility, and creating markdown research articles with professional templates.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
metadata:
  version: "1.0.0"
  author: platxa
  tags:
    - ml
    - research
    - hugging-face
    - papers
    - arxiv
    - guide
  provenance:
    upstream_source: hugging-face-paper-publisher
    upstream_sha: "c0e08fdaa8ed6929110c97d1b867d101fd70218f"
    regenerated_at: "2026-02-04T18:00:00Z"
    generator_version: "1.0.0"
    intent_confidence: 0.8
---

# Hugging Face Paper Publisher

Publish research papers on Hugging Face Hub, link them to models and datasets, and manage authorship.

## Overview

Hugging Face Hub hosts Paper Pages -- dedicated pages for research papers that aggregate all linked models, datasets, and Spaces citing a paper. This skill guides users through the full lifecycle: indexing papers from arXiv, linking them to Hub repositories via YAML metadata, claiming authorship, and generating markdown research articles.

**Use this skill when users want to:**
- Index a paper on Hugging Face from its arXiv ID
- Add paper citations to model or dataset README metadata
- Claim or verify authorship on published papers
- Create research articles from markdown templates
- Manage which papers appear on their HF profile

**Prerequisites:**
- Hugging Face account with a write-access token (`HF_TOKEN` env variable)
- Python 3.10+ with `huggingface_hub`, `pyyaml`, `requests` packages
- arXiv paper IDs for papers to be published

## Learning Path

### Level 1: Paper Indexing

Papers are indexed on Hugging Face by visiting their Paper Page URL. The Hub automatically creates a page when any user first accesses `https://huggingface.co/papers/{arxiv-id}`.

**Index a paper programmatically:**

```bash
python3 scripts/paper_manager.py index --arxiv-id "2301.12345"
```

This checks whether the paper exists on HF. If not indexed yet, it provides the URL to visit for automatic indexing. The Hub pulls metadata (title, authors, abstract) directly from the arXiv API.

**Check if a paper is already indexed:**

```bash
python3 scripts/paper_manager.py check --arxiv-id "2301.12345"
```

**Direct browser access:**
Visit `https://huggingface.co/papers/2301.12345` to trigger indexing and view the Paper Page.

### Level 2: Linking Papers to Repositories

When a model or dataset README contains an arXiv URL, the Hub automatically:
1. Extracts the arXiv ID from the link
2. Adds an `arxiv:PAPER_ID` tag to the repository
3. Shows the repository on the Paper Page under linked artifacts
4. Makes the paper discoverable through Hub search filters

**Link a paper to a model:**

```bash
python3 scripts/paper_manager.py link \
  --repo-id "username/model-name" \
  --repo-type "model" \
  --arxiv-id "2301.12345"
```

**Link to a dataset:**

```bash
python3 scripts/paper_manager.py link \
  --repo-id "username/dataset-name" \
  --repo-type "dataset" \
  --arxiv-id "2301.12345"
```

**Link multiple papers at once:**

```bash
python3 scripts/paper_manager.py link \
  --repo-id "username/model-name" \
  --repo-type "model" \
  --arxiv-ids "2301.12345,2302.67890,2303.11111"
```

The script modifies the repository README to include the arXiv URL and optionally adds a BibTeX citation block. See `references/yaml-metadata.md` for the YAML frontmatter format.

### Level 3: Authorship and Visibility

**Claim authorship on a paper:**

1. Navigate to `https://huggingface.co/papers/{arxiv-id}`
2. Find your name in the author list
3. Click your name and select "Claim authorship"
4. The HF admin team verifies the claim (usually within 24-48 hours)

**Programmatic claim:**

```bash
python3 scripts/paper_manager.py claim \
  --arxiv-id "2301.12345" \
  --email "your.email@institution.edu"
```

**Manage paper visibility on your profile:**

```bash
python3 scripts/paper_manager.py list-my-papers
python3 scripts/paper_manager.py toggle-visibility \
  --arxiv-id "2301.12345" --show true
```

Verified papers appear on your HF profile under the Papers tab. Toggle visibility in account settings to control which papers are public.

## Best Practices

### Do
- Index papers immediately after arXiv publication for early visibility
- Link papers to all related repositories (models, datasets, Spaces)
- Include BibTeX citations in model and dataset cards
- Use institutional email for authorship claims to speed verification
- Add `arxiv:PAPER_ID` tags to repository metadata for discoverability

### Don't
- Skip YAML frontmatter in model/dataset cards (Hub needs it for metadata)
- Use bare arXiv IDs without the full URL (Hub extracts IDs from URLs only)
- Claim authorship on papers where you are not a listed author
- Forget `HF_TOKEN` before running link operations (write access required)

## Common Questions

### Q: How long does authorship verification take?
**A**: The HF admin team typically verifies claims within 24-48 hours. Use an institutional email matching the paper's author affiliations to expedite.

### Q: Can I link non-arXiv papers?
**A**: Paper Pages currently support arXiv papers only. Conference proceedings or journal papers can be referenced in README text, but won't generate a dedicated Paper Page with aggregated artifact views.

### Q: What happens when I link a paper to a model?
**A**: The Hub adds an `arxiv:PAPER_ID` tag to the model. The Paper Page at `hf.co/papers/{id}` shows your model under "Models citing this paper." Users browsing the paper discover your model directly.

### Q: Do I need a paid account?
**A**: No. Paper indexing, linking, and authorship are free features. You only need a write-access token for modifying repository READMEs via the API.

## Examples

### Example 1: Publish New Research End-to-End

```bash
# 1. Index on Hugging Face after arXiv publication
python3 scripts/paper_manager.py index --arxiv-id "2401.15839"

# 2. Link to your trained model
python3 scripts/paper_manager.py link \
  --repo-id "jdoe/llama-finetuned-legal" \
  --repo-type "model" \
  --arxiv-id "2401.15839"

# 3. Link to your training dataset
python3 scripts/paper_manager.py link \
  --repo-id "jdoe/legal-qa-dataset" \
  --repo-type "dataset" \
  --arxiv-id "2401.15839"

# 4. Claim authorship
python3 scripts/paper_manager.py claim \
  --arxiv-id "2401.15839" \
  --email "jane.doe@stanford.edu"
```

### Example 2: Add Paper Reference to Existing Model

```bash
# Check if the paper is already indexed
python3 scripts/paper_manager.py check --arxiv-id "2310.06825"

# Link paper with a custom BibTeX citation
python3 scripts/paper_manager.py link \
  --repo-id "myorg/mistral-7b-instruct" \
  --repo-type "model" \
  --arxiv-id "2310.06825" \
  --citation "@article{jiang2023mistral,
  title={Mistral 7B},
  author={Jiang, Albert Q and Sablayrolles, Alexandre and others},
  journal={arXiv preprint arXiv:2310.06825},
  year={2023}
}"
```

### Example 3: Create a Research Article

```bash
# Generate article from template
python3 scripts/paper_manager.py create \
  --template "standard" \
  --title "Efficient Fine-Tuning with Adapter Layers" \
  --authors "Jane Doe, John Smith" \
  --output "paper.md"

# Available templates: standard, modern, arxiv, ml-report
```

## Workflow Patterns

### Pattern 1: New Paper Publication

```
Write paper -> Submit to arXiv -> Index on HF -> Link to repos -> Claim authorship
```

```bash
python3 scripts/paper_manager.py create --template modern --output paper.md
# (edit paper.md, submit to arXiv, obtain arXiv ID)
python3 scripts/paper_manager.py index --arxiv-id "2401.XXXXX"
python3 scripts/paper_manager.py link --repo-id "user/model" \
  --repo-type model --arxiv-id "2401.XXXXX"
python3 scripts/paper_manager.py claim --arxiv-id "2401.XXXXX" \
  --email "user@institution.edu"
```

### Pattern 2: Link Existing Paper to Multiple Repos

```bash
for repo in "user/model-v1" "user/model-v2" "user/training-data"; do
  repo_type="model"
  [[ "$repo" == *data* ]] && repo_type="dataset"
  python3 scripts/paper_manager.py link \
    --repo-id "$repo" --repo-type "$repo_type" \
    --arxiv-id "2301.12345"
done
```

### Pattern 3: Author Portfolio Management

```bash
python3 scripts/paper_manager.py list-my-papers
python3 scripts/paper_manager.py toggle-visibility \
  --arxiv-id "2301.12345" --show true
python3 scripts/paper_manager.py toggle-visibility \
  --arxiv-id "2205.99999" --show false
```

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Paper not found | arXiv ID not indexed on HF | Visit `hf.co/papers/{id}` to trigger indexing |
| Permission denied | Token lacks write access | Regenerate `HF_TOKEN` with write permissions |
| Invalid YAML | Malformed README frontmatter | Validate YAML syntax before upload |
| Authorship failed | Email mismatch | Use email matching arXiv author records |
| Rate limited | Too many API requests | Wait 60 seconds between batch operations |

## Resources

### References
- `references/yaml-metadata.md` -- Model and dataset card YAML format with examples
- `references/paper-pages-guide.md` -- How Paper Pages work on HF Hub

### Scripts
- `scripts/paper_manager.py` -- CLI tool for all paper operations (index, link, claim, create)

### External
- [Hugging Face Paper Pages](https://huggingface.co/papers)
- [Model Cards Guide](https://huggingface.co/docs/hub/en/model-cards)
- [Dataset Cards Guide](https://huggingface.co/docs/hub/en/datasets-cards)
- [arXiv Submission Help](https://arxiv.org/help/submit)
