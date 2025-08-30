"""
Tests for crew management functionality.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import Crew, Organization, User


class TestCrewAPI:
    """Test crew API endpoints."""
    
    async def test_create_crew(self, client: AsyncClient, sample_crew_data):
        """Test crew creation."""
        response = await client.post("/v1/crews/", json=sample_crew_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_crew_data["name"]
        assert data["description"] == sample_crew_data["description"]
        assert data["id"] is not None
    
    async def test_get_crew(self, client: AsyncClient, sample_crew_data):
        """Test getting a crew by ID."""
        # Create crew first
        create_response = await client.post("/v1/crews/", json=sample_crew_data)
        crew_id = create_response.json()["id"]
        
        # Get crew
        response = await client.get(f"/v1/crews/{crew_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == crew_id
        assert data["name"] == sample_crew_data["name"]
    
    async def test_get_nonexistent_crew(self, client: AsyncClient):
        """Test getting a crew that doesn't exist."""
        response = await client.get("/v1/crews/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_list_crews(self, client: AsyncClient, sample_crew_data):
        """Test listing crews."""
        # Create multiple crews
        crew1_data = sample_crew_data.copy()
        crew1_data["name"] = "Test Crew 1"
        
        crew2_data = sample_crew_data.copy()
        crew2_data["name"] = "Test Crew 2"
        crew2_data["is_template"] = True
        
        await client.post("/v1/crews/", json=crew1_data)
        await client.post("/v1/crews/", json=crew2_data)
        
        # List all crews
        response = await client.get("/v1/crews/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # List only templates
        response = await client.get("/v1/crews/?is_template=true")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_template"] is True
    
    async def test_update_crew(self, client: AsyncClient, sample_crew_data):
        """Test updating a crew."""
        # Create crew first
        create_response = await client.post("/v1/crews/", json=sample_crew_data)
        crew_id = create_response.json()["id"]
        
        # Update crew
        update_data = {
            "name": "Updated Test Crew",
            "description": "Updated description"
        }
        
        response = await client.put(f"/v1/crews/{crew_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
    
    async def test_delete_crew(self, client: AsyncClient, sample_crew_data):
        """Test deleting a crew."""
        # Create crew first
        create_response = await client.post("/v1/crews/", json=sample_crew_data)
        crew_id = create_response.json()["id"]
        
        # Delete crew
        response = await client.delete(f"/v1/crews/{crew_id}")
        
        assert response.status_code == 204
        
        # Verify crew is deleted
        get_response = await client.get(f"/v1/crews/{crew_id}")
        assert get_response.status_code == 404


class TestCrewValidation:
    """Test crew data validation."""
    
    async def test_create_crew_missing_name(self, client: AsyncClient):
        """Test creating crew without name."""
        invalid_data = {
            "description": "Test crew without name"
        }
        
        response = await client.post("/v1/crews/", json=invalid_data)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("name" in str(error).lower() for error in error_detail)
    
    async def test_create_crew_invalid_config(self, client: AsyncClient):
        """Test creating crew with invalid configuration."""
        invalid_data = {
            "name": "Test Crew",
            "crew_config": "invalid_json_string"  # Should be dict, not string
        }
        
        response = await client.post("/v1/crews/", json=invalid_data)
        
        # Should still create crew but with null config
        assert response.status_code == 201


class TestCrewBuilder:
    """Test crew builder worker functionality."""
    
    def test_generate_crew_config(self):
        """Test crew configuration generation."""
        from ..workers.crew_builder import CrewBuilderWorker
        
        builder = CrewBuilderWorker()
        
        crew_data = {
            "name": "Test Crew",
            "description": "Test description",
            "execution_mode": "parallel",
            "max_execution_time": 1800,
            "verbose": False
        }
        
        config = builder.generate_crew_config(crew_data)
        
        assert config["name"] == "Test Crew"
        assert config["description"] == "Test description"
        assert config["execution_mode"] == "parallel"
        assert config["max_execution_time"] == 1800
        assert config["verbose"] is False
        assert "version" in config
        assert "created_at" in config
    
    def test_generate_roles_config(self):
        """Test roles configuration generation."""
        from ..workers.crew_builder import CrewBuilderWorker
        
        builder = CrewBuilderWorker()
        
        agents_data = [
            {
                "name": "Agent 1",
                "role": "Researcher",
                "goal": "Research topics",
                "backstory": "Expert researcher"
            },
            {
                "name": "Agent 2",
                "role": "Writer",
                "goal": "Write content",
                "backstory": "Professional writer"
            }
        ]
        
        config = builder.generate_roles_config(agents_data)
        
        assert "version" in config
        assert "roles" in config
        assert len(config["roles"]) == 2
        
        agent_1 = config["roles"]["agent_1"]
        assert agent_1["name"] == "Agent 1"
        assert agent_1["role"] == "Researcher"
        assert agent_1["goal"] == "Research topics"
    
    def test_generate_workflows_config(self):
        """Test workflows configuration generation."""
        from ..workers.crew_builder import CrewBuilderWorker
        
        builder = CrewBuilderWorker()
        
        tasks_data = [
            {
                "description": "Task 1",
                "expected_output": "Output 1",
                "agent": "agent_1"
            },
            {
                "description": "Task 2",
                "expected_output": "Output 2",
                "agent": "agent_2"
            }
        ]
        
        config = builder.generate_workflows_config(tasks_data)
        
        assert "version" in config
        assert "tasks" in config
        assert "dependencies" in config
        assert len(config["tasks"]) == 2
        
        task_1 = config["tasks"]["task_1"]
        assert task_1["description"] == "Task 1"
        assert task_1["expected_output"] == "Output 1"
        assert task_1["agent"] == "agent_1"
        
        # Check dependencies
        deps = config["dependencies"]
        assert deps["task_1"] == []  # First task has no dependencies
        assert deps["task_2"] == ["task_1"]  # Second task depends on first
    
    def test_build_complete_crew(self):
        """Test building complete crew configuration."""
        from ..workers.crew_builder import CrewBuilderWorker
        
        builder = CrewBuilderWorker()
        
        crew_data = {
            "name": "Complete Test Crew",
            "description": "A complete test crew",
            "agents": [
                {
                    "name": "Test Agent",
                    "role": "Tester",
                    "goal": "Test everything",
                    "backstory": "Professional tester"
                }
            ],
            "tasks": [
                {
                    "description": "Run tests",
                    "expected_output": "Test results",
                    "agent": "agent_1"
                }
            ]
        }
        
        result = builder.build_crew(crew_data)
        
        assert "crew_config" in result
        assert "roles_config" in result
        assert "workflows_config" in result
        
        assert result["crew_config"]["name"] == "Complete Test Crew"
        assert len(result["roles_config"]["roles"]) == 1
        assert len(result["workflows_config"]["tasks"]) == 1
