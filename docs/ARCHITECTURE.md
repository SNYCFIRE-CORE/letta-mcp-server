# Letta MCP Server Architecture

This document provides a comprehensive overview of the Letta MCP Server architecture, detailing how it enables seamless communication between Claude and Letta.ai agents through the Model Context Protocol.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Core Components](#core-components)
4. [Transport Mechanisms](#transport-mechanisms)
5. [Authentication Flow](#authentication-flow)
6. [Message Flow](#message-flow)
7. [Error Handling](#error-handling)
8. [Security Architecture](#security-architecture)
9. [Performance Considerations](#performance-considerations)
10. [Deployment Patterns](#deployment-patterns)

## System Overview

The Letta MCP Server acts as a bridge between Claude (the MCP client) and Letta.ai's stateful agent platform. It translates MCP protocol messages into Letta API calls and vice versa, enabling Claude users to interact with persistent, memory-enabled AI agents.

### Key Architectural Principles

1. **Protocol Translation**: Seamless conversion between MCP JSON-RPC and Letta REST API
2. **Stateless Server**: MCP server maintains no session state; all persistence handled by Letta.ai
3. **Async Operation**: Full async/await support for high-concurrency scenarios
4. **Error Resilience**: Comprehensive error handling with graceful degradation
5. **Security First**: Multi-layer authentication and authorization

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Claude Desktop/Code                          │
│                         (MCP Client)                               │
└─────────────────────┬───────────────────────────────────────────────┘
                      │ JSON-RPC over STDIO/HTTP
                      │
┌─────────────────────▼───────────────────────────────────────────────┐
│                   Letta MCP Server                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Transport Layer                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │   │
│  │  │   STDIO     │  │    HTTP     │  │    Server-Sent      │ │   │
│  │  │ Transport   │  │  Transport  │  │   Events (SSE)      │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Protocol Layer                                 │   │
│  │  • JSON-RPC 2.0 Message Parsing                            │   │
│  │  • Request/Response Correlation                             │   │
│  │  • Error Code Translation                                   │   │
│  │  • Schema Validation                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              MCP Tool Handlers                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │   │
│  │  │   Agent     │  │   Memory    │  │    Conversation     │ │   │
│  │  │ Management  │  │ Operations  │  │    Management       │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │   │
│  │  │    Tool     │  │   Cross-    │  │    Batch            │ │   │
│  │  │ Management  │  │ Agent Comm  │  │   Operations        │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              HTTP Client Layer                              │   │
│  │  • Connection Pooling                                       │   │
│  │  • Request Retry Logic                                      │   │
│  │  • Rate Limiting                                            │   │
│  │  • Authentication Header Management                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────┘
                      │ HTTPS REST API
                      │
┌─────────────────────▼───────────────────────────────────────────────┐
│                      Letta.ai Cloud                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Agent Runtime                                  │   │
│  │  • Claude Sonnet/Opus Models                               │   │
│  │  • Memory Management (Core + Archival)                     │   │
│  │  • Tool Execution                                          │   │
│  │  • Context Management                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Data Persistence                               │   │
│  │  • Agent Configurations                                    │   │
│  │  • Conversation History                                    │   │
│  │  • Memory Blocks                                           │   │
│  │  • Tool Definitions                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Transport Layer

The transport layer handles the underlying communication between Claude and the MCP server, supporting multiple transport mechanisms:

#### STDIO Transport
- **Use Case**: Local Claude Desktop integration
- **Protocol**: JSON-RPC over standard input/output
- **Benefits**: Simple, direct communication with no network overhead
- **Security**: Process-level isolation

```python
# STDIO Transport Implementation
transport = StdioServerTransport()
await server.connect(transport)
```

#### HTTP Transport  
- **Use Case**: Remote deployments, web integrations
- **Protocol**: JSON-RPC over HTTP POST requests
- **Benefits**: Network transparent, supports load balancing
- **Security**: TLS encryption, authentication headers

```python
# HTTP Transport Implementation
transport = HTTPServerTransport(host="0.0.0.0", port=8080)
await server.connect(transport)
```

#### Server-Sent Events (SSE)
- **Use Case**: Real-time streaming responses
- **Protocol**: HTTP with event-stream content type
- **Benefits**: Real-time updates, connection resumability
- **Security**: Same as HTTP with session management

### 2. Protocol Layer

The protocol layer manages JSON-RPC 2.0 message handling:

#### Message Types

**Requests** - Expect responses:
```json
{
  "jsonrpc": "2.0",
  "id": "req-123",
  "method": "letta_list_agents",
  "params": {"limit": 10}
}
```

**Responses** - Reply to requests:
```json
{
  "jsonrpc": "2.0", 
  "id": "req-123",
  "result": {
    "agents": [...]
  }
}
```

**Notifications** - One-way messages:
```json
{
  "jsonrpc": "2.0",
  "method": "letta_agent_status_changed",
  "params": {"agent_id": "agent-123", "status": "ready"}
}
```

**Errors** - Failure responses:
```json
{
  "jsonrpc": "2.0",
  "id": "req-123", 
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {"field": "agent_id", "issue": "required"}
  }
}
```

### 3. MCP Tool Handlers

The MCP server exposes 30+ tools organized into functional categories:

#### Agent Management Tools
- `letta_list_agents` - List all user agents
- `letta_create_agent` - Create new agent
- `letta_get_agent_info` - Get agent details
- `letta_update_agent` - Modify agent configuration
- `letta_delete_agent` - Remove agent

#### Memory Operations Tools
- `letta_get_agent_memory` - Retrieve memory blocks
- `letta_update_agent_memory` - Modify memory content
- `letta_search_archival_memory` - Search long-term memory
- `letta_insert_archival_memory` - Add archival memory

#### Conversation Management Tools
- `letta_send_message` - Send message to agent
- `letta_stream_chat` - Stream agent responses
- `letta_get_conversation_history` - Retrieve message history

#### Tool Management Tools
- `letta_list_tools` - List available tools
- `letta_get_agent_tools` - Get agent's tools
- `letta_attach_tool` - Add tool to agent
- `letta_detach_tool` - Remove tool from agent

#### Cross-Agent Communication Tools
- `letta_cross_agent_message` - Agent-to-agent messaging
- `letta_list_connections` - List agent connections

### 4. HTTP Client Layer

The HTTP client layer manages communication with Letta.ai:

#### Connection Management
- **Connection Pooling**: Reuses HTTP connections for efficiency
- **Timeout Configuration**: Request, connection, and read timeouts
- **Retry Logic**: Exponential backoff for transient failures
- **Rate Limiting**: Respects Letta.ai API rate limits

#### Authentication
- **Bearer Token**: Uses Letta API keys in Authorization header
- **Token Validation**: Validates key format and expiration
- **Security Headers**: Adds required security headers

```python
# HTTP Client Configuration
http_client = AsyncHTTPClient(
    base_url="https://api.letta.com/v1",
    timeout=httpx.Timeout(30.0, connect=10.0),
    limits=httpx.Limits(max_connections=20),
    headers={"Authorization": f"Bearer {api_key}"}
)
```

## Transport Mechanisms

### STDIO (Standard Input/Output)

**How it works:**
1. Claude launches MCP server as subprocess
2. Claude sends JSON-RPC requests via stdin
3. MCP server responds via stdout
4. Error logs go to stderr (visible in Claude logs)

**Configuration:**
```json
{
  "mcpServers": {
    "letta": {
      "command": "python",
      "args": ["-m", "letta_mcp_server"],
      "env": {
        "LETTA_API_KEY": "sk-let-your-key-here"
      }
    }
  }
}
```

**Advantages:**
- Simple setup and configuration
- No network security concerns
- Direct process communication
- Automatic process lifecycle management

**Disadvantages:**
- Limited to local deployments
- No shared server instances
- Process startup overhead

### HTTP (HyperText Transfer Protocol)

**How it works:**
1. MCP server runs as HTTP service
2. Claude connects via HTTP client transport
3. Requests sent as HTTP POST to `/mcp` endpoint
4. Responses returned as JSON or SSE streams

**Configuration:**
```json
{
  "mcpServers": {
    "letta": {
      "transport": {
        "type": "http",
        "url": "http://localhost:8080/mcp"
      },
      "env": {
        "LETTA_API_KEY": "sk-let-your-key-here"
      }
    }
  }
}
```

**Advantages:**
- Remote deployment capability
- Shared server instances
- Load balancing support
- Better for production environments

**Disadvantages:**
- Network security requirements
- More complex deployment
- Latency considerations

### Server-Sent Events (SSE)

**How it works:**
1. Client establishes SSE connection to server
2. Server can push real-time updates
3. Connection automatically reconnects on failure
4. Events include unique IDs for replay capability

**Event Types:**
- `agent_response` - Agent message chunks
- `tool_execution` - Tool call progress
- `memory_update` - Memory modification events
- `error` - Error notifications

**Advantages:**
- Real-time updates
- Connection resumability
- Browser-native support
- Efficient for streaming data

**Disadvantages:**
- One-way communication only
- Requires HTTP transport
- Browser connection limits

## Authentication Flow

### 1. API Key Validation

```mermaid
sequenceDiagram
    participant Claude as Claude Client
    participant MCP as Letta MCP Server
    participant Letta as Letta.ai API

    Claude->>MCP: JSON-RPC Request
    MCP->>MCP: Extract API Key from Environment
    MCP->>Letta: Validate API Key (GET /agents)
    alt Valid Key
        Letta->>MCP: 200 OK + Agent List
        MCP->>Claude: Process Request
    else Invalid Key
        Letta->>MCP: 401 Unauthorized
        MCP->>Claude: Authentication Error
    end
```

### 2. Request Authentication

Every request to Letta.ai includes:

```http
POST /v1/agents HTTP/1.1
Host: api.letta.com
Authorization: Bearer sk-let-your-key-here
Content-Type: application/json
User-Agent: letta-mcp-server/1.0.0

{
  "name": "automotive-assistant",
  "persona": "You are an expert automotive sales agent..."
}
```

### 3. Error Handling

Authentication errors are mapped to MCP error codes:

- **401 Unauthorized** → `-32001` (Authentication failed)
- **403 Forbidden** → `-32002` (Permission denied)  
- **429 Rate Limited** → `-32003` (Rate limit exceeded)

## Message Flow

### Agent Creation Flow

```mermaid
sequenceDiagram
    participant Claude as Claude Client
    participant MCP as Letta MCP Server
    participant Letta as Letta.ai API

    Claude->>MCP: letta_create_agent(name, persona, tools)
    MCP->>MCP: Validate Parameters
    MCP->>Letta: POST /v1/agents
    Letta->>Letta: Create Agent Instance
    Letta->>MCP: 201 Created + Agent Object
    MCP->>MCP: Transform Response to MCP Format
    MCP->>Claude: Agent Created Successfully
```

### Message Sending Flow

```mermaid
sequenceDiagram
    participant Claude as Claude Client
    participant MCP as Letta MCP Server
    participant Letta as Letta.ai API
    participant Agent as Letta Agent

    Claude->>MCP: letta_send_message(agent_id, message)
    MCP->>MCP: Validate Agent ID
    MCP->>Letta: POST /v1/agents/{id}/messages
    Letta->>Agent: Process Message
    Agent->>Agent: Generate Response
    Agent->>Letta: Response + Tool Calls
    Letta->>MCP: 200 OK + Response Object
    MCP->>Claude: Agent Response with Tool Results
```

### Streaming Response Flow

```mermaid
sequenceDiagram
    participant Claude as Claude Client
    participant MCP as Letta MCP Server
    participant Letta as Letta.ai API

    Claude->>MCP: letta_stream_chat(agent_id, message)
    MCP->>Letta: POST /v1/agents/{id}/messages (stream=true)
    loop Streaming Response
        Letta->>MCP: SSE Event Chunk
        MCP->>MCP: Parse Chunk
        MCP->>Claude: MCP Response Chunk
    end
    Letta->>MCP: [DONE]
    MCP->>Claude: Stream Complete
```

## Error Handling

### Error Categories

1. **Transport Errors**
   - Connection failures
   - Timeout errors
   - Protocol violations

2. **Authentication Errors**
   - Invalid API keys
   - Expired tokens
   - Permission denials

3. **API Errors**
   - Invalid parameters
   - Resource not found
   - Rate limiting

4. **Agent Errors**
   - Agent not found
   - Agent busy/unavailable
   - Memory corruption

### Error Mapping

| Letta API Error | HTTP Status | MCP Error Code | Description |
|-----------------|-------------|----------------|-------------|
| Authentication Failed | 401 | -32001 | Invalid API key |
| Permission Denied | 403 | -32002 | Insufficient permissions |
| Rate Limited | 429 | -32003 | Too many requests |
| Not Found | 404 | -32004 | Resource not found |
| Invalid Request | 400 | -32602 | Invalid parameters |
| Server Error | 500 | -32603 | Internal server error |

### Retry Strategy

```python
async def retry_request(func, max_attempts=3, backoff_factor=2):
    for attempt in range(max_attempts):
        try:
            return await func()
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_attempts - 1:
                raise
            await asyncio.sleep(backoff_factor ** attempt)
```

## Security Architecture

### 1. Authentication Layers

- **Environment Variables**: API keys stored securely
- **Header Authentication**: Bearer token in all requests  
- **Key Validation**: Real-time validation against Letta.ai
- **Permission Checking**: Operation-level access control

### 2. Input Validation

- **Schema Validation**: JSON schema validation for all inputs
- **Parameter Sanitization**: Clean and validate all parameters
- **Length Limits**: Maximum length for text fields
- **Type Checking**: Strict type validation

### 3. Transport Security

- **TLS Encryption**: All HTTP communication encrypted
- **Certificate Validation**: Verify Letta.ai SSL certificates
- **Header Injection Prevention**: Sanitize custom headers
- **Request Size Limits**: Prevent oversized requests

### 4. Error Information Security

- **Error Sanitization**: Remove sensitive data from error messages
- **Log Redaction**: Redact API keys and tokens from logs
- **Stack Trace Filtering**: Hide internal implementation details

## Performance Considerations

### 1. Connection Management

- **Connection Pooling**: Reuse HTTP connections
- **Keep-Alive**: Use persistent connections
- **Concurrent Requests**: Support multiple simultaneous requests
- **Resource Limits**: Prevent resource exhaustion

### 2. Caching Strategy

- **Agent Metadata**: Cache agent configurations
- **Tool Definitions**: Cache tool schemas
- **Memory Blocks**: Cache frequently accessed memory
- **TTL Management**: Automatic cache expiration

### 3. Streaming Optimization

- **Chunk Size**: Optimal chunk sizes for streaming
- **Buffer Management**: Efficient memory usage
- **Backpressure**: Handle slow consumers
- **Connection Recovery**: Automatic reconnection

### 4. Resource Management

- **Memory Usage**: Monitor memory consumption
- **CPU Optimization**: Async I/O for CPU efficiency
- **File Descriptors**: Manage file descriptor limits
- **Garbage Collection**: Efficient memory cleanup

## Deployment Patterns

### 1. Local Development

```bash
# Install and run locally
pip install letta-mcp-server
python -m letta_mcp_server
```

**Configuration:**
- STDIO transport for Claude Desktop
- Environment variables for API keys
- Local debugging enabled

### 2. Single-User Server

```bash
# Run as HTTP server
python -m letta_mcp_server --transport http --port 8080
```

**Configuration:**
- HTTP transport on localhost
- Single API key authentication
- Basic logging

### 3. Multi-User Production

```bash
# Production deployment with multiple workers
gunicorn letta_mcp_server:app --workers 4 --bind 0.0.0.0:8080
```

**Configuration:**
- Load balancer (nginx/AWS ALB)
- Multiple worker processes
- Centralized logging (ELK stack)
- Health checks and monitoring
- Auto-scaling capabilities

### 4. Containerized Deployment

```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -e .
EXPOSE 8080
CMD ["python", "-m", "letta_mcp_server", "--transport", "http"]
```

**Configuration:**
- Docker containers with health checks
- Kubernetes deployment with secrets
- Service mesh for communication
- Distributed tracing

## Sources

- [Model Context Protocol Architecture](https://modelcontextprotocol.io/docs/concepts/architecture)
- [MCP Transport Documentation](https://modelcontextprotocol.io/docs/concepts/transports)
- [Letta.ai API Reference](https://docs.letta.com/api-reference/)
- [Letta Python SDK Documentation](https://github.com/letta-ai/letta-python)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/)
- [FastMCP Framework Documentation](https://github.com/jlowin/fastmcp)