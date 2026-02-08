# Skill Adapter — Project Instructions

## Project Overview
RLVF training pipeline for fine-tuning HuggingFace models to follow Agent Skills (SKILL.md files).

## Stack
- Backend: Python 3.12+, FastAPI, PyTorch, TRL, PEFT, HuggingFace Transformers
- Frontend: React 19, Vite, TypeScript, TailwindCSS
- Infra: Docker Compose, Helm 3, Kubernetes (DGX Spark)
- DB: Redis for job queue and caching

## Development
- Backend: `cd backend && uv sync && uv run uvicorn src.main:app --reload`
- Frontend: `cd frontend && npm install && npm run dev`
- Tests: `cd backend && uv run pytest`
- Lint: `cd backend && uv run ruff check src/`

## Conventions
- Backend follows MVC: src/controllers/, src/services/, src/models/, src/views/
- All API routes go in controllers, business logic in services
- Frontend uses pages/ for routes, components/ for reusable UI, hooks/ for custom hooks, api/ for API client
- Helm charts: one sub-chart per service under charts/, umbrella chart at charts/skill-adapter/
