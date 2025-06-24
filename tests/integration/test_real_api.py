"""
Integration tests with real Letta API

These tests require a valid Letta API key and test against the actual API.
Set RUN_INTEGRATION_TESTS=1 to enable these tests.
"""

import os
import pytest
import asyncio
from fastmcp import Client

from letta_mcp.server import LettaMCPServer
from letta_mcp.config import LettaConfig


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS", "").lower() in ("1", "true", "yes"),
    reason="Integration tests require RUN_INTEGRATION_TESTS=1"
)


class TestRealAPIConnection:
    """Test real API connection and basic functionality"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, real_client):
        """Test health check against real API"""
        result = await real_client.call_tool("letta_health_check", {})
        
        # Extract the result content
        response = result[0].text
        assert "success" in response
        
        # Parse if it's JSON string
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            assert response_data["success"] is True
            assert response_data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_list_agents(self, real_client):
        """Test listing agents from real API"""
        result = await real_client.call_tool("letta_list_agents", {})
        
        response = result[0].text
        assert "success" in response
        
        # Parse response
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            assert response_data["success"] is True
            assert "agents" in response_data
            assert isinstance(response_data["agents"], list)
    
    @pytest.mark.asyncio
    async def test_get_axle_agent(self, real_client):
        """Test getting the specific AXLE agent"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        result = await real_client.call_tool("letta_get_agent", {"agent_id": agent_id})
        
        response = result[0].text
        assert "success" in response
        
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            assert response_data["success"] is True
            assert response_data["agent"]["id"] == agent_id
    
    @pytest.mark.asyncio
    async def test_get_axle_memory(self, real_client):
        """Test getting AXLE agent memory"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        result = await real_client.call_tool("letta_get_memory", {"agent_id": agent_id})
        
        response = result[0].text
        assert "success" in response
        
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            assert response_data["success"] is True
            assert "memory_blocks" in response_data
            
            # AXLE should have human and persona blocks
            memory_blocks = response_data["memory_blocks"]
            assert "human" in memory_blocks or "persona" in memory_blocks
    
    @pytest.mark.asyncio
    async def test_list_tools(self, real_client):
        """Test listing available tools"""
        result = await real_client.call_tool("letta_list_tools", {})
        
        response = result[0].text
        assert "success" in response
        
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            assert response_data["success"] is True
            assert "tools" in response_data
    
    @pytest.mark.asyncio
    async def test_get_axle_tools(self, real_client):
        """Test getting tools attached to AXLE agent"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        result = await real_client.call_tool("letta_get_agent_tools", {"agent_id": agent_id})
        
        response = result[0].text
        assert "success" in response
        
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            assert response_data["success"] is True
            assert "tools" in response_data
            
            # AXLE should have multiple tools including firecrawl tools
            tools = response_data["tools"]
            assert len(tools) > 0


