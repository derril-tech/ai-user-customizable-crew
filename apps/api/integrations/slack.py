"""
Slack Integration - Send notifications and receive commands
"""
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from pydantic import BaseModel

from ..config import settings
from ..database import AsyncSessionLocal, AuditLog


class SlackMessage(BaseModel):
    """Slack message model."""
    channel: str
    text: str
    blocks: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    thread_ts: Optional[str] = None


class SlackIntegration:
    """Slack integration for notifications and commands."""
    
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or settings.SLACK_BOT_TOKEN
        self.base_url = "https://slack.com/api"
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def send_message(self, message: SlackMessage) -> Dict[str, Any]:
        """Send a message to Slack."""
        if not self.bot_token:
            raise ValueError("Slack bot token not configured")
        
        session = await self._get_session()
        
        payload = {
            "channel": message.channel,
            "text": message.text
        }
        
        if message.blocks:
            payload["blocks"] = message.blocks
        
        if message.attachments:
            payload["attachments"] = message.attachments
        
        if message.thread_ts:
            payload["thread_ts"] = message.thread_ts
        
        async with session.post(f"{self.base_url}/chat.postMessage", json=payload) as response:
            result = await response.json()
            
            if not result.get("ok"):
                raise Exception(f"Slack API error: {result.get('error', 'Unknown error')}")
            
            return result
    
    async def notify_crew_started(self, crew_name: str, job_id: int, channel: str = "#ai-crews"):
        """Send notification when a crew starts execution."""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🚀 *Crew Started*\n*{crew_name}* is now executing"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Job ID:*\n{job_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Started:*\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Progress"
                        },
                        "url": f"{settings.FRONTEND_URL}/jobs/{job_id}",
                        "action_id": "view_progress"
                    }
                ]
            }
        ]
        
        message = SlackMessage(
            channel=channel,
            text=f"Crew {crew_name} started execution",
            blocks=blocks
        )
        
        return await self.send_message(message)
    
    async def notify_crew_completed(
        self, 
        crew_name: str, 
        job_id: int, 
        status: str,
        execution_time: Optional[int] = None,
        cost: Optional[float] = None,
        channel: str = "#ai-crews"
    ):
        """Send notification when a crew completes execution."""
        
        status_emoji = "✅" if status == "completed" else "❌"
        status_color = "good" if status == "completed" else "danger"
        
        fields = [
            {
                "type": "mrkdwn",
                "text": f"*Job ID:*\n{job_id}"
            },
            {
                "type": "mrkdwn",
                "text": f"*Status:*\n{status_emoji} {status.title()}"
            }
        ]
        
        if execution_time:
            fields.append({
                "type": "mrkdwn",
                "text": f"*Duration:*\n{execution_time}s"
            })
        
        if cost:
            fields.append({
                "type": "mrkdwn",
                "text": f"*Cost:*\n${cost:.4f}"
            })
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji} *Crew {status.title()}*\n*{crew_name}* has finished execution"
                }
            },
            {
                "type": "section",
                "fields": fields
            }
        ]
        
        if status == "completed":
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Results"
                        },
                        "url": f"{settings.FRONTEND_URL}/jobs/{job_id}",
                        "action_id": "view_results"
                    }
                ]
            })
        
        message = SlackMessage(
            channel=channel,
            text=f"Crew {crew_name} {status}",
            blocks=blocks
        )
        
        return await self.send_message(message)
    
    async def notify_cost_alert(self, alert_type: str, message_text: str, channel: str = "#ai-crews-alerts"):
        """Send cost alert notification."""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🚨 *Cost Alert*\n{message_text}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Alert Type:*\n{alert_type.replace('_', ' ').title()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                    }
                ]
            }
        ]
        
        message = SlackMessage(
            channel=channel,
            text=f"Cost Alert: {alert_type}",
            blocks=blocks
        )
        
        return await self.send_message(message)
    
    async def notify_safety_alert(self, job_id: int, safety_score: float, channel: str = "#ai-crews-alerts"):
        """Send safety alert notification."""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *Safety Alert*\nJob {job_id} has a low safety score"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Job ID:*\n{job_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Safety Score:*\n{safety_score:.2f}/1.0"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Review Job"
                        },
                        "url": f"{settings.FRONTEND_URL}/jobs/{job_id}",
                        "action_id": "review_job",
                        "style": "danger"
                    }
                ]
            }
        ]
        
        message = SlackMessage(
            channel=channel,
            text=f"Safety Alert for Job {job_id}",
            blocks=blocks
        )
        
        return await self.send_message(message)
    
    async def handle_slash_command(self, command: str, text: str, user_id: str, channel_id: str) -> Dict[str, Any]:
        """Handle Slack slash commands."""
        
        if command == "/crew-status":
            # Get recent job statuses
            return await self._handle_crew_status_command(text, user_id, channel_id)
        
        elif command == "/crew-run":
            # Trigger crew execution
            return await self._handle_crew_run_command(text, user_id, channel_id)
        
        elif command == "/crew-list":
            # List available crews
            return await self._handle_crew_list_command(user_id, channel_id)
        
        else:
            return {
                "response_type": "ephemeral",
                "text": f"Unknown command: {command}"
            }
    
    async def _handle_crew_status_command(self, text: str, user_id: str, channel_id: str) -> Dict[str, Any]:
        """Handle /crew-status command."""
        # TODO: Implement job status lookup
        return {
            "response_type": "ephemeral",
            "text": "Crew status feature coming soon!"
        }
    
    async def _handle_crew_run_command(self, text: str, user_id: str, channel_id: str) -> Dict[str, Any]:
        """Handle /crew-run command."""
        # TODO: Implement crew execution trigger
        return {
            "response_type": "ephemeral",
            "text": "Crew execution via Slack coming soon!"
        }
    
    async def _handle_crew_list_command(self, user_id: str, channel_id: str) -> Dict[str, Any]:
        """Handle /crew-list command."""
        # TODO: Implement crew listing
        return {
            "response_type": "ephemeral",
            "text": "Crew listing feature coming soon!"
        }
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
