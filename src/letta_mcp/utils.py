"""
Utility functions for Letta MCP Server
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from .models import Message, MessageType, ToolCall
from .exceptions import ValidationError, APIError

logger = logging.getLogger(__name__)

# Agent ID validation regex
AGENT_ID_PATTERN = re.compile(r'^agent-[a-f0-9\-]{36}$')

def validate_agent_id(agent_id: str) -> None:
    """Validate agent ID format"""
    if not agent_id:
        raise ValidationError("Agent ID cannot be empty")
    
    if not AGENT_ID_PATTERN.match(agent_id):
        raise ValidationError(
            f"Invalid agent ID format: {agent_id}. "
            "Expected format: agent-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )

def parse_message_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a message response from Letta API"""
    result = {
        "assistant_message": None,
        "tool_calls": [],
        "reasoning": [],
        "messages": []
    }
    
    messages = response.get("messages", [])
    
    for msg in messages:
        msg_type = msg.get("message_type")
        
        if msg_type == "assistant_message":
            result["assistant_message"] = msg.get("content", "")
        
        elif msg_type == "tool_call_message":
            tool_call = msg.get("tool_call", {})
            result["tool_calls"].append({
                "name": tool_call.get("name"),
                "arguments": tool_call.get("arguments", {}),
                "id": tool_call.get("id")
            })
        
        elif msg_type == "reasoning_message":
            result["reasoning"].append(msg.get("reasoning", ""))
        
        # Add to full message list
        result["messages"].append(msg)
    
    # If no assistant message found, try to extract from other fields
    if not result["assistant_message"] and messages:
        for msg in messages:
            if msg.get("content"):
                result["assistant_message"] = msg["content"]
                break
    
    return result

def extract_assistant_message(messages: List[Dict[str, Any]]) -> Optional[str]:
    """Extract the assistant's response from a list of messages"""
    for msg in messages:
        if msg.get("message_type") == "assistant_message":
            return msg.get("content")
    
    # Fallback: look for any message with content
    for msg in messages:
        if msg.get("content"):
            return msg["content"]
    
    return None

def format_memory_blocks(blocks: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Format memory blocks for better readability"""
    formatted = {}
    
    for block in blocks:
        label = block.get("label", "unknown")
        formatted[label] = {
            "id": block.get("id"),
            "value": block.get("value", ""),
            "description": block.get("description"),
            "metadata": block.get("metadata", {})
        }
    
    return formatted

def format_timestamp(timestamp: Union[str, datetime, None]) -> Optional[str]:
    """Format timestamp to ISO format"""
    if not timestamp:
        return None
    
    if isinstance(timestamp, str):
        # Try to parse and reformat
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.isoformat()
        except:
            return timestamp
    
    elif isinstance(timestamp, datetime):
        return timestamp.isoformat()
    
    return str(timestamp)

def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def sanitize_json(data: Any) -> Any:
    """Sanitize data for JSON serialization"""
    if isinstance(data, dict):
        return {k: sanitize_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, bytes):
        return data.decode('utf-8', errors='replace')
    elif hasattr(data, 'to_dict'):
        return sanitize_json(data.to_dict())
    else:
        return data

def create_retry_client(
    base_url: str,
    headers: Dict[str, str],
    timeout: int = 60,
    max_retries: int = 3,
    pool_size: int = 10
) -> httpx.AsyncClient:
    """Create an HTTP client with retry logic"""
    
    # Configure connection pooling
    limits = httpx.Limits(
        max_keepalive_connections=pool_size,
        max_connections=pool_size * 2
    )
    
    # Create transport with retries
    transport = httpx.AsyncHTTPTransport(
        limits=limits,
        retries=max_retries
    )
    
    # Create client
    client = httpx.AsyncClient(
        base_url=base_url,
        headers=headers,
        timeout=httpx.Timeout(timeout),
        transport=transport
    )
    
    return client

def parse_tool_definition(tool_def: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a tool definition for MCP format"""
    return {
        "name": tool_def.get("name", ""),
        "description": tool_def.get("description", ""),
        "inputSchema": tool_def.get("parameters", {
            "type": "object",
            "properties": {},
            "required": []
        })
    }

def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format an error for MCP response"""
    if hasattr(error, 'to_dict'):
        return error.to_dict()
    
    return {
        "success": False,
        "error": str(error),
        "type": error.__class__.__name__
    }

def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge multiple configuration dictionaries"""
    result = {}
    
    for config in configs:
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value
    
    return result

def calculate_token_estimate(text: str) -> int:
    """Rough estimate of token count (4 chars = 1 token)"""
    return len(text) // 4

def is_streaming_supported(model: str) -> bool:
    """Check if a model supports streaming"""
    # Most models support streaming, but some older ones don't
    non_streaming_models = {
        "gpt-3.5-turbo-0301",
        "text-davinci-003"
    }
    
    return model not in non_streaming_models

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(httpx.HTTPError),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def resilient_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    **kwargs
) -> httpx.Response:
    """Make an HTTP request with automatic retries"""
    response = await client.request(method, url, **kwargs)
    
    # Raise for status codes that should trigger retry
    if response.status_code in [429, 500, 502, 503, 504]:
        response.raise_for_status()
    
    return response