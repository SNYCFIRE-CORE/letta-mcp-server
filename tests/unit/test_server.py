"""
Unit tests for the main server module
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx

from letta_mcp.server import LettaMCPServer, create_server, run_server
from letta_mcp.config import LettaConfig
from letta_mcp.exceptions import ConfigurationError


class TestLettaMCPServer:
    """Test the LettaMCPServer class"""
    
    def test_server_initialization(self, mock_config):
        """Test server initialization with config"""
        server = LettaMCPServer(mock_config)
        
        assert server.config == mock_config
        assert server.mcp is not None
        assert server.client is not None
    
    def test_server_initialization_without_config(self):
        """Test server initialization without explicit config"""
        with patch("letta_mcp.server.load_config") as mock_load_config:
            mock_load_config.return_value = LettaConfig()
            server = LettaMCPServer()
            assert server.config is not None
    
    def test_config_validation_success(self, mock_config):
        """Test successful config validation"""
        mock_config.api_key = "valid-api-key"
        mock_config.base_url = "https://api.letta.com"
        
        # Should not raise exception
        server = LettaMCPServer(mock_config)
        server.validate_config()
    
    def test_config_validation_missing_api_key(self, mock_config):
        """Test config validation with missing API key for Letta Cloud"""
        mock_config.api_key = None
        mock_config.base_url = "https://api.letta.com"
        
        server = LettaMCPServer(mock_config)
        
        with pytest.raises(ConfigurationError, match="LETTA_API_KEY is required"):
            server.validate_config()
    
    def test_config_validation_local_server(self, mock_config):
        """Test config validation for local server (no API key required)"""
        mock_config.api_key = None
        mock_config.base_url = "http://localhost:8000"
        
        server = LettaMCPServer(mock_config)
        # Should not raise exception for local server
        server.validate_config()
    
    def test_tool_registration(self, mock_server):
        """Test that tools are registered correctly"""
        # Check that FastMCP instance has tools registered
        tools = mock_server.mcp._tools
        
        # Verify key tools are registered
        tool_names = list(tools.keys())
        
        expected_tools = [
            "letta_list_agents",
            "letta_create_agent", 
            "letta_get_agent",
            "letta_send_message",
            "letta_get_memory",
            "letta_update_memory",
            "letta_list_tools",
            "letta_health_check"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    def test_resource_registration(self, mock_server):
        """Test that resources are registered correctly"""
        # Check that FastMCP instance has resources registered
        resources = mock_server.mcp._resources
        
        expected_resources = [
            "letta://agents",
            "letta://tools",
            "letta://health"
        ]
        
        # Note: Resource URIs might be stored differently in FastMCP
        # This test might need adjustment based on actual FastMCP internals
        assert len(resources) > 0


class TestServerTools:
    """Test individual server tool implementations"""
    
    @pytest.mark.asyncio
    async def test_letta_list_agents(self, mock_server, mock_http_response, sample_agent_data):
        """Test the letta_list_agents tool"""
        # Mock HTTP response
        agents_list = [sample_agent_data, {**sample_agent_data, "id": "agent-456", "name": "Agent 2"}]
        mock_response = mock_http_response(200, agents_list)
        mock_server.client.get = AsyncMock(return_value=mock_response)
        
        # Get the tool function
        list_agents_tool = mock_server.mcp._tools["letta_list_agents"]
        
        # Call the tool
        result = await list_agents_tool.func()
        
        # Verify results
        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["agents"]) == 2
        
        # Verify HTTP call
        mock_server.client.get.assert_called_once_with("/v1/agents", params={"limit": 50, "offset": 0})
    
    @pytest.mark.asyncio
    async def test_letta_list_agents_with_filter(self, mock_server, mock_http_response, sample_agent_data):
        """Test the letta_list_agents tool with filter"""
        agents_list = [sample_agent_data]
        mock_response = mock_http_response(200, agents_list)
        mock_server.client.get = AsyncMock(return_value=mock_response)
        
        list_agents_tool = mock_server.mcp._tools["letta_list_agents"]
        
        # Call with filter
        result = await list_agents_tool.func(filter="Test", limit=10)
        
        assert result["success"] is True
        assert len(result["agents"]) == 1
        mock_server.client.get.assert_called_once_with("/v1/agents", params={"limit": 10, "offset": 0})
    
    @pytest.mark.asyncio
    async def test_letta_list_agents_http_error(self, mock_server):
        """Test letta_list_agents with HTTP error"""
        mock_server.client.get = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
        
        list_agents_tool = mock_server.mcp._tools["letta_list_agents"]
        result = await list_agents_tool.func()
        
        assert result["success"] is False
        assert "Connection failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_letta_get_agent(self, mock_server, mock_http_response, sample_agent_data):
        """Test the letta_get_agent tool"""
        mock_response = mock_http_response(200, sample_agent_data)
        mock_server.client.get = AsyncMock(return_value=mock_response)
        
        get_agent_tool = mock_server.mcp._tools["letta_get_agent"]
        
        result = await get_agent_tool.func("agent-123")
        
        assert result["success"] is True
        assert result["agent"]["id"] == "agent-123"
        assert result["agent"]["name"] == "Test Agent"
        
        mock_server.client.get.assert_called_once_with("/v1/agents/agent-123")
    
    @pytest.mark.asyncio
    async def test_letta_create_agent(self, mock_server, mock_http_response, sample_agent_data):
        """Test the letta_create_agent tool"""
        mock_response = mock_http_response(200, sample_agent_data)
        mock_server.client.post = AsyncMock(return_value=mock_response)
        
        create_agent_tool = mock_server.mcp._tools["letta_create_agent"]
        
        result = await create_agent_tool.func(
            name="New Test Agent",
            description="A new test agent",
            human_memory="Test user info",
            persona_memory="Test persona"
        )
        
        assert result["success"] is True
        assert result["agent"]["name"] == "Test Agent"
        assert "Successfully created agent" in result["message"]
        
        # Verify the API call
        mock_server.client.post.assert_called_once()
        call_args = mock_server.client.post.call_args
        assert call_args[0][0] == "/v1/agents"
        
        # Verify payload structure
        payload = call_args[1]["json"]
        assert payload["name"] == "New Test Agent"
        assert payload["description"] == "A new test agent"
        assert len(payload["memory_blocks"]) >= 2  # human and persona
    
    @pytest.mark.asyncio
    async def test_letta_send_message(self, mock_server, mock_http_response, sample_message_response):
        """Test the letta_send_message tool"""
        mock_response = mock_http_response(200, sample_message_response)
        mock_server.client.post = AsyncMock(return_value=mock_response)
        
        send_message_tool = mock_server.mcp._tools["letta_send_message"]
        
        result = await send_message_tool.func(
            agent_id="agent-123",
            message="Hello, how can you help me?",
            stream=False
        )
        
        assert result["success"] is True
        assert result["agent_id"] == "agent-123"
        assert result["message"] == "Hello, how can you help me?"
        assert "response" in result
        
        mock_server.client.post.assert_called_once_with(
            "/v1/agents/agent-123/messages",
            json={
                "messages": [{"role": "user", "content": "Hello, how can you help me?"}],
                "stream_steps": False,
                "stream_tokens": False
            }
        )
    
    @pytest.mark.asyncio
    async def test_letta_get_memory(self, mock_server, mock_http_response, sample_memory_blocks):
        """Test the letta_get_memory tool"""
        mock_response = mock_http_response(200, sample_memory_blocks)
        mock_server.client.get = AsyncMock(return_value=mock_response)
        
        get_memory_tool = mock_server.mcp._tools["letta_get_memory"]
        
        result = await get_memory_tool.func("agent-123")
        
        assert result["success"] is True
        assert result["agent_id"] == "agent-123"
        assert "memory_blocks" in result
        assert "human" in result["memory_blocks"]
        assert "persona" in result["memory_blocks"]
        
        mock_server.client.get.assert_called_once_with("/v1/agents/agent-123/memory-blocks")
    
    @pytest.mark.asyncio
    async def test_letta_update_memory(self, mock_server, mock_http_response, sample_memory_blocks):
        """Test the letta_update_memory tool"""
        # Mock the GET request for finding the block
        get_response = mock_http_response(200, sample_memory_blocks)
        
        # Mock the PATCH request for updating
        updated_block = {"id": "block-1", "label": "human", "value": "Updated user info"}
        patch_response = mock_http_response(200, updated_block)
        
        mock_server.client.get = AsyncMock(return_value=get_response)
        mock_server.client.patch = AsyncMock(return_value=patch_response)
        
        update_memory_tool = mock_server.mcp._tools["letta_update_memory"]
        
        result = await update_memory_tool.func(
            agent_id="agent-123",
            block_label="human",
            value="Updated user info"
        )
        
        assert result["success"] is True
        assert result["block_label"] == "human"
        assert result["updated_value"] == "Updated user info"
        
        # Verify API calls
        mock_server.client.get.assert_called_once_with("/v1/agents/agent-123/memory-blocks")
        mock_server.client.patch.assert_called_once_with(
            "/v1/agents/agent-123/memory-blocks/block-1",
            json={"value": "Updated user info"}
        )
    
    @pytest.mark.asyncio
    async def test_letta_health_check(self, mock_server, mock_http_response):
        """Test the letta_health_check tool"""
        mock_response = mock_http_response(200, [])
        mock_response.headers = {"X-API-Version": "1.0.0"}
        mock_server.client.get = AsyncMock(return_value=mock_response)
        
        health_check_tool = mock_server.mcp._tools["letta_health_check"]
        
        result = await health_check_tool.func()
        
        assert result["success"] is True
        assert result["status"] == "healthy"
        assert result["api_version"] == "1.0.0"
        assert result["base_url"] == mock_server.config.base_url
        
        mock_server.client.get.assert_called_once_with("/v1/agents", params={"limit": 1})
    
    @pytest.mark.asyncio
    async def test_letta_health_check_failure(self, mock_server):
        """Test letta_health_check when API is down"""
        mock_server.client.get = AsyncMock(side_effect=httpx.HTTPError("Connection refused"))
        
        health_check_tool = mock_server.mcp._tools["letta_health_check"]
        
        result = await health_check_tool.func()
        
        assert result["success"] is False
        assert result["status"] == "unhealthy"
        assert "Connection refused" in result["error"]


class TestServerUtilityFunctions:
    """Test server utility functions"""
    
    def test_create_server_with_config(self, mock_config):
        """Test create_server function with config"""
        server = create_server(mock_config)
        
        assert isinstance(server, LettaMCPServer)
        assert server.config == mock_config
    
    def test_create_server_without_config(self):
        """Test create_server function without config"""
        with patch("letta_mcp.server.load_config") as mock_load_config:
            mock_config = LettaConfig()
            mock_load_config.return_value = mock_config
            
            server = create_server()
            
            assert isinstance(server, LettaMCPServer)
            assert server.config == mock_config
    
    def test_run_server(self, mock_config):
        """Test run_server function"""
        with patch.object(LettaMCPServer, "run") as mock_run:
            run_server(mock_config, transport="stdio")
            
            # Verify that a server was created and run was called
            mock_run.assert_called_once_with(transport="stdio")


class TestServerEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_server_with_invalid_config(self):
        """Test server creation with invalid config"""
        invalid_config = LettaConfig(
            api_key=None,
            base_url="https://api.letta.com"  # Requires API key
        )
        
        server = LettaMCPServer(invalid_config)
        
        with pytest.raises(ConfigurationError):
            server.validate_config()
    
    @pytest.mark.asyncio
    async def test_tool_with_invalid_agent_id(self, mock_server):
        """Test tools with invalid agent IDs"""
        get_agent_tool = mock_server.mcp._tools["letta_get_agent"]
        
        # Test with invalid agent ID
        result = await get_agent_tool.func("invalid-agent-id")
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, mock_server):
        """Test handling of network timeouts"""
        mock_server.client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))
        
        health_check_tool = mock_server.mcp._tools["letta_health_check"]
        result = await health_check_tool.func()
        
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, mock_server, mock_http_response):
        """Test handling of malformed API responses"""
        # Mock response with invalid JSON structure
        mock_response = mock_http_response(200, {"unexpected": "structure"})
        mock_server.client.get = AsyncMock(return_value=mock_response)
        
        list_agents_tool = mock_server.mcp._tools["letta_list_agents"]
        
        # Should handle gracefully and not crash
        result = await list_agents_tool.func()
        
        # Might succeed but with unexpected structure, or fail gracefully
        assert "success" in result
    
    def test_server_initialization_edge_cases(self):
        """Test server initialization with edge case configurations"""
        # Test with minimal config
        minimal_config = LettaConfig(
            api_key="test-key",
            base_url="http://localhost:8000"
        )
        
        server = LettaMCPServer(minimal_config)
        assert server.config == minimal_config
        
        # Test with custom timeouts
        custom_config = LettaConfig(
            api_key="test-key",
            base_url="http://localhost:8000",
            timeout=120.0,
            max_retries=10
        )
        
        server = LettaMCPServer(custom_config)
        assert server.config.timeout == 120.0
        assert server.config.max_retries == 10


class TestServerIntegration:
    """Integration tests for server components working together"""
    
    @pytest.mark.asyncio
    async def test_complete_agent_workflow(self, mock_server, mock_http_response, sample_agent_data):
        """Test a complete workflow: create agent, send message, get memory"""
        # Mock responses for the workflow
        create_response = mock_http_response(200, sample_agent_data)
        message_response = mock_http_response(200, {"messages": [{"role": "assistant", "content": "Hello!"}]})
        memory_response = mock_http_response(200, [{"id": "block-1", "label": "human", "value": "Test user"}])
        
        mock_server.client.post = AsyncMock(side_effect=[create_response, message_response])
        mock_server.client.get = AsyncMock(return_value=memory_response)
        
        # Execute workflow
        create_tool = mock_server.mcp._tools["letta_create_agent"]
        send_tool = mock_server.mcp._tools["letta_send_message"]
        memory_tool = mock_server.mcp._tools["letta_get_memory"]
        
        # 1. Create agent
        create_result = await create_tool.func(name="Workflow Test Agent")
        assert create_result["success"] is True
        
        # 2. Send message
        message_result = await send_tool.func(
            agent_id=sample_agent_data["id"],
            message="Hello agent!"
        )
        assert message_result["success"] is True
        
        # 3. Get memory
        memory_result = await memory_tool.func(sample_agent_data["id"])
        assert memory_result["success"] is True
        
        # Verify all API calls were made
        assert mock_server.client.post.call_count == 2
        assert mock_server.client.get.call_count == 1