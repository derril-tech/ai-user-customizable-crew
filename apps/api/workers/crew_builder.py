"""
Crew Builder Worker - generates crew.json, roles.json, workflows.json
"""
import json
from typing import Dict, Any, List
from datetime import datetime


class CrewBuilderWorker:
    """Worker for building crew configurations."""
    
    def __init__(self):
        self.default_llm_config = {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        }
    
    def generate_crew_config(self, crew_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate crew.json configuration."""
        return {
            "name": crew_data.get("name", "Untitled Crew"),
            "description": crew_data.get("description", ""),
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "execution_mode": crew_data.get("execution_mode", "sequential"),
            "max_execution_time": crew_data.get("max_execution_time", 3600),
            "verbose": crew_data.get("verbose", True),
            "memory": crew_data.get("memory", True),
            "cache": crew_data.get("cache", True),
            "max_rpm": crew_data.get("max_rpm", 10),
            "share_crew": crew_data.get("share_crew", False)
        }
    
    def generate_roles_config(self, agents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate roles.json configuration."""
        roles = {}
        
        for i, agent in enumerate(agents_data):
            role_id = f"agent_{i + 1}"
            roles[role_id] = {
                "name": agent.get("name", f"Agent {i + 1}"),
                "role": agent.get("role", "Assistant"),
                "goal": agent.get("goal", "Complete assigned tasks efficiently"),
                "backstory": agent.get("backstory", "An AI assistant ready to help"),
                "tools": agent.get("tools", []),
                "llm_config": agent.get("llm_config", self.default_llm_config),
                "max_iter": agent.get("max_iter", 5),
                "max_execution_time": agent.get("max_execution_time", 300),
                "verbose": agent.get("verbose", True),
                "allow_delegation": agent.get("allow_delegation", False),
                "step_callback": None
            }
        
        return {
            "version": "1.0.0",
            "roles": roles,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def generate_workflows_config(self, tasks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate workflows.json configuration."""
        tasks = {}
        
        for i, task in enumerate(tasks_data):
            task_id = f"task_{i + 1}"
            tasks[task_id] = {
                "description": task.get("description", f"Task {i + 1}"),
                "expected_output": task.get("expected_output", "Completed task output"),
                "agent": task.get("agent", f"agent_{i + 1}"),
                "tools": task.get("tools", []),
                "async_execution": task.get("async_execution", False),
                "context": task.get("context", []),
                "output_json": task.get("output_json", None),
                "output_pydantic": task.get("output_pydantic", None),
                "output_file": task.get("output_file", None),
                "callback": task.get("callback", None)
            }
        
        return {
            "version": "1.0.0",
            "tasks": tasks,
            "dependencies": self._generate_task_dependencies(tasks_data),
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _generate_task_dependencies(self, tasks_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate task dependencies based on task order."""
        dependencies = {}
        
        for i, task in enumerate(tasks_data):
            task_id = f"task_{i + 1}"
            if i > 0:
                # Each task depends on the previous one by default
                dependencies[task_id] = [f"task_{i}"]
            else:
                dependencies[task_id] = []
        
        return dependencies
    
    def build_crew(self, crew_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Build complete crew configuration."""
        agents_data = crew_data.get("agents", [])
        tasks_data = crew_data.get("tasks", [])
        
        crew_config = self.generate_crew_config(crew_data)
        roles_config = self.generate_roles_config(agents_data)
        workflows_config = self.generate_workflows_config(tasks_data)
        
        return {
            "crew_config": crew_config,
            "roles_config": roles_config,
            "workflows_config": workflows_config
        }
