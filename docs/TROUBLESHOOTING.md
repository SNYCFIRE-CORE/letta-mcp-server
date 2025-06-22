# MCP Troubleshooting Guide

This guide helps diagnose and resolve common issues with Model Context Protocol (MCP) servers, specifically for the Letta MCP Server implementation.

## Table of Contents

- [Connection Issues](#connection-issues)
- [Authentication Problems](#authentication-problems)
- [Configuration Errors](#configuration-errors)
- [Transport Protocol Issues](#transport-protocol-issues)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)
- [Debugging Tools and Techniques](#debugging-tools-and-techniques)
- [Logging and Monitoring](#logging-and-monitoring)

---

## Connection Issues

### Symptoms
- "Failed to connect" errors
- Server not responding to client requests
- Connection timeouts
- Transport errors

### Common Causes

1. **Server Misconfiguration**
   - Incorrect network ports
   - Firewall blocking connections
   - Missing dependencies
   - Server not running or crashed

2. **Network Issues**
   - Port conflicts with other services
   - Firewall rules blocking MCP traffic
   - Network connectivity problems

### Solutions

1. **Verify Server Status**
   ```bash
   # Check if server process is running
   ps aux | grep letta-mcp
   
   # Check port availability
   netstat -tuln | grep :8080
   ```

2. **Check Dependencies**
   ```bash
   # Verify all required packages are installed
   pip list | grep -E "(fastapi|uvicorn|letta)"
   ```

3. **Network Configuration**
   - Ensure the server port (default 8080) is not blocked by firewall
   - Verify no other services are using the same port
   - Test local connectivity: `curl http://localhost:8080/health`

4. **Server Logs Analysis**
   - Check server startup logs for initialization errors
   - Monitor connection attempts in real-time
   - Look for dependency loading failures

**Source**: [Research on MCP common issues](https://docs.modelcontextprotocol.io/)

---

## Authentication Problems

### Symptoms
- 401 Unauthorized responses
- API key validation failures
- Authentication token expired errors
- Permission denied messages

### Common Causes

1. **Credential Issues**
   - Missing or incorrect API keys
   - Expired authentication tokens
   - Malformed credentials format

2. **Configuration Problems**
   - Mismatched client/server authentication methods
   - Incorrect credential storage or retrieval

### Solutions

1. **Verify API Keys**
   ```bash
   # Check environment variables
   echo $LETTA_API_KEY
   echo $ANTHROPIC_API_KEY
   
   # Validate key format (should start with specific prefixes)
   # Letta keys: sk-let-
   # Anthropic keys: sk-ant-
   ```

2. **Test Authentication**
   ```bash
   # Test Letta API directly
   curl -H "Authorization: Bearer $LETTA_API_KEY" \
        https://api.letta.com/v1/agents
   ```

3. **Configuration Audit**
   - Review `.env` file for correct key names
   - Ensure no trailing spaces in environment variables
   - Verify credential rotation policies are up to date

4. **Security Best Practices**
   - Store credentials securely (environment variables, not hardcoded)
   - Implement proper credential rotation
   - Use separate keys for development/production

**Source**: [MCP Authentication troubleshooting](https://modelcontextprotocol.info/docs/concepts/transports/)

---

## Configuration Errors

### Symptoms
- Context scope issues (data leaks or isolation problems)
- Memory leaks from unreleased contexts
- Schema validation failures
- Lifecycle management errors

### Common Causes

1. **Context Scoping Problems**
   - Context boundaries too broad (shared across users/sessions)
   - Context boundaries too narrow (excessive isolation)
   - Poor context lifecycle management

2. **Configuration Mismatches**
   - Invalid JSON configuration files
   - Missing required configuration parameters
   - Version compatibility issues

### Solutions

1. **Context Boundary Definition**
   ```python
   # Correct context scoping example
   @contextmanager
   def user_session_context(user_id: str, session_id: str):
       context = create_context(scope=f"user:{user_id}:session:{session_id}")
       try:
           yield context
       finally:
           context.cleanup()  # Proper lifecycle management
   ```

2. **Configuration Validation**
   ```bash
   # Validate JSON configuration
   python -m json.tool config.json
   
   # Check required parameters
   python -c "import json; config=json.load(open('config.json')); print(config.keys())"
   ```

3. **Schema Validation**
   - Use tools to automatically check schema conformity
   - Implement runtime validation for context data
   - Regular configuration audits

4. **Lifecycle Management**
   - Implement proper context initialization and disposal
   - Use context managers for automatic cleanup
   - Monitor for memory leaks from unreleased contexts

**Source**: [MCP Configuration best practices](https://stackoverflow.com/questions/79582846/)

---

## Transport Protocol Issues

### Symptoms
- "SSE connection not established" errors
- Transport type mismatches
- Protocol negotiation failures
- Message format errors

### Common Causes

1. **Transport Mismatch**
   - Client expects SSE but server uses STDIO
   - Protocol version incompatibilities
   - Missing transport adapters

2. **Message Format Issues**
   - Invalid JSON-RPC messages
   - Incorrect message serialization
   - Protocol violations

### Solutions

1. **Transport Configuration**
   ```python
   # For STDIO transport
   transport = StdioServerTransport()
   
   # For SSE transport  
   transport = SSEServerTransport("/messages", response)
   
   # For HTTP transport
   transport = HTTPServerTransport()
   ```

2. **MCP Inspector Issues**
   - MCP Inspector always negotiates SSE layer even for STDIO servers
   - **Solution Options**:
     a. Make Inspector spawn server via STDIO with exact Python binary/env
     b. Switch server to SSE transport to match Inspector expectations
     c. Use `mcp-proxy` as stdio→sse bridge
     d. Use more flexible MCP client that supports transport declaration

3. **Protocol Debugging**
   ```bash
   # Test different transport methods
   # STDIO
   python server.py
   
   # SSE
   curl -H "Accept: text/event-stream" http://localhost:8080/sse
   
   # HTTP
   curl -X POST http://localhost:8080/messages
   ```

4. **Message Validation**
   - Ensure all stdout messages are valid JSON-RPC
   - Use stderr for logging, never stdout in STDIO mode
   - Implement custom logging utility for mode switching

**Source**: [MCP Transport debugging guide](https://jianliao.github.io/blog/debug-mcp-stdio-transport)

---

## Performance Issues

### Symptoms
- Slow response times
- Request timeouts
- High memory usage
- CPU bottlenecks

### Common Causes

1. **Resource Constraints**
   - Insufficient memory allocation
   - CPU limitations during inference
   - GPU allocation failures

2. **Network Latency**
   - Slow external API calls
   - High network round-trip times
   - Inefficient request batching

### Solutions

1. **Resource Monitoring**
   ```bash
   # Monitor system resources
   htop
   nvidia-smi  # For GPU usage
   
   # Check memory usage
   ps aux --sort=-%mem | head
   ```

2. **Performance Optimization**
   - Implement request caching for repeated calls
   - Use connection pooling for external APIs
   - Optimize batch processing
   - Consider async/await patterns for I/O operations

3. **Timeout Configuration**
   ```python
   # Configure appropriate timeouts
   TIMEOUT_CONFIG = {
       "request_timeout": 30,      # seconds
       "connection_timeout": 10,   # seconds
       "read_timeout": 60         # seconds
   }
   ```

4. **Resource Allocation**
   - Monitor memory allocation failures
   - Implement CPU fallback for GPU failures
   - Use resource pooling for expensive operations

**Source**: [MCP Performance debugging](https://modelcontextprotocol.io/docs/tools/debugging)

---

## Common Error Messages

### "Error: SSE connection not established"

**Cause**: Transport protocol mismatch between client and server.

**Solution**:
```bash
# Option 1: Use mcp-proxy bridge
npm install -g mcp-proxy
mcp-proxy --stdio-command "python server.py" --port 8080

# Option 2: Switch to SSE transport in server
# Update server code to use SSEServerTransport
```

### "Failed to connect: [error details]"

**Cause**: Network connectivity or server availability issues.

**Solutions**:
1. Check server is running: `ps aux | grep server`
2. Verify port accessibility: `telnet localhost 8080`
3. Check firewall rules
4. Review server logs for startup errors

### "Transport error: [exception details]"

**Cause**: Protocol-level communication failures.

**Solutions**:
1. Validate message format (JSON-RPC compliance)
2. Check transport configuration matches client expectations
3. Implement proper error handling in transport layer

### "Authorization failed" / "Invalid API key"

**Cause**: Authentication credential issues.

**Solutions**:
1. Verify API key format and validity
2. Check environment variable loading
3. Test credentials with direct API calls
4. Ensure proper credential storage/rotation

**Source**: [MCP Error handling patterns](https://levelup.gitconnected.com/mcp-server-and-client-with-sse-the-new-streamable-http-d860850d9d9d)

---

## Debugging Tools and Techniques

### 1. MCP Inspector

Interactive tool for testing MCP servers:
```bash
# Install and run MCP Inspector
npm install -g @modelcontextprotocol/inspector
mcp-inspector
```

**Features**:
- Live connection state monitoring
- Interactive request/response testing
- Error condition simulation
- Protocol message inspection

### 2. Server Logging

**For STDIO Transport**:
```python
import sys
import logging

# Configure logging to stderr (stdout interferes with protocol)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)
```

**For HTTP/SSE Transport**:
```python
# Can use stdout safely
logging.basicConfig(level=logging.DEBUG)
```

### 3. Client-Side Debugging

**Claude Desktop**:
```bash
# View MCP logs (macOS)
tail -f ~/Library/Logs/Claude/mcp*.log

# Enable Chrome DevTools in Claude Desktop
# Open Developer > Toggle Developer Tools
```

**Custom Clients**:
- Use browser DevTools Network panel
- Monitor WebSocket connections
- Inspect JSON-RPC message payloads

### 4. Network Debugging

```bash
# Monitor network connections
netstat -an | grep :8080

# Trace network requests
tcpdump -i lo port 8080

# Test HTTP endpoints
curl -v http://localhost:8080/health
```

**Source**: [MCP Debugging documentation](https://modelcontextprotocol.io/docs/tools/debugging)

---

## Logging and Monitoring

### Essential Log Categories

1. **Connection/Authentication Events**
   ```python
   logger.info(f"Client connected: {client_ip} at {timestamp}")
   logger.warning(f"Authentication failed: {user_id} - {error_type}")
   logger.info(f"Session created: {session_id} for user {user_id}")
   ```

2. **Request/Response Handling**
   ```python
   logger.debug(f"Request {request_id}: {sanitized_params}")
   logger.info(f"Processing time: {processing_time}ms for {request_id}")
   logger.error(f"Request failed {request_id}: {error_details}")
   ```

3. **System Resource Events**
   ```python
   logger.warning(f"High memory usage: {memory_percent}%")
   logger.error(f"GPU allocation failed, falling back to CPU")
   logger.info(f"Resource pool status: {active_connections}/{max_connections}")
   ```

### Log Analysis

```bash
# Real-time log monitoring
tail -n 20 -F ~/Library/Logs/Claude/mcp*.log

# Search for specific errors
grep -i "error\|failed\|timeout" server.log

# Analyze connection patterns
grep "Client connected" server.log | awk '{print $4}' | sort | uniq -c
```

### Monitoring Strategy

1. **Proactive Monitoring**
   - Set up alerts for error rate thresholds
   - Monitor response time percentiles
   - Track resource utilization trends

2. **Error Tracking**
   - Categorize errors by type and frequency
   - Implement error rate limiting
   - Maintain error resolution documentation

3. **Performance Metrics**
   - Track request/response latencies
   - Monitor concurrent connection counts
   - Measure resource utilization patterns

**Source**: [MCP Logging best practices](https://modelcontextprotocol.info/docs/concepts/transports/)

---

## Real-World Troubleshooting Scenarios

### Scenario 1: "Headers Already Sent" Error in HTTP Transport

**Symptoms:**
```
Error: Cannot set headers after they are sent to the client
```

**Root Cause**: Attempting to send response headers after SSE stream has started.

**Solution**:
```python
async def handle_streaming_response(request, response):
    # Check if headers already sent
    if not response.headers_sent:
        response.headers["Content-Type"] = "text/event-stream"
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Connection"] = "keep-alive"
    
    # Start streaming
    await response.start_stream()
```

### Scenario 2: MCP Inspector SSE Negotiation Issues

**Problem**: MCP Inspector always negotiates SSE layer even for STDIO servers.

**Solutions**:
1. **Use stdio→sse bridge**:
   ```bash
   npm install -g mcp-proxy
   mcp-proxy --stdio-command "python server.py" --port 8080
   ```

2. **Switch server to SSE transport**:
   ```python
   # Instead of StdioServerTransport
   transport = SSEServerTransport("/messages", response)
   ```

3. **Use flexible MCP client**:
   ```python
   # Custom client that supports transport declaration
   client = FlexibleMCPClient(transport_type="stdio")
   ```

### Scenario 3: Letta Rate Limiting in Production

**Symptoms:**
- HTTP 429 responses
- "Rate limit exceeded" errors
- Delayed responses during peak usage

**Solutions**:
```python
import asyncio
from datetime import datetime, timedelta

class RateLimitedLettaClient:
    def __init__(self, api_key, rate_limit=100):
        self.client = Letta(token=api_key)
        self.rate_limit = rate_limit
        self.request_times = []
    
    async def _wait_for_rate_limit(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        self.request_times = [
            t for t in self.request_times 
            if now - t < timedelta(minutes=1)
        ]
        
        if len(self.request_times) >= self.rate_limit:
            # Wait until oldest request is 1 minute old
            sleep_time = 60 - (now - self.request_times[0]).seconds
            await asyncio.sleep(sleep_time)
    
    async def send_message(self, agent_id, message):
        await self._wait_for_rate_limit()
        self.request_times.append(datetime.now())
        return await self.client.agents.messages.create(
            agent_id=agent_id, 
            messages=[{"role": "user", "content": message}]
        )
```

### Scenario 4: Memory Block Corruption

**Symptoms:**
- Agent responses seem inconsistent
- Memory searches return unexpected results
- Agent "forgets" recent interactions

**Debugging Steps**:
```python
# 1. Inspect current memory state
memory = client.agents.memory.get_core(agent_id="agent-123")
print(f"Human block: {memory.human}")
print(f"Persona block: {memory.persona}")

# 2. Check archival memory integrity
archival_search = client.agents.memory.archival_search(
    agent_id="agent-123",
    query="recent interactions",
    count=50
)
print(f"Archival entries: {len(archival_search)}")

# 3. Validate memory block checksums (if available)
memory_stats = client.agents.memory.analytics(agent_id="agent-123")
if memory_stats.corruption_detected:
    print("Memory corruption detected!")
    
    # Backup current state
    backup = client.agents.export(agent_id="agent-123")
    
    # Restore from known good state
    client.agents.memory.restore_from_backup(
        agent_id="agent-123",
        backup_id="backup-xyz"
    )
```

### Scenario 5: WebSocket Connection Drops in Streaming

**Symptoms:**
- Streaming responses cut off mid-stream
- Connection errors during long operations
- Inconsistent streaming behavior

**Solution with Auto-Reconnect**:
```python
import asyncio
import websockets
from websockets.exceptions import ConnectionClosed

class ResilientStreamingClient:
    def __init__(self, agent_id, api_key):
        self.agent_id = agent_id
        self.api_key = api_key
        self.websocket = None
        self.max_retries = 3
        
    async def connect(self):
        uri = f"wss://api.letta.com/v1/agents/{self.agent_id}/stream"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        for attempt in range(self.max_retries):
            try:
                self.websocket = await websockets.connect(uri, extra_headers=headers)
                return True
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return False
    
    async def stream_chat(self, message):
        if not self.websocket:
            if not await self.connect():
                raise Exception("Failed to establish connection")
        
        try:
            await self.websocket.send(json.dumps({
                "type": "message",
                "content": message
            }))
            
            async for raw_message in self.websocket:
                data = json.loads(raw_message)
                if data["type"] == "response_chunk":
                    yield data["content"]
                elif data["type"] == "done":
                    break
                    
        except ConnectionClosed:
            print("Connection lost, attempting to reconnect...")
            if await self.connect():
                # Resume streaming with context
                await self.stream_chat(f"Please continue from: {message}")
```

### Scenario 6: Agent Tool Execution Timeouts

**Symptoms:**
- Tools never complete execution
- Agent appears "stuck" or unresponsive
- Timeout errors in logs

**Diagnostic Script**:
```python
async def diagnose_agent_health(client, agent_id):
    """Comprehensive agent health check"""
    
    # 1. Check agent status
    agent = client.agents.get(agent_id=agent_id)
    print(f"Agent status: {agent.status}")
    
    # 2. List active tools
    tools = client.agents.tools.list(agent_id=agent_id)
    print(f"Available tools: {[t.name for t in tools]}")
    
    # 3. Check for stuck operations
    active_runs = client.runs.list_active()
    stuck_runs = [r for r in active_runs if r.agent_id == agent_id]
    if stuck_runs:
        print(f"Warning: {len(stuck_runs)} stuck operations")
        for run in stuck_runs:
            print(f"  Run {run.id}: {run.status} (started {run.created_at})")
    
    # 4. Test basic responsiveness
    try:
        test_response = await asyncio.wait_for(
            client.agents.messages.create(
                agent_id=agent_id,
                messages=[{"role": "user", "content": "Health check - please respond"}]
            ),
            timeout=30.0
        )
        print("Agent is responsive")
    except asyncio.TimeoutError:
        print("Agent is unresponsive - may need restart")
        
        # Force restart agent (if supported)
        client.agents.restart(agent_id=agent_id)

# Usage
await diagnose_agent_health(client, "agent-123")
```

### Scenario 7: Context Window Exceeded

**Symptoms:**
- "Context length exceeded" errors
- Agent responses become truncated
- Memory operations fail

**Context Management Solution**:
```python
class ContextManager:
    def __init__(self, client, agent_id, max_context=100000):
        self.client = client
        self.agent_id = agent_id
        self.max_context = max_context
    
    async def estimate_context_usage(self):
        """Estimate current context usage"""
        # Get conversation history
        history = self.client.agents.messages.list(
            agent_id=self.agent_id,
            limit=100
        )
        
        # Rough token estimation (4 chars ≈ 1 token)
        total_chars = sum(len(msg.content) for msg in history.messages)
        estimated_tokens = total_chars // 4
        
        return estimated_tokens
    
    async def manage_context(self, new_message):
        """Send message with context management"""
        current_usage = await self.estimate_context_usage()
        
        if current_usage > self.max_context * 0.8:  # 80% threshold
            print("Context approaching limit, summarizing...")
            
            # Get older messages for summarization
            old_messages = self.client.agents.messages.list(
                agent_id=self.agent_id,
                limit=50,
                before=history.messages[-20].id  # Skip recent 20 messages
            )
            
            # Create summary
            summary_content = "Previous conversation summary: " + \
                await self._summarize_messages(old_messages.messages)
            
            # Store summary in archival memory
            self.client.agents.memory.archival_insert(
                agent_id=self.agent_id,
                content=summary_content
            )
            
            # Remove old messages (if API supports)
            for msg in old_messages.messages:
                try:
                    self.client.agents.messages.delete(
                        agent_id=self.agent_id,
                        message_id=msg.id
                    )
                except Exception as e:
                    print(f"Could not delete message {msg.id}: {e}")
        
        # Send new message
        return self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": new_message}]
        )
    
    async def _summarize_messages(self, messages):
        """Create summary of message list"""
        # Use another agent or LLM to create summary
        summary_agent = "agent-summarizer"
        content = "\n".join(f"{msg.role}: {msg.content}" for msg in messages)
        
        summary_response = self.client.agents.messages.create(
            agent_id=summary_agent,
            messages=[{
                "role": "user",
                "content": f"Summarize this conversation concisely:\n{content}"
            }]
        )
        
        return summary_response.messages[-1].content
```

**Source**: [Real-world MCP deployment experiences](https://superagi.com/how-to-troubleshoot-common-mcp-server-issues-a-step-by-step-guide-for-beginners-2/)

---

## Advanced Debugging Techniques

### Using Network Proxy for Deep Inspection

```bash
# Install mitmproxy
pip install mitmproxy

# Start proxy
mitmproxy --port 8080

# Configure MCP server to use proxy
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080

# Run MCP server with proxy
python -m letta_mcp_server
```

### Custom Logging for Production Debugging

```python
import logging
import json
from datetime import datetime

class MCPDebugLogger:
    def __init__(self, log_file="mcp_debug.log"):
        self.logger = logging.getLogger("mcp_debug")
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
    
    def log_request(self, method, params, request_id):
        self.logger.info(f"REQ {request_id}: {method} - {json.dumps(params)}")
    
    def log_response(self, response, request_id, duration_ms):
        self.logger.info(f"RES {request_id}: {duration_ms}ms - {json.dumps(response)}")
    
    def log_error(self, error, request_id):
        self.logger.error(f"ERR {request_id}: {error}")

# Usage in MCP server
debug_logger = MCPDebugLogger()

async def handle_mcp_request(request):
    start_time = datetime.now()
    request_id = request.get("id", "unknown")
    
    try:
        debug_logger.log_request(
            request["method"], 
            request.get("params", {}),
            request_id
        )
        
        # Process request
        response = await process_request(request)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        debug_logger.log_response(response, request_id, duration)
        
        return response
        
    except Exception as e:
        debug_logger.log_error(str(e), request_id)
        raise
```

**Source**: [MCP Debugging and monitoring best practices](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices)

---

## Additional Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/) - Complete protocol specification
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Python implementation
- [MCP Transport Concepts](https://modelcontextprotocol.info/docs/concepts/transports/) - Transport layer details
- [Letta API Documentation](https://docs.letta.com/) - Letta.ai API reference
- [MCP Troubleshooting Community](https://superagi.com/how-to-troubleshoot-common-mcp-server-issues-a-step-by-step-guide-for-beginners-2/) - Community troubleshooting guides
- [Performance Optimization Guide](https://markaicode.com/fix-slow-model-context-protocol-queries-guide/) - MCP performance tuning

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs** using the techniques described above
2. **Search existing issues** in the repository
3. **Create a detailed issue report** including:
   - Error messages and logs
   - Configuration details
   - Steps to reproduce
   - Environment information

For urgent issues, consider:
- Testing with simplified configurations
- Using alternative transport methods
- Implementing graceful degradation strategies

Remember: Clear, context-rich logging is your best tool for diagnosing MCP issues efficiently.