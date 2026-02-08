# Model Serving Guide

This guide covers deploying Text Generation Inference (TGI) to serve the Qwen3-8B model with an OpenAI-compatible API.

## Overview

Text Generation Inference (TGI) is a model serving solution that provides:
- Fast inference with optimized kernels
- OpenAI-compatible API endpoints
- Support for various model architectures
- Health checks and monitoring

**Note**: TGI entered maintenance mode in December 2025. For new deployments, consider using **vLLM** as an alternative, which offers similar features with active development.

## Deployment via Helm

The Agent Skill Adapter uses the InfraCloud Helm chart to deploy TGI on Kubernetes.

### Install TGI Helm Chart

```bash
# Add the InfraCloud Helm repository
helm repo add infracloud https://infracloud-io.github.io/charts
helm repo update

# Install TGI configured for Qwen3-8B
helm install tgi infracloud/text-generation-inference \
  --set model.name="Qwen/Qwen3-8B" \
  --set model.cache="/cache/huggingface" \
  --set resources.limits.nvidia\.com/gpu=1 \
  --namespace skill-adapter \
  --create-namespace
```

### Configuration Options

Key Helm values for TGI deployment:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `model.name` | HuggingFace model ID | `Qwen/Qwen3-8B` |
| `model.cache` | HuggingFace cache directory | `/cache/huggingface` |
| `resources.limits.nvidia.com/gpu` | Number of GPUs | `1` |
| `service.type` | Kubernetes service type | `ClusterIP` or `LoadBalancer` |
| `service.port` | Service port | `80` |

### Verify Deployment

Check TGI pod status:

```bash
kubectl get pods -n skill-adapter
```

View TGI logs:

```bash
kubectl logs -n skill-adapter -l app=text-generation-inference --tail=50 -f
```

## OpenAI-Compatible API

TGI exposes an OpenAI-compatible API with the following endpoints:

### Completions Endpoint

```bash
POST /v1/completions
```

Example request:

```bash
curl -X POST http://tgi-service/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-8B",
    "prompt": "What is the meaning of life?",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Chat Completions Endpoint

```bash
POST /v1/chat/completions
```

Example request:

```bash
curl -X POST http://tgi-service/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-8B",
    "messages": [
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "max_tokens": 150,
    "temperature": 0.7
  }'
```

## Health Checks

TGI provides health check endpoints for monitoring:

### Liveness Probe

```bash
GET /health
```

Returns `200 OK` when the service is alive.

### Readiness Probe

```bash
GET /health
```

Returns `200 OK` when the model is loaded and ready to serve requests.

### Metrics

TGI exposes Prometheus metrics at:

```bash
GET /metrics
```

## Testing the Deployment

### Basic Test Request

```bash
curl -X POST http://tgi-service/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-8B",
    "prompt": "Hello, world!",
    "max_tokens": 10
  }'
```

Expected response:

```json
{
  "id": "cmpl-...",
  "object": "text_completion",
  "created": 1234567890,
  "model": "Qwen/Qwen3-8B",
  "choices": [
    {
      "text": " How can I help you today?",
      "index": 0,
      "finish_reason": "length"
    }
  ]
}
```

## Environment Configuration

Set the `SKILL_ADAPTER_INFERENCE_URL` environment variable to point to the TGI service:

```bash
export SKILL_ADAPTER_INFERENCE_URL="http://tgi-service/v1"
```

Or in `.env`:

```
SKILL_ADAPTER_INFERENCE_URL=http://tgi-service/v1
```

## Alternative: vLLM

Since TGI is in maintenance mode, consider using **vLLM** for new deployments:

```bash
# vLLM Helm install (example)
helm install vllm vllm/vllm \
  --set model="Qwen/Qwen3-8B" \
  --set gpu.count=1 \
  --namespace skill-adapter
```

vLLM provides:
- Active development and support
- Better performance for some workloads
- Similar OpenAI-compatible API
- More frequent updates and bug fixes

## Troubleshooting

### Out of Memory

If TGI crashes with OOM errors:
- Reduce batch size
- Enable quantization
- Use a smaller model
- Allocate more GPU memory

### Slow Inference

Optimize performance by:
- Enabling tensor parallelism for multi-GPU setups
- Using Flash Attention
- Adjusting batch size
- Pre-warming the model cache

## Next Steps

- [Training Guide](./04_training_guide.md) — Fine-tune the model with LoRA/QLoRA
- [Docker Deployment](./05_docker_deployment.md) — Deploy locally with Docker Compose
