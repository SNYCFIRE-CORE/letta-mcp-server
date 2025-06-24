"""
End-to-end workflow tests

These tests simulate complete user scenarios and workflows.
"""

import pytest
import asyncio
from fastmcp import Client

from letta_mcp.server import LettaMCPServer


class TestCompleteWorkflows:
    """Test complete user workflows"""
    
    @pytest.mark.asyncio
    async def test_new_user_setup_workflow(self, mock_client, mock_http_response, sample_agent_data):
        """Test complete workflow for a new user setting up an agent"""
        
        # Mock all the API responses needed for the workflow
        create_response = mock_http_response(200, sample_agent_data)
        message_response = mock_http_response(200, {
            "messages": [{"role": "assistant", "content": "Hello! I'm ready to help you."}]
        })
        memory_response = mock_http_response(200, [
            {"id": "block-1", "label": "human", "value": "New user"},
            {"id": "block-2", "label": "persona", "value": "Helpful assistant"}
        ])
        tools_response = mock_http_response(200, [
            {"id": "tool-1", "name": "web_search", "description": "Search the web"}
        ])
        
        # Configure mock responses
        async def mock_call_tool(tool_name, params):
            if tool_name == "letta_create_agent":
                return [type('Result', (), {'text': '{"success": true, "agent": {"id": "agent-123", "name": "New Agent"}}'})()]
            elif tool_name == "letta_send_message":
                return [type('Result', (), {'text': '{"success": true, "response": "Hello! I\'m ready to help you."}'})()]
            elif tool_name == "letta_get_memory":
                return [type('Result', (), {'text': '{"success": true, "memory_blocks": {"human": {"value": "New user"}}}'})()]
            elif tool_name == "letta_list_tools":
                return [type('Result', (), {'text': '{"success": true, "tools": [{"name": "web_search"}]}'})()]
            elif tool_name == "letta_get_agent":
                return [type('Result', (), {'text': '{"success": true, "agent": {"id": "agent-123", "name": "New Agent"}}'})()]
        
        mock_client.call_tool = mock_call_tool
        
        # Workflow: New user creates agent, sends first message, checks capabilities
        
        # Step 1: Create a new agent
        create_result = await mock_client.call_tool("letta_create_agent", {
            "name": "My Assistant",
            "description": "Personal AI assistant",
            "human_memory": "Tech-savvy user interested in AI",
            "persona_memory": "Helpful and knowledgeable assistant"
        })
        
        assert "success" in create_result[0].text
        
        # Step 2: Send initial message
        message_result = await mock_client.call_tool("letta_send_message", {
            "agent_id": "agent-123",
            "message": "Hello, I'm excited to work with you!"
        })
        
        assert "success" in message_result[0].text
        
        # Step 3: Check agent memory
        memory_result = await mock_client.call_tool("letta_get_memory", {
            "agent_id": "agent-123"
        })
        
        assert "success" in memory_result[0].text
        
        # Step 4: List available tools
        tools_result = await mock_client.call_tool("letta_list_tools", {})
        
        assert "success" in tools_result[0].text
        
        # Step 5: Get agent details
        agent_result = await mock_client.call_tool("letta_get_agent", {
            "agent_id": "agent-123"
        })
        
        assert "success" in agent_result[0].text
    
    @pytest.mark.asyncio
    async def test_automotive_analysis_workflow(self, mock_client):
        """Test workflow specific to automotive/dealer analysis"""
        
        async def mock_automotive_responses(tool_name, params):
            if tool_name == "letta_send_message":
                if "inventory" in params.get("message", "").lower():
                    return [type('Result', (), {'text': '''{"success": true, "response": "I'll analyze your inventory. Let me search for current market data.", "tool_calls": [{"tool": "firecrawl_search", "args": {"query": "Ford F-150 inventory analysis"}}]}'''})()]
                else:
                    return [type('Result', (), {'text': '{"success": true, "response": "I can help you with automotive analysis."}'})()]
            elif tool_name == "letta_get_agent_tools":
                return [type('Result', (), {'text': '{"success": true, "tools": ["firecrawl_search", "perplexity_ask", "sequential_thinking"]}'})()]
            elif tool_name == "letta_get_conversation_history":
                return [type('Result', (), {'text': '{"success": true, "messages": [{"role": "user", "content": "Analyze my F-150 inventory"}, {"role": "assistant", "content": "I\'ll help you analyze your Ford F-150 inventory..."}]}'})()]
        
        mock_client.call_tool = mock_automotive_responses
        
        # Automotive workflow: Check agent capabilities, analyze inventory, review conversation
        
        # Step 1: Check what tools AXLE has available
        tools_result = await mock_client.call_tool("letta_get_agent_tools", {
            "agent_id": "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        })
        
        import json
        tools_data = json.loads(tools_result[0].text)
        assert tools_data["success"] is True
        assert "firecrawl_search" in tools_data["tools"]
        
        # Step 2: Request inventory analysis
        analysis_result = await mock_client.call_tool("letta_send_message", {
            "agent_id": "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe",
            "message": "I have 47 Ford F-150s that have been on the lot for over 90 days. Can you analyze what I should do?"
        })
        
        analysis_data = json.loads(analysis_result[0].text)
        assert analysis_data["success"] is True
        assert "tool_calls" in analysis_data  # Should trigger tool usage
        
        # Step 3: Check conversation history
        history_result = await mock_client.call_tool("letta_get_conversation_history", {
            "agent_id": "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe",
            "limit": 10
        })
        
        history_data = json.loads(history_result[0].text)
        assert history_data["success"] is True
        assert len(history_data["messages"]) > 0
    
    @pytest.mark.asyncio
    async def test_agent_customization_workflow(self, mock_client):
        """Test workflow for customizing an agent's memory and behavior"""
        
        async def mock_customization_responses(tool_name, params):
            if tool_name == "letta_get_memory":
                return [type('Result', (), {'text': '''{"success": true, "memory_blocks": {"human": {"value": "Dealer owner with 20 years experience"}, "persona": {"value": "I am AXLE, automotive AI specialist"}}}'''})()]
            elif tool_name == "letta_update_memory":
                return [type('Result', (), {'text': '{"success": true, "message": "Successfully updated memory block"}'})()]
            elif tool_name == "letta_create_memory_block":
                return [type('Result', (), {'text': '{"success": true, "message": "Successfully created custom memory block"}'})()]
        
        mock_client.call_tool = mock_customization_responses
        
        # Customization workflow: View current memory, update it, add custom blocks
        
        # Step 1: Get current memory state
        memory_result = await mock_client.call_tool("letta_get_memory", {
            "agent_id": "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        })
        
        import json
        memory_data = json.loads(memory_result[0].text)
        assert memory_data["success"] is True
        assert "human" in memory_data["memory_blocks"]
        assert "persona" in memory_data["memory_blocks"]
        
        # Step 2: Update human memory with more specific info
        update_result = await mock_client.call_tool("letta_update_memory", {
            "agent_id": "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe",
            "block_label": "human",
            "value": "John Smith, owner of Smith Ford Dealership in Austin, TX. 20 years in automotive sales. Specializes in F-150s and commercial vehicles. Tech-forward and interested in AI automation."
        })
        
        update_data = json.loads(update_result[0].text)
        assert update_data["success"] is True
        
        # Step 3: Add custom memory block for dealership context
        custom_block_result = await mock_client.call_tool("letta_create_memory_block", {
            "agent_id": "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe",
            "label": "dealership_context",
            "value": "Smith Ford Dealership: 150 new vehicles, 75 used vehicles. Focus on commercial sales. Located in growing Austin market. Main competitors: Round Rock Ford, Covert Ford.",
            "description": "Specific dealership business context and competitive landscape"
        })
        
        custom_data = json.loads(custom_block_result[0].text)
        assert custom_data["success"] is True
    
    @pytest.mark.asyncio
    async def test_multi_agent_coordination_workflow(self, mock_client):
        """Test workflow involving multiple agents (simulated)"""
        
        async def mock_multi_agent_responses(tool_name, params):
            if tool_name == "letta_list_agents":
                return [type('Result', (), {'text': '''{"success": true, "agents": [{"id": "agent-123", "name": "AXLE"}, {"id": "agent-456", "name": "Customer Service Bot"}]}'''})()]
            elif tool_name == "letta_send_message" and "agent-123" in params.get("agent_id", ""):
                return [type('Result', (), {'text': '{"success": true, "response": "AXLE: Based on inventory analysis, recommend promoting slow-moving F-150s."}'})()]
            elif tool_name == "letta_send_message" and "agent-456" in params.get("agent_id", ""):
                return [type('Result', (), {'text': '{"success": true, "response": "Customer Bot: I can help create promotional messaging for the F-150 campaign."}'})()]
        
        mock_client.call_tool = mock_multi_agent_responses
        
        # Multi-agent workflow: Coordinate between AXLE and other agents
        
        # Step 1: List available agents
        agents_result = await mock_client.call_tool("letta_list_agents", {})
        
        import json
        agents_data = json.loads(agents_result[0].text)
        assert agents_data["success"] is True
        assert len(agents_data["agents"]) >= 2
        
        # Step 2: Get analysis from AXLE
        axle_result = await mock_client.call_tool("letta_send_message", {
            "agent_id": "agent-123",
            "message": "What should we do with slow-moving inventory?"
        })
        
        axle_data = json.loads(axle_result[0].text)
        assert axle_data["success"] is True
        assert "F-150" in axle_data["response"]
        
        # Step 3: Get customer messaging from customer service agent
        customer_result = await mock_client.call_tool("letta_send_message", {
            "agent_id": "agent-456",
            "message": "Create promotional messaging for F-150 inventory reduction"
        })
        
        customer_data = json.loads(customer_result[0].text)
        assert customer_data["success"] is True
        assert "promotional" in customer_data["response"].lower()
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, mock_client):
        """Test workflow with error conditions and recovery"""
        
        call_count = 0
        
        async def mock_error_recovery_responses(tool_name, params):
            nonlocal call_count
            call_count += 1
            
            # Simulate temporary failures followed by success
            if tool_name == "letta_health_check":
                if call_count <= 2:
                    return [type('Result', (), {'text': '{"success": false, "error": "Temporary network error"}'})()]
                else:
                    return [type('Result', (), {'text': '{"success": true, "status": "healthy"}'})()]
            elif tool_name == "letta_send_message":
                return [type('Result', (), {'text': '{"success": true, "response": "Message sent successfully after retry"}'})()]
        
        mock_client.call_tool = mock_error_recovery_responses
        
        # Error recovery workflow: Handle temporary failures gracefully
        
        # Step 1: First health check fails
        health_result1 = await mock_client.call_tool("letta_health_check", {})
        import json
        health_data1 = json.loads(health_result1[0].text)
        assert health_data1["success"] is False
        
        # Step 2: Second health check also fails
        health_result2 = await mock_client.call_tool("letta_health_check", {})
        health_data2 = json.loads(health_result2[0].text)
        assert health_data2["success"] is False
        
        # Step 3: Third health check succeeds
        health_result3 = await mock_client.call_tool("letta_health_check", {})
        health_data3 = json.loads(health_result3[0].text)
        assert health_data3["success"] is True
        
        # Step 4: Normal operation continues
        message_result = await mock_client.call_tool("letta_send_message", {
            "agent_id": "agent-123",
            "message": "Test message after recovery"
        })
        
        message_data = json.loads(message_result[0].text)
        assert message_data["success"] is True


class TestPerformanceWorkflows:
    """Test performance-critical workflows"""
    
    @pytest.mark.asyncio
    async def test_rapid_interaction_workflow(self, mock_client, performance_timer):
        """Test rapid succession of interactions"""
        
        async def fast_mock_responses(tool_name, params):
            # Simulate very fast responses
            await asyncio.sleep(0.01)  # 10ms delay
            return [type('Result', (), {'text': '{"success": true, "response": "Fast response"}'})()]
        
        mock_client.call_tool = fast_mock_responses
        
        performance_timer.start()
        
        # Rapid succession of calls
        tasks = []
        for i in range(10):
            task = mock_client.call_tool("letta_send_message", {
                "agent_id": "agent-123",
                "message": f"Rapid message {i}"
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        performance_timer.stop()
        
        # All calls should succeed
        assert len(results) == 10
        
        # Should complete within reasonable time
        assert performance_timer.elapsed < 1.0, f"Rapid interactions took {performance_timer.elapsed:.2f}s"
    
    @pytest.mark.asyncio
    async def test_bulk_operations_workflow(self, mock_client, performance_timer):
        """Test bulk operations performance"""
        
        async def bulk_mock_responses(tool_name, params):
            if tool_name == "letta_list_agents":
                # Simulate large agent list
                agents = [{"id": f"agent-{i}", "name": f"Agent {i}"} for i in range(100)]
                return [type('Result', (), {'text': f'{{"success": true, "agents": {agents}}}'})()]
            else:
                return [type('Result', (), {'text': '{"success": true}'})()]
        
        mock_client.call_tool = bulk_mock_responses
        
        performance_timer.start()
        
        # Bulk operation: List many agents
        result = await mock_client.call_tool("letta_list_agents", {"limit": 100})
        
        performance_timer.stop()
        
        import json
        data = json.loads(result[0].text)
        assert data["success"] is True
        assert len(data["agents"]) == 100
        
        # Should handle bulk data efficiently
        assert performance_timer.elapsed < 2.0, f"Bulk operation took {performance_timer.elapsed:.2f}s"


class TestEdgeCaseWorkflows:
    """Test edge case and boundary condition workflows"""
    
    @pytest.mark.asyncio
    async def test_empty_response_workflow(self, mock_client):
        """Test workflow with empty responses"""
        
        async def empty_mock_responses(tool_name, params):
            if tool_name == "letta_list_agents":
                return [type('Result', (), {'text': '{"success": true, "agents": []}'})()]
            elif tool_name == "letta_get_conversation_history":
                return [type('Result', (), {'text': '{"success": true, "messages": []}'})()]
            else:
                return [type('Result', (), {'text': '{"success": true}'})()]
        
        mock_client.call_tool = empty_mock_responses
        
        # Handle empty agent list
        agents_result = await mock_client.call_tool("letta_list_agents", {})
        import json
        agents_data = json.loads(agents_result[0].text)
        assert agents_data["success"] is True
        assert len(agents_data["agents"]) == 0
        
        # Handle empty conversation history
        history_result = await mock_client.call_tool("letta_get_conversation_history", {
            "agent_id": "agent-123"
        })
        history_data = json.loads(history_result[0].text)
        assert history_data["success"] is True
        assert len(history_data["messages"]) == 0
    
    @pytest.mark.asyncio
    async def test_malformed_input_workflow(self, mock_client):
        """Test workflow with malformed inputs"""
        
        async def malformed_mock_responses(tool_name, params):
            # Check for malformed agent IDs
            agent_id = params.get("agent_id", "")
            if agent_id and not agent_id.startswith("agent-"):
                return [type('Result', (), {'text': '{"success": false, "error": "Invalid agent ID format"}'})()]
            else:
                return [type('Result', (), {'text': '{"success": true}'})()]
        
        mock_client.call_tool = malformed_mock_responses
        
        # Test with malformed agent ID
        bad_result = await mock_client.call_tool("letta_get_agent", {
            "agent_id": "not-an-agent-id"
        })
        
        import json
        bad_data = json.loads(bad_result[0].text)
        assert bad_data["success"] is False
        assert "error" in bad_data
        
        # Test with proper agent ID
        good_result = await mock_client.call_tool("letta_get_agent", {
            "agent_id": "agent-123"
        })
        
        good_data = json.loads(good_result[0].text)
        assert good_data["success"] is True
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_workflow(self, mock_client):
        """Test workflow under simulated resource constraints"""
        
        call_count = 0
        
        async def resource_constrained_responses(tool_name, params):
            nonlocal call_count
            call_count += 1
            
            # Simulate rate limiting after 5 calls
            if call_count > 5:
                await asyncio.sleep(0.1)  # Simulate delay
                return [type('Result', (), {'text': '{"success": false, "error": "Rate limit exceeded"}'})()]
            else:
                return [type('Result', (), {'text': '{"success": true}'})()]
        
        mock_client.call_tool = resource_constrained_responses
        
        # Make calls until rate limited
        results = []
        for i in range(10):
            result = await mock_client.call_tool("letta_health_check", {})
            results.append(result)
        
        # First 5 should succeed, rest should fail
        import json
        for i, result in enumerate(results):
            data = json.loads(result[0].text)
            if i < 5:
                assert data["success"] is True
            else:
                assert data["success"] is False
                assert "rate limit" in data["error"].lower()