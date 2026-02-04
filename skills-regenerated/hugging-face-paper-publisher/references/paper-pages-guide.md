# Hugging Face Paper Pages

## How Paper Pages Work

Paper Pages are auto-generated pages on Hugging Face Hub for arXiv papers. Each page aggregates all models, datasets, and Spaces that cite the paper.

**URL format**: `https://huggingface.co/papers/{arxiv-id}`

### Page Contents

A Paper Page displays:
- **Title and authors** (pulled from arXiv metadata)
- **Abstract** (from arXiv)
- **Linked models** (repositories with `arxiv:PAPER_ID` tag)
- **Linked datasets** (repositories citing the paper)
- **Linked Spaces** (demos referencing the paper)
- **Discussion thread** (community comments)
- **Daily Papers** (if selected by the community)

### Indexing Process

1. A user visits `https://huggingface.co/papers/{arxiv-id}`
2. Hub checks its database for the paper
3. If not found, Hub fetches metadata from the arXiv API
4. Paper Page is created with title, authors, and abstract
5. Hub scans all repositories for matching `arxiv:PAPER_ID` tags
6. Linked artifacts appear on the page

Papers are also indexed when:
- A repository README containing an arXiv URL is pushed
- The `paper_manager.py index` command triggers a page visit
- A user submits the paper to the Daily Papers feed

### Discovery

Papers are discoverable through:
- **Search**: `https://huggingface.co/papers?search=transformer+attention`
- **Daily Papers**: `https://huggingface.co/papers` (curated daily feed)
- **Tag filters**: Click any `arxiv:PAPER_ID` tag on a model/dataset
- **Author profiles**: Papers tab on verified author profiles
- **Direct URL**: `https://huggingface.co/papers/{arxiv-id}`

### Authorship Verification

Authors can claim papers to link them to their HF profile:

1. Visit the Paper Page
2. Find your name in the author list
3. Click "Claim authorship"
4. HF admin team verifies against arXiv author records
5. Verified papers appear on your profile's Papers tab

**Tips for faster verification:**
- Use the same email as your arXiv account
- Ensure your HF profile name matches the paper author name
- Claims from institutional emails are prioritized

### Visibility Controls

After claiming authorship:
- Papers automatically appear on your HF profile
- Toggle individual paper visibility in Settings > Papers
- Hidden papers remain on the Paper Page but not on your profile

### API Access

Paper metadata is accessible via the HF Hub API:

```python
from huggingface_hub import HfApi

api = HfApi()

# Search models by paper tag
models = api.list_models(filter="arxiv:2301.12345")

# Search datasets by paper tag
datasets = api.list_datasets(filter="arxiv:2301.12345")
```

### Limitations

- Only arXiv papers are supported (no DOI, conference proceedings, or journals)
- Paper metadata updates lag behind arXiv by a few hours
- Authorship claims require manual admin review
- The paper must have a valid arXiv ID in the standard format (YYMM.NNNNN)
