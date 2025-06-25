#!/bin/bash
# Wrapper script to run Letta MCP Server from the correct directory

# Change to the server directory
cd /root/letta-mcp-server-enhanced

# Activate virtual environment and run server
exec .venv/bin/python -m letta_mcp.server