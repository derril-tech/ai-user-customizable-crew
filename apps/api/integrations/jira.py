"""
Jira Integration - Create tickets and update issues based on crew results
"""
import json
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from pydantic import BaseModel

from ..config import settings


class JiraIssue(BaseModel):
    """Jira issue model."""
    project_key: str
    summary: str
    description: str
    issue_type: str = "Task"
    priority: str = "Medium"
    labels: Optional[List[str]] = None
    assignee: Optional[str] = None
    components: Optional[List[str]] = None


class JiraIntegration:
    """Jira integration for creating tickets and tracking crew results."""
    
    def __init__(self, base_url: Optional[str] = None, email: Optional[str] = None, api_token: Optional[str] = None):
        self.base_url = (base_url or settings.JIRA_BASE_URL).rstrip('/')
        self.email = email or settings.JIRA_EMAIL
        self.api_token = api_token or settings.JIRA_API_TOKEN
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with authentication."""
        if not self.session:
            # Create basic auth header
            auth_string = f"{self.email}:{self.api_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def create_issue(self, issue: JiraIssue) -> Dict[str, Any]:
        """Create a new Jira issue."""
        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError("Jira credentials not fully configured")
        
        session = await self._get_session()
        
        # Prepare issue data
        issue_data = {
            "fields": {
                "project": {
                    "key": issue.project_key
                },
                "summary": issue.summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": issue.description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": issue.issue_type
                },
                "priority": {
                    "name": issue.priority
                }
            }
        }
        
        # Add optional fields
        if issue.labels:
            issue_data["fields"]["labels"] = issue.labels
        
        if issue.assignee:
            issue_data["fields"]["assignee"] = {
                "name": issue.assignee
            }
        
        if issue.components:
            issue_data["fields"]["components"] = [
                {"name": component} for component in issue.components
            ]
        
        async with session.post(f"{self.base_url}/rest/api/3/issue", json=issue_data) as response:
            if response.status not in [200, 201]:
                error_text = await response.text()
                raise Exception(f"Jira API error: {response.status} - {error_text}")
            
            return await response.json()
    
    async def create_crew_execution_ticket(
        self,
        crew_name: str,
        job_id: int,
        status: str,
        output_data: Dict[str, Any],
        project_key: str,
        cost: Optional[float] = None,
        execution_time: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a Jira ticket for crew execution results."""
        
        # Determine issue type and priority based on status
        if status == "completed":
            issue_type = "Task"
            priority = "Low"
            summary = f"✅ Crew Execution Completed: {crew_name}"
        elif status == "failed":
            issue_type = "Bug"
            priority = "High"
            summary = f"❌ Crew Execution Failed: {crew_name}"
        else:
            issue_type = "Task"
            priority = "Medium"
            summary = f"🔄 Crew Execution {status.title()}: {crew_name}"
        
        # Build description
        description_parts = [
            f"Crew '{crew_name}' execution completed with status: {status}",
            f"Job ID: {job_id}",
            f"Execution Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ]
        
        if execution_time:
            description_parts.append(f"Duration: {execution_time} seconds")
        
        if cost:
            description_parts.append(f"Cost: ${cost:.4f}")
        
        if error_message and status == "failed":
            description_parts.extend([
                "",
                "Error Details:",
                error_message
            ])
        
        if output_data and status == "completed":
            description_parts.extend([
                "",
                "Results Summary:",
                f"Tasks completed: {len(output_data.get('tasks', {}))}"
            ])
            
            # Add task breakdown
            if "tasks" in output_data:
                description_parts.append("")
                description_parts.append("Task Breakdown:")
                for task_id, task_data in output_data["tasks"].items():
                    description_parts.append(f"- {task_id}: {task_data.get('description', 'No description')}")
        
        description = "\n".join(description_parts)
        
        # Create labels
        labels = ["ai-crew", f"job-{job_id}", status]
        if cost and cost > 1.0:
            labels.append("high-cost")
        
        issue = JiraIssue(
            project_key=project_key,
            summary=summary,
            description=description,
            issue_type=issue_type,
            priority=priority,
            labels=labels
        )
        
        return await self.create_issue(issue)
    
    async def create_crew_template_epic(
        self,
        crew_name: str,
        crew_description: str,
        agents: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        project_key: str
    ) -> Dict[str, Any]:
        """Create an epic for a new crew template with subtasks."""
        
        # Create main epic
        epic_description = f"""
New AI Crew Template: {crew_name}

Description: {crew_description}

Agents ({len(agents)}):
{chr(10).join([f"- {agent.get('name', 'Unnamed')}: {agent.get('role', 'No role')}" for agent in agents])}

Tasks ({len(tasks)}):
{chr(10).join([f"- {task.get('description', f'Task {i+1}')}" for i, task in enumerate(tasks)])}

Created: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """.strip()
        
        epic = JiraIssue(
            project_key=project_key,
            summary=f"AI Crew Template: {crew_name}",
            description=epic_description,
            issue_type="Epic",
            priority="Medium",
            labels=["ai-crew", "template", "new-crew"]
        )
        
        epic_result = await self.create_issue(epic)
        epic_key = epic_result.get("key")
        
        # Create subtasks for each agent
        subtasks = []
        for i, agent in enumerate(agents, 1):
            agent_task = JiraIssue(
                project_key=project_key,
                summary=f"Configure Agent {i}: {agent.get('name', 'Unnamed Agent')}",
                description=f"""
Agent Configuration:
- Name: {agent.get('name', 'Unnamed Agent')}
- Role: {agent.get('role', 'No role specified')}
- Goal: {agent.get('goal', 'No goal specified')}
- Backstory: {agent.get('backstory', 'No backstory specified')}
- Model: {agent.get('llm_config', {}).get('model', 'Not specified')}
                """.strip(),
                issue_type="Sub-task",
                priority="Medium",
                labels=["ai-crew", "agent-config"]
            )
            
            subtask_result = await self.create_issue(agent_task)
            subtasks.append(subtask_result)
        
        # Create subtasks for workflow tasks
        for i, task in enumerate(tasks, 1):
            workflow_task = JiraIssue(
                project_key=project_key,
                summary=f"Configure Task {i}: {task.get('description', 'Unnamed Task')[:50]}...",
                description=f"""
Task Configuration:
- Description: {task.get('description', 'No description')}
- Expected Output: {task.get('expected_output', 'No expected output specified')}
- Assigned Agent: {task.get('agent_id', 'Not assigned')}
                """.strip(),
                issue_type="Sub-task",
                priority="Medium",
                labels=["ai-crew", "task-config"]
            )
            
            subtask_result = await self.create_issue(workflow_task)
            subtasks.append(subtask_result)
        
        return {
            "epic": epic_result,
            "subtasks": subtasks
        }
    
    async def update_issue_status(self, issue_key: str, status: str) -> Dict[str, Any]:
        """Update the status of a Jira issue."""
        session = await self._get_session()
        
        # Get available transitions
        async with session.get(f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions") as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to get transitions: {response.status} - {error_text}")
            
            transitions_data = await response.json()
            transitions = transitions_data.get("transitions", [])
        
        # Find matching transition
        transition_id = None
        for transition in transitions:
            if transition["to"]["name"].lower() == status.lower():
                transition_id = transition["id"]
                break
        
        if not transition_id:
            raise Exception(f"No transition found for status: {status}")
        
        # Execute transition
        transition_data = {
            "transition": {
                "id": transition_id
            }
        }
        
        async with session.post(f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions", json=transition_data) as response:
            if response.status != 204:
                error_text = await response.text()
                raise Exception(f"Failed to transition issue: {response.status} - {error_text}")
            
            return {"success": True, "issue_key": issue_key, "new_status": status}
    
    async def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to a Jira issue."""
        session = await self._get_session()
        
        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }
        
        async with session.post(f"{self.base_url}/rest/api/3/issue/{issue_key}/comment", json=comment_data) as response:
            if response.status not in [200, 201]:
                error_text = await response.text()
                raise Exception(f"Failed to add comment: {response.status} - {error_text}")
            
            return await response.json()
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
