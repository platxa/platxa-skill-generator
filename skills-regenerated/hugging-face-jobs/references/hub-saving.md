# Saving Results to Hugging Face Hub

**Job environments are ephemeral. ALL results are lost when the job ends unless explicitly persisted.**

## Required Configuration

Every job that pushes results must include:

1. **Job config:** `"secrets": {"HF_TOKEN": "$HF_TOKEN"}`
2. **Script assertion:** `assert "HF_TOKEN" in os.environ, "HF_TOKEN required!"`

## Method 1: Push to Hub (Recommended)

### Models

```python
model.push_to_hub("username/model-name", token=os.environ["HF_TOKEN"])
tokenizer.push_to_hub("username/model-name", token=os.environ["HF_TOKEN"])
```

### Datasets

```python
from datasets import Dataset
dataset = Dataset.from_dict({"text": results})
dataset.push_to_hub("username/dataset-name", token=os.environ["HF_TOKEN"])
```

### Arbitrary Files

```python
from huggingface_hub import HfApi
api = HfApi(token=os.environ.get("HF_TOKEN"))

# Single file
api.upload_file(
    path_or_fileobj="results.json",
    path_in_repo="results.json",
    repo_id="username/results",
    repo_type="dataset"
)

# Entire directory
api.upload_folder(
    folder_path="./output",
    repo_id="username/results",
    repo_type="dataset"
)
```

## Method 2: External Storage

```python
# S3
import boto3
boto3.client('s3').upload_file('results.json', 'bucket', 'key/results.json')

# HTTP API
import requests
requests.post("https://your-api.com/results", json=results)
```

Provide cloud credentials via `secrets` parameter (same as HF_TOKEN).

## Complete Example

```python
hf_jobs("uv", {
    "script": """
# /// script
# dependencies = ["datasets", "huggingface-hub"]
# ///
import os
from datasets import Dataset

assert "HF_TOKEN" in os.environ, "HF_TOKEN required!"

data = {"text": ["Sample 1", "Sample 2"], "label": [0, 1]}
ds = Dataset.from_dict(data)
ds.push_to_hub("username/my-dataset", token=os.environ["HF_TOKEN"])
print("Dataset pushed successfully!")
""",
    "flavor": "cpu-basic",
    "timeout": "30m",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

## Persistence Checklist

- [ ] `secrets: {"HF_TOKEN": "$HF_TOKEN"}` in job config
- [ ] Script asserts `"HF_TOKEN" in os.environ`
- [ ] Push/upload code executes before script exits
- [ ] Target repository name does not conflict with existing repos
- [ ] Token has write permissions
- [ ] Error handling wraps push operations with clear error messages
