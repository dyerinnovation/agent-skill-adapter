"""Pydantic schemas for API request/response models."""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class RubricItem(BaseModel):
    name: str
    description: str
    weight: float = 1.0
    category: str = "structural"  # structural | behavioral


class SkillInfo(BaseModel):
    id: str
    path: str
    description: str = ""
    rubrics: list[RubricItem] = []


class TrainingRequest(BaseModel):
    skill_id: str
    model: str = "Qwen/Qwen3-30B-A3B"
    adapter: str = "lora"
    lora_rank: int = 16
    lora_alpha: int = 32
    quant_bits: int = 4
    batch_size: int = 4
    num_epochs: int = 1
    learning_rate: float = 5e-5
    num_samples: int = 100


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class TrainingJob(BaseModel):
    job_id: str
    skill_id: str
    status: JobStatus = JobStatus.pending
    progress: float = 0.0
    error: str | None = None


class EvalRequest(BaseModel):
    skill_id: str
    model_path: str | None = None
    prompts: list[str] = Field(default_factory=list)
    num_samples: int = 10


class EvalScore(BaseModel):
    rubric: str
    score: float
    detail: str = ""


class EvalResult(BaseModel):
    eval_id: str
    skill_id: str
    scores: list[EvalScore] = []
    aggregate_score: float = 0.0
