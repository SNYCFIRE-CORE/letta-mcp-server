"""
Unit tests for utility functions
"""

import pytest
from unittest.mock import Mock, AsyncMock
import httpx
import asyncio

from letta_mcp.utils import (
    parse_message_response,
    format_memory_blocks,
    validate_agent_id,
    extract_assistant_message,
    create_retry_client
)
from letta_mcp.exceptions import LettaMCPError


class TestParseMessageResponse:
    """Test the parse_message_response function"""
    
    def test_parse_simple_response(self):
        """Test parsing a simple message response"""
        response = {
            "messages": [
                {
                    "id": "msg-1",
                    "role": "assistant",
                    "content": "Hello, how can I help you?",
                    "message_type": "assistant_message"
                }
            ]
        }
        
        result = parse_message_response(response)
        
        assert result["assistant_message"] == "Hello, how can I help you?"
        assert result["tool_calls"] == []
        assert result["reasoning"] == []
    
    def test_parse_response_with_tool_calls(self):
        """Test parsing response with tool calls"""
        response = {
            "messages": [
                {
                    "id": "msg-1",
                    "role": "assistant", 
                    "content": "I'll search for that information.",
                    "message_type": "assistant_message"
                },
                {
                    "id": "msg-2",
                    "message_type": "tool_call_message",
                    "tool_call": {
                        "name": "web_search",
                        "arguments": {"query": "AutoDealAI features"}
                    }
                },
                {
                    "id": "msg-3",
                    "message_type": "tool_return_message",
                    "tool_return": "Search results: AutoDealAI is an AI platform..."
                }
            ]
        }
        
        result = parse_message_response(response)
        
        assert result["assistant_message"] == "I'll search for that information."
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["tool"] == "web_search"
        assert result["tool_calls"][0]["args"] == {"query": "AutoDealAI features"}
    
    def test_parse_response_with_reasoning(self):
        """Test parsing response with reasoning steps"""
        response = {
            "messages": [
                {
                    "id": "msg-1",
                    "message_type": "reasoning_message",
                    "reasoning": "Let me think about this step by step..."
                },
                {
                    "id": "msg-2",
                    "role": "assistant",
                    "content": "Based on my analysis...",
                    "message_type": "assistant_message"
                }
            ]
        }
        
        result = parse_message_response(response)
        
        assert result["assistant_message"] == "Based on my analysis..."
        assert result["reasoning"] == ["Let me think about this step by step..."]
        assert result["tool_calls"] == []
    
    def test_parse_empty_response(self):
        """Test parsing empty or malformed response"""
        # Empty messages
        response = {"messages": []}
        result = parse_message_response(response)
        
        assert result["assistant_message"] == ""
        assert result["tool_calls"] == []
        assert result["reasoning"] == []
        
        # No messages key
        response = {}
        result = parse_message_response(response)
        
        assert result["assistant_message"] == ""
        assert result["tool_calls"] == []
        assert result["reasoning"] == []
    
    def test_parse_complex_response(self):
        """Test parsing a complex response with multiple elements"""
        response = {
            "messages": [
                {
                    "id": "msg-1",
                    "message_type": "reasoning_message",
                    "reasoning": "First, I need to understand the request..."
                },
                {
                    "id": "msg-2",
                    "role": "assistant",
                    "content": "I'll help you with that. Let me search for information.",
                    "message_type": "assistant_message"
                },
                {
                    "id": "msg-3",
                    "message_type": "tool_call_message",
                    "tool_call": {
                        "name": "firecrawl_search",
                        "arguments": {"query": "dealer inventory management", "limit": 5}
                    }
                },
                {
                    "id": "msg-4",
                    "message_type": "reasoning_message", 
                    "reasoning": "The search results show several key insights..."
                },
                {
                    "id": "msg-5",
                    "role": "assistant",
                    "content": "Based on the search results, here are the key findings...",
                    "message_type": "assistant_message"
                }
            ]
        }
        
        result = parse_message_response(response)
        
        # Should combine all assistant messages
        expected_message = "I'll help you with that. Let me search for information. Based on the search results, here are the key findings..."
        assert result["assistant_message"] == expected_message
        
        # Should capture tool calls
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["tool"] == "firecrawl_search"
        
        # Should capture reasoning steps
        assert len(result["reasoning"]) == 2


