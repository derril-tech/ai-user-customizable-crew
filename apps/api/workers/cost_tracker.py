"""
Cost Tracker Service - logs token usage and alerts
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from decimal import Decimal

from ..database import AsyncSessionLocal, Job, AuditLog
from ..config import settings


class CostTracker:
    """Service for tracking and managing AI usage costs."""
    
    # Token costs per model (per 1K tokens)
    MODEL_COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    }
    
    # Cost thresholds for alerts
    DAILY_THRESHOLD = 100.0  # $100 per day
    MONTHLY_THRESHOLD = 1000.0  # $1000 per month
    JOB_THRESHOLD = 10.0  # $10 per job
    
    def __init__(self):
        self.job_costs = {}  # In-memory tracking for active jobs
    
    async def track_usage(
        self,
        job_id: int,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task_id: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> float:
        """Track token usage and calculate cost."""
        
        # Calculate cost
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        # Update in-memory tracking
        if job_id not in self.job_costs:
            self.job_costs[job_id] = {
                "total_cost": 0.0,
                "total_tokens": 0,
                "tasks": {}
            }
        
        self.job_costs[job_id]["total_cost"] += cost
        self.job_costs[job_id]["total_tokens"] += input_tokens + output_tokens
        
        if task_id:
            self.job_costs[job_id]["tasks"][task_id] = {
                "cost": cost,
                "tokens": input_tokens + output_tokens,
                "model": model,
                "agent": agent_name
            }
        
        # Log usage event
        await self._log_usage_event(
            job_id, model, input_tokens, output_tokens, cost, task_id, agent_name
        )
        
        # Check thresholds
        await self._check_cost_thresholds(job_id, cost)
        
        return cost
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on model and token usage."""
        if model not in self.MODEL_COSTS:
            # Default to GPT-4 pricing for unknown models
            model = "gpt-4"
        
        costs = self.MODEL_COSTS[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return round(input_cost + output_cost, 4)
    
    async def _log_usage_event(
        self,
        job_id: int,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        task_id: Optional[str] = None,
        agent_name: Optional[str] = None
    ):
        """Log usage event to audit log."""
        async with AsyncSessionLocal() as db:
            audit_log = AuditLog(
                event_type="token_usage",
                event_data={
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "cost_usd": cost,
                    "task_id": task_id,
                    "agent_name": agent_name
                },
                job_id=job_id,
                user_id=1  # TODO: Get from context
            )
            
            db.add(audit_log)
            await db.commit()
    
    async def _check_cost_thresholds(self, job_id: int, current_cost: float):
        """Check if cost thresholds are exceeded and send alerts."""
        
        # Check job threshold
        job_total = self.job_costs.get(job_id, {}).get("total_cost", 0.0)
        if job_total > self.JOB_THRESHOLD:
            await self._send_cost_alert(
                "job_threshold_exceeded",
                f"Job {job_id} has exceeded ${self.JOB_THRESHOLD} threshold. Current cost: ${job_total:.2f}"
            )
        
        # Check daily threshold
        daily_cost = await self._get_daily_cost()
        if daily_cost > self.DAILY_THRESHOLD:
            await self._send_cost_alert(
                "daily_threshold_exceeded",
                f"Daily cost threshold exceeded: ${daily_cost:.2f}"
            )
        
        # Check monthly threshold
        monthly_cost = await self._get_monthly_cost()
        if monthly_cost > self.MONTHLY_THRESHOLD:
            await self._send_cost_alert(
                "monthly_threshold_exceeded",
                f"Monthly cost threshold exceeded: ${monthly_cost:.2f}"
            )
    
    async def _get_daily_cost(self) -> float:
        """Get total cost for today."""
        async with AsyncSessionLocal() as db:
            today = datetime.utcnow().date()
            
            result = await db.execute(
                select(func.sum(Job.cost_usd))
                .where(
                    and_(
                        Job.created_at >= today,
                        Job.created_at < today + timedelta(days=1)
                    )
                )
            )
            
            return float(result.scalar() or 0.0)
    
    async def _get_monthly_cost(self) -> float:
        """Get total cost for this month."""
        async with AsyncSessionLocal() as db:
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            result = await db.execute(
                select(func.sum(Job.cost_usd))
                .where(Job.created_at >= month_start)
            )
            
            return float(result.scalar() or 0.0)
    
    async def _send_cost_alert(self, alert_type: str, message: str):
        """Send cost alert notification."""
        # Log alert
        async with AsyncSessionLocal() as db:
            audit_log = AuditLog(
                event_type="cost_alert",
                event_data={
                    "alert_type": alert_type,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                },
                user_id=1  # TODO: Get admin user
            )
            
            db.add(audit_log)
            await db.commit()
        
        # TODO: Send actual notifications (email, Slack, etc.)
        print(f"COST ALERT: {alert_type} - {message}")
    
    async def get_job_cost(self, job_id: int) -> Dict[str, Any]:
        """Get cost breakdown for a specific job."""
        return self.job_costs.get(job_id, {
            "total_cost": 0.0,
            "total_tokens": 0,
            "tasks": {}
        })
    
    async def get_cost_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get cost analytics for a date range."""
        async with AsyncSessionLocal() as db:
            # Default to last 30 days
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Total cost
            total_result = await db.execute(
                select(func.sum(Job.cost_usd))
                .where(
                    and_(
                        Job.created_at >= start_date,
                        Job.created_at <= end_date
                    )
                )
            )
            total_cost = float(total_result.scalar() or 0.0)
            
            # Total jobs
            jobs_result = await db.execute(
                select(func.count(Job.id))
                .where(
                    and_(
                        Job.created_at >= start_date,
                        Job.created_at <= end_date
                    )
                )
            )
            total_jobs = jobs_result.scalar() or 0
            
            # Average cost per job
            avg_cost = total_cost / total_jobs if total_jobs > 0 else 0.0
            
            return {
                "total_cost": total_cost,
                "total_jobs": total_jobs,
                "average_cost_per_job": avg_cost,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "daily_threshold": self.DAILY_THRESHOLD,
                "monthly_threshold": self.MONTHLY_THRESHOLD
            }
    
    async def update_job_final_cost(self, job_id: int):
        """Update job record with final cost."""
        job_cost_data = await self.get_job_cost(job_id)
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            
            if job:
                job.cost_usd = Decimal(str(job_cost_data["total_cost"]))
                job.tokens_used = job_cost_data["total_tokens"]
                await db.commit()
        
        # Clean up in-memory tracking
        if job_id in self.job_costs:
            del self.job_costs[job_id]
