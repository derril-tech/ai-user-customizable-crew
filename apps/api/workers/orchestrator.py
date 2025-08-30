"""
Orchestrator Worker - manages agent execution order and dependencies
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..database import AsyncSessionLocal, Job
from ..config import settings


class OrchestratorWorker:
    """Worker for orchestrating crew execution."""
    
    def __init__(self):
        self.cost_tracker = CostTracker()
    
    async def execute_crew(self, job_id: int, crew: Any, input_data: Dict[str, Any]):
        """Execute a crew workflow."""
        async with AsyncSessionLocal() as db:
            try:
                # Update job status to running
                await self._update_job_status(db, job_id, "running")
                
                # Parse crew configurations
                crew_config = crew.crew_config or {}
                roles_config = crew.roles_config or {}
                workflows_config = crew.workflows_config or {}
                
                # Execute workflow tasks
                output_data = await self._execute_workflow(
                    workflows_config, roles_config, input_data, job_id
                )
                
                # Calculate final cost
                total_cost = await self.cost_tracker.get_job_cost(job_id)
                
                # Update job with results
                await self._update_job_completion(
                    db, job_id, "completed", output_data, total_cost
                )
                
            except Exception as e:
                # Update job with error
                await self._update_job_completion(
                    db, job_id, "failed", None, 0.0, str(e)
                )
    
    async def _execute_workflow(
        self, 
        workflows_config: Dict[str, Any], 
        roles_config: Dict[str, Any], 
        input_data: Dict[str, Any],
        job_id: int
    ) -> Dict[str, Any]:
        """Execute workflow tasks in dependency order."""
        tasks = workflows_config.get("tasks", {})
        dependencies = workflows_config.get("dependencies", {})
        
        # Topological sort for task execution order
        execution_order = self._topological_sort(tasks, dependencies)
        
        task_outputs = {}
        
        for task_id in execution_order:
            task_config = tasks[task_id]
            
            # Get agent for this task
            agent_id = task_config.get("agent", "agent_1")
            agent_config = roles_config.get("roles", {}).get(agent_id, {})
            
            # Execute task
            task_output = await self._execute_task(
                task_id, task_config, agent_config, input_data, task_outputs, job_id
            )
            
            task_outputs[task_id] = task_output
        
        return {
            "tasks": task_outputs,
            "final_output": task_outputs.get(execution_order[-1], {}) if execution_order else {},
            "execution_order": execution_order
        }
    
    async def _execute_task(
        self,
        task_id: str,
        task_config: Dict[str, Any],
        agent_config: Dict[str, Any],
        input_data: Dict[str, Any],
        previous_outputs: Dict[str, Any],
        job_id: int
    ) -> Dict[str, Any]:
        """Execute a single task."""
        # Simulate task execution
        # In a real implementation, this would use CrewAI/LangChain
        
        description = task_config.get("description", "")
        expected_output = task_config.get("expected_output", "")
        
        # Build context from previous task outputs
        context = []
        for context_task in task_config.get("context", []):
            if context_task in previous_outputs:
                context.append(previous_outputs[context_task])
        
        # Simulate AI agent execution
        await asyncio.sleep(2)  # Simulate processing time
        
        # Track cost
        await self.cost_tracker.track_task_cost(job_id, task_id, 0.05, 1000)
        
        return {
            "task_id": task_id,
            "description": description,
            "output": f"Completed: {description}",
            "expected_output": expected_output,
            "agent": agent_config.get("name", "Unknown Agent"),
            "execution_time": 2.0,
            "tokens_used": 1000,
            "cost_usd": 0.05,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _topological_sort(self, tasks: Dict[str, Any], dependencies: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort on tasks based on dependencies."""
        # Simple topological sort implementation
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(task_id: str):
            if task_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving task {task_id}")
            if task_id in visited:
                return
            
            temp_visited.add(task_id)
            
            # Visit dependencies first
            for dep in dependencies.get(task_id, []):
                if dep in tasks:
                    visit(dep)
            
            temp_visited.remove(task_id)
            visited.add(task_id)
            result.append(task_id)
        
        for task_id in tasks:
            if task_id not in visited:
                visit(task_id)
        
        return result
    
    async def _update_job_status(self, db: AsyncSession, job_id: int, status: str):
        """Update job status."""
        await db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status=status, updated_at=datetime.utcnow())
        )
        await db.commit()
    
    async def _update_job_completion(
        self, 
        db: AsyncSession, 
        job_id: int, 
        status: str, 
        output_data: Optional[Dict[str, Any]], 
        cost_usd: float,
        error_message: Optional[str] = None
    ):
        """Update job completion data."""
        update_data = {
            "status": status,
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "cost_usd": cost_usd
        }
        
        if output_data:
            update_data["output_data"] = output_data
        
        if error_message:
            update_data["error_message"] = error_message
        
        await db.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(**update_data)
        )
        await db.commit()


class CostTracker:
    """Track costs for job execution."""
    
    def __init__(self):
        self.job_costs = {}
    
    async def track_task_cost(self, job_id: int, task_id: str, cost: float, tokens: int):
        """Track cost for a specific task."""
        if job_id not in self.job_costs:
            self.job_costs[job_id] = {"total_cost": 0.0, "total_tokens": 0, "tasks": {}}
        
        self.job_costs[job_id]["tasks"][task_id] = {"cost": cost, "tokens": tokens}
        self.job_costs[job_id]["total_cost"] += cost
        self.job_costs[job_id]["total_tokens"] += tokens
    
    async def get_job_cost(self, job_id: int) -> float:
        """Get total cost for a job."""
        return self.job_costs.get(job_id, {}).get("total_cost", 0.0)
