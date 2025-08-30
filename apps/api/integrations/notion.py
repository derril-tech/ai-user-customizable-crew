"""
Notion Integration - Create pages and databases for crew results
"""
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from pydantic import BaseModel

from ..config import settings


class NotionPage(BaseModel):
    """Notion page model."""
    parent: Dict[str, Any]
    properties: Dict[str, Any]
    children: Optional[List[Dict[str, Any]]] = None


class NotionIntegration:
    """Notion integration for creating documentation and reports."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.NOTION_TOKEN
        self.base_url = "https://api.notion.com/v1"
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def create_page(self, page: NotionPage) -> Dict[str, Any]:
        """Create a new Notion page."""
        if not self.token:
            raise ValueError("Notion token not configured")
        
        session = await self._get_session()
        
        payload = {
            "parent": page.parent,
            "properties": page.properties
        }
        
        if page.children:
            payload["children"] = page.children
        
        async with session.post(f"{self.base_url}/pages", json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Notion API error: {response.status} - {error_text}")
            
            return await response.json()
    
    async def create_crew_execution_report(
        self,
        crew_name: str,
        job_id: int,
        status: str,
        output_data: Dict[str, Any],
        cost: Optional[float] = None,
        execution_time: Optional[int] = None,
        database_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a Notion page documenting crew execution results."""
        
        # Use default database if not specified
        if not database_id:
            database_id = settings.NOTION_DATABASE_ID
        
        if not database_id:
            raise ValueError("Notion database ID not configured")
        
        # Prepare page properties
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": f"{crew_name} - Job {job_id}"
                        }
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": status.title()
                }
            },
            "Job ID": {
                "number": job_id
            },
            "Crew Name": {
                "rich_text": [
                    {
                        "text": {
                            "content": crew_name
                        }
                    }
                ]
            },
            "Execution Date": {
                "date": {
                    "start": datetime.utcnow().isoformat()
                }
            }
        }
        
        if cost is not None:
            properties["Cost ($)"] = {
                "number": cost
            }
        
        if execution_time is not None:
            properties["Duration (s)"] = {
                "number": execution_time
            }
        
        # Prepare page content
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Execution Summary"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"Crew '{crew_name}' executed on {datetime.utcnow().strftime('%Y-%m-%d at %H:%M:%S')} UTC with status: {status}"
                            }
                        }
                    ]
                }
            }
        ]
        
        # Add execution details
        if execution_time or cost:
            details_text = []
            if execution_time:
                details_text.append(f"Duration: {execution_time} seconds")
            if cost:
                details_text.append(f"Cost: ${cost:.4f}")
            
            children.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": " | ".join(details_text)
                            }
                        }
                    ]
                }
            })
        
        # Add output data if available
        if output_data and status == "completed":
            children.extend([
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Results"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "language": "json",
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": json.dumps(output_data, indent=2)
                                }
                            }
                        ]
                    }
                }
            ])
        
        # Add task breakdown if available
        if output_data and "tasks" in output_data:
            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Task Breakdown"
                            }
                        }
                    ]
                }
            })
            
            for task_id, task_data in output_data["tasks"].items():
                children.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"{task_id}: {task_data.get('description', 'No description')}"
                                },
                                "annotations": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                })
                
                if task_data.get("output"):
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": str(task_data["output"])
                                    }
                                }
                            ]
                        }
                    })
        
        page = NotionPage(
            parent={"database_id": database_id},
            properties=properties,
            children=children
        )
        
        return await self.create_page(page)
    
    async def create_crew_template_documentation(
        self,
        crew_name: str,
        crew_description: str,
        agents: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        database_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create documentation for a crew template."""
        
        if not database_id:
            database_id = settings.NOTION_TEMPLATES_DATABASE_ID
        
        if not database_id:
            raise ValueError("Notion templates database ID not configured")
        
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": crew_name
                        }
                    }
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": crew_description
                        }
                    }
                ]
            },
            "Agents Count": {
                "number": len(agents)
            },
            "Tasks Count": {
                "number": len(tasks)
            },
            "Created": {
                "date": {
                    "start": datetime.utcnow().isoformat()
                }
            }
        }
        
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Overview"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": crew_description
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Agents"
                            }
                        }
                    ]
                }
            }
        ]
        
        # Add agent details
        for agent in agents:
            children.extend([
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"{agent.get('name', 'Unnamed Agent')} - {agent.get('role', 'No role')}"
                                },
                                "annotations": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": agent.get('goal', 'No goal specified')
                                }
                            }
                        ]
                    }
                }
            ])
        
        # Add task details
        children.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Tasks"
                        }
                    }
                ]
            }
        })
        
        for i, task in enumerate(tasks, 1):
            children.extend([
                {
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": task.get('description', f'Task {i}')
                                },
                                "annotations": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Expected Output: {task.get('expected_output', 'Not specified')}"
                                }
                            }
                        ]
                    }
                }
            ])
        
        page = NotionPage(
            parent={"database_id": database_id},
            properties=properties,
            children=children
        )
        
        return await self.create_page(page)
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