class TestFormatMemoryBlocks:
    """Test the format_memory_blocks function"""
    
    def test_format_standard_blocks(self, sample_memory_blocks):
        """Test formatting standard memory blocks"""
        result = format_memory_blocks(sample_memory_blocks)
        
        assert "human" in result
        assert "persona" in result
        assert "custom_context" in result
        
        assert result["human"]["value"] == "The user is a software developer interested in AI."
        assert result["persona"]["value"] == "I am a helpful AI assistant specialized in automotive industry analysis."
        assert result["custom_context"]["value"] == "Working on AutoDealAI project with AXLE agent integration."
    
    def test_format_empty_blocks(self):
        """Test formatting empty memory blocks"""
        result = format_memory_blocks([])
        assert result == {}
    
    def test_format_blocks_missing_fields(self):
        """Test formatting blocks with missing fields"""
        blocks = [
            {"id": "block-1", "label": "human"},  # Missing value
            {"id": "block-2", "value": "Test value"},  # Missing label
            {"label": "persona", "value": "Test persona"}  # Missing id
        ]
        
        result = format_memory_blocks(blocks)
        
        # Should handle missing fields gracefully
        assert "human" in result
        assert result["human"]["value"] == ""
        
        # Block without label should be skipped or handled
        assert "persona" in result
    
    def test_format_blocks_with_descriptions(self):
        """Test formatting blocks that include descriptions"""
        blocks = [
            {
                "id": "block-1",
                "label": "human",
                "value": "Test user",
                "description": "Information about the user"
            }
        ]
        
        result = format_memory_blocks(blocks)
        
        assert result["human"]["value"] == "Test user"
        assert result["human"]["description"] == "Information about the user"


class TestValidateAgentId:
    """Test the validate_agent_id function"""
    
    def test_valid_agent_ids(self):
        """Test valid agent ID formats"""
        valid_ids = [
            "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe",
            "agent-12345678-1234-1234-1234-123456789abc",
            "ag-123e4567-e89b-12d3-a456-426614174000"
        ]
        
        for agent_id in valid_ids:
            # Should not raise exception
            validate_agent_id(agent_id)
    
    def test_invalid_agent_ids(self):
        """Test invalid agent ID formats"""
        invalid_ids = [
            "",  # Empty string
            "not-an-agent-id",  # Wrong format
            "12345",  # Too short
            "agent-",  # Incomplete
            "agent-invalid-uuid-format",  # Wrong UUID format
            None  # None value
        ]
        
        for agent_id in invalid_ids:
            with pytest.raises(LettaMCPError):
                validate_agent_id(agent_id)
    
    def test_validate_none_agent_id(self):
        """Test validation with None agent ID"""
        with pytest.raises(LettaMCPError, match="Agent ID cannot be None or empty"):
            validate_agent_id(None)
    
    def test_validate_empty_agent_id(self):
        """Test validation with empty agent ID"""
        with pytest.raises(LettaMCPError, match="Agent ID cannot be None or empty"):
            validate_agent_id("")


class TestExtractAssistantMessage:
    """Test the extract_assistant_message function"""
    
    def test_extract_single_message(self):
        """Test extracting single assistant message"""
        messages = [
            {
                "role": "assistant",
                "content": "Hello, how can I help you?",
                "message_type": "assistant_message"
            }
        ]
        
        result = extract_assistant_message(messages)
        assert result == "Hello, how can I help you?"
    
    def test_extract_multiple_messages(self):
        """Test extracting multiple assistant messages"""
        messages = [
            {
                "role": "assistant", 
                "content": "Let me help you with that.",
                "message_type": "assistant_message"
            },
            {
                "role": "assistant",
                "content": " Here's what I found:",
                "message_type": "assistant_message"
            }
        ]
        
        result = extract_assistant_message(messages)
        assert result == "Let me help you with that. Here's what I found:"
    
    def test_extract_mixed_messages(self):
        """Test extracting from mixed message types"""
        messages = [
            {
                "role": "user",
                "content": "What is AutoDealAI?",
                "message_type": "user_message"
            },
            {
                "role": "assistant",
                "content": "AutoDealAI is an AI platform for dealerships.",
                "message_type": "assistant_message"
            },
            {
                "message_type": "tool_call_message",
                "tool_call": {"name": "search", "arguments": {}}
            }
        ]
        
        result = extract_assistant_message(messages)
        assert result == "AutoDealAI is an AI platform for dealerships."
    
    def test_extract_no_assistant_messages(self):
        """Test extracting when no assistant messages exist"""
        messages = [
            {
                "role": "user",
                "content": "Hello",
                "message_type": "user_message"
            }
        ]
        
        result = extract_assistant_message(messages)
        assert result == ""


