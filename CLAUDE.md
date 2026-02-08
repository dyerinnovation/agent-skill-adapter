# Agent Skill Adapter — Project Instructions

## Project Overview

The Agent Skill Adapter is an **RLVF (Reinforcement Learning from Verifiable Feedback) training pipeline** for fine-tuning HuggingFace language models to follow Agent Skills defined in SKILL.md files. The system enables:

- Loading and parsing Agent Skills from SKILL.md files
- Generating synthetic training data from skill specifications
- Fine-tuning models using LoRA/QLoRA parameter-efficient methods
- Evaluating model adherence to skill constraints
- Serving fine-tuned models via OpenAI-compatible API

**Repository**: https://github.com/dyerinnovation/agent-skill-adapter

## Technology Stack

### Backend
- **Python**: 3.12+
- **Framework**: FastAPI
- **ML Libraries**: PyTorch, HuggingFace Transformers, TRL, PEFT
- **Package Manager**: uv
- **Queue/Cache**: Redis
- **Model Serving**: Text Generation Inference (TGI) via Helm

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Package Manager**: npm

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Orchestration**: K3s v1.34.3 (Kubernetes), Helm 3.20
- **GPU Support**: NVIDIA GPU Operator v25.10.1 (v25.10.0+ required for GB10)
- **Ingress**: NGINX Ingress Controller (Traefik disabled in K3s)
- **Deployment Target**: DGX Spark (CUDA 13.0, GB10 GPU, 125GB RAM)

## Directory Structure

```
agent-skill-adapter/
├── backend/                    # FastAPI service
│   ├── src/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── controllers/       # API route handlers
│   │   ├── services/          # Business logic layer
│   │   ├── models/            # Data models and schemas
│   │   └── views/             # Response formatters
│   ├── tests/                 # Backend tests (pytest)
│   ├── pyproject.toml         # Python dependencies (uv)
│   └── uv.lock                # Lockfile
├── frontend/                   # React dashboard
│   ├── src/
│   │   ├── main.tsx           # React app entry point
│   │   ├── pages/             # Route components
│   │   ├── components/        # Reusable UI components
│   │   ├── hooks/             # Custom React hooks
│   │   └── api/               # API client functions
│   ├── tests/                 # Frontend tests (Playwright)
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
├── charts/                     # Helm charts
│   ├── skill-adapter/         # Umbrella chart
│   ├── backend/               # Backend sub-chart
│   ├── frontend/              # Frontend sub-chart
│   ├── redis/                 # Redis sub-chart
│   ├── ingress/               # NGINX Ingress routing sub-chart
├── docs/                       # Documentation
│   ├── 01_dgx_spark_setup.md
│   ├── 02_model_download.md
│   ├── 03_model_serving.md
│   ├── 04_training_guide.md
│   └── 05_docker_deployment.md
├── research/                   # Design docs and references
├── scripts/                    # Utility scripts
├── docker-compose.yaml         # Local development stack
├── .env.example                # Environment variables template
├── README.md                   # Project overview
└── CLAUDE.md                   # This file
```

## Development Commands

### Backend

```bash
# Install dependencies
cd backend && uv sync

# Run development server (with hot reload)
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Lint code
uv run ruff check src/

# Format code
uv run ruff format src/

# Type check
uv run mypy src/
```

### Frontend

```bash
# Install dependencies
cd frontend && npm install

# Run development server (with HMR)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Run e2e tests
npm run test:e2e

# Lint code
npm run lint
```

### Docker Compose

```bash
# Start all services
docker compose up

# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Restart a service
docker compose restart backend

# Stop all services
docker compose down

# Clean volumes
docker compose down -v
```

## Code Conventions

### Backend (MVC Pattern)

- **Controllers** (`src/controllers/`): Handle HTTP requests, validate input, call services, return responses
  - Use FastAPI dependency injection
  - Keep thin — delegate business logic to services
  - Return Pydantic models or Response objects

- **Services** (`src/services/`): Implement business logic
  - Pure Python functions or classes
  - Handle domain operations (skill parsing, data generation, training)
  - Raise custom exceptions for error handling

