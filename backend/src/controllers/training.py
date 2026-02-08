from fastapi import APIRouter, HTTPException

from src.models.schemas import TrainingRequest, TrainingJob, JobStatus
from src.services.queue import JobQueue

router = APIRouter()
job_queue = JobQueue()


@router.post("/start", response_model=TrainingJob)
async def start_training(request: TrainingRequest):
    """Start a training run."""
    config = request.model_dump()
    
    job_id = await job_queue.submit_job(
        skill_id=request.skill_id,
        config=config,
    )
    
    job = await job_queue.get_status(job_id)
    if job is None:
        raise HTTPException(status_code=500, detail="Failed to create job")
    
    return job


@router.get("/status/{job_id}", response_model=TrainingJob)
async def training_status(job_id: str):
    """Get training job status."""
    job = await job_queue.get_status(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return job


@router.get("/jobs", response_model=list[TrainingJob])
async def list_jobs(skill_id: str | None = None, status: JobStatus | None = None):
    """List training jobs with optional filtering."""
    jobs = await job_queue.list_jobs(skill_id=skill_id, status=status)
    return jobs
