# Training Guide

This guide covers fine-tuning models using LoRA (Low-Rank Adaptation) and QLoRA (Quantized LoRA) for the Agent Skill Adapter.

## Overview

The Agent Skill Adapter uses Parameter-Efficient Fine-Tuning (PEFT) methods to adapt large language models to follow Agent Skills:

- **LoRA**: Low-rank adaptation that trains small adapter layers
- **QLoRA**: LoRA with quantization for reduced memory usage

## Prerequisites

- Python 3.12+ with `uv` installed
- Backend dependencies installed: `cd backend && uv sync`
- Base model downloaded (see [Model Download Guide](./02_model_download.md))
- GPU with sufficient VRAM (16GB+ recommended for 7B models)

## Environment Setup

1. **Configure Environment Variables**

Create or update `.env` with training configuration:

```bash
# Model configuration
SKILL_ADAPTER_MODEL=Qwen/Qwen3-8B
SKILL_ADAPTER_ADAPTER=lora  # or qlora
SKILL_ADAPTER_QUANT_BITS=4

# Training hyperparameters
SKILL_ADAPTER_LEARNING_RATE=2e-4
SKILL_ADAPTER_BATCH_SIZE=4
SKILL_ADAPTER_GRADIENT_ACCUMULATION_STEPS=4
SKILL_ADAPTER_NUM_EPOCHS=3
SKILL_ADAPTER_MAX_SEQ_LENGTH=2048

# LoRA configuration
SKILL_ADAPTER_LORA_R=16
SKILL_ADAPTER_LORA_ALPHA=32
SKILL_ADAPTER_LORA_DROPOUT=0.05
```

2. **Verify GPU Availability**

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## Starting a Training Job

Training jobs are managed via the FastAPI backend.

### Via API

Send a POST request to start training:

```bash
curl -X POST http://localhost:8000/api/training/start \
  -H "Content-Type: application/json" \
  -d '{
    "skill_path": "/path/to/SKILL.md",
    "adapter_type": "lora",
    "num_epochs": 3,
    "learning_rate": 2e-4,
    "batch_size": 4
  }'
```

Response:

```json
{
  "job_id": "train-abc123",
  "status": "queued",
  "created_at": "2026-02-07T10:30:00Z"
}
```

### Via Frontend

1. Navigate to `http://localhost:5173`
2. Go to **Training** tab
3. Upload a SKILL.md file
4. Configure training parameters
5. Click **Start Training**

## Monitoring Training Progress

### Check Job Status

```bash
curl http://localhost:8000/api/training/{job_id}/status
```

Response:

```json
{
  "job_id": "train-abc123",
  "status": "running",
  "progress": 0.45,
  "current_epoch": 2,
  "total_epochs": 3,
  "loss": 0.234,
  "started_at": "2026-02-07T10:30:05Z"
}
```

### View Training Logs

```bash
curl http://localhost:8000/api/training/{job_id}/logs
```

### Monitor via Frontend

The frontend dashboard displays:
- Real-time training progress
- Loss curves
- Learning rate schedule
- GPU utilization
- Estimated time remaining

## Training Configuration

### LoRA vs QLoRA

**LoRA** (Low-Rank Adaptation):
- Trains small adapter matrices
- Requires full model precision (bf16/fp16)
- Higher VRAM usage (~16GB for 7B models)
- Faster training speed

**QLoRA** (Quantized LoRA):
- Quantizes base model to 4-bit or 8-bit
- Trains adapters in higher precision
- Lower VRAM usage (~8GB for 7B models)
- Slightly slower training

Choose based on available GPU memory:
- **16GB+ VRAM**: Use LoRA for best quality
- **8-16GB VRAM**: Use QLoRA with 4-bit quantization

### Hyperparameter Guidelines

| Parameter | LoRA Default | QLoRA Default | Notes |
|-----------|--------------|---------------|-------|
| `learning_rate` | `2e-4` | `2e-4` | Lower for stability |
| `lora_r` | `16` | `16` | Rank of adapter matrices |
| `lora_alpha` | `32` | `32` | Scaling factor (2x `lora_r`) |
| `lora_dropout` | `0.05` | `0.05` | Regularization |
| `batch_size` | `4` | `4` | Per-device batch size |
| `gradient_accumulation_steps` | `4` | `4` | Effective batch size = 16 |
| `num_epochs` | `3` | `3` | Number of training passes |
| `max_seq_length` | `2048` | `2048` | Maximum sequence length |

## Checkpoints

Training checkpoints are saved periodically:

### Checkpoint Location

```bash
./checkpoints/train-{job_id}/
├── checkpoint-100/
│   ├── adapter_model.bin
│   ├── adapter_config.json
│   └── optimizer.pt
├── checkpoint-200/
└── final/
```

### Loading Checkpoints

Checkpoints can be loaded for:
- Resuming interrupted training
- Inference with fine-tuned model
- Further fine-tuning

Example:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-8B")
model = PeftModel.from_pretrained(base_model, "./checkpoints/train-abc123/final")
```

## Post-Training Evaluation

After training completes, evaluate the model:

```bash
curl -X POST http://localhost:8000/api/training/{job_id}/evaluate
```

This will:
1. Load the fine-tuned model
2. Run evaluation on held-out examples
3. Compute metrics (accuracy, BLEU, perplexity)
4. Generate a report

## Troubleshooting

### Out of Memory (OOM)

If training crashes with OOM errors:

1. **Reduce batch size**:
   ```bash
   SKILL_ADAPTER_BATCH_SIZE=2
   ```

2. **Use gradient accumulation**:
   ```bash
   SKILL_ADAPTER_GRADIENT_ACCUMULATION_STEPS=8
   ```

3. **Switch to QLoRA**:
   ```bash
   SKILL_ADAPTER_ADAPTER=qlora
   SKILL_ADAPTER_QUANT_BITS=4
   ```

4. **Reduce sequence length**:
   ```bash
   SKILL_ADAPTER_MAX_SEQ_LENGTH=1024
   ```

### Poor Training Loss

If loss doesn't decrease:

1. **Check learning rate**: Try lower values (1e-4, 5e-5)
2. **Verify data quality**: Ensure SKILL.md is well-formatted
3. **Increase LoRA rank**: Try `lora_r=32`
4. **Check for overfitting**: Monitor validation loss

### Slow Training

To speed up training:

1. **Use Flash Attention**: Enabled by default in recent versions
2. **Increase batch size**: If VRAM allows
3. **Use mixed precision**: Enabled by default (bf16)
4. **Enable gradient checkpointing**: Trades compute for memory

## Next Steps

- [Model Serving Guide](./03_model_serving.md) — Deploy the fine-tuned model
- [Docker Deployment](./05_docker_deployment.md) — Containerize training workflows
