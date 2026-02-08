# Model Download Guide

This guide covers downloading the Qwen3-8B model from HuggingFace Hub.

## Prerequisites

- Access to DGX Spark (see [DGX Spark Setup](./01_dgx_spark_setup.md))
- ~14GB of available disk space
- HuggingFace account (optional, for gated models)

## Download Qwen3-8B

Use the `huggingface-cli` tool via `uv run` to download the model:

```bash
uv run huggingface-cli download Qwen/Qwen3-8B
```

This command will:
1. Download all model files (weights, tokenizer, config)
2. Cache them locally at `~/.cache/huggingface`
3. Verify checksums for data integrity

## Download Size

The Qwen3-8B model requires approximately **14GB** of disk space.

## Cache Location

Models are cached at:

```bash
~/.cache/huggingface/hub/models--Qwen--Qwen3-8B
```

This cache is shared across all applications using HuggingFace Transformers, so the model only needs to be downloaded once.

## Verify Download

Check the downloaded model using the cache scanning tool:

```bash
uv run huggingface-cli scan-cache
```

This will show:
- Downloaded models
- Disk usage per model
- Cache locations
- Revision information

Expected output:

```
REPO ID                 REPO TYPE SIZE ON DISK NB FILES REFS
Qwen/Qwen3-8B          model          14.0G        15 main
```

## Authentication (Optional)

If downloading gated or private models, authenticate with HuggingFace:

```bash
uv run huggingface-cli login
```

Enter your HuggingFace access token when prompted.

## Troubleshooting

### Slow Download Speeds

If downloads are slow, consider:
- Using a mirror or CDN (if available)
- Downloading during off-peak hours
- Checking network bandwidth

### Insufficient Disk Space

Check available disk space:

```bash
df -h ~/.cache/huggingface
```

If space is limited, consider:
- Removing unused model caches
- Mounting additional storage
- Using a different cache directory via `HF_HOME` environment variable

### Download Interruption

If the download is interrupted, simply re-run the command. The CLI will resume from where it left off.

## Next Steps

- [Model Serving Guide](./03_model_serving.md) — Deploy TGI to serve the downloaded model
- [Training Guide](./04_training_guide.md) — Fine-tune the model with LoRA/QLoRA
