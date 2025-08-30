"""
Tests for safety and compliance functionality.
"""
import pytest
from unittest.mock import AsyncMock, patch

from ..workers.safety_enforcer import SafetyEnforcer


class TestSafetyEnforcer:
    """Test safety enforcement functionality."""
    
    @pytest.fixture
    def safety_enforcer(self):
        """Create safety enforcer instance."""
        return SafetyEnforcer()
    
    async def test_scrub_email_pii(self, safety_enforcer):
        """Test email PII scrubbing."""
        content = "Contact us at john.doe@example.com for more information."
        
        cleaned_content, pii_report = await safety_enforcer._scrub_pii(content)
        
        assert "john.doe@example.com" not in cleaned_content
        assert "j***e@example.com" in cleaned_content
        assert pii_report["email"] == 1
    
    async def test_scrub_phone_pii(self, safety_enforcer):
        """Test phone number PII scrubbing."""
        content = "Call us at (555) 123-4567 or 555.987.6543"
        
        cleaned_content, pii_report = await safety_enforcer._scrub_pii(content)
        
        assert "(555) 123-4567" not in cleaned_content
        assert "555.987.6543" not in cleaned_content
        assert "[PHONE_REDACTED]" in cleaned_content
        assert pii_report["phone"] == 2
    
    async def test_scrub_ssn_pii(self, safety_enforcer):
        """Test SSN PII scrubbing."""
        content = "SSN: 123-45-6789"
        
        cleaned_content, pii_report = await safety_enforcer._scrub_pii(content)
        
        assert "123-45-6789" not in cleaned_content
        assert "XXX-XX-XXXX" in cleaned_content
        assert pii_report["ssn"] == 1
    
    async def test_scrub_credit_card_pii(self, safety_enforcer):
        """Test credit card PII scrubbing."""
        content = "Card number: 4111111111111111"
        
        cleaned_content, pii_report = await safety_enforcer._scrub_pii(content)
        
        assert "4111111111111111" not in cleaned_content
        assert "[CARD_REDACTED]" in cleaned_content
        assert pii_report["credit_card"] == 1
    
    async def test_scrub_api_key_pii(self, safety_enforcer):
        """Test API key PII scrubbing."""
        content = "API key: sk-1234567890abcdef1234567890abcdef"
        
        cleaned_content, pii_report = await safety_enforcer._scrub_pii(content)
        
        assert "sk-1234567890abcdef1234567890abcdef" not in cleaned_content
        assert "[API_KEY_REDACTED]" in cleaned_content
        assert pii_report["api_key"] == 1
    
    async def test_check_prohibited_violence(self, safety_enforcer):
        """Test detection of violent content."""
        content = "We need to kill this bug and bomb the server with requests."
        
        prohibited_report = await safety_enforcer._check_prohibited_content(content)
        
        assert "violence" in prohibited_report
        assert len(prohibited_report["violence"]) > 0
    
    async def test_check_prohibited_illegal(self, safety_enforcer):
        """Test detection of illegal content."""
        content = "This is an illegal drug operation and money laundering scheme."
        
        prohibited_report = await safety_enforcer._check_prohibited_content(content)
        
        assert "illegal" in prohibited_report
        assert len(prohibited_report["illegal"]) > 0
    
    def test_calculate_safety_score_clean_content(self, safety_enforcer):
        """Test safety score calculation for clean content."""
        pii_found = {"email": 0, "phone": 0, "ssn": 0}
        prohibited_content = {}
        
        score = safety_enforcer._calculate_safety_score(pii_found, prohibited_content)
        
        assert score == 1.0
    
    def test_calculate_safety_score_with_pii(self, safety_enforcer):
        """Test safety score calculation with PII."""
        pii_found = {"email": 2, "phone": 1, "ssn": 0}
        prohibited_content = {}
        
        score = safety_enforcer._calculate_safety_score(pii_found, prohibited_content)
        
        assert score < 1.0
        assert score >= 0.7  # Should not be too low for just PII
    
    def test_calculate_safety_score_with_violence(self, safety_enforcer):
        """Test safety score calculation with violent content."""
        pii_found = {"email": 0, "phone": 0, "ssn": 0}
        prohibited_content = {"violence": ["kill", "bomb"]}
        
        score = safety_enforcer._calculate_safety_score(pii_found, prohibited_content)
        
        assert score == 0.6  # 1.0 - 0.4 for violence
    
    def test_calculate_safety_score_with_hate_speech(self, safety_enforcer):
        """Test safety score calculation with hate speech."""
        pii_found = {"email": 0, "phone": 0, "ssn": 0}
        prohibited_content = {"hate_speech": ["hate", "racist"]}
        
        score = safety_enforcer._calculate_safety_score(pii_found, prohibited_content)
        
        assert score == 0.5  # 1.0 - 0.5 for hate speech
    
    def test_calculate_safety_score_with_illegal_content(self, safety_enforcer):
        """Test safety score calculation with illegal content."""
        pii_found = {"email": 0, "phone": 0, "ssn": 0}
        prohibited_content = {"illegal": ["drug", "fraud"]}
        
        score = safety_enforcer._calculate_safety_score(pii_found, prohibited_content)
        
        assert score == 0.4  # 1.0 - 0.6 for illegal content
    
    @patch('apps.api.workers.safety_enforcer.AsyncSessionLocal')
    async def test_enforce_safety_clean_content(self, mock_session, safety_enforcer):
        """Test safety enforcement on clean content."""
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        
        content = "This is clean content with no issues."
        job_id = 1
        
        cleaned_content, safety_report = await safety_enforcer.enforce_safety(content, job_id)
        
        assert cleaned_content == content
        assert safety_report["safety_score"] == 1.0
        assert sum(safety_report["pii_found"].values()) == 0
        assert len(safety_report["prohibited_content"]) == 0
    
    @patch('apps.api.workers.safety_enforcer.AsyncSessionLocal')
    async def test_enforce_safety_with_pii(self, mock_session, safety_enforcer):
        """Test safety enforcement on content with PII."""
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        
        content = "Contact john.doe@example.com or call (555) 123-4567"
        job_id = 1
        
        cleaned_content, safety_report = await safety_enforcer.enforce_safety(content, job_id)
        
        assert "john.doe@example.com" not in cleaned_content
        assert "(555) 123-4567" not in cleaned_content
        assert safety_report["safety_score"] < 1.0
        assert safety_report["pii_found"]["email"] == 1
        assert safety_report["pii_found"]["phone"] == 1
        assert safety_report["redactions_made"] == 2
    
    @patch('apps.api.workers.safety_enforcer.AsyncSessionLocal')
    async def test_enforce_safety_low_score_alert(self, mock_session, safety_enforcer):
        """Test that low safety scores trigger alerts."""
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        
        content = "This illegal drug operation involves hate and violence."
        job_id = 1
        
        with patch.object(safety_enforcer, '_raise_safety_alert') as mock_alert:
            cleaned_content, safety_report = await safety_enforcer.enforce_safety(content, job_id)
            
            assert safety_report["safety_score"] < 0.7
            mock_alert.assert_called_once()
    
    async def test_validate_input_data(self, safety_enforcer):
        """Test input data validation."""
        with patch.object(safety_enforcer, 'enforce_safety') as mock_enforce:
            mock_enforce.return_value = ("cleaned text", {})
            
            input_data = {
                "text_field": "Some text with PII",
                "number_field": 123,
                "nested_field": {"inner": "more text"}
            }
            
            result = await safety_enforcer.validate_input(input_data, 1)
            
            # Should only call enforce_safety on string fields
            assert mock_enforce.call_count == 1
            assert result["number_field"] == 123
    
    async def test_validate_output_data(self, safety_enforcer):
        """Test output data validation."""
        with patch.object(safety_enforcer, 'enforce_safety') as mock_enforce:
            mock_enforce.return_value = ("cleaned text", {})
            
            output_data = {
                "result": "Task completed successfully",
                "metadata": {
                    "agent": "Test Agent",
                    "cost": 0.05
                }
            }
            
            result = await safety_enforcer.validate_output(output_data, 1)
            
            # Should call enforce_safety on string fields recursively
            assert mock_enforce.call_count == 2  # "result" and nested "agent"


class TestPIIRedaction:
    """Test specific PII redaction functionality."""
    
    def test_redact_email_short(self):
        """Test email redaction for short emails."""
        from ..workers.safety_enforcer import SafetyEnforcer
        
        enforcer = SafetyEnforcer()
        
        # Short email (2 characters)
        result = enforcer._redact_email("ab@test.com")
        assert result == "***@test.com"
        
        # Normal email
        result = enforcer._redact_email("john.doe@example.com")
        assert result == "j*****e@example.com"
        
        # Very long email
        result = enforcer._redact_email("verylongusername@example.com")
        assert result == "v*************e@example.com"
    
    def test_redact_email_malformed(self):
        """Test email redaction for malformed emails."""
        from ..workers.safety_enforcer import SafetyEnforcer
        
        enforcer = SafetyEnforcer()
        
        result = enforcer._redact_email("notanemail")
        assert result == "[EMAIL_REDACTED]"
        
        result = enforcer._redact_email("multiple@at@signs.com")
        assert result == "[EMAIL_REDACTED]"
