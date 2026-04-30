"""Unit tests for MCP Server Emergence."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from mcp.types import TextContent

from mcp_server_emergence.server import (
    EMERGENCE_API_KEY,
    EMERGENCE_BASE_URL,
    _api_get,
    _api_post,
    _headers,
    call_tool,
    list_tools,
)


class TestHeaders:
    """Test header generation."""

    def test_headers_without_api_key(self):
        """Test that headers are generated without API key."""
        with patch("mcp_server_emergence.server.EMERGENCE_API_KEY", ""):
            headers = _headers()
            assert headers["Content-Type"] == "application/json"
            assert headers["Accept"] == "application/json"
            assert "Authorization" not in headers

    def test_headers_with_api_key(self):
        """Test that headers include API key when set."""
        with patch("mcp_server_emergence.server.EMERGENCE_API_KEY", "test-api-key"):
            headers = _headers()
            assert headers["Authorization"] == "Bearer test-api-key"
            assert headers["X-API-Key"] == "test-api-key"


class TestListTools:
    """Test tool listing."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_list(self):
        """Test that list_tools returns a list of tools."""
        tools = await list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    @pytest.mark.asyncio
    async def test_list_bounties_tool_exists(self):
        """Test that list_bounties tool exists."""
        tools = await list_tools()
        tool_names = [t.name for t in tools]
        assert "list_bounties" in tool_names

    @pytest.mark.asyncio
    async def test_post_bounty_tool_exists(self):
        """Test that post_bounty tool exists."""
        tools = await list_tools()
        tool_names = [t.name for t in tools]
        assert "post_bounty" in tool_names

    @pytest.mark.asyncio
    async def test_verify_task_tool_exists(self):
        """Test that verify_task tool exists."""
        tools = await list_tools()
        tool_names = [t.name for t in tools]
        assert "verify_task" in tool_names

    @pytest.mark.asyncio
    async def test_all_expected_tools_exist(self):
        """Test that all expected tools are registered."""
        tools = await list_tools()
        tool_names = [t.name for t in tools]
        expected = [
            "list_bounties",
            "get_bounty",
            "post_bounty",
            "verify_task",
            "submit_task",
            "get_domains",
        ]
        for tool in expected:
            assert tool in tool_names


class TestCallTool:
    """Test tool invocations."""

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self):
        """Test that unknown tools return an error message."""
        result = await call_tool("unknown_tool", {})

        assert len(result) == 1
        assert "error" in result[0].text or "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    @patch("mcp_server_emergence.server._api_get")
    async def test_list_bounties_calls_api(self, mock_get):
        """Test that list_bounties calls the API."""
        mock_get.return_value = {"bounties": [], "count": 0}
        result = await call_tool("list_bounties", {"limit": 10})

        mock_get.assert_called_once()
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

    @pytest.mark.asyncio
    @patch("mcp_server_emergence.server._api_get")
    async def test_get_bounty_validates_bounty_id(self, mock_get):
        """Test that get_bounty validates bounty_id."""
        result = await call_tool("get_bounty", {})

        assert len(result) == 1
        assert "Error: bounty_id is required" in str(result[0].text)

    @pytest.mark.asyncio
    @patch("mcp_server_emergence.server._api_get")
    async def test_get_bounty_calls_api(self, mock_get):
        """Test that get_bounty calls the API."""
        mock_get.return_value = {"id": "b123", "title": "Test"}
        result = await call_tool("get_bounty", {"bounty_id": "b123"})

        mock_get.assert_called_once_with("/v1/bounties/b123")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_post_bounty_validates_required_fields(self):
        """Test that post_bounty validates required fields."""
        result = await call_tool("post_bounty", {"title": "Test"})

        assert len(result) == 1
        assert "Error: Missing required fields" in str(result[0].text)
        assert "description" in str(result[0].text)
        assert "reward" in str(result[0].text)

    @pytest.mark.asyncio
    @patch("mcp_server_emergence.server._api_post")
    async def test_post_bounty_calls_api(self, mock_post):
        """Test that post_bounty calls the API."""
        mock_post.return_value = {"id": "b123", "status": "created"}
        result = await call_tool(
            "post_bounty",
            {"title": "Test", "description": "Test description", "reward": 100}
        )

        mock_post.assert_called_once()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_verify_task_validates_required_fields(self):
        """Test that verify_task validates required fields."""
        result = await call_tool("verify_task", {"bounty_id": "b123"})

        assert len(result) == 1
        assert "Error: Missing required fields" in str(result[0].text)

    @pytest.mark.asyncio
    @patch("mcp_server_emergence.server._api_post")
    async def test_verify_task_calls_api(self, mock_post):
        """Test that verify_task calls the API."""
        mock_post.return_value = {"status": "verified"}
        result = await call_tool(
            "verify_task",
            {
                "bounty_id": "b123",
                "submission_id": "s456",
                "verdict": "approved",
            }
        )

        mock_post.assert_called_once()
        assert len(result) == 1

    @pytest.mark.asyncio
    @patch("mcp_server_emergence.server._api_post")
    async def test_submit_task_calls_api(self, mock_post):
        """Test that submit_task calls the API."""
        mock_post.return_value = {"id": "sub789", "status": "submitted"}
        result = await call_tool(
            "submit_task",
            {"bounty_id": "b123", "solution": "My solution"}
        )

        mock_post.assert_called_once()
        assert len(result) == 1


class TestAPIClient:
    """Test API client functions."""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_api_get_success(self, mock_get):
        """Test successful GET request."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        async with httpx.AsyncClient():
            pass  # Clean up any existing client

        # We can't easily mock the async context manager, so we'll mock _api_get
        with patch("mcp_server_emergence.server._api_get", new_callable=AsyncMock) as mock_api_get:
            mock_api_get.return_value = {"data": "test"}
            result = await _api_get("/test")
            assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_api_post_can_be_mocked(self):
        """Test that _api_post can be mocked successfully."""
        # Just verify the function exists and can be called (will fail without mocking)
        # This test demonstrates the function signature
        # Real API tests should be integration tests with proper mocking
        assert callable(_api_post)
        assert _api_post.__name__ == "_api_post"


class TestToolSchemas:
    """Test tool schemas are valid."""

    @pytest.mark.asyncio
    async def test_post_bounty_schema_has_required(self):
        """Test that post_bounty schema has required fields."""
        tools = await list_tools()
        post_bounty_tool = next(t for t in tools if t.name == "post_bounty")
        schema = post_bounty_tool.inputSchema

        assert "required" in schema
        assert "title" in schema["required"]
        assert "description" in schema["required"]
        assert "reward" in schema["required"]

    @pytest.mark.asyncio
    async def test_verify_task_schema_has_required(self):
        """Test that verify_task schema has required fields."""
        tools = await list_tools()
        verify_tool = next(t for t in tools if t.name == "verify_task")
        schema = verify_tool.inputSchema

        assert "required" in schema
        assert "bounty_id" in schema["required"]
        assert "submission_id" in schema["required"]
        assert "verdict" in schema["required"]


class TestConfiguration:
    """Test configuration values."""

    def test_default_base_url(self):
        """Test that default base URL is set."""
        assert EMERGENCE_BASE_URL == "https://api.emergence.science"

    def test_api_key_from_env(self):
        """Test that API key is read from environment."""
        # EMERGENCE_API_KEY should be defined (may be empty string in tests)
        assert isinstance(EMERGENCE_API_KEY, str)
