# Agent Skill Adapter

RLVF (Reinforcement Learning from Verifiable Feedback) training pipeline that fine-tunes HuggingFace models to follow Agent Skills defined as SKILL.md files.

## Architecture

- **backend/** — FastAPI service: skill loading, synthetic data generation, evaluation, LoRA training
- **frontend/** — React+Vite dashboard: skill management, training monitoring, eval results
- **charts/** — Helm charts for Kubernetes deployment on DGX Spark
- **research/** — Design docs and research references

## Quick Start

```bash
# Backend
cd backend && uv sync && uv run uvicorn src.main:app --reload

# Frontend
cd frontend && npm install && npm run dev

# Docker
docker compose up
```

## Documentation

Comprehensive guides for setup, deployment, and development:

- [DGX Spark Setup](./docs/01_dgx_spark_setup.md) — SSH access, tool installation, PATH configuration
- [Model Download](./docs/02_model_download.md) — Download Qwen3-8B from HuggingFace Hub
- [Model Serving](./docs/03_model_serving.md) — Deploy TGI with OpenAI-compatible API
- [Training Guide](./docs/04_training_guide.md) — LoRA/QLoRA fine-tuning workflow
- [Docker Deployment](./docs/05_docker_deployment.md) — Docker Compose and Helm deployment

## Environment

Copy `.env.example` to `.env` and configure. Key settings:

| Variable | Default | Description |
|---|---|---|
| `SKILL_ADAPTER_MODEL` | `Qwen/Qwen3-8B` | Base model to fine-tune |
| `SKILL_ADAPTER_ADAPTER` | `lora` | Adapter type (lora/qlora) |
| `SKILL_ADAPTER_QUANT_BITS` | `4` | Quantization bits |

## License

MIT
