"""Redis-based job queue for training tasks."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

import redis.asyncio as redis

from src.models.config import settings
from src.models.schemas import JobStatus, TrainingJob


class JobQueue:
    """Redis-backed job queue."""
    
    def __init__(self, redis_url: str = settings.redis_url):
        self.redis_url = redis_url
        self.redis_client: redis.Redis | None = None
    
    async def connect(self) -> None:
        """Connect to Redis."""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client is not None:
            await self.redis_client.close()
            self.redis_client = None
    
    async def submit_job(
        self,
        skill_id: str,
        config: dict[str, Any],
    ) -> str:
        """
        Submit a new training job.
        
        Args:
            skill_id: Skill identifier
            config: Training configuration
        
        Returns:
            Job ID
        """
        await self.connect()
        
        job_id = str(uuid.uuid4())
        job = TrainingJob(
            job_id=job_id,
            skill_id=skill_id,
            status=JobStatus.pending,
        )
        
        # Store job metadata
        job_key = f"job:{job_id}"
        job_data = {
            **job.model_dump(),
            "config": json.dumps(config),
            "created_at": datetime.utcnow().isoformat(),
        }
        
        await self.redis_client.hset(job_key, mapping=job_data)
        
        # Add to pending queue
        await self.redis_client.lpush("queue:pending", job_id)
        
        # Add to skill index
        await self.redis_client.sadd(f"skill:{skill_id}:jobs", job_id)
        
        return job_id
    
    async def get_status(self, job_id: str) -> TrainingJob | None:
        """
        Get job status.
        
        Args:
            job_id: Job identifier
        
        Returns:
            TrainingJob or None if not found
        """
        await self.connect()
        
        job_key = f"job:{job_id}"
        job_data = await self.redis_client.hgetall(job_key)
        
        if not job_data:
            return None
        
        # Parse config if present
        if "config" in job_data:
            del job_data["config"]  # Don't include in job object
        
        return TrainingJob(**job_data)
    
    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: float = 0.0,
        error: str | None = None,
    ) -> None:
        """
        Update job status.
        
        Args:
            job_id: Job identifier
            status: New status
            progress: Progress percentage (0.0 to 1.0)
            error: Error message if failed
        """
        await self.connect()
        
        job_key = f"job:{job_id}"
        updates = {
            "status": status.value,
            "progress": str(progress),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        if error is not None:
            updates["error"] = error
        
        await self.redis_client.hset(job_key, mapping=updates)
    
    async def list_jobs(
        self,
        skill_id: str | None = None,
        status: JobStatus | None = None,
        limit: int = 100,
    ) -> list[TrainingJob]:
        """
        List jobs with optional filtering.
        
        Args:
            skill_id: Filter by skill ID
            status: Filter by status
            limit: Maximum number of jobs to return
        
        Returns:
            List of TrainingJob objects
        """
        await self.connect()
        
        job_ids: set[str] = set()
        
        if skill_id:
            # Get jobs for specific skill
            job_ids = await self.redis_client.smembers(f"skill:{skill_id}:jobs")
        else:
            # Get all job IDs by scanning keys
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor,
                    match="job:*",
                    count=100,
                )
                for key in keys:
                    if key.startswith("job:") and ":" in key[4:]:
                        job_id = key[4:]
                        job_ids.add(job_id)
                
                if cursor == 0:
                    break
        
        # Fetch job details
        jobs: list[TrainingJob] = []
        for job_id in list(job_ids)[:limit]:
            job = await self.get_status(job_id)
            if job is None:
                continue
            
            # Filter by status if specified
            if status and job.status != status:
                continue
            
            jobs.append(job)
        
        return jobs
    
    async def get_next_job(self) -> tuple[str, dict[str, Any]] | None:
        """
        Get next pending job from queue.
        
        Returns:
            Tuple of (job_id, config) or None if queue is empty
        """
        await self.connect()
        
        # Pop from pending queue
        job_id = await self.redis_client.rpop("queue:pending")
        if not job_id:
            return None
        
        # Get job config
        job_key = f"job:{job_id}"
        config_str = await self.redis_client.hget(job_key, "config")
        
        config = json.loads(config_str) if config_str else {}
        
        # Mark as running
        await self.update_status(job_id, JobStatus.running)
        
        return job_id, config
