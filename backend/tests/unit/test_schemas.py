"""Unit tests for schemas module."""
import pytest
from pydantic import ValidationError

from src.models.schemas import (
    RubricItem,
    SkillInfo,
    TrainingRequest,
    JobStatus,
    TrainingJob,
    EvalRequest,
    EvalScore,
    EvalResult,
)


def test_rubric_item_valid():
    """Test creating a valid RubricItem."""
    rubric = RubricItem(
        name="test_rubric",
        description="Test description",
        weight=1.5,
        category="structural",
    )
    
    assert rubric.name == "test_rubric"
    assert rubric.description == "Test description"
    assert rubric.weight == 1.5
    assert rubric.category == "structural"


def test_rubric_item_defaults():
    """Test RubricItem default values."""
    rubric = RubricItem(
        name="test",
        description="desc",
    )
    
    assert rubric.weight == 1.0
    assert rubric.category == "structural"


def test_skill_info_valid():
    """Test creating a valid SkillInfo."""
    skill = SkillInfo(
        id="skill1",
        path="/path/to/skill",
        description="Skill description",
        rubrics=[
            RubricItem(name="r1", description="desc1"),
            RubricItem(name="r2", description="desc2"),
        ],
    )
    
    assert skill.id == "skill1"
    assert skill.path == "/path/to/skill"
    assert skill.description == "Skill description"
    assert len(skill.rubrics) == 2


def test_skill_info_defaults():
    """Test SkillInfo default values."""
    skill = SkillInfo(id="skill1", path="/path")
    
    assert skill.description == ""
    assert skill.rubrics == []


def test_training_request_valid():
    """Test creating a valid TrainingRequest."""
    request = TrainingRequest(
        skill_id="skill1",
        model="Qwen/Qwen3-8B",
        adapter="lora",
        lora_rank=32,
        lora_alpha=64,
        quant_bits=8,
        batch_size=8,
        num_epochs=3,
        learning_rate=1e-4,
        num_samples=200,
    )
    
    assert request.skill_id == "skill1"
    assert request.lora_rank == 32
    assert request.num_samples == 200


def test_training_request_defaults():
    """Test TrainingRequest default values."""
    request = TrainingRequest(skill_id="skill1")
    
    assert request.model == "Qwen/Qwen3-8B"
    assert request.adapter == "lora"
    assert request.lora_rank == 16
    assert request.lora_alpha == 32
    assert request.quant_bits == 4
    assert request.batch_size == 4
    assert request.num_epochs == 1
    assert request.learning_rate == 5e-5
    assert request.num_samples == 100


def test_job_status_enum():
    """Test JobStatus enum values."""
    assert JobStatus.pending == "pending"
    assert JobStatus.running == "running"
    assert JobStatus.completed == "completed"
    assert JobStatus.failed == "failed"


def test_training_job_valid():
    """Test creating a valid TrainingJob."""
    job = TrainingJob(
        job_id="job123",
        skill_id="skill1",
        status=JobStatus.running,
        progress=0.5,
        error=None,
    )
    
    assert job.job_id == "job123"
    assert job.skill_id == "skill1"
    assert job.status == JobStatus.running
    assert job.progress == 0.5
    assert job.error is None


def test_training_job_defaults():
    """Test TrainingJob default values."""
    job = TrainingJob(job_id="job123", skill_id="skill1")
    
    assert job.status == JobStatus.pending
    assert job.progress == 0.0
    assert job.error is None


def test_eval_request_valid():
    """Test creating a valid EvalRequest."""
    request = EvalRequest(
        skill_id="skill1",
        model_path="/path/to/model",
        prompts=["prompt1", "prompt2"],
        num_samples=20,
    )
    
    assert request.skill_id == "skill1"
    assert request.model_path == "/path/to/model"
    assert len(request.prompts) == 2
    assert request.num_samples == 20


def test_eval_request_defaults():
    """Test EvalRequest default values."""
    request = EvalRequest(skill_id="skill1")
    
    assert request.model_path is None
    assert request.prompts == []
    assert request.num_samples == 10


def test_eval_score_valid():
    """Test creating a valid EvalScore."""
    score = EvalScore(
        rubric="test_rubric",
        score=0.85,
        detail="Test detail",
    )
    
    assert score.rubric == "test_rubric"
    assert score.score == 0.85
    assert score.detail == "Test detail"


def test_eval_score_defaults():
    """Test EvalScore default values."""
    score = EvalScore(rubric="test", score=0.5)
    
    assert score.detail == ""


def test_eval_result_valid():
    """Test creating a valid EvalResult."""
    result = EvalResult(
        eval_id="eval123",
        skill_id="skill1",
        scores=[
            EvalScore(rubric="r1", score=0.8),
            EvalScore(rubric="r2", score=0.9),
        ],
        aggregate_score=0.85,
    )
    
    assert result.eval_id == "eval123"
    assert result.skill_id == "skill1"
    assert len(result.scores) == 2
    assert result.aggregate_score == 0.85


def test_eval_result_defaults():
    """Test EvalResult default values."""
    result = EvalResult(eval_id="eval123", skill_id="skill1")
    
    assert result.scores == []
    assert result.aggregate_score == 0.0


def test_pydantic_validation():
    """Test that Pydantic validates required fields."""
    with pytest.raises(ValidationError):
        RubricItem(name="test")  # Missing description
    
    with pytest.raises(ValidationError):
        SkillInfo(id="skill1")  # Missing path
    
    with pytest.raises(ValidationError):
        TrainingRequest()  # Missing skill_id
