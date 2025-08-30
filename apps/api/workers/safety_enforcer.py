"""
Safety Enforcer Worker - compliance guardrails, PII scrubbing, redaction
"""
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import AsyncSessionLocal, AuditLog
from ..config import settings


class SafetyEnforcer:
    """Worker for enforcing safety and compliance guardrails."""
    
    # PII patterns
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        "ssn": r'\b(?!000|666|9\d{2})\d{3}[-.\s]?(?!00)\d{2}[-.\s]?(?!0000)\d{4}\b',
        "credit_card": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
        "ip_address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        "api_key": r'\b[A-Za-z0-9]{32,}\b',
    }
    
    # Prohibited content patterns
    PROHIBITED_PATTERNS = {
        "violence": [
            r'\b(?:kill|murder|assassinate|bomb|terrorist|weapon)\b',
            r'\b(?:violence|violent|attack|assault)\b'
        ],
        "hate_speech": [
            r'\b(?:hate|racist|discrimination|bigot)\b'
        ],
        "illegal": [
            r'\b(?:illegal|drug|narcotic|cocaine|heroin)\b',
            r'\b(?:fraud|scam|money laundering)\b'
        ]
    }
    
    def __init__(self):
        self.redaction_char = "*"
    
    async def enforce_safety(
        self,
        content: str,
        job_id: int,
        context: Dict[str, Any] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Enforce safety guardrails on content.
        Returns (cleaned_content, safety_report)
        """
        safety_report = {
            "original_length": len(content),
            "pii_found": {},
            "prohibited_content": {},
            "redactions_made": 0,
            "safety_score": 1.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check for PII
        cleaned_content, pii_report = await self._scrub_pii(content)
        safety_report["pii_found"] = pii_report
        safety_report["redactions_made"] += sum(pii_report.values())
        
        # Check for prohibited content
        prohibited_report = await self._check_prohibited_content(cleaned_content)
        safety_report["prohibited_content"] = prohibited_report
        
        # Calculate safety score
        safety_report["safety_score"] = self._calculate_safety_score(
            safety_report["pii_found"],
            safety_report["prohibited_content"]
        )
        
        # Log safety check
        await self._log_safety_check(job_id, safety_report, context)
        
        # Raise alert if safety score is too low
        if safety_report["safety_score"] < 0.7:
            await self._raise_safety_alert(job_id, safety_report)
        
        return cleaned_content, safety_report
    
    async def _scrub_pii(self, content: str) -> Tuple[str, Dict[str, int]]:
        """Scrub personally identifiable information from content."""
        cleaned_content = content
        pii_counts = {}
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, cleaned_content, re.IGNORECASE)
            pii_counts[pii_type] = len(matches)
            
            if matches:
                # Replace with redacted version
                if pii_type == "email":
                    cleaned_content = re.sub(
                        pattern,
                        lambda m: self._redact_email(m.group()),
                        cleaned_content,
                        flags=re.IGNORECASE
                    )
                elif pii_type == "phone":
                    cleaned_content = re.sub(
                        pattern,
                        "[PHONE_REDACTED]",
                        cleaned_content,
                        flags=re.IGNORECASE
                    )
                elif pii_type == "ssn":
                    cleaned_content = re.sub(
                        pattern,
                        "XXX-XX-XXXX",
                        cleaned_content,
                        flags=re.IGNORECASE
                    )
                elif pii_type == "credit_card":
                    cleaned_content = re.sub(
                        pattern,
                        "[CARD_REDACTED]",
                        cleaned_content,
                        flags=re.IGNORECASE
                    )
                elif pii_type == "ip_address":
                    cleaned_content = re.sub(
                        pattern,
                        "XXX.XXX.XXX.XXX",
                        cleaned_content,
                        flags=re.IGNORECASE
                    )
                elif pii_type == "api_key":
                    cleaned_content = re.sub(
                        pattern,
                        "[API_KEY_REDACTED]",
                        cleaned_content,
                        flags=re.IGNORECASE
                    )
        
        return cleaned_content, pii_counts
    
    def _redact_email(self, email: str) -> str:
        """Redact email while preserving domain."""
        parts = email.split("@")
        if len(parts) == 2:
            username = parts[0]
            domain = parts[1]
            redacted_username = username[0] + "*" * (len(username) - 2) + username[-1] if len(username) > 2 else "***"
            return f"{redacted_username}@{domain}"
        return "[EMAIL_REDACTED]"
    
    async def _check_prohibited_content(self, content: str) -> Dict[str, List[str]]:
        """Check for prohibited content patterns."""
        prohibited_matches = {}
        
        for category, patterns in self.PROHIBITED_PATTERNS.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, content, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                prohibited_matches[category] = list(set(matches))  # Remove duplicates
        
        return prohibited_matches
    
    def _calculate_safety_score(
        self,
        pii_found: Dict[str, int],
        prohibited_content: Dict[str, List[str]]
    ) -> float:
        """Calculate safety score based on findings."""
        score = 1.0
        
        # Deduct for PII
        total_pii = sum(pii_found.values())
        if total_pii > 0:
            score -= min(0.3, total_pii * 0.05)  # Max 0.3 deduction for PII
        
        # Deduct for prohibited content
        for category, matches in prohibited_content.items():
            if matches:
                if category == "violence":
                    score -= 0.4
                elif category == "hate_speech":
                    score -= 0.5
                elif category == "illegal":
                    score -= 0.6
        
        return max(0.0, score)
    
    async def _log_safety_check(
        self,
        job_id: int,
        safety_report: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ):
        """Log safety check results."""
        async with AsyncSessionLocal() as db:
            audit_log = AuditLog(
                event_type="safety_check",
                event_data={
                    "safety_report": safety_report,
                    "context": context or {}
                },
                job_id=job_id,
                user_id=1  # TODO: Get from context
            )
            
            db.add(audit_log)
            await db.commit()
    
    async def _raise_safety_alert(self, job_id: int, safety_report: Dict[str, Any]):
        """Raise safety alert for low safety scores."""
        async with AsyncSessionLocal() as db:
            audit_log = AuditLog(
                event_type="safety_alert",
                event_data={
                    "alert_type": "low_safety_score",
                    "safety_score": safety_report["safety_score"],
                    "pii_found": safety_report["pii_found"],
                    "prohibited_content": safety_report["prohibited_content"],
                    "job_id": job_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                job_id=job_id,
                user_id=1  # TODO: Get admin user
            )
            
            db.add(audit_log)
            await db.commit()
        
        # TODO: Send actual alert notifications
        print(f"SAFETY ALERT: Job {job_id} has low safety score: {safety_report['safety_score']}")
    
    async def validate_input(self, input_data: Dict[str, Any], job_id: int) -> Dict[str, Any]:
        """Validate and clean input data before processing."""
        cleaned_data = {}
        
        for key, value in input_data.items():
            if isinstance(value, str):
                cleaned_value, _ = await self.enforce_safety(value, job_id, {"input_field": key})
                cleaned_data[key] = cleaned_value
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    async def validate_output(self, output_data: Dict[str, Any], job_id: int) -> Dict[str, Any]:
        """Validate and clean output data before returning."""
        cleaned_data = {}
        
        for key, value in output_data.items():
            if isinstance(value, str):
                cleaned_value, _ = await self.enforce_safety(value, job_id, {"output_field": key})
                cleaned_data[key] = cleaned_value
            elif isinstance(value, dict):
                # Recursively clean nested dictionaries
                cleaned_data[key] = await self.validate_output(value, job_id)
            else:
                cleaned_data[key] = value
        
        return cleaned_data
