"""
Database configuration and models.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, 
    ForeignKey, JSON, Numeric, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship
from .config import settings

Base = declarative_base()

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Organization(Base):
    """Organization model."""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    crews = relationship("Crew", back_populates="organization")


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    crews = relationship("Crew", back_populates="created_by")
    jobs = relationship("Job", back_populates="created_by")


class Crew(Base):
    """Crew model."""
    __tablename__ = "crews"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    crew_config = Column(JSON)  # crew.json
    roles_config = Column(JSON)  # roles.json
    workflows_config = Column(JSON)  # workflows.json
    is_template = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="crews")
    created_by = relationship("User", back_populates="crews")
    agents = relationship("Agent", back_populates="crew")
    jobs = relationship("Job", back_populates="crew")


class Agent(Base):
    """Agent model."""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    goal = Column(Text)
    backstory = Column(Text)
    tools = Column(JSON)  # List of tool configurations
    llm_config = Column(JSON)  # LLM settings
    crew_id = Column(Integer, ForeignKey("crews.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    crew = relationship("Crew", back_populates="agents")


class Job(Base):
    """Job execution model."""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    cost_usd = Column(Numeric(10, 4), default=0.0)
    tokens_used = Column(Integer, default=0)
    execution_time_seconds = Column(Integer)
    crew_id = Column(Integer, ForeignKey("crews.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    crew = relationship("Crew", back_populates="jobs")
    created_by = relationship("User", back_populates="jobs")
    audit_logs = relationship("AuditLog", back_populates="job")


class AuditLog(Base):
    """Audit log model."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)  # crew_created, job_started, agent_executed, etc.
    event_data = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="audit_logs")


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
