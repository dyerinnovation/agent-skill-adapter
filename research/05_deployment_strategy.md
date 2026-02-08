# Deployment Strategy

## Target Environment
DGX Spark running Kubernetes (single node).

## Helm Charts

### Sub-charts
- **api**: FastAPI backend, GPU-enabled pod
- **frontend**: React dashboard, nginx reverse proxy
- **redis**: Redis 7 for job queue
- **training-job**: Kubernetes Job for training runs

### Umbrella Chart
`charts/skill-adapter/` — deploys all sub-charts with shared values.

## Docker Images
- Backend: Python 3.12-slim + CUDA runtime, uv for deps
- Frontend: Node 22 build stage → nginx serve stage

## Resource Allocation
| Service | CPU | Memory | GPU |
|---|---|---|---|
| API | 2 | 4Gi | 0 |
| Frontend | 0.5 | 512Mi | 0 |
| Redis | 0.5 | 1Gi | 0 |
| Training Job | 4 | 32Gi | 1 |

## CI/CD (future)
- GitHub Actions: lint, test, build images
- Push to GHCR
- Helm upgrade on DGX Spark via SSH
