# HF CLI Workflows & Examples

## Model Workflows

### Download for Local Inference
```bash
hf download meta-llama/Llama-3.2-1B-Instruct                          # To cache
hf download meta-llama/Llama-3.2-1B-Instruct --local-dir ./models     # To directory
hf download meta-llama/Llama-3.2-1B-Instruct --include "*.safetensors" --exclude "*.bin"
MODEL_PATH=$(hf download gpt2 --quiet)                                 # Get path for scripts
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

```bash
# Download
hf download HuggingFaceH4/ultrachat_200k --repo-type dataset
hf download tatsu-lab/alpaca --repo-type dataset --local-dir ./data/alpaca

# Upload
hf repo create my-username/my-dataset --repo-type dataset --private
hf upload my-username/my-dataset ./data . --repo-type dataset --commit-message="Add data"

# Contribute via PR
hf upload community/shared-dataset ./contribution /contributed --repo-type dataset --create-pr
```

## Space Workflows

```bash
# Create and deploy
hf repo create my-username/my-app --repo-type space --space_sdk gradio
hf upload my-username/my-app . . --repo-type space --exclude="__pycache__/*"

# Sync local changes (delete removed remote files)
hf upload my-username/my-app . . --repo-type space --exclude="/logs/*" --delete="*"

# Auto-upload during development
hf upload my-username/my-app . . --repo-type space --every=5
```

## Automation Patterns

### CI/CD Authentication
```bash
hf auth login --token $HF_TOKEN --add-to-git-credential
hf auth whoami
```

### Quiet Mode for Scripting
```bash
MODEL_PATH=$(hf download gpt2 --quiet)
UPLOAD_URL=$(hf upload my-model ./output . --quiet)
```

### CI/CD Model Publishing
```bash
hf auth login --token $HF_TOKEN
hf repo create $ORG/$MODEL_NAME --private || true
hf upload $ORG/$MODEL_NAME ./output . --commit-message="Release v${VERSION}"
hf repo tag create $ORG/$MODEL_NAME "v${VERSION}"
```

### GPU Training Job
```bash
hf jobs run --flavor a100-large pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel \
  --secrets HF_TOKEN -e WANDB_API_KEY=$WANDB_KEY python train.py
hf jobs ps && hf jobs logs <job_id>
```

### Scheduled Data Pipeline
```bash
hf jobs scheduled run "0 0 * * *" python:3.12 --secrets HF_TOKEN python -c "..."
hf jobs scheduled ps
```
