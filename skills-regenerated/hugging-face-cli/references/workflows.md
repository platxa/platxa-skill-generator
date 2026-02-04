# HF CLI Workflows and Patterns

## Model Workflows

### Download for Local Inference

```bash
# To cache (returns cache path)
hf download meta-llama/Llama-3.2-1B-Instruct

# To local directory for deployment
hf download meta-llama/Llama-3.2-1B-Instruct --local-dir ./model

# Only safetensors format
hf download meta-llama/Llama-3.2-1B-Instruct --include "*.safetensors" --exclude "*.bin"

# Get path for use in scripts
MODEL_PATH=$(hf download gpt2 --quiet)
```

### Publish a Fine-Tuned Model

```bash
hf repo create my-username/my-model --private
hf upload my-username/my-model ./output . --commit-message="Initial release"
hf repo tag create my-username/my-model v1.0
```

### Download Specific Revision

```bash
hf download stabilityai/stable-diffusion-xl-base-1.0 --revision fp16
hf download bigcode/starcoder2 --revision refs/pr/42
```

## Dataset Workflows

### Download and Use Dataset

```bash
hf download HuggingFaceH4/ultrachat_200k --repo-type dataset
hf download tatsu-lab/alpaca --repo-type dataset --local-dir ./data/alpaca
```

### Publish a Dataset

```bash
hf repo create my-username/my-dataset --repo-type dataset --private
hf upload my-username/my-dataset ./data . --repo-type dataset --commit-message="Add training data"
```

### Contribute via Pull Request

```bash
hf upload community/shared-dataset ./contribution /contributed --repo-type dataset --create-pr
```

## Space Workflows

### Create and Deploy a Gradio Space

```bash
hf repo create my-username/my-app --repo-type space --space-sdk gradio
hf upload my-username/my-app . . --repo-type space --exclude="__pycache__/*"
```

### Sync Local Development with Space

```bash
# Delete removed files, exclude logs
hf upload my-username/my-app . . --repo-type space --exclude="/logs/*" --delete="*"

# Auto-sync every 5 minutes during development
hf upload my-username/my-app . . --repo-type space --every=5
```

## CI/CD Patterns

### Non-Interactive Authentication

```bash
hf auth login --token $HF_TOKEN --add-to-git-credential
hf auth whoami
```

### Quiet Mode for Scripting

```bash
MODEL_PATH=$(hf download gpt2 --quiet)
UPLOAD_URL=$(hf upload my-model ./output . --quiet)
```

### Automated Model Publishing Pipeline

```bash
hf auth login --token $HF_TOKEN
hf repo create $ORG/$MODEL_NAME --private --exist-ok
hf upload $ORG/$MODEL_NAME ./output . --commit-message="Release v${VERSION}"
hf repo tag create $ORG/$MODEL_NAME "v${VERSION}"
```

## Compute Workflows

### GPU Training Job

```bash
hf jobs run --flavor a100-large --timeout 4h \
  --secrets HF_TOKEN -e WANDB_TOKEN=$WANDB_TOKEN \
  pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel python train.py
hf jobs ps && hf jobs logs <job_id>
```

### UV Script Execution

```bash
hf jobs uv run --with transformers --with torch --flavor t4-small train.py
```

### Scheduled Data Pipeline

```bash
hf jobs scheduled run "0 0 * * *" --timeout 2h --secrets HF_TOKEN \
  python:3.12 python daily_pipeline.py
hf jobs scheduled ps
```

### Detached Job with Monitoring

```bash
JOB_ID=$(hf jobs run --detach --flavor a10g-small my-image python eval.py)
hf jobs logs $JOB_ID
hf jobs stats $JOB_ID
```

## Cache Management Patterns

### Inspect and Clean Cache

```bash
# Overview
hf cache ls

# Find large items
hf cache ls --sort size:desc --limit 5

# Remove old unused models
hf cache rm $(hf cache ls --filter "accessed>6m" -q) -y

# Prune detached revisions
hf cache prune -y
```

### Verify Downloaded Files

```bash
hf cache verify deepseek-ai/DeepSeek-OCR
hf cache verify my-model --local-dir ./model --fail-on-missing-files
```

## Endpoint Deployment

### Deploy from Catalog

```bash
hf endpoints catalog deploy --repo meta-llama/Llama-3.2-1B-Instruct --name my-llama
hf endpoints describe my-llama
```

### Full Custom Deployment

```bash
hf endpoints deploy my-endpoint \
  --repo gpt2 \
  --framework pytorch \
  --accelerator gpu \
  --instance-size x4 \
  --instance-type nvidia-a10g \
  --region us-east-1 \
  --vendor aws
```

### Scale and Lifecycle

```bash
hf endpoints pause my-endpoint       # Stop billing
hf endpoints resume my-endpoint      # Resume serving
hf endpoints scale-to-zero my-endpoint  # Scale down when idle
hf endpoints delete my-endpoint --yes   # Permanent removal
```

## Error Recovery

### Timeout on Large Downloads

```bash
export HF_HUB_DOWNLOAD_TIMEOUT=60
hf download large-model/weights --local-dir ./model
```

### Resume Interrupted Large Uploads

```bash
# upload-large-folder automatically resumes from last checkpoint
hf upload-large-folder my-username/my-large-model ./model_dir
```

### Offline Workflow

```bash
# Pre-download while online
hf download my-model

# Later, work offline
export HF_HUB_OFFLINE=1
MODEL_PATH=$(hf download my-model --quiet)  # Uses cache
```
