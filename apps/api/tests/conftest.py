"""
Test configuration and fixtures.
"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from ..main import app
from ..database import Base, get_db
from ..config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_crew_data():
    """Sample crew data for testing."""
    return {
        "name": "Test Crew",
        "description": "A test crew for unit testing",
        "crew_config": {
            "execution_mode": "sequential",
            "max_execution_time": 3600,
            "verbose": True
        },
        "roles_config": {
            "roles": {
                "agent_1": {
                    "name": "Test Agent",
                    "role": "Tester",
                    "goal": "Test things",
                    "backstory": "A testing agent",
                    "llm_config": {
                        "model": "gpt-4",
                        "temperature": 0.7
                    }
                }
            }
        },
        "workflows_config": {
            "tasks": {
                "task_1": {
                    "description": "Test task",
                    "expected_output": "Test output",
                    "agent": "agent_1"
                }
            }
        }
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "name": "Test Agent",
        "role": "Senior Tester",
        "goal": "Ensure quality through comprehensive testing",
        "backstory": "An experienced testing agent with expertise in quality assurance",
        "tools": ["test_runner", "bug_tracker"],
        "llm_config": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        }
    }


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "input_data": {
            "task": "Run comprehensive tests",
            "parameters": {
                "test_suite": "full",
                "environment": "staging"
            }
        }
    }