class TestRealAPIMessaging:
    """Test real API messaging functionality"""
    
    @pytest.mark.asyncio
    async def test_send_simple_message_to_axle(self, real_client):
        """Test sending a simple message to AXLE agent"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        result = await real_client.call_tool("letta_send_message", {
            "agent_id": agent_id,
            "message": "Hello AXLE, this is a test message from the integration test suite.",
            "stream": False
        })
        
        response = result[0].text
        assert "success" in response
        
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            assert response_data["success"] is True
            assert "response" in response_data
            assert len(response_data["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_conversation_history(self, real_client):
        """Test getting conversation history"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        result = await real_client.call_tool("letta_get_conversation_history", {
            "agent_id": agent_id,
            "limit": 5
        })
        
        response = result[0].text
        assert "success" in response
        
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            assert response_data["success"] is True
            assert "messages" in response_data
    
    @pytest.mark.asyncio
    async def test_search_memory(self, real_client):
        """Test searching through agent memory"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        result = await real_client.call_tool("letta_search_memory", {
            "agent_id": agent_id,
            "query": "automotive",
            "limit": 3
        })
        
        response = result[0].text
        # Note: This might fail if search endpoint doesn't exist,
        # but should handle gracefully
        assert "success" in response or "error" in response


class TestRealAPIErrorHandling:
    """Test error handling with real API"""
    
    @pytest.mark.asyncio
    async def test_invalid_agent_id(self, real_client):
        """Test behavior with invalid agent ID"""
        result = await real_client.call_tool("letta_get_agent", {
            "agent_id": "invalid-agent-id-12345"
        })
        
        response = result[0].text
        
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            # Should gracefully handle invalid agent ID
            assert response_data["success"] is False
            assert "error" in response_data
    
    @pytest.mark.asyncio
    async def test_nonexistent_agent(self, real_client):
        """Test behavior with properly formatted but nonexistent agent ID"""
        fake_agent_id = "agent-12345678-1234-1234-1234-123456789abc"
        
        result = await real_client.call_tool("letta_get_agent", {
            "agent_id": fake_agent_id
        })
        
        response = result[0].text
        
        import json
        if response.startswith('{'):
            response_data = json.loads(response)
            # Should handle nonexistent agent gracefully
            assert response_data["success"] is False or "error" in response_data
    
    @pytest.mark.asyncio
    async def test_missing_required_parameters(self, real_client):
        """Test behavior when required parameters are missing"""
        # This should be handled by FastMCP parameter validation
        with pytest.raises(Exception):
            await real_client.call_tool("letta_get_agent", {})


class TestRealAPIPerformance:
    """Test performance characteristics of real API"""
    
    @pytest.mark.asyncio
    async def test_response_time_health_check(self, real_client, performance_timer):
        """Test response time for health check"""
        performance_timer.start()
        
        await real_client.call_tool("letta_health_check", {})
        
        performance_timer.stop()
        
        # Health check should be fast (under 5 seconds)
        assert performance_timer.elapsed < 5.0, f"Health check took {performance_timer.elapsed:.2f}s"
    
    @pytest.mark.asyncio
    async def test_response_time_list_agents(self, real_client, performance_timer):
        """Test response time for listing agents"""
        performance_timer.start()
        
        await real_client.call_tool("letta_list_agents", {"limit": 10})
        
        performance_timer.stop()
        
        # List agents should be reasonably fast (under 10 seconds)
        assert performance_timer.elapsed < 10.0, f"List agents took {performance_timer.elapsed:.2f}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, real_client):
        """Test handling of concurrent requests"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        # Create multiple concurrent requests
        tasks = [
            real_client.call_tool("letta_health_check", {}),
            real_client.call_tool("letta_get_agent", {"agent_id": agent_id}),
            real_client.call_tool("letta_list_tools", {}),
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should succeed or fail gracefully
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent request failed: {result}")
            
            assert len(result) > 0  # Should have response content


class TestRealAPIResources:
    """Test MCP resources with real API"""
    
    @pytest.mark.asyncio
    async def test_agents_resource(self, real_client):
        """Test the agents resource"""
        resources = await real_client.list_resources()
        
        # Should have letta://agents resource
        resource_uris = [r.uri for r in resources]
        assert "letta://agents" in resource_uris
        
        # Try to read the resource
        content = await real_client.read_resource("letta://agents")
        assert content is not None
    
    @pytest.mark.asyncio
    async def test_tools_resource(self, real_client):
        """Test the tools resource"""
        resources = await real_client.list_resources()
        
        resource_uris = [r.uri for r in resources]
        assert "letta://tools" in resource_uris
        
        content = await real_client.read_resource("letta://tools")
        assert content is not None
    
    @pytest.mark.asyncio
    async def test_health_resource(self, real_client):
        """Test the health resource"""
        resources = await real_client.list_resources()
        
        resource_uris = [r.uri for r in resources]
        assert "letta://health" in resource_uris
        
        content = await real_client.read_resource("letta://health")
        assert content is not None
        
        # Parse the content and verify it's valid health data
        import json
        if content.startswith('{'):
            health_data = json.loads(content)
            assert "success" in health_data
    
    @pytest.mark.asyncio
    async def test_agent_specific_resource(self, real_client):
        """Test agent-specific resources"""
        agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        
        # Test agent info resource
        agent_uri = f"letta://agent/{agent_id}"
        content = await real_client.read_resource(agent_uri)
        assert content is not None
        
        # Test agent memory resource
        memory_uri = f"letta://agent/{agent_id}/memory"
        memory_content = await real_client.read_resource(memory_uri)
        assert memory_content is not None


class TestRealAPIStressTest:
    """Stress tests for real API (only run if explicitly enabled)"""
    
    @pytest.mark.skipif(
        not os.getenv("RUN_STRESS_TESTS", "").lower() in ("1", "true", "yes"),
        reason="Stress tests require RUN_STRESS_TESTS=1"
    )
    @pytest.mark.asyncio
    async def test_rapid_health_checks(self, real_client):
        """Test rapid successive health checks"""
        num_requests = 20
        
        start_time = asyncio.get_event_loop().time()
        
        # Make rapid requests
        tasks = [
            real_client.call_tool("letta_health_check", {})
            for _ in range(num_requests)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        # Check that most requests succeeded
        successful_requests = sum(1 for r in results if not isinstance(r, Exception))
        success_rate = successful_requests / num_requests
        
        # Should have at least 80% success rate
        assert success_rate >= 0.8, f"Success rate: {success_rate:.2%}"
        
        # Average response time should be reasonable
        avg_time = total_time / num_requests
        assert avg_time < 2.0, f"Average response time: {avg_time:.2f}s"
    
    @pytest.mark.skipif(
        not os.getenv("RUN_STRESS_TESTS", "").lower() in ("1", "true", "yes"),
        reason="Stress tests require RUN_STRESS_TESTS=1"
    )
    @pytest.mark.asyncio
    async def test_sustained_load(self, real_client):
        """Test sustained load over time"""
        duration_seconds = 30
        request_interval = 0.5  # Request every 500ms
        
        start_time = asyncio.get_event_loop().time()
        results = []
        
        while (asyncio.get_event_loop().time() - start_time) < duration_seconds:
            try:
                result = await real_client.call_tool("letta_health_check", {})
                results.append(True)
            except Exception as e:
                results.append(False)
                print(f"Request failed: {e}")
            
            await asyncio.sleep(request_interval)
        
        # Analyze results
        total_requests = len(results)
        successful_requests = sum(results)
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        print(f"Sustained load test: {successful_requests}/{total_requests} requests succeeded ({success_rate:.2%})")
        
        # Should maintain reasonable success rate under sustained load
        assert success_rate >= 0.7, f"Success rate under load: {success_rate:.2%}"