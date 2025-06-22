# Letta MCP Server API Reference

This document provides a comprehensive reference for all API endpoints and operations available through the Letta MCP Server, including agent management, memory operations, tool management, and conversation handling.

## Table of Contents

1. [Authentication](#authentication)
2. [Agent Management](#agent-management)
3. [Memory Operations](#memory-operations)
4. [Tool Management](#tool-management)
5. [Message & Conversation APIs](#message--conversation-apis)
6. [Cross-Agent Communication](#cross-agent-communication)
7. [Python SDK Reference](#python-sdk-reference)
8. [TypeScript SDK Reference](#typescript-sdk-reference)
9. [Error Handling](#error-handling)
10. [Examples](#examples)

## Authentication

All API requests require authentication using your Letta API key.

### API Key Format
```
sk-let-[rest-of-key]
```

### Authentication Methods

**REST API:**
```bash
curl -H "Authorization: Bearer sk-let-your-key-here" \
     https://api.letta.com/v1/agents
```

**Python SDK:**
```python
from letta_client import Letta

# Connect to Letta Cloud
client = Letta(token="sk-let-your-key-here")

# Connect to local server
client = Letta(base_url="http://localhost:8283")
```

**TypeScript SDK:**
```typescript
import { LettaClient } from '@letta-ai/letta-client'

// Connect to Letta Cloud
const client = new LettaClient({
    token: "sk-let-your-key-here"
});

// Connect to local server
const client = new LettaClient({
    baseUrl: "http://localhost:8283"
});
```

## Agent Management

### Create Agent

Creates a new stateful agent with specified configuration.

**Endpoint:** `POST /v1/agents`

**Parameters:**
- `name` (string, required): Unique name for the agent
- `persona` (string, optional): Agent's personality and behavior description
- `memory` (object, optional): Initial memory configuration
- `tools` (array, optional): List of tool names to attach
- `model` (string, optional): LLM model to use (defaults to configured model)

**Python SDK:**
```python
agent = client.agents.create(
    name="sales-assistant",
    persona="You are a helpful automotive sales assistant with expertise in vehicle pricing and dealer operations.",
    memory={
        "human": "Dealer specializing in Ford vehicles",
        "persona": "Experienced sales professional"
    },
    tools=["web_search", "calculator"]
)
print(f"Created agent: {agent.id}")
```

**TypeScript SDK:**
```typescript
const agent = await client.agents.create({
    name: "sales-assistant",
    persona: "You are a helpful automotive sales assistant...",
    memory: {
        human: "Dealer specializing in Ford vehicles",
        persona: "Experienced sales professional"
    },
    tools: ["web_search", "calculator"]
});
console.log(`Created agent: ${agent.id}`);
```

**Response:**
```json
{
    "id": "agent-123",
    "name": "sales-assistant",
    "created_at": "2025-06-21T10:00:00Z",
    "message_ids": [],
    "memory": {
        "human": "Dealer specializing in Ford vehicles",
        "persona": "Experienced sales professional"
    },
    "tools": ["web_search", "calculator"]
}
```

### List Agents

Retrieves all agents associated with the authenticated user.

**Endpoint:** `GET /v1/agents`

**Parameters:**
- `limit` (int, optional): Maximum number of agents to return
- `offset` (int, optional): Number of agents to skip

**Python SDK:**
```python
agents = client.agents.list(limit=10)
for agent in agents:
    print(f"Agent: {agent.name} (ID: {agent.id})")
```

**Response:**
```json
{
    "agents": [
        {
            "id": "agent-123",
            "name": "sales-assistant",
            "created_at": "2025-06-21T10:00:00Z"
        }
    ],
    "total": 1
}
```

### Get Agent

Retrieves detailed information about a specific agent.

**Endpoint:** `GET /v1/agents/{agent_id}`

**Python SDK:**
```python
agent = client.agents.get(agent_id="agent-123")
print(f"Agent: {agent.name}")
print(f"Tools: {agent.tools}")
```

### Update Agent

Modifies an existing agent's configuration.

**Endpoint:** `PATCH /v1/agents/{agent_id}`

**Parameters:**
- `name` (string, optional): New name for the agent
- `persona` (string, optional): Updated persona description
- `model` (string, optional): Change the LLM model

**Python SDK:**
```python
updated_agent = client.agents.update(
    agent_id="agent-123",
    persona="Updated persona with more automotive expertise"
)
```

### Delete Agent

Permanently removes an agent and all associated data.

**Endpoint:** `DELETE /v1/agents/{agent_id}`

**Python SDK:**
```python
client.agents.delete(agent_id="agent-123")
```

## Memory Operations

### Core Memory

Core memory represents information that's currently "top of mind" for the agent.

#### Get Core Memory

**Endpoint:** `GET /v1/agents/{agent_id}/memory/core`

**Python SDK:**
```python
core_memory = client.agents.memory.get_core(agent_id="agent-123")
print(f"Human: {core_memory.human}")
print(f"Persona: {core_memory.persona}")
```

#### Update Core Memory Block

**Endpoint:** `PATCH /v1/agents/{agent_id}/memory/core/{block_label}`

**Parameters:**
- `block_label` (string): Either "human" or "persona"
- `value` (string): New content for the memory block

**Python SDK:**
```python
# Update human memory block
client.agents.memory.update_core_block(
    agent_id="agent-123",
    block_label="human",
    value="Updated dealer information: Ford dealership in Detroit with 500+ vehicle inventory"
)

# Update persona memory block
client.agents.memory.update_core_block(
    agent_id="agent-123",
    block_label="persona",
    value="Expert automotive sales agent with 10+ years experience"
)
```

#### Append to Core Memory

**Endpoint:** `POST /v1/agents/{agent_id}/memory/core/append`

**Python SDK:**
```python
client.agents.memory.core_append(
    agent_id="agent-123",
    block_label="human",
    content="Additional context: specializes in F-150 trucks"
)
```

#### Replace Core Memory Content

**Python SDK:**
```python
client.agents.memory.core_replace(
    agent_id="agent-123",
    block_label="human",
    old_content="Ford dealership",
    new_content="Premium Ford dealership"
)
```

### Archival Memory

Archival memory provides long-term storage with semantic search capabilities.

#### Search Archival Memory

**Endpoint:** `POST /v1/agents/{agent_id}/memory/archival/search`

**Parameters:**
- `query` (string): Search query
- `count` (int, optional): Number of results to return (default: 5)
- `start` (int, optional): Starting index for pagination

**Python SDK:**
```python
results = client.agents.memory.archival_search(
    agent_id="agent-123",
    query="Ford F-150 pricing",
    count=10
)

for result in results:
    print(f"Memory: {result.content}")
    print(f"Score: {result.score}")
```

#### Insert Archival Memory

**Endpoint:** `POST /v1/agents/{agent_id}/memory/archival/insert`

**Parameters:**
- `content` (string): Content to store in archival memory

**Python SDK:**
```python
client.agents.memory.archival_insert(
    agent_id="agent-123",
    content="Customer John Smith prefers blue F-150s and has a trade-in budget of $25,000"
)
```

## Tool Management

### List Available Tools

**Endpoint:** `GET /v1/tools`

**Python SDK:**
```python
tools = client.tools.list()
for tool in tools:
    print(f"Tool: {tool.name} - {tool.description}")
```

### Get Tool Details

**Endpoint:** `GET /v1/tools/{tool_name}`

**Python SDK:**
```python
tool = client.tools.get(tool_name="web_search")
print(f"Description: {tool.description}")
print(f"Parameters: {tool.parameters}")
```

### Attach Tool to Agent

**Endpoint:** `POST /v1/agents/{agent_id}/tools/{tool_name}`

**Python SDK:**
```python
client.agents.attach_tool(
    agent_id="agent-123",
    tool_name="calculator"
)
```

### Detach Tool from Agent

**Endpoint:** `DELETE /v1/agents/{agent_id}/tools/{tool_name}`

**Python SDK:**
```python
client.agents.detach_tool(
    agent_id="agent-123",
    tool_name="calculator"
)
```

## Message & Conversation APIs

### Send Message

Sends a message to an agent and receives a response.

**Endpoint:** `POST /v1/agents/{agent_id}/messages`

**Parameters:**
- `messages` (array): Array of message objects
- `stream` (boolean, optional): Whether to stream the response

**Python SDK:**
```python
response = client.agents.messages.create(
    agent_id="agent-123",
    messages=[{
        "role": "user",
        "content": "What's the best pricing strategy for my F-150 inventory?"
    }]
)

for message in response.messages:
    print(f"{message.role}: {message.content}")
```

### Stream Messages

**Python SDK:**
```python
stream = client.agents.messages.create_stream(
    agent_id="agent-123",
    messages=[{
        "role": "user", 
        "content": "Analyze current market trends"
    }]
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Get Conversation History

**Endpoint:** `GET /v1/agents/{agent_id}/messages`

**Parameters:**
- `limit` (int, optional): Number of messages to return
- `before` (string, optional): Message ID to paginate before

**Python SDK:**
```python
history = client.agents.messages.list(
    agent_id="agent-123",
    limit=50
)

for message in history.messages:
    print(f"{message.timestamp}: {message.role} - {message.content}")
```

### Search Conversations

**Python SDK:**
```python
# Search by content
results = client.agents.tools.conversation_search(
    agent_id="agent-123",
    query="F-150 pricing",
    count=10
)

# Search by date range
date_results = client.agents.tools.conversation_search_date(
    agent_id="agent-123",
    start_date="2025-06-01",
    end_date="2025-06-21"
)
```

## Cross-Agent Communication

### Send Message to Another Agent

**Python SDK:**
```python
# Agent A sends message to Agent B
response = client.agents.cross_agent.send_message(
    sender_agent_id="agent-123",
    recipient_agent_id="agent-456",
    message="Please analyze the inventory data I'm sharing"
)
```

### List Agent Connections

**Python SDK:**
```python
connections = client.agents.cross_agent.list_connections(
    agent_id="agent-123"
)
```

## Python SDK Reference

### Installation

```bash
pip install letta-client
```

### Client Initialization

```python
from letta_client import Letta, AsyncLetta

# Synchronous client
client = Letta(token="sk-let-your-key")

# Asynchronous client
async_client = AsyncLetta(token="sk-let-your-key")
```

### Async Operations

```python
import asyncio
from letta_client import AsyncLetta

async def create_agent_async():
    client = AsyncLetta(token="sk-let-your-key")
    
    agent = await client.agents.create(
        name="async-agent",
        persona="Async automotive assistant"
    )
    
    response = await client.agents.messages.create(
        agent_id=agent.id,
        messages=[{"role": "user", "content": "Hello!"}]
    )
    
    return response

# Run async function
response = asyncio.run(create_agent_async())
```

## TypeScript SDK Reference

### Installation

```bash
npm install @letta-ai/letta-client
```

### Basic Usage

```typescript
import { LettaClient } from '@letta-ai/letta-client';

const client = new LettaClient({
    token: "sk-let-your-key"
});

// Create agent
const agent = await client.agents.create({
    name: "ts-agent",
    persona: "TypeScript automotive assistant"
});

// Send message
const response = await client.agents.messages.create({
    agentId: agent.id,
    messages: [{
        role: "user",
        content: "Analyze my inventory"
    }]
});
```

## Error Handling

### Python SDK Error Handling

```python
from letta_client.core.api_error import ApiError

try:
    agent = client.agents.create(name="test-agent")
except ApiError as e:
    print(f"API Error: {e.status_code}")
    print(f"Message: {e.body}")
    
    # Handle specific error codes
    if e.status_code == 401:
        print("Authentication failed - check your API key")
    elif e.status_code == 403:
        print("Permission denied")
    elif e.status_code == 404:
        print("Agent not found")
    elif e.status_code == 429:
        print("Rate limit exceeded")
```

### TypeScript SDK Error Handling

```typescript
try {
    const agent = await client.agents.create({
        name: "test-agent"
    });
} catch (error) {
    if (error.statusCode === 401) {
        console.log("Authentication failed");
    } else if (error.statusCode === 429) {
        console.log("Rate limit exceeded");
    }
    console.error("Error:", error.message);
}
```

## Examples

### Complete Agent Setup Example

**Python:**
```python
from letta_client import Letta

# Initialize client
client = Letta(token="sk-let-your-key")

# Create agent
agent = client.agents.create(
    name="automotive-expert",
    persona="""You are an expert automotive sales assistant with deep knowledge of:
    - Vehicle pricing and market trends
    - Inventory management
    - Customer relationship management
    - Trade-in valuations
    Always provide data-driven insights and actionable recommendations.""",
    tools=["web_search", "calculator", "archival_memory_search"]
)

# Set up initial memory
client.agents.memory.update_core_block(
    agent_id=agent.id,
    block_label="human",
    value="Ford dealership in Detroit with 500+ vehicle inventory, specializing in F-150 trucks and SUVs"
)

# Add some archival memory
client.agents.memory.archival_insert(
    agent_id=agent.id,
    content="Historical data: F-150 models sell best in Q4, average days on lot: 45 days"
)

# Send initial message
response = client.agents.messages.create(
    agent_id=agent.id,
    messages=[{
        "role": "user",
        "content": "I have 47 F-150s that have been on the lot for over 90 days. What's my action plan?"
    }]
)

# Process response
for message in response.messages:
    if message.role == "assistant":
        print(f"Agent Response: {message.content}")
```

### Streaming Conversation Example

**Python:**
```python
def stream_conversation(client, agent_id, user_message):
    stream = client.agents.messages.create_stream(
        agent_id=agent_id,
        messages=[{
            "role": "user",
            "content": user_message
        }]
    )
    
    print("Agent: ", end="", flush=True)
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # New line after complete response

# Usage
stream_conversation(
    client, 
    "agent-123", 
    "What's the current market value for a 2023 Ford F-150 XLT?"
)
```

### Multi-Agent Collaboration Example

**Python:**
```python
# Create inventory analysis agent
inventory_agent = client.agents.create(
    name="inventory-analyzer",
    persona="Specialized in inventory analysis and pricing optimization"
)

# Create market research agent  
market_agent = client.agents.create(
    name="market-researcher",
    persona="Expert in automotive market trends and competitive analysis"
)

# Market agent researches trends
market_response = client.agents.messages.create(
    agent_id=market_agent.id,
    messages=[{
        "role": "user",
        "content": "Research current F-150 market trends and pricing"
    }]
)

# Share findings with inventory agent
inventory_response = client.agents.messages.create(
    agent_id=inventory_agent.id,
    messages=[{
        "role": "user",
        "content": f"Based on this market research: {market_response.messages[-1].content}, analyze our F-150 inventory strategy"
    }]
)
```

### Batch Operations Example

**Python:**
```python
# Create batch operations for multiple agents
batch_requests = [
    {
        "agent_id": "agent-123",
        "messages": [{"role": "user", "content": "Analyze Q1 sales"}]
    },
    {
        "agent_id": "agent-456", 
        "messages": [{"role": "user", "content": "Review inventory levels"}]
    }
]

# Process batch
batch = client.batches.create(requests=batch_requests)

# Monitor batch status
while batch.status != "completed":
    batch = client.batches.retrieve(batch_id=batch.id)
    print(f"Batch status: {batch.status}")
    await asyncio.sleep(5)

# Retrieve results
results = client.batches.results.list(batch_id=batch.id)
```

### Health Check and Monitoring

**Python:**
```python
# Health check
try:
    health = client.health.check()
    print(f"Service status: {health.status}")
except Exception as e:
    print(f"Service unavailable: {e}")

# Usage statistics  
usage = client.usage.retrieve(
    start_date="2025-06-01",
    end_date="2025-06-21"
)
print(f"Total API calls: {usage.total_requests}")
print(f"Total tokens: {usage.total_tokens}")
```

### Advanced Memory Operations

**Python:**
```python
# Create custom memory block
client.agents.memory.create_block(
    agent_id="agent-123",
    block_label="customer_preferences",
    value="Customer prefers blue vehicles, budget $30k, needs financing",
    description="Customer-specific preferences and requirements"
)

# Bulk memory operations
memory_updates = [
    {"block_label": "human", "content": "Updated dealer info"},
    {"block_label": "persona", "content": "Enhanced expertise level"}
]

client.agents.memory.bulk_update(
    agent_id="agent-123",
    updates=memory_updates
)

# Memory analytics
memory_stats = client.agents.memory.analytics(agent_id="agent-123")
print(f"Total memory blocks: {memory_stats.total_blocks}")
print(f"Memory usage: {memory_stats.size_bytes} bytes")
```

### Template and Configuration Management

**Python:**
```python
# Create agent template
template = client.agents.templates.create(
    agent_id="agent-123",
    name="automotive-sales-template",
    description="Template for automotive sales agents",
    version="1.0.0"
)

# Apply template to new agent
new_agent = client.agents.create_from_template(
    template_id=template.id,
    name="dealer-assistant-2",
    customizations={
        "persona": "Specialized in truck sales",
        "tools": ["web_search", "calculator", "inventory_lookup"]
    }
)

# List available templates
templates = client.templates.list(category="automotive")
for template in templates:
    print(f"Template: {template.name} - {template.description}")
```

### Voice and Multimodal Capabilities

**Python:**
```python
# Voice chat completions
voice_response = client.voice.create_voice_chat_completions(
    agent_id="agent-123",
    request={
        "messages": [
            {
                "role": "user",
                "content": "What's the best financing option for this customer?",
                "audio": {
                    "format": "wav",
                    "data": base64_audio_data
                }
            }
        ],
        "model": "claude-sonnet-4",
        "voice": "nova",
        "response_format": {"type": "audio"}
    }
)

# Image analysis with agent
image_response = client.agents.messages.create(
    agent_id="agent-123",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Analyze this vehicle image for damage assessment"
            },
            {
                "type": "image",
                "image": {
                    "url": "data:image/jpeg;base64,..." 
                }
            }
        ]
    }]
)
```

### Identity and Access Management

**Python:**
```python
# Create organization identity
org_identity = client.identities.create(
    identifier_key="dealership-001",
    name="Premier Ford Dealership",
    identity_type="org"
)

# Set identity properties
client.identities.properties.upsert(
    identity_id=org_identity.id,
    request=[
        {"key": "location", "value": "Detroit, MI", "type": "string"},
        {"key": "specialization", "value": "Ford F-150", "type": "string"},
        {"key": "inventory_size", "value": "500", "type": "number"}
    ]
)

# List user identities
identities = client.identities.list()
for identity in identities:
    print(f"Identity: {identity.name} ({identity.identity_type})")
```

### MCP Tool Integration

**Python:**
```python
# Add MCP tool to agent
client.tools.add_mcp_tool(
    mcp_server_name="firecrawl-server",
    mcp_tool_name="web_scrape"
)

# Add Composio integration
client.tools.add_composio_tool(
    composio_action_name="gmail_send_email"
)

# List available Composio apps
composio_apps = client.tools.list_composio_apps()
for app in composio_apps:
    print(f"Available app: {app.name}")

# List actions for specific app
gmail_actions = client.tools.list_composio_actions_by_app(
    composio_app_name="gmail"
)
```

## Sources

- [Letta API Overview](https://docs.letta.com/api-reference/overview) - Official API documentation
- [Letta Python SDK Documentation](https://github.com/letta-ai/letta-python) - Complete Python SDK reference
- [Letta TypeScript SDK Documentation](https://github.com/letta-ai/letta-node) - TypeScript/Node.js SDK
- [Letta Quickstart Guide](https://docs.letta.com/quickstart) - Getting started tutorial
- [Letta Multi-Agent Systems](https://docs.letta.com/guides/agents/multi-agent) - Multi-agent coordination
- [Letta Vibecoding Guide](https://docs.letta.com/prompts.md) - AI assistant development best practices
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification) - MCP technical specification
- [Context7 Letta Documentation](https://context7.ai/) - Additional code examples and patterns