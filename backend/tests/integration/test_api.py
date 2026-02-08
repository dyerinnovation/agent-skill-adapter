"""Integration tests for API endpoints - FIXED VERSION."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import app
from src.models.schemas import JobStatus


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_skills_empty(client):
    """Test listing skills when directory is empty."""
    with patch("src.controllers.skills.load_skills", return_value=[]):
        response = client.get("/api/skills/")
        
        assert response.status_code == 200
        assert response.json() == []


def test_list_skills_with_data(client):
    """Test listing skills with mock data."""
    from src.models.schemas import SkillInfo, RubricItem
    
    mock_skills = [
        SkillInfo(
            id="skill1",
            path="/path/to/skill1",
            description="First skill",
            rubrics=[],
        ),
        SkillInfo(
            id="skill2",
            path="/path/to/skill2",
            description="Second skill",
            rubrics=[
                RubricItem(name="r1", description="rubric1"),
            ],
        ),
    ]
    
    with patch("src.controllers.skills.load_skills", return_value=mock_skills):
        response = client.get("/api/skills/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "skill1"
        assert data[1]["id"] == "skill2"


def test_get_skill_found(client):
    """Test getting a specific skill."""
    from src.models.schemas import SkillInfo
    
    mock_skill = SkillInfo(
        id="skill1",
        path="/path/to/skill1",
        description="Test skill",
        rubrics=[],
    )
    
    with patch("src.controllers.skills.load_skills", return_value=[mock_skill]):
        response = client.get("/api/skills/skill1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "skill1"
        assert data["description"] == "Test skill"


def test_get_skill_not_found(client):
    """Test getting a nonexistent skill."""
    with patch("src.controllers.skills.load_skills", return_value=[]):
        response = client.get("/api/skills/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_start_training(client):
    """Test starting a training job."""
    mock_queue = AsyncMock()
    mock_queue.submit_job = AsyncMock(return_value="job123")
    
    from src.models.schemas import TrainingJob
    mock_job = TrainingJob(
        job_id="job123",
        skill_id="skill1",
        status=JobStatus.pending,
    )
    mock_queue.get_status = AsyncMock(return_value=mock_job)
    
    with patch("src.controllers.training.job_queue", mock_queue):
        response = client.post(
            "/api/training/start",
            json={
                "skill_id": "skill1",
                "model": "Qwen/Qwen3-8B",
                "adapter": "lora",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "job123"
        assert data["skill_id"] == "skill1"
        assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_training_status_found(client):
    """Test getting training job status."""
    mock_queue = AsyncMock()
    
    from src.models.schemas import TrainingJob
    mock_job = TrainingJob(
        job_id="job123",
        skill_id="skill1",
        status=JobStatus.running,
        progress=0.5,
    )
    mock_queue.get_status = AsyncMock(return_value=mock_job)
    
    with patch("src.controllers.training.job_queue", mock_queue):
        response = client.get("/api/training/status/job123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "job123"
        assert data["status"] == "running"
        assert data["progress"] == 0.5


@pytest.mark.asyncio
async def test_training_status_not_found(client):
    """Test getting status for nonexistent job."""
    mock_queue = AsyncMock()
    mock_queue.get_status = AsyncMock(return_value=None)
    
    with patch("src.controllers.training.job_queue", mock_queue):
        response = client.get("/api/training/status/nonexistent")
        
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_jobs(client):
    """Test listing training jobs."""
    mock_queue = AsyncMock()
    
    from src.models.schemas import TrainingJob
    mock_jobs = [
        TrainingJob(job_id="job1", skill_id="skill1", status=JobStatus.pending),
        TrainingJob(job_id="job2", skill_id="skill2", status=JobStatus.running),
    ]
    mock_queue.list_jobs = AsyncMock(return_value=mock_jobs)
    
    with patch("src.controllers.training.job_queue", mock_queue):
        response = client.get("/api/training/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


@pytest.mark.asyncio
async def test_list_jobs_filtered_by_skill(client):
    """Test listing jobs filtered by skill."""
    mock_queue = AsyncMock()
    
    from src.models.schemas import TrainingJob
    mock_jobs = [
        TrainingJob(job_id="job1", skill_id="skill1", status=JobStatus.pending),
    ]
    mock_queue.list_jobs = AsyncMock(return_value=mock_jobs)
    
    with patch("src.controllers.training.job_queue", mock_queue):
        response = client.get("/api/training/jobs?skill_id=skill1")
        
        assert response.status_code == 200
        mock_queue.list_jobs.assert_called_once_with(skill_id="skill1", status=None)


def test_run_evaluation_skill_not_found(client):
    """Test running evaluation for nonexistent skill."""
    with patch("src.controllers.evaluation.load_skills", return_value=[]):
        response = client.post(
            "/api/evaluation/run",
            json={
                "skill_id": "nonexistent",
                "prompts": ["test prompt"],
            },
        )
        
        assert response.status_code == 404


def test_run_evaluation_no_model(client):
    """Test running evaluation without model (baseline)."""
    from src.models.schemas import SkillInfo, RubricItem
    
    mock_skill = SkillInfo(
        id="skill1",
        path="/path",
        description="Test skill",
        rubrics=[
            RubricItem(name="r1", description="Test rubric"),
        ],
    )
    
    with patch("src.controllers.evaluation.load_skills", return_value=[mock_skill]):
        response = client.post(
            "/api/evaluation/run",
            json={
                "skill_id": "skill1",
                "prompts": ["test prompt"],
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "eval_id" in data
        assert data["skill_id"] == "skill1"
        assert "scores" in data
        assert len(data["scores"]) >= 1
        assert "aggregate_score" in data


def test_run_evaluation_generate_prompts(client):
    """Test running evaluation with auto-generated prompts."""
    from src.models.schemas import SkillInfo, RubricItem
    
    mock_skill = SkillInfo(
        id="skill1",
        path="/path",
        description="Test skill",
        rubrics=[
            RubricItem(name="r1", description="Test rubric"),
        ],
    )
    
    with patch("src.controllers.evaluation.load_skills", return_value=[mock_skill]):
        response = client.post(
            "/api/evaluation/run",
            json={
                "skill_id": "skill1",
                "num_samples": 5,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["skill_id"] == "skill1"
        assert len(data["scores"]) >= 1


def test_get_evaluation_results(client):
    """Test getting evaluation results."""
    response = client.get("/api/evaluation/results/eval123")
    
    # This is a placeholder endpoint, should return basic structure
    assert response.status_code == 200
    data = response.json()
    assert "eval_id" in data
    assert "skill_id" in data
