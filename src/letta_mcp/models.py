"""
Data models for Letta MCP Server
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class MessageType(str, Enum):
    """Types of messages in Letta"""
    USER = "user_message"
    ASSISTANT = "assistant_message"
    SYSTEM = "system_message"
    TOOL_CALL = "tool_call_message"
    TOOL_RETURN = "tool_return_message"
    REASONING = "reasoning_message"
    FUNCTION = "function_message"
    FUNCTION_RETURN = "function_return_message"

class ToolStatus(str, Enum):
    """Status of tool execution"""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    TIMEOUT = "timeout"

@dataclass
class MemoryBlock:
    """Represents a memory block in Letta"""
    id: str
    label: str
    value: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryBlock":
        """Create from API response"""
        return cls(
            id=data.get("id", ""),
            label=data.get("label", ""),
            value=data.get("value", ""),
            description=data.get("description"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API format"""
        return {
            "id": self.id,
            "label": self.label,
            "value": self.value,
            "description": self.description,
            "metadata": self.metadata
        }

@dataclass
class ToolCall:
    """Represents a tool call in a message"""
    name: str
    arguments: Dict[str, Any]
    id: Optional[str] = None
    status: ToolStatus = ToolStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCall":
        """Create from API response"""
        return cls(
            name=data.get("name", ""),
            arguments=data.get("arguments", {}),
            id=data.get("id"),
            status=ToolStatus(data.get("status", "pending")),
            result=data.get("result"),
            error=data.get("error")
        )

@dataclass
class Message:
    """Represents a message in Letta"""
    id: str
    type: MessageType
    role: Optional[str] = None
    content: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    tool_return: Optional[Any] = None
    reasoning: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create from API response"""
        msg_type = MessageType(data.get("message_type", ""))
        
        tool_call = None
        if msg_type == MessageType.TOOL_CALL and "tool_call" in data:
            tool_call = ToolCall.from_dict(data["tool_call"])
        
        return cls(
            id=data.get("id", ""),
            type=msg_type,
            role=data.get("role"),
            content=data.get("content"),
            tool_call=tool_call,
            tool_return=data.get("tool_return"),
            reasoning=data.get("reasoning"),
            created_at=data.get("created_at"),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API format"""
        result = {
            "id": self.id,
            "message_type": self.type.value,
            "metadata": self.metadata
        }
        
        if self.role:
            result["role"] = self.role
        if self.content:
            result["content"] = self.content
        if self.tool_call:
            result["tool_call"] = {
                "name": self.tool_call.name,
                "arguments": self.tool_call.arguments
            }
        if self.tool_return is not None:
            result["tool_return"] = self.tool_return
        if self.reasoning:
            result["reasoning"] = self.reasoning
        if self.created_at:
            result["created_at"] = self.created_at.isoformat()
        
        return result

@dataclass
class StreamChunk:
    """Represents a streaming chunk"""
    type: str
    content: Optional[str] = None
    delta: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    done: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolInfo:
    """Information about a tool"""
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolInfo":
        """Create from API response"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            parameters=data.get("parameters", {}),
            returns=data.get("returns", {}),
            examples=data.get("examples", []),
            metadata=data.get("metadata", {})
        )

@dataclass  
class AgentInfo:
    """Information about an agent"""
    id: str
    name: str
    description: Optional[str] = None
    model: Optional[str] = None
    tools: List[str] = field(default_factory=list)
    memory_blocks: List[MemoryBlock] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentInfo":
        """Create from API response"""
        memory_blocks = []
        for block_data in data.get("memory_blocks", []):
            if isinstance(block_data, dict):
                memory_blocks.append(MemoryBlock.from_dict(block_data))
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            model=data.get("model"),
            tools=data.get("tools", []),
            memory_blocks=memory_blocks,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at") or data.get("last_modified"),
            message_count=data.get("message_count", 0),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API format"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "tools": self.tools,
            "memory_blocks": [block.to_dict() for block in self.memory_blocks],
            "message_count": self.message_count,
            "metadata": self.metadata
        }

@dataclass
class Project:
    """Represents a project in Letta (new in 2025)"""
    id: str
    name: str
    description: Optional[str] = None
    agents: List[str] = field(default_factory=list)
    templates: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create from API response"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            agents=data.get("agents", []),
            templates=data.get("templates", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {})
        )

@dataclass
class ExecutionStep:
    """Represents an execution step (new in 2025)"""
    id: str
    agent_id: str
    step_number: int
    type: str
    status: str
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionStep":
        """Create from API response"""
        return cls(
            id=data.get("id", ""),
            agent_id=data.get("agent_id", ""),
            step_number=data.get("step_number", 0),
            type=data.get("type", ""),
            status=data.get("status", ""),
            input=data.get("input"),
            output=data.get("output"),
            error=data.get("error"),
            duration_ms=data.get("duration_ms"),
            created_at=data.get("created_at"),
            metadata=data.get("metadata", {})
        )