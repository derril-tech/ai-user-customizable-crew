"""
Jobs API router.
"""
import asyncio
import json
from typing import List, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ..database import get_db, Job, Crew
from ..schemas import JobCreate, JobResponse, JobUpdate
from ..workers.orchestrator import OrchestratorWorker

router = APIRouter()


@router.post("/{crew_id}/run", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def run_crew(
    crew_id: int,
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Execute a crew workflow."""
    # Check if crew exists
    result = await db.execute(select(Crew).where(Crew.id == crew_id))
    crew = result.scalar_one_or_none()
    
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crew not found"
        )
    
    # Create job record
    job = Job(
        status="pending",
        input_data=job_data.input_data,
        crew_id=crew_id,
        created_by_id=1,  # TODO: Get from authenticated user
        started_at=datetime.utcnow()
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Start orchestrator worker asynchronously
    orchestrator = OrchestratorWorker()
    asyncio.create_task(orchestrator.execute_crew(job.id, crew, job_data.input_data))
    
    return JobResponse.from_orm(job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a job by ID."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return JobResponse.from_orm(job)


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List jobs with optional filtering."""
    query = select(Job)
    
    if status_filter:
        query = query.where(Job.status == status_filter)
    
    query = query.offset(skip).limit(limit).order_by(Job.created_at.desc())
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [JobResponse.from_orm(job) for job in jobs]


async def job_stream_generator(job_id: int) -> AsyncGenerator[str, None]:
    """Generate SSE stream for job monitoring."""
    # TODO: Implement real-time job monitoring using Redis/NATS
    # For now, simulate with periodic status updates
    
    async with AsyncSessionLocal() as db:
        while True:
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            
            if not job:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break
            
            # Send job status update
            event_data = {
                "job_id": job.id,
                "status": job.status,
                "progress": 50 if job.status == "running" else (100 if job.status == "completed" else 0),
                "timestamp": datetime.utcnow().isoformat(),
                "output_data": job.output_data
            }
            
            yield f"data: {json.dumps(event_data)}\n\n"
            
            # Break if job is completed or failed
            if job.status in ["completed", "failed"]:
                break
            
            await asyncio.sleep(2)  # Poll every 2 seconds


@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: int):
    """Stream job execution progress via SSE."""
    return StreamingResponse(
        job_stream_generator(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
