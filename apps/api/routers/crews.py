"""
Crews API router.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from ..database import get_db, Crew, User, Organization
from ..schemas import CrewCreate, CrewResponse, CrewUpdate

router = APIRouter()


@router.post("/", response_model=CrewResponse, status_code=status.HTTP_201_CREATED)
async def create_crew(
    crew_data: CrewCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new crew."""
    # TODO: Add authentication and get current user
    # For now, use a default organization_id and created_by_id
    
    crew = Crew(
        name=crew_data.name,
        description=crew_data.description,
        crew_config=crew_data.crew_config,
        roles_config=crew_data.roles_config,
        workflows_config=crew_data.workflows_config,
        is_template=crew_data.is_template,
        is_public=crew_data.is_public,
        organization_id=1,  # TODO: Get from authenticated user
        created_by_id=1,    # TODO: Get from authenticated user
    )
    
    db.add(crew)
    await db.commit()
    await db.refresh(crew)
    
    return CrewResponse.from_orm(crew)


@router.get("/{crew_id}", response_model=CrewResponse)
async def get_crew(
    crew_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a crew by ID."""
    result = await db.execute(select(Crew).where(Crew.id == crew_id))
    crew = result.scalar_one_or_none()
    
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crew not found"
        )
    
    return CrewResponse.from_orm(crew)


@router.get("/", response_model=List[CrewResponse])
async def list_crews(
    skip: int = 0,
    limit: int = 100,
    is_template: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """List crews with optional filtering."""
    query = select(Crew)
    
    if is_template is not None:
        query = query.where(Crew.is_template == is_template)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    crews = result.scalars().all()
    
    return [CrewResponse.from_orm(crew) for crew in crews]


@router.put("/{crew_id}", response_model=CrewResponse)
async def update_crew(
    crew_id: int,
    crew_update: CrewUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a crew."""
    result = await db.execute(select(Crew).where(Crew.id == crew_id))
    crew = result.scalar_one_or_none()
    
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crew not found"
        )
    
    # Update fields
    update_data = crew_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(crew, field, value)
    
    await db.commit()
    await db.refresh(crew)
    
    return CrewResponse.from_orm(crew)


@router.delete("/{crew_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crew(
    crew_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a crew."""
    result = await db.execute(select(Crew).where(Crew.id == crew_id))
    crew = result.scalar_one_or_none()
    
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crew not found"
        )
    
    await db.delete(crew)
    await db.commit()
