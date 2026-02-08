# Docker Deployment Guide

This guide covers deploying the Agent Skill Adapter using Docker Compose for local development and Helm for Kubernetes production deployments.

## Docker Compose (Local Development)

Docker Compose provides a simple way to run the full stack locally.

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 16GB+ RAM recommended
- GPU support (optional, for training)

### Quick Start

1. **Clone the repository**:

```bash
git clone https://github.com/dyerinnovation/agent-skill-adapter.git
cd agent-skill-adapter
```

2. **Configure environment**:

```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start services**:

```bash
docker compose up
```

This will start:
- **Backend** on http://localhost:8000
- **Frontend** on http://localhost:5173
- **Redis** on localhost:6379

### Docker Compose Configuration

The `docker-compose.yaml` defines three services:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./backend:/app
      - ~/.cache/huggingface:/root/.cache/huggingface
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### GPU Support (Optional)

To enable GPU support for training:

1. **Install NVIDIA Container Toolkit**:

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

2. **Update docker-compose.yaml**:

```yaml
services:
  backend:
    # ... existing config ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

3. **Restart services**:

```bash
docker compose up -d
```

### Development Workflow

**Hot reloading** is enabled by default:
- Backend: Changes to Python files trigger uvicorn reload
- Frontend: Vite hot module replacement (HMR)

**View logs**:

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
```

**Restart a service**:

```bash
docker compose restart backend
```

**Stop services**:

```bash
docker compose down
```

**Clean volumes**:

```bash
docker compose down -v
```

## Building Docker Images

### Backend Image

```bash
cd backend
docker build -t agent-skill-adapter-backend:latest .
```

The backend Dockerfile:
- Uses Python 3.12 slim base image
- Installs `uv` for dependency management
- Copies source code and installs dependencies
- Exposes port 8000
- Runs uvicorn with reload for development

### Frontend Image

```bash
cd frontend
docker build -t agent-skill-adapter-frontend:latest .
```

The frontend Dockerfile:
- Uses Node 22 alpine base image
- Installs npm dependencies
- Copies source code
- Exposes port 5173
- Runs Vite dev server

### Multi-stage Production Builds

For production, use multi-stage builds to reduce image size:

**Backend**:

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --no-dev

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend**:

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Helm Deployment (Kubernetes)

For production deployments on Kubernetes (e.g., DGX Spark).

### Prerequisites

- Kubernetes cluster (1.24+)
- Helm 3.20+
- kubectl configured
- Access to DGX Spark (see [DGX Spark Setup](./01_dgx_spark_setup.md))

### Helm Chart Structure

```
charts/
├── skill-adapter/          # Umbrella chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── backend/                # Backend sub-chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ingress.yaml
├── frontend/               # Frontend sub-chart
└── redis/                  # Redis sub-chart
```

### Install Helm Chart

1. **Navigate to charts directory**:

```bash
cd charts/skill-adapter
```

2. **Review values**:

```bash
cat values.yaml
```

3. **Install the chart**:

```bash
helm install skill-adapter . \
  --namespace skill-adapter \
  --create-namespace \
  --values values.yaml
```

### Customize Deployment

Override values via CLI:

```bash
helm install skill-adapter . \
  --set backend.replicaCount=3 \
  --set backend.resources.limits.nvidia\.com/gpu=1 \
  --set frontend.ingress.enabled=true \
  --set frontend.ingress.host=skill-adapter.example.com
```

Or create a custom values file:

```yaml
# custom-values.yaml
backend:
  replicaCount: 2
  image:
    tag: "v1.0.0"
  resources:
    limits:
      nvidia.com/gpu: 1
      memory: "16Gi"
    requests:
      memory: "8Gi"

frontend:
  replicaCount: 2
  ingress:
    enabled: true
    host: skill-adapter.example.com
```

```bash
helm install skill-adapter . -f custom-values.yaml
```

### Verify Deployment

```bash
# Check release status
helm status skill-adapter -n skill-adapter

# List pods
kubectl get pods -n skill-adapter

# Check services
kubectl get svc -n skill-adapter

# View logs
kubectl logs -n skill-adapter -l app=backend --tail=50 -f
```

### Upgrade Deployment

```bash
helm upgrade skill-adapter . \
  --namespace skill-adapter \
  --values values.yaml
```

### Rollback

```bash
# List revisions
helm history skill-adapter -n skill-adapter

# Rollback to previous version
helm rollback skill-adapter -n skill-adapter

# Rollback to specific revision
helm rollback skill-adapter 2 -n skill-adapter
```

### Uninstall

```bash
helm uninstall skill-adapter -n skill-adapter
```

## Environment Variables

Configure via `.env` (Docker Compose) or Helm values (Kubernetes):

| Variable | Description | Default |
|----------|-------------|---------|
| `SKILL_ADAPTER_MODEL` | Base model ID | `Qwen/Qwen3-8B` |
| `SKILL_ADAPTER_ADAPTER` | Adapter type | `lora` |
| `SKILL_ADAPTER_QUANT_BITS` | Quantization bits | `4` |
| `SKILL_ADAPTER_INFERENCE_URL` | TGI service URL | `http://tgi-service/v1` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379` |
| `DATABASE_URL` | Database connection URL | - |

## Next Steps

- [DGX Spark Setup](./01_dgx_spark_setup.md) — Configure the Kubernetes cluster
- [Model Serving](./03_model_serving.md) — Deploy TGI for inference
- [Training Guide](./04_training_guide.md) — Fine-tune models in production