- **Models** (`src/models/`): Define data structures
  - Pydantic models for API schemas
  - SQLAlchemy models for database (if used)
  - Type annotations required

- **Views** (`src/views/`): Format responses
  - Transform service output to API schemas
  - Handle serialization

### Frontend (React + TypeScript)

- **Pages** (`src/pages/`): Top-level route components
  - One file per route
  - Handle page-level state and data fetching
  - Use custom hooks for logic

- **Components** (`src/components/`): Reusable UI components
  - Small, focused, single-responsibility
  - Props should be typed with TypeScript interfaces
  - Use TailwindCSS for styling

- **Hooks** (`src/hooks/`): Custom React hooks
  - Extract reusable stateful logic
  - Name with `use` prefix (e.g., `useTrainingJob`)

- **API** (`src/api/`): API client functions
  - One file per API resource (e.g., `training.ts`)
  - Use Fetch API or Axios
  - Type API responses

### General Conventions

- **File naming**: Use snake_case for Python, camelCase for TypeScript/JavaScript
- **Imports**: Absolute imports preferred (configured in tsconfig.json and Python paths)
- **Error handling**: Use custom exceptions in backend, error boundaries in frontend
- **Testing**: Write tests for business logic; aim for >80% coverage on services
- **Git commits**: Descriptive messages, no "Co-Authored-By: Claude" attribution (per project instructions)

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `SKILL_ADAPTER_MODEL` | `Qwen/Qwen3-8B` | HuggingFace model ID for base model |
| `SKILL_ADAPTER_ADAPTER` | `lora` | Adapter type: `lora` or `qlora` |
| `SKILL_ADAPTER_QUANT_BITS` | `4` | Quantization bits (4 or 8) for QLoRA |
| `SKILL_ADAPTER_LEARNING_RATE` | `2e-4` | Learning rate for training |
| `SKILL_ADAPTER_BATCH_SIZE` | `4` | Per-device batch size |
| `SKILL_ADAPTER_GRADIENT_ACCUMULATION_STEPS` | `4` | Gradient accumulation steps |
| `SKILL_ADAPTER_NUM_EPOCHS` | `3` | Number of training epochs |
| `SKILL_ADAPTER_MAX_SEQ_LENGTH` | `2048` | Maximum sequence length |
| `SKILL_ADAPTER_LORA_R` | `16` | LoRA rank |
| `SKILL_ADAPTER_LORA_ALPHA` | `32` | LoRA alpha scaling factor |
| `SKILL_ADAPTER_LORA_DROPOUT` | `0.05` | LoRA dropout rate |
| `SKILL_ADAPTER_INFERENCE_URL` | - | TGI service URL (e.g., `http://tgi-service/v1`) |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `DATABASE_URL` | - | Database connection URL (if needed) |

## Deployment

### Docker Compose (Local Development)

```bash
docker compose up
```

Services:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **Redis**: localhost:6379

### Helm (Kubernetes on DGX Spark)

```bash
cd charts/skill-adapter
helm install skill-adapter . \
  --namespace skill-adapter \
  --create-namespace
```

Check deployment:

```bash
kubectl get pods -n skill-adapter
kubectl get svc -n skill-adapter
```

Upgrade:

```bash
helm upgrade skill-adapter . --namespace skill-adapter
```

## Testing

### Backend Tests (pytest)

```bash
cd backend
uv run pytest
```

Test structure:
- `tests/unit/` — Unit tests for services and models
- `tests/integration/` — API integration tests
- `tests/conftest.py` — Shared fixtures

### Frontend Tests (Playwright)

```bash
cd frontend
npm run test:e2e
```

Test structure:
- `tests/e2e/` — End-to-end tests
- `playwright.config.ts` — Playwright configuration

## DGX Spark Access

The project is deployed on a DGX Spark server:

**SSH Access**:
```bash
ssh jondyer3@spark-b0f2.local
```

**Project Path**:
```bash
~/agent-skill-adapter
```

**Environment**:
- **PATH**: `$HOME/.local/bin:$HOME/.nvm/versions/node/v22.22.0/bin:$PATH`
- **GPU**: GB10 GPU with CUDA 13.0
- **RAM**: 125GB
- **Tools**: uv, node v22.22.0, helm v3.20, gh CLI (authenticated as dyerinnovation)

**Git Configuration**:
```bash
git config user.name "Jonathan Dyer"
git config user.email "jon@dyerinnovation.com"
```

**GitHub Authentication**:
- `gh auth setup-git` has been run (enables HTTPS push)

## Model Serving

The project uses **Text Generation Inference (TGI)** to serve models via OpenAI-compatible API.

**Note**: The inference chart (`charts/tgi/`) now uses **vLLM** via the NVIDIA NGC image (`nvcr.io/nvidia/vllm:26.01-py3`), which is ARM64-native for DGX Spark. The original TGI Docker image is x86-only and doesn't work on ARM64.

### vLLM Deployment

Deploy vLLM via Helm:

```bash
helm install tgi charts/tgi/
```

Or via the umbrella chart which includes all services.

### API Endpoints (OpenAI-compatible)

- **Completions**: `POST /v1/completions`
- **Chat Completions**: `POST /v1/chat/completions`
- **Models**: `GET /v1/models`
- **Health**: `GET /health`

### Configuration

Set `SKILL_ADAPTER_INFERENCE_URL` to point to the vLLM service:

```bash
export SKILL_ADAPTER_INFERENCE_URL="http://tgi:8080/v1"
```

## Git Workflow

**Repository**: https://github.com/dyerinnovation/agent-skill-adapter

**Commit Conventions**:
- Write clear, descriptive commit messages
- **Do not** add "Co-Authored-By: Claude" or similar attribution (per project instructions)
- Always commit and push changes after completing work

**Branch Strategy**:
- `main` — Production-ready code
- `develop` — Integration branch
- Feature branches: `feature/<name>`

## Documentation

Comprehensive guides are available in `docs/`:

1. [DGX Spark Setup](./docs/01_dgx_spark_setup.md) — SSH, tools, PATH, GPU verification
2. [Model Download](./docs/02_model_download.md) — Download Qwen3-8B via huggingface-cli
3. [Model Serving](./docs/03_model_serving.md) — Deploy TGI with Helm, API endpoints
4. [Training Guide](./docs/04_training_guide.md) — LoRA/QLoRA training, monitoring, checkpoints
5. [Docker Deployment](./docs/05_docker_deployment.md) — Docker Compose and Helm deployment
6. [Kubernetes Setup](./docs/06_kubernetes_setup.md) — K3s, GPU Operator, NGINX Ingress on DGX Spark

## Common Tasks

### Download a Model

```bash
uv run huggingface-cli download Qwen/Qwen3-8B
```

### Start a Training Job

Via API:

```bash
curl -X POST http://localhost:8000/api/training/start \
  -H "Content-Type: application/json" \
  -d '{
    "skill_path": "/path/to/SKILL.md",
    "adapter_type": "lora",
    "num_epochs": 3
  }'
```

### Monitor Training

```bash
curl http://localhost:8000/api/training/{job_id}/status
```

### Deploy to Kubernetes

```bash
cd charts/skill-adapter
helm install skill-adapter . --namespace skill-adapter --create-namespace
```

## Troubleshooting

### Out of Memory During Training

1. Reduce batch size: `SKILL_ADAPTER_BATCH_SIZE=2`
2. Use QLoRA: `SKILL_ADAPTER_ADAPTER=qlora`
3. Reduce sequence length: `SKILL_ADAPTER_MAX_SEQ_LENGTH=1024`

### TGI Service Not Starting

1. Check GPU availability: `kubectl describe pod -n skill-adapter`
2. Verify model is downloaded: `ls ~/.cache/huggingface/hub/`
3. Check TGI logs: `kubectl logs -n skill-adapter -l app=text-generation-inference`

### Frontend Build Errors

1. Clear node_modules: `rm -rf node_modules && npm install`
2. Clear Vite cache: `rm -rf .vite`
3. Check Node version: `node --version` (should be v22+)

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- [React Documentation](https://react.dev/)
- [Helm Documentation](https://helm.sh/docs/)