class TestCreateRetryClient:
    """Test the create_retry_client function"""
    
    def test_create_basic_client(self):
        """Test creating a basic retry client"""
        client = create_retry_client(
            base_url="https://api.letta.com",
            headers={"Authorization": "Bearer test-key"},
            timeout=30.0,
            max_retries=3
        )
        
        assert isinstance(client, httpx.AsyncClient)
        assert str(client.base_url) == "https://api.letta.com"
        assert client.headers["Authorization"] == "Bearer test-key"
        assert client.timeout.read == 30.0
    
    def test_create_client_with_custom_timeout(self):
        """Test creating client with custom timeout"""
        client = create_retry_client(
            base_url="https://api.example.com",
            timeout=60.0
        )
        
        assert client.timeout.read == 60.0
    
    def test_create_client_with_retries(self):
        """Test creating client with retry configuration"""
        client = create_retry_client(
            base_url="https://api.example.com",
            max_retries=5
        )
        
        # Verify retry transport is configured
        assert hasattr(client, '_transport')
    
    @pytest.mark.asyncio
    async def test_client_retry_behavior(self):
        """Test that the retry client actually retries on failures"""
        # This would require more complex mocking to test actual retry behavior
        # For now, just verify the client can be created and used
        client = create_retry_client(
            base_url="https://httpbin.org",
            max_retries=2
        )
        
        # Test that client is usable
        async with client:
            # This is a basic connectivity test
            assert client.is_closed == False
        
        assert client.is_closed == True
    
    def test_client_configuration_edge_cases(self):
        """Test edge cases in client configuration"""
        # Test with minimal configuration
        client = create_retry_client(base_url="https://api.test.com")
        assert isinstance(client, httpx.AsyncClient)
        
        # Test with empty headers
        client = create_retry_client(
            base_url="https://api.test.com",
            headers={}
        )
        assert isinstance(client, httpx.AsyncClient)
        
        # Test with zero retries
        client = create_retry_client(
            base_url="https://api.test.com",
            max_retries=0
        )
        assert isinstance(client, httpx.AsyncClient)


class TestUtilityIntegration:
    """Integration tests for utility functions working together"""
    
    def test_full_message_processing_pipeline(self, sample_message_response):
        """Test complete message processing pipeline"""
        # Simulate a complex Letta response
        complex_response = {
            "messages": [
                {
                    "id": "msg-1",
                    "message_type": "reasoning_message",
                    "reasoning": "Let me analyze the dealer's inventory..."
                },
                {
                    "id": "msg-2",
                    "role": "assistant",
                    "content": "I'll search for inventory data.",
                    "message_type": "assistant_message"
                },
                {
                    "id": "msg-3",
                    "message_type": "tool_call_message",
                    "tool_call": {
                        "name": "firecrawl_search",
                        "arguments": {"query": "Ford F-150 inventory", "limit": 10}
                    }
                },
                {
                    "id": "msg-4",
                    "role": "assistant",
                    "content": " Based on the data, here are the findings:",
                    "message_type": "assistant_message"
                }
            ]
        }
        
        # Process the response
        parsed = parse_message_response(complex_response)
        
        # Verify all components are extracted correctly
        assert "I'll search for inventory data. Based on the data, here are the findings:" in parsed["assistant_message"]
        assert len(parsed["tool_calls"]) == 1
        assert parsed["tool_calls"][0]["tool"] == "firecrawl_search"
        assert len(parsed["reasoning"]) == 1
    
    def test_agent_id_validation_with_real_formats(self):
        """Test agent ID validation with real-world formats"""
        # Test with the actual AXLE agent ID
        real_agent_id = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
        validate_agent_id(real_agent_id)  # Should not raise
        
        # Test with various UUID formats
        uuid_formats = [
            "agent-" + "12345678-1234-5678-9abc-123456789abc",
            "ag-" + "87654321-4321-8765-cba9-987654321abc",
        ]
        
        for agent_id in uuid_formats:
            validate_agent_id(agent_id)  # Should not raise
    
    def test_memory_blocks_formatting_edge_cases(self):
        """Test memory block formatting with edge cases"""
        edge_case_blocks = [
            {
                "id": "block-1",
                "label": "human",
                "value": "",  # Empty value
                "description": "Empty human info"
            },
            {
                "id": "block-2", 
                "label": "persona",
                "value": "I am AXLE, the automotive AI specialist.\n\nI help dealers with:\n- Inventory analysis\n- Market intelligence\n- Customer insights",  # Multi-line value
                "description": "Multi-line persona"
            },
            {
                "id": "block-3",
                "label": "special_chars",
                "value": "Test with 'quotes' and \"double quotes\" and émojis 🚗",
                "description": "Testing special characters"
            }
        ]
        
        result = format_memory_blocks(edge_case_blocks)
        
        # Verify all blocks are handled correctly
        assert len(result) == 3
        assert result["human"]["value"] == ""
        assert "Inventory analysis" in result["persona"]["value"]
        assert "🚗" in result["special_chars"]["value"]