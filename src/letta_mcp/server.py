#!/usr/bin/env python3
"""
Letta MCP Server - Main server implementation using FastMCP
"""

import os
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import httpx
from fastmcp import FastMCP

from .config import LettaConfig, load_config
from .models import AgentInfo, MemoryBlock, ToolInfo, Message, StreamChunk
from .exceptions import LettaMCPError, APIError, ConfigurationError
from .utils import (
    parse_message_response,
    format_memory_blocks,
    validate_agent_id,
    extract_assistant_message,
    create_retry_client
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LettaMCPServer:
    """Main Letta MCP Server implementation"""
    
    def __init__(self, config: Optional[LettaConfig] = None):
        """Initialize the Letta MCP Server"""
        self.config = config or load_config()
        self.validate_config()
        
        # Initialize FastMCP server
        self.mcp = FastMCP(
            "Letta MCP Server",
            instructions="""
This server provides seamless integration between Claude and Letta.ai agents.

Key features:
- Stateful agent conversations (no need to send history)
- Memory block management (human, persona, custom)
- Tool orchestration and workflow rules
- Real-time streaming responses
- Cross-agent communication

Remember: Letta agents maintain their own conversation history!
"""
        )
        
        # Create HTTP client with retry logic
        self.client = create_retry_client(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        
        # Register all tools
        self._register_tools()
        
        # Register resources
        self._register_resources()
    
    def validate_config(self):
        """Validate the configuration"""
        if not self.config.api_key and self.config.base_url == "https://api.letta.com":
            raise ConfigurationError(
                "LETTA_API_KEY is required for Letta Cloud. "
                "Set it in environment or config file."
            )
    
    def _register_tools(self):
        """Register all MCP tools"""
        # Agent Management
        self._register_agent_tools()
        
        # Conversation Tools
        self._register_conversation_tools()
        
        # Memory Management
        self._register_memory_tools()
        
        # Tool Management
        self._register_tool_management()
        
        # Utility Tools
        self._register_utility_tools()
    
    def _register_agent_tools(self):
        """Register agent management tools"""
        
        @self.mcp.tool()
        async def letta_list_agents(
            filter: Optional[str] = None,
            limit: int = 50,
            offset: int = 0
        ) -> Dict[str, Any]:
            """
            List all available Letta agents with pagination support.
            
            Args:
                filter: Optional text to filter agent names
                limit: Number of agents to return (max 100)
                offset: Offset for pagination
            
            Returns:
                List of agents with their details
            """
            try:
                params = {"limit": min(limit, 100), "offset": offset}
                response = await self.client.get("/v1/agents", params=params)
                response.raise_for_status()
                
                agents = response.json()
                
                # Apply filter if provided
                if filter:
                    filter_lower = filter.lower()
                    agents = [
                        a for a in agents 
                        if filter_lower in a.get("name", "").lower() or
                           filter_lower in a.get("description", "").lower()
                    ]
                
                return {
                    "success": True,
                    "count": len(agents),
                    "total": response.headers.get("X-Total-Count", len(agents)),
                    "agents": agents
                }
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error listing agents: {e}")
                return {"success": False, "error": str(e)}
            except Exception as e:
                logger.error(f"Error listing agents: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_create_agent(
            name: str,
            description: Optional[str] = None,
            human_memory: Optional[str] = None,
            persona_memory: Optional[str] = None,
            custom_blocks: Optional[List[Dict[str, str]]] = None,
            model: Optional[str] = None,
            tools: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            Create a new Letta agent with memory blocks and tools.
            
            Args:
                name: Name for the new agent
                description: Description of the agent's purpose
                human_memory: Information about the human user
                persona_memory: Agent's persona and behavior
                custom_blocks: Additional memory blocks with label, value, description
                model: LLM model to use (default: from config)
                tools: List of tool names to attach
            
            Returns:
                Created agent details
            """
            try:
                # Build memory blocks
                memory_blocks = []
                
                if human_memory:
                    memory_blocks.append({
                        "label": "human",
                        "value": human_memory
                    })
                else:
                    memory_blocks.append({
                        "label": "human", 
                        "value": "The user is interested in AI development."
                    })
                
                if persona_memory:
                    memory_blocks.append({
                        "label": "persona",
                        "value": persona_memory
                    })
                else:
                    memory_blocks.append({
                        "label": "persona",
                        "value": f"I am {name}, an AI assistant. I am helpful, professional, and knowledgeable."
                    })
                
                # Add custom blocks
                if custom_blocks:
                    for block in custom_blocks:
                        if "label" in block and "value" in block:
                            memory_blocks.append(block)
                
                # Create agent
                payload = {
                    "name": name,
                    "description": description or f"AI assistant named {name}",
                    "memory_blocks": memory_blocks,
                    "model": model or self.config.default_model,
                    "embedding": self.config.default_embedding,
                    "tools": tools or ["web_search", "run_code"]
                }
                
                response = await self.client.post("/v1/agents", json=payload)
                response.raise_for_status()
                
                agent = response.json()
                
                return {
                    "success": True,
                    "agent": agent,
                    "message": f"Successfully created agent '{name}' with ID: {agent['id']}"
                }
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error creating agent: {e}")
                return {"success": False, "error": str(e)}
            except Exception as e:
                logger.error(f"Error creating agent: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_get_agent(agent_id: str) -> Dict[str, Any]:
            """Get detailed information about a specific Letta agent."""
            try:
                validate_agent_id(agent_id)
                
                response = await self.client.get(f"/v1/agents/{agent_id}")
                response.raise_for_status()
                
                agent = response.json()
                
                # Format the response nicely
                return {
                    "success": True,
                    "agent": {
                        "id": agent["id"],
                        "name": agent.get("name", "Unknown"),
                        "description": agent.get("description", ""),
                        "model": agent.get("model", ""),
                        "created_at": agent.get("created_at", ""),
                        "last_modified": agent.get("last_modified", ""),
                        "tools": agent.get("tools", []),
                        "memory_blocks": len(agent.get("memory_blocks", [])),
                        "message_count": agent.get("message_count", 0)
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting agent info: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_update_agent(
            agent_id: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            model: Optional[str] = None
        ) -> Dict[str, Any]:
            """Update an existing agent's configuration."""
            try:
                validate_agent_id(agent_id)
                
                # Build update payload
                updates = {}
                if name is not None:
                    updates["name"] = name
                if description is not None:
                    updates["description"] = description
                if model is not None:
                    updates["model"] = model
                
                if not updates:
                    return {
                        "success": False,
                        "error": "No updates provided"
                    }
                
                response = await self.client.patch(
                    f"/v1/agents/{agent_id}",
                    json=updates
                )
                response.raise_for_status()
                
                return {
                    "success": True,
                    "message": f"Successfully updated agent {agent_id}",
                    "updates": updates
                }
                
            except Exception as e:
                logger.error(f"Error updating agent: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_delete_agent(
            agent_id: str,
            confirm: bool = False
        ) -> Dict[str, Any]:
            """
            Delete a Letta agent (requires confirmation).
            
            Args:
                agent_id: ID of the agent to delete
                confirm: Must be True to confirm deletion
            
            Returns:
                Deletion status
            """
            try:
                if not confirm:
                    return {
                        "success": False,
                        "error": "Deletion requires confirm=True to prevent accidents"
                    }
                
                validate_agent_id(agent_id)
                
                response = await self.client.delete(f"/v1/agents/{agent_id}")
                response.raise_for_status()
                
                return {
                    "success": True,
                    "message": f"Successfully deleted agent {agent_id}"
                }
                
            except Exception as e:
                logger.error(f"Error deleting agent: {e}")
                return {"success": False, "error": str(e)}
    
    def _register_conversation_tools(self):
        """Register conversation management tools"""
        
        @self.mcp.tool()
        async def letta_send_message(
            agent_id: str,
            message: str,
            stream: bool = False
        ) -> Dict[str, Any]:
            """
            Send a message to a Letta agent and get the response.
            
            Args:
                agent_id: ID of the agent to message
                message: Message content to send
                stream: Whether to stream the response
            
            Returns:
                Agent's response with tool calls and reasoning
            """
            try:
                validate_agent_id(agent_id)
                
                if stream:
                    return await self._stream_message(agent_id, message)
                
                response = await self.client.post(
                    f"/v1/agents/{agent_id}/messages",
                    json={
                        "messages": [{"role": "user", "content": message}],
                        "stream_steps": False,
                        "stream_tokens": False
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Parse the response
                parsed = parse_message_response(result)
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message": message,
                    "response": parsed["assistant_message"],
                    "tool_calls": parsed["tool_calls"],
                    "reasoning": parsed["reasoning"],
                    "full_response": result
                }
                
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "agent_id": agent_id
                }
        
        async def _stream_message(self, agent_id: str, message: str) -> Dict[str, Any]:
            """Stream a message response from an agent"""
            try:
                chunks = []
                
                async with self.client.stream(
                    "POST",
                    f"/v1/agents/{agent_id}/messages",
                    json={
                        "messages": [{"role": "user", "content": message}],
                        "stream_steps": True,
                        "stream_tokens": True
                    }
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                chunk_data = json.loads(line[6:])
                                chunks.append(chunk_data)
                                
                                # Yield progress for UI
                                if chunk_data.get("messageType") == "assistant_message":
                                    logger.info(f"Streaming: {chunk_data.get('content', '')}")
                                    
                            except json.JSONDecodeError:
                                continue
                
                # Combine chunks into final response
                final_content = ""
                tool_calls = []
                reasoning = []
                
                for chunk in chunks:
                    msg_type = chunk.get("messageType")
                    
                    if msg_type == "assistant_message":
                        final_content += chunk.get("content", "")
                    elif msg_type == "tool_call_message":
                        tool_calls.append({
                            "tool": chunk.get("toolCall", {}).get("name"),
                            "args": chunk.get("toolCall", {}).get("arguments")
                        })
                    elif msg_type == "reasoning_message":
                        reasoning.append(chunk.get("reasoning", ""))
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message": message,
                    "response": final_content,
                    "tool_calls": tool_calls,
                    "reasoning": reasoning,
                    "streamed": True
                }
                
            except Exception as e:
                logger.error(f"Error streaming message: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_get_conversation_history(
            agent_id: str,
            limit: int = 20,
            before: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get recent conversation history for a Letta agent.
            
            Args:
                agent_id: ID of the agent
                limit: Number of messages to retrieve
                before: Get messages before this timestamp
            
            Returns:
                Conversation history with messages
            """
            try:
                validate_agent_id(agent_id)
                
                params = {"limit": min(limit, 100)}
                if before:
                    params["before"] = before
                
                response = await self.client.get(
                    f"/v1/agents/{agent_id}/messages",
                    params=params
                )
                response.raise_for_status()
                
                messages = response.json()
                
                # Format messages for readability
                formatted_messages = []
                for msg in messages:
                    formatted = {
                        "timestamp": msg.get("created_at"),
                        "type": msg.get("message_type"),
                        "role": msg.get("role")
                    }
                    
                    # Add content based on type
                    if msg.get("message_type") == "assistant_message":
                        formatted["content"] = msg.get("content")
                    elif msg.get("message_type") == "tool_call_message":
                        formatted["tool"] = msg.get("tool_call", {}).get("name")
                        formatted["args"] = msg.get("tool_call", {}).get("arguments")
                    elif msg.get("message_type") == "tool_return_message":
                        formatted["result"] = msg.get("tool_return")
                    
                    formatted_messages.append(formatted)
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message_count": len(formatted_messages),
                    "messages": formatted_messages
                }
                
            except Exception as e:
                logger.error(f"Error getting conversation history: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_export_conversation(
            agent_id: str,
            format: str = "markdown",
            include_tools: bool = False
        ) -> Dict[str, Any]:
            """
            Export a conversation in various formats.
            
            Args:
                agent_id: ID of the agent
                format: Export format (markdown, json, text)
                include_tools: Whether to include tool calls
            
            Returns:
                Exported conversation content
            """
            try:
                # Get full conversation history
                history_result = await letta_get_conversation_history(
                    agent_id, 
                    limit=1000
                )
                
                if not history_result["success"]:
                    return history_result
                
                messages = history_result["messages"]
                
                if format == "markdown":
                    content = f"# Conversation with Agent {agent_id}\n\n"
                    content += f"*Exported on {datetime.now().isoformat()}*\n\n"
                    
                    for msg in reversed(messages):  # Chronological order
                        timestamp = msg.get("timestamp", "")
                        
                        if msg["type"] == "user_message":
                            content += f"## User ({timestamp})\n{msg.get('content', '')}\n\n"
                        elif msg["type"] == "assistant_message":
                            content += f"## Assistant ({timestamp})\n{msg.get('content', '')}\n\n"
                        elif include_tools and msg["type"] == "tool_call_message":
                            content += f"### Tool Call: {msg.get('tool')}\n"
                            content += f"```json\n{json.dumps(msg.get('args', {}), indent=2)}\n```\n\n"
                
                elif format == "json":
                    content = json.dumps(messages, indent=2)
                
                elif format == "text":
                    content = ""
                    for msg in reversed(messages):
                        if msg["type"] in ["user_message", "assistant_message"]:
                            role = "User" if msg["type"] == "user_message" else "Assistant"
                            content += f"{role}: {msg.get('content', '')}\n\n"
                
                else:
                    return {
                        "success": False,
                        "error": f"Unknown format: {format}. Use markdown, json, or text."
                    }
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "format": format,
                    "content": content,
                    "message_count": len(messages)
                }
                
            except Exception as e:
                logger.error(f"Error exporting conversation: {e}")
                return {"success": False, "error": str(e)}
    
    def _register_memory_tools(self):
        """Register memory management tools"""
        
        @self.mcp.tool()
        async def letta_get_memory(agent_id: str) -> Dict[str, Any]:
            """Get all memory blocks for a Letta agent."""
            try:
                validate_agent_id(agent_id)
                
                response = await self.client.get(f"/v1/agents/{agent_id}/memory-blocks")
                response.raise_for_status()
                
                memory_blocks = response.json()
                
                # Format memory blocks
                formatted = format_memory_blocks(memory_blocks)
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "memory_blocks": formatted,
                    "raw_blocks": memory_blocks
                }
                
            except Exception as e:
                logger.error(f"Error getting memory: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_update_memory(
            agent_id: str,
            block_label: str,
            value: str
        ) -> Dict[str, Any]:
            """
            Update a memory block for a Letta agent.
            
            Args:
                agent_id: ID of the agent
                block_label: Label of the memory block (e.g., 'human', 'persona')
                value: New value for the memory block
            
            Returns:
                Update status
            """
            try:
                validate_agent_id(agent_id)
                
                # First get all memory blocks to find the right one
                response = await self.client.get(f"/v1/agents/{agent_id}/memory-blocks")
                response.raise_for_status()
                memory_blocks = response.json()
                
                # Find the block with matching label
                block_id = None
                for block in memory_blocks:
                    if block.get("label") == block_label:
                        block_id = block.get("id")
                        break
                
                if not block_id:
                    return {
                        "success": False,
                        "error": f"Memory block '{block_label}' not found. Available blocks: {[b.get('label') for b in memory_blocks]}"
                    }
                
                # Update the block
                response = await self.client.patch(
                    f"/v1/agents/{agent_id}/memory-blocks/{block_id}",
                    json={"value": value}
                )
                response.raise_for_status()
                
                updated_block = response.json()
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "block_label": block_label,
                    "block_id": block_id,
                    "updated_value": value,
                    "message": f"Successfully updated '{block_label}' memory block"
                }
                
            except Exception as e:
                logger.error(f"Error updating memory: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_create_memory_block(
            agent_id: str,
            label: str,
            value: str,
            description: str
        ) -> Dict[str, Any]:
            """
            Create a new custom memory block for an agent.
            
            Args:
                agent_id: ID of the agent
                label: Label for the new block
                value: Initial value
                description: Description of what this block stores
            
            Returns:
                Created memory block details
            """
            try:
                validate_agent_id(agent_id)
                
                # Create the memory block
                response = await self.client.post(
                    f"/v1/agents/{agent_id}/memory-blocks",
                    json={
                        "label": label,
                        "value": value,
                        "description": description
                    }
                )
                response.raise_for_status()
                
                block = response.json()
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "block": block,
                    "message": f"Successfully created memory block '{label}'"
                }
                
            except Exception as e:
                logger.error(f"Error creating memory block: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_search_memory(
            agent_id: str,
            query: str,
            limit: int = 10
        ) -> Dict[str, Any]:
            """
            Search through agent's conversation memory.
            
            Args:
                agent_id: ID of the agent
                query: Search query
                limit: Maximum results to return
            
            Returns:
                Matching messages from memory
            """
            try:
                validate_agent_id(agent_id)
                
                # Search through messages
                response = await self.client.get(
                    f"/v1/agents/{agent_id}/messages/search",
                    params={
                        "query": query,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                
                results = response.json()
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "query": query,
                    "result_count": len(results),
                    "results": results
                }
                
            except Exception as e:
                # If search endpoint doesn't exist, fall back to manual search
                if "404" in str(e):
                    history = await letta_get_conversation_history(agent_id, limit=1000)
                    if history["success"]:
                        # Manual search through messages
                        query_lower = query.lower()
                        matches = []
                        
                        for msg in history["messages"]:
                            content = msg.get("content", "").lower()
                            if query_lower in content:
                                matches.append(msg)
                                if len(matches) >= limit:
                                    break
                        
                        return {
                            "success": True,
                            "agent_id": agent_id,
                            "query": query,
                            "result_count": len(matches),
                            "results": matches,
                            "method": "manual_search"
                        }
                
                logger.error(f"Error searching memory: {e}")
                return {"success": False, "error": str(e)}
    
    def _register_tool_management(self):
        """Register tool management functionality"""
        
        @self.mcp.tool()
        async def letta_list_tools(
            filter: Optional[str] = None,
            tags: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            List all available tools in the Letta system.
            
            Args:
                filter: Text filter for tool names/descriptions
                tags: Filter by tool tags
            
            Returns:
                List of available tools
            """
            try:
                response = await self.client.get("/v1/tools")
                response.raise_for_status()
                
                tools = response.json()
                
                # Apply filters
                if filter:
                    filter_lower = filter.lower()
                    tools = [
                        t for t in tools
                        if filter_lower in t.get("name", "").lower() or
                           filter_lower in t.get("description", "").lower()
                    ]
                
                if tags:
                    tools = [
                        t for t in tools
                        if any(tag in t.get("tags", []) for tag in tags)
                    ]
                
                # Group by tags
                tools_by_tag = {}
                for tool in tools:
                    for tag in tool.get("tags", ["other"]):
                        if tag not in tools_by_tag:
                            tools_by_tag[tag] = []
                        tools_by_tag[tag].append({
                            "name": tool.get("name"),
                            "description": tool.get("description"),
                            "id": tool.get("id")
                        })
                
                return {
                    "success": True,
                    "total_tools": len(tools),
                    "tools_by_tag": tools_by_tag,
                    "tools": tools
                }
                
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_get_agent_tools(agent_id: str) -> Dict[str, Any]:
            """Get the tools attached to a specific agent."""
            try:
                validate_agent_id(agent_id)
                
                response = await self.client.get(f"/v1/agents/{agent_id}")
                response.raise_for_status()
                
                agent = response.json()
                tools = agent.get("tools", [])
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "agent_name": agent.get("name"),
                    "tool_count": len(tools),
                    "tools": tools
                }
                
            except Exception as e:
                logger.error(f"Error getting agent tools: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_attach_tool(
            agent_id: str,
            tool_name: str
        ) -> Dict[str, Any]:
            """
            Attach a tool to an agent.
            
            Args:
                agent_id: ID of the agent
                tool_name: Name of the tool to attach
            
            Returns:
                Attachment status
            """
            try:
                validate_agent_id(agent_id)
                
                # Get current tools
                agent_response = await self.client.get(f"/v1/agents/{agent_id}")
                agent_response.raise_for_status()
                agent = agent_response.json()
                
                current_tools = agent.get("tools", [])
                
                # Check if already attached
                if tool_name in current_tools:
                    return {
                        "success": True,
                        "message": f"Tool '{tool_name}' is already attached to agent",
                        "tools": current_tools
                    }
                
                # Add the new tool
                updated_tools = current_tools + [tool_name]
                
                # Update agent
                response = await self.client.patch(
                    f"/v1/agents/{agent_id}",
                    json={"tools": updated_tools}
                )
                response.raise_for_status()
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message": f"Successfully attached tool '{tool_name}'",
                    "tools": updated_tools
                }
                
            except Exception as e:
                logger.error(f"Error attaching tool: {e}")
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def letta_detach_tool(
            agent_id: str,
            tool_name: str
        ) -> Dict[str, Any]:
            """
            Detach a tool from an agent.
            
            Args:
                agent_id: ID of the agent
                tool_name: Name of the tool to detach
            
            Returns:
                Detachment status
            """
            try:
                validate_agent_id(agent_id)
                
                # Get current tools
                agent_response = await self.client.get(f"/v1/agents/{agent_id}")
                agent_response.raise_for_status()
                agent = agent_response.json()
                
                current_tools = agent.get("tools", [])
                
                # Check if attached
                if tool_name not in current_tools:
                    return {
                        "success": False,
                        "error": f"Tool '{tool_name}' is not attached to this agent",
                        "tools": current_tools
                    }
                
                # Remove the tool
                updated_tools = [t for t in current_tools if t != tool_name]
                
                # Update agent
                response = await self.client.patch(
                    f"/v1/agents/{agent_id}",
                    json={"tools": updated_tools}
                )
                response.raise_for_status()
                
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message": f"Successfully detached tool '{tool_name}'",
                    "tools": updated_tools
                }
                
            except Exception as e:
                logger.error(f"Error detaching tool: {e}")
                return {"success": False, "error": str(e)}
    
    def _register_utility_tools(self):
        """Register utility and helper tools"""
        
        @self.mcp.tool()
        async def letta_health_check() -> Dict[str, Any]:
            """Check the health of the Letta API connection."""
            try:
                # Try to list agents with limit=1 as a health check
                response = await self.client.get("/v1/agents", params={"limit": 1})
                response.raise_for_status()
                
                return {
                    "success": True,
                    "status": "healthy",
                    "base_url": self.config.base_url,
                    "api_version": response.headers.get("X-API-Version", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return {
                    "success": False,
                    "status": "unhealthy",
                    "error": str(e),
                    "base_url": self.config.base_url,
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.mcp.tool()
        async def letta_get_usage_stats(
            agent_id: Optional[str] = None,
            period: str = "day"
        ) -> Dict[str, Any]:
            """
            Get usage statistics for agents.
            
            Args:
                agent_id: Specific agent ID or None for all agents
                period: Time period (day, week, month)
            
            Returns:
                Usage statistics
            """
            try:
                params = {"period": period}
                if agent_id:
                    params["agent_id"] = agent_id
                
                response = await self.client.get("/v1/stats/usage", params=params)
                response.raise_for_status()
                
                stats = response.json()
                
                return {
                    "success": True,
                    "period": period,
                    "agent_id": agent_id,
                    "stats": stats
                }
                
            except Exception as e:
                # If stats endpoint doesn't exist, return mock data
                if "404" in str(e):
                    return {
                        "success": True,
                        "period": period,
                        "agent_id": agent_id,
                        "stats": {
                            "message_count": "N/A",
                            "tool_calls": "N/A",
                            "tokens_used": "N/A"
                        },
                        "note": "Usage stats endpoint not available"
                    }
                
                logger.error(f"Error getting usage stats: {e}")
                return {"success": False, "error": str(e)}
    
    def _register_resources(self):
        """Register MCP resources for data access"""
        
        @self.mcp.resource("letta://agents")
        async def get_agents_resource() -> str:
            """List of all Letta agents"""
            result = await letta_list_agents()
            return json.dumps(result, indent=2)
        
        @self.mcp.resource("letta://tools")
        async def get_tools_resource() -> str:
            """List of all available tools"""
            result = await letta_list_tools()
            return json.dumps(result, indent=2)
        
        @self.mcp.resource("letta://agent/{agent_id}")
        async def get_agent_resource(agent_id: str) -> str:
            """Get detailed information about a specific agent"""
            result = await letta_get_agent(agent_id)
            return json.dumps(result, indent=2)
        
        @self.mcp.resource("letta://agent/{agent_id}/memory")
        async def get_agent_memory_resource(agent_id: str) -> str:
            """Get memory blocks for a specific agent"""
            result = await letta_get_memory(agent_id)
            return json.dumps(result, indent=2)
        
        @self.mcp.resource("letta://health")
        async def get_health_resource() -> str:
            """Health status of the Letta connection"""
            result = await letta_health_check()
            return json.dumps(result, indent=2)
    
    def run(self, transport: str = "stdio"):
        """Run the MCP server"""
        from ._version import __version__
        logger.info(f"Starting Letta MCP Server v{__version__}")
        logger.info(f"Connected to: {self.config.base_url}")
        logger.info(f"Transport: {transport}")
        
        self.mcp.run(transport=transport)

def create_server(config: Optional[LettaConfig] = None) -> LettaMCPServer:
    """Create a new Letta MCP Server instance"""
    return LettaMCPServer(config)

def run_server(config: Optional[LettaConfig] = None, transport: str = "stdio"):
    """Create and run a Letta MCP Server"""
    server = create_server(config)
    server.run(transport)

if __name__ == "__main__":
    run_server()