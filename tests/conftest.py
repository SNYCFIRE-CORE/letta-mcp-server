"""
Shared pytest fixtures for Letta MCP Server tests
"""

import os
import pytest
import asyncio
from typing import Optional, Dict, Any
from unittest.mock import Mock, AsyncMock
import httpx

from letta_mcp.config import LettaConfig
from letta_mcp.server import LettaMCPServer
from fastmcp import Client


# Test configuration
TEST_API_KEY = "sk-let-MTVhMWI3YmYtNWEzMi00NDQ5LWJiMzAtNTAwZTE5NGQ4N2FjOmEwZjc1NzQwLTU2NjAtNDI0Ny04YThkLTVlM2MyZDNhYjUyNA=="
TEST_AGENT_ID = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
LETTA_BASE_URL = "https://api.letta.com"


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for the test session"""
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return LettaConfig(
        api_key="test-api-key",
        base_url="http://localhost:8000",
        timeout=30.0,
        max_retries=3,
        default_model="claude-sonnet-4-20250514",
        default_embedding="text-embedding-ada-002"
    )


@pytest.fixture
def real_config():
    """Real configuration for integration tests"""
    return LettaConfig(
        api_key=TEST_API_KEY,
        base_url=LETTA_BASE_URL,
        timeout=30.0,
        max_retries=3,
        default_model="claude-sonnet-4-20250514",
        default_embedding="text-embedding-ada-002"
    )


@pytest.fixture
def mock_server(mock_config):
    """Mock server instance for unit tests"""
    server = LettaMCPServer(mock_config)
    # Replace HTTP client with mock
    server.client = Mock()
    return server


@pytest.fixture
def real_server(real_config):
    """Real server instance for integration tests"""
    return LettaMCPServer(real_config)


@pytest.fixture
async def mock_client(mock_server):
    """Mock FastMCP client for unit tests"""
    async with Client(mock_server) as client:
        yield client


@pytest.fixture
async def real_client(real_server):
    """Real FastMCP client for integration tests"""
    async with Client(real_server) as client:
        yield client


@pytest.fixture
def mock_http_response():
    """Mock HTTP response factory"""
    def _create_response(
        status_code: int = 200,
        json_data: Optional[Dict[Any, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        response = Mock(spec=httpx.Response)
        response.status_code = status_code
        response.headers = headers or {}
        
        if json_data is not None:
            response.json.return_value = json_data
        
        # Mock raise_for_status
        if status_code >= 400:
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "HTTP Error", request=Mock(), response=response
            )
        else:
            response.raise_for_status.return_value = None
            
        return response
    
    return _create_response


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing"""
    return {
        "id": "agent-123",
        "name": "Test Agent",
        "description": "A test agent for unit tests",
        "model": "claude-sonnet-4-20250514",
        "created_at": "2025-06-24T10:00:00Z",
        "last_modified": "2025-06-24T10:00:00Z",
        "tools": ["web_search", "run_code"],
        "memory_blocks": [
            {
                "id": "block-1",
                "label": "human",
                "value": "Test user information"
            },
            {
                "id": "block-2", 
                "label": "persona",
                "value": "Test agent persona"
            }
        ],
        "message_count": 5
    }


@pytest.fixture
def sample_memory_blocks():
    """Sample memory blocks for testing"""
    return [
        {
            "id": "block-1",
            "label": "human",
            "value": "The user is a software developer interested in AI.",
            "description": "Information about the human user"
        },
        {
            "id": "block-2",
            "label": "persona", 
            "value": "I am a helpful AI assistant specialized in automotive industry analysis.",
            "description": "The agent's persona and behavior"
        },
        {
            "id": "block-3",
            "label": "custom_context",
            "value": "Working on AutoDealAI project with AXLE agent integration.",
            "description": "Custom context information"
        }
    ]


@pytest.fixture
def sample_message_response():
    """Sample message response for testing"""
    return {
        "messages": [
            {
                "id": "msg-1",
                "role": "user",
                "content": "Hello, can you help me?",
                "timestamp": "2025-06-24T10:00:00Z"
            },
            {
                "id": "msg-2", 
                "role": "assistant",
                "content": "Hello! I'd be happy to help you. What can I assist you with today?",
                "timestamp": "2025-06-24T10:00:01Z"
            }
        ]
    }


@pytest.fixture
def sample_tools():
    """Sample tools data for testing"""
    return [
        {
            "id": "tool-1",
            "name": "web_search",
            "description": "Search the web for information",
            "tags": ["search", "web"]
        },
        {
            "id": "tool-2",
            "name": "run_code", 
            "description": "Execute Python code",
            "tags": ["code", "execution"]
        },
        {
            "id": "tool-3",
            "name": "firecrawl_search",
            "description": "Advanced web scraping and search",
            "tags": ["scraping", "firecrawl"]
        }
    ]


@pytest.fixture
def integration_test_marker():
    """Marker for integration tests that require real API access"""
    return pytest.mark.skipif(
        not os.getenv("RUN_INTEGRATION_TESTS", "").lower() in ("1", "true", "yes"),
        reason="Integration tests require RUN_INTEGRATION_TESTS=1"
    )


@pytest.fixture
def performance_test_marker():
    """Marker for performance tests"""
    return pytest.mark.skipif(
        not os.getenv("RUN_PERFORMANCE_TESTS", "").lower() in ("1", "true", "yes"),
        reason="Performance tests require RUN_PERFORMANCE_TESTS=1"
    )


# Session-scoped fixtures for expensive operations
@pytest.fixture(scope="session")
async def session_real_server():
    """Session-scoped real server for expensive setup"""
    config = LettaConfig(
        api_key=TEST_API_KEY,
        base_url=LETTA_BASE_URL,
        timeout=30.0,
        max_retries=3
    )
    return LettaMCPServer(config)


@pytest.fixture(scope="session") 
async def session_real_client(session_real_server):
    """Session-scoped real client for integration tests"""
    async with Client(session_real_server) as client:
        yield client


# Async utilities
@pytest.fixture
def async_mock():
    """Factory for creating async mocks"""
    def _create_async_mock(*args, **kwargs):
        mock = AsyncMock(*args, **kwargs)
        return mock
    return _create_async_mock


# Performance measurement fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance measurements"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            
        def start(self):
            self.start_time = time.perf_counter()
            
        def stop(self):
            self.end_time = time.perf_counter()
            
        @property
        def elapsed(self):
            if self.start_time is None or self.end_time is None:
                return None
            return self.end_time - self.start_time
            
    return Timer()


# Environment variable helpers
@pytest.fixture
def env_var_helper():
    """Helper for setting/restoring environment variables during tests"""
    class EnvHelper:
        def __init__(self):
            self.original_values = {}
            
        def set(self, key: str, value: str):
            if key not in self.original_values:
                self.original_values[key] = os.environ.get(key)
            os.environ[key] = value
            
        def restore(self):
            for key, original_value in self.original_values.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
            self.original_values.clear()
            
    helper = EnvHelper()
    yield helper
    helper.restore()