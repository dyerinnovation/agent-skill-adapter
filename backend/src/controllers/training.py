from fastapi import APIRouter

router = APIRouter()


@router.post("/start")
async def start_training():
    """Start a training run."""
    return {"status": "queued"}


@router.get("/status/{job_id}")
async def training_status(job_id: str):
    """Get training job status."""
    return {"job_id": job_id, "status": "pending"}
