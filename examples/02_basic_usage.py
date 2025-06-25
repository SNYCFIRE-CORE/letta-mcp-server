#!/usr/bin/env python3
"""
Basic Usage Example

This example demonstrates simple usage of the Letta MCP Server.
Shows how to configure and test basic functionality.
"""

import os

def main():
    """Basic usage demonstration"""
    print("🤖 Letta MCP Server - Basic Usage Example")
    print("=" * 50)
    print()
    
    print("1. First, ensure you have installed the server:")
    print("   pip install letta-mcp-server")
    print()
    
    print("2. Set your API key:")
    print("   export LETTA_API_KEY=sk-let-your-key-here")
    print()
    
    print("3. Configure for Claude Desktop:")
    print("   letta-mcp configure")
    print()
    
    print("4. Restart Claude Desktop and try these tools:")
    print("   • letta_list_agents - See your available agents")
    print("   • letta_send_message - Chat with an agent")
    print("   • letta_get_memory - View agent memory")
    print()
    
    # Check API key
    api_key = os.getenv('LETTA_API_KEY')
    if api_key:
        if api_key.startswith('sk-let-'):
            print("✅ API key detected and properly formatted")
        else:
            print("⚠️  API key found but doesn't match expected format")
    else:
        print("❌ No API key found - set LETTA_API_KEY environment variable")
    
    print()
    print("📚 For more information:")
    print("   • GitHub: https://github.com/SNYCFIRE-CORE/letta-mcp-server")
    print("   • PyPI: https://pypi.org/project/letta-mcp-server/")
    print("   • Letta.ai: https://letta.ai")

if __name__ == "__main__":
    main()