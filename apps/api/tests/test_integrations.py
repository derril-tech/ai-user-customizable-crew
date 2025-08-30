"""
Tests for integration functionality.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ..integrations.slack import SlackIntegration, SlackMessage
from ..integrations.notion import NotionIntegration, NotionPage
from ..integrations.jira import JiraIntegration, JiraIssue


class TestSlackIntegration:
    """Test Slack integration functionality."""
    
    @pytest.fixture
    def slack_integration(self):
        """Create Slack integration instance."""
        return SlackIntegration(bot_token="test_token")
    
    @patch('aiohttp.ClientSession.post')
    async def test_send_message_success(self, mock_post, slack_integration):
        """Test successful message sending."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.json.return_value = {"ok": True, "ts": "1234567890.123456"}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        message = SlackMessage(
            channel="#test",
            text="Test message"
        )
        
        result = await slack_integration.send_message(message)
        
        assert result["ok"] is True
        assert "ts" in result
        mock_post.assert_called_once()
    
    @patch('aiohttp.ClientSession.post')
    async def test_send_message_failure(self, mock_post, slack_integration):
        """Test message sending failure."""
        # Mock error response
        mock_response = AsyncMock()
        mock_response.json.return_value = {"ok": False, "error": "channel_not_found"}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        message = SlackMessage(
            channel="#nonexistent",
            text="Test message"
        )
        
        with pytest.raises(Exception) as exc_info:
            await slack_integration.send_message(message)
        
        assert "channel_not_found" in str(exc_info.value)
    
    async def test_send_message_no_token(self):
        """Test sending message without token."""
        integration = SlackIntegration(bot_token=None)
        
        message = SlackMessage(
            channel="#test",
            text="Test message"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await integration.send_message(message)
        
        assert "token not configured" in str(exc_info.value)
    
    @patch.object(SlackIntegration, 'send_message')
    async def test_notify_crew_started(self, mock_send, slack_integration):
        """Test crew started notification."""
        mock_send.return_value = {"ok": True}
        
        await slack_integration.notify_crew_started("Test Crew", 123)
        
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args.channel == "#ai-crews"
        assert "Test Crew" in call_args.text
        assert call_args.blocks is not None
    
    @patch.object(SlackIntegration, 'send_message')
    async def test_notify_crew_completed(self, mock_send, slack_integration):
        """Test crew completed notification."""
        mock_send.return_value = {"ok": True}
        
        await slack_integration.notify_crew_completed(
            "Test Crew", 123, "completed", 30, 0.05
        )
        
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert "✅" in call_args.text
        assert "completed" in call_args.text.lower()


class TestNotionIntegration:
    """Test Notion integration functionality."""
    
    @pytest.fixture
    def notion_integration(self):
        """Create Notion integration instance."""
        return NotionIntegration(token="test_token")
    
    @patch('aiohttp.ClientSession.post')
    async def test_create_page_success(self, mock_post, notion_integration):
        """Test successful page creation."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "id": "test_page_id",
            "url": "https://notion.so/test_page_id"
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        page = NotionPage(
            parent={"database_id": "test_db_id"},
            properties={
                "Name": {
                    "title": [{"text": {"content": "Test Page"}}]
                }
            }
        )
        
        result = await notion_integration.create_page(page)
        
        assert result["id"] == "test_page_id"
        mock_post.assert_called_once()
    
    @patch('aiohttp.ClientSession.post')
    async def test_create_page_failure(self, mock_post, notion_integration):
        """Test page creation failure."""
        # Mock error response
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text.return_value = "Bad Request"
        mock_post.return_value.__aenter__.return_value = mock_response
        
        page = NotionPage(
            parent={"database_id": "invalid_db_id"},
            properties={}
        )
        
        with pytest.raises(Exception) as exc_info:
            await notion_integration.create_page(page)
        
        assert "400" in str(exc_info.value)
    
    @patch.object(NotionIntegration, 'create_page')
    async def test_create_crew_execution_report(self, mock_create, notion_integration):
        """Test crew execution report creation."""
        mock_create.return_value = {"id": "report_page_id"}
        
        output_data = {
            "tasks": {
                "task_1": {
                    "description": "Test task",
                    "output": "Test output"
                }
            }
        }
        
        result = await notion_integration.create_crew_execution_report(
            "Test Crew", 123, "completed", output_data, 0.05, 30, "test_db_id"
        )
        
        assert result["id"] == "report_page_id"
        mock_create.assert_called_once()
        
        # Check the page structure
        call_args = mock_create.call_args[0][0]
        assert "Test Crew - Job 123" in str(call_args.properties)
        assert call_args.children is not None


class TestJiraIntegration:
    """Test Jira integration functionality."""
    
    @pytest.fixture
    def jira_integration(self):
        """Create Jira integration instance."""
        return JiraIntegration(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test_token"
        )
    
    @patch('aiohttp.ClientSession.post')
    async def test_create_issue_success(self, mock_post, jira_integration):
        """Test successful issue creation."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json.return_value = {
            "id": "10001",
            "key": "TEST-123",
            "self": "https://test.atlassian.net/rest/api/3/issue/10001"
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        issue = JiraIssue(
            project_key="TEST",
            summary="Test Issue",
            description="Test description"
        )
        
        result = await jira_integration.create_issue(issue)
        
        assert result["key"] == "TEST-123"
        mock_post.assert_called_once()
    
    @patch('aiohttp.ClientSession.post')
    async def test_create_issue_failure(self, mock_post, jira_integration):
        """Test issue creation failure."""
        # Mock error response
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text.return_value = "Bad Request: Invalid project key"
        mock_post.return_value.__aenter__.return_value = mock_response
        
        issue = JiraIssue(
            project_key="INVALID",
            summary="Test Issue",
            description="Test description"
        )
        
        with pytest.raises(Exception) as exc_info:
            await jira_integration.create_issue(issue)
        
        assert "400" in str(exc_info.value)
    
    async def test_create_issue_missing_credentials(self):
        """Test creating issue without credentials."""
        integration = JiraIntegration(base_url=None, email=None, api_token=None)
        
        issue = JiraIssue(
            project_key="TEST",
            summary="Test Issue",
            description="Test description"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await integration.create_issue(issue)
        
        assert "not fully configured" in str(exc_info.value)
    
    @patch.object(JiraIntegration, 'create_issue')
    async def test_create_crew_execution_ticket(self, mock_create, jira_integration):
        """Test crew execution ticket creation."""
        mock_create.return_value = {"key": "TEST-123"}
        
        output_data = {
            "tasks": {
                "task_1": {"description": "Test task"}
            }
        }
        
        result = await jira_integration.create_crew_execution_ticket(
            "Test Crew", 123, "completed", output_data, "TEST", 0.05, 30
        )
        
        assert result["key"] == "TEST-123"
        mock_create.assert_called_once()
        
        # Check issue data
        call_args = mock_create.call_args[0][0]
        assert call_args.project_key == "TEST"
        assert "Test Crew" in call_args.summary
        assert call_args.issue_type == "Task"
        assert call_args.priority == "Low"  # Completed status = Low priority
    
    @patch.object(JiraIntegration, 'create_issue')
    async def test_create_crew_execution_ticket_failed(self, mock_create, jira_integration):
        """Test crew execution ticket for failed job."""
        mock_create.return_value = {"key": "TEST-124"}
        
        result = await jira_integration.create_crew_execution_ticket(
            "Test Crew", 124, "failed", {}, "TEST", error_message="Something went wrong"
        )
        
        call_args = mock_create.call_args[0][0]
        assert call_args.issue_type == "Bug"
        assert call_args.priority == "High"
        assert "❌" in call_args.summary
        assert "Something went wrong" in call_args.description


class TestIntegrationModels:
    """Test integration data models."""
    
    def test_slack_message_model(self):
        """Test SlackMessage model validation."""
        # Valid message
        message = SlackMessage(
            channel="#test",
            text="Test message"
        )
        assert message.channel == "#test"
        assert message.text == "Test message"
        assert message.blocks is None
        
        # Message with blocks
        message_with_blocks = SlackMessage(
            channel="#test",
            text="Test message",
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": "Hello"}}]
        )
        assert len(message_with_blocks.blocks) == 1
    
    def test_notion_page_model(self):
        """Test NotionPage model validation."""
        page = NotionPage(
            parent={"database_id": "test_db"},
            properties={
                "Name": {"title": [{"text": {"content": "Test"}}]}
            }
        )
        assert page.parent["database_id"] == "test_db"
        assert page.children is None
    
    def test_jira_issue_model(self):
        """Test JiraIssue model validation."""
        # Minimal issue
        issue = JiraIssue(
            project_key="TEST",
            summary="Test Issue",
            description="Test description"
        )
        assert issue.project_key == "TEST"
        assert issue.issue_type == "Task"  # Default value
        assert issue.priority == "Medium"  # Default value
        
        # Issue with all fields
        full_issue = JiraIssue(
            project_key="PROJ",
            summary="Full Issue",
            description="Full description",
            issue_type="Bug",
            priority="High",
            labels=["urgent", "bug"],
            assignee="john.doe",
            components=["Backend", "API"]
        )
        assert full_issue.issue_type == "Bug"
        assert full_issue.priority == "High"
        assert len(full_issue.labels) == 2
        assert full_issue.assignee == "john.doe"
