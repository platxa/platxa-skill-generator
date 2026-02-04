# Saving Results to Hugging Face Hub

**Job environments are ephemeral. ALL results lost when job ends unless persisted.**

## Required Configuration

Job config must include: `"secrets": {"HF_TOKEN": "$HF_TOKEN"}`
Script must verify: `assert "HF_TOKEN" in os.environ, "HF_TOKEN required!"`

## Persistence Methods

### 1. Push to Hub (Recommended)

```python
# Models
model.push_to_hub("username/model-name", token=os.environ["HF_TOKEN"])

# Datasets
dataset.push_to_hub("username/dataset-name", token=os.environ["HF_TOKEN"])

# Arbitrary files
from huggingface_hub import HfApi
api = HfApi(token=os.environ.get("HF_TOKEN"))
api.upload_file(
    path_or_fileobj="results.json",
    path_in_repo="results.json",
    repo_id="username/results",
    repo_type="dataset"
)
```

### 2. External Storage

```python
# S3
import boto3
boto3.client('s3').upload_file('results.json', 'bucket', 'results.json')

# API endpoint
import requests
requests.post("https://your-api.com/results", json=results)
```

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
data = {"text": ["Sample 1", "Sample 2"]}
Dataset.from_dict(data).push_to_hub("username/my-dataset")
print("Done!")
""",
    "flavor": "cpu-basic",
    "timeout": "30m",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

## Checklist

- [ ] `secrets={"HF_TOKEN": "$HF_TOKEN"}` in job config
- [ ] Script asserts token exists
- [ ] Push code included and tested
- [ ] Repository name doesn't conflict
- [ ] Token has write permissions
