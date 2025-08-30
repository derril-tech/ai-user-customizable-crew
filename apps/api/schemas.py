"""
Pydantic schemas for API models.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


class CrewBase(BaseModel):
    """Base crew schema."""
    name: str
    description: Optional[str] = None
    crew_config: Optional[Dict[str, Any]] = None
    roles_config: Optional[Dict[str, Any]] = None
    workflows_config: Optional[Dict[str, Any]] = None
    is_template: bool = False
    is_public: bool = False


class CrewCreate(CrewBase):
    """Crew creation schema."""
    pass


class CrewUpdate(BaseModel):
    """Crew update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    crew_config: Optional[Dict[str, Any]] = None
    roles_config: Optional[Dict[str, Any]] = None
    workflows_config: Optional[Dict[str, Any]] = None
    is_template: Optional[bool] = None
    is_public: Optional[bool] = None


class CrewResponse(CrewBase):
    """Crew response schema."""
    id: int
    organization_id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class JobBase(BaseModel):
    """Base job schema."""
    input_data: Dict[str, Any]


class JobCreate(JobBase):
    """Job creation schema."""
    pass


class JobUpdate(BaseModel):
    """Job update schema."""
    status: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    cost_usd: Optional[float] = None
    tokens_used: Optional[int] = None
    execution_time_seconds: Optional[int] = None


class JobResponse(JobBase):
    """Job response schema."""
    id: int
    status: str
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    cost_usd: Optional[float] = None
    tokens_used: Optional[int] = None
    execution_time_seconds: Optional[int] = None
    crew_id: int
    created_by_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str
    role: str
    goal: Optional[str] = None
    backstory: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    llm_config: Optional[Dict[str, Any]] = None


class AgentCreate(AgentBase):
    """Agent creation schema."""
    crew_id: int


class AgentResponse(AgentBase):
    """Agent response schema."""
    id: int
    crew_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
