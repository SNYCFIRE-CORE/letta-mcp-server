#!/usr/bin/env python3
"""
Multi-Client MCP Setup Example

This example demonstrates how to configure the Letta MCP Server for use across
multiple AI clients including Claude Desktop, GitHub Copilot, Cursor, and others.

The beauty of MCP is that you configure the server once and it works with
any compatible client.
"""

import json
import os
from pathlib import Path

def generate_mcp_config():
    """Generate universal MCP server configuration"""
    return {
        "mcpServers": {
            "letta": {
                "command": "letta-mcp",
                "args": ["run"],
                "env": {
                    "LETTA_API_KEY": "${LETTA_API_KEY}",
                    "LETTA_BASE_URL": "https://api.letta.com",
                    "LETTA_TIMEOUT": "60",
                    "LETTA_MAX_RETRIES": "3"
                }
            }
        }
    }

def setup_claude_desktop():
    """Setup for Claude Desktop"""
    print("🖥️ Setting up Claude Desktop...")
    
    # Claude Desktop config location (cross-platform)
    if os.name == 'nt':  # Windows
        config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
    else:  # macOS/Linux
        config_dir = Path.home() / ".config" / "claude"
    
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "claude_desktop_config.json"
    
    config = generate_mcp_config()
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Claude Desktop config written to: {config_file}")
    print("   Restart Claude Desktop to apply changes")

def setup_vs_code_copilot():
    """Setup instructions for GitHub Copilot in VS Code"""
    print("\n🚀 Setting up GitHub Copilot (VS Code)...")
    print("1. Enable MCP support in VS Code:")
    print('   - Open settings (Ctrl/Cmd + ,)')
    print('   - Search for "chat.mcp.enabled"')
    print('   - Check the box to enable')
    print()
    print("2. Create .vscode/settings.json in your project:")
    
    vscode_config = {
        "chat.mcp.enabled": True,
        "chat.mcp.servers": generate_mcp_config()["mcpServers"]
    }
    
    print(json.dumps(vscode_config, indent=2))
    print("\n✅ GitHub Copilot will now have access to Letta agents")

def setup_cursor():
    """Setup instructions for Cursor"""
    print("\n⚡ Setting up Cursor...")
    print("1. Open Cursor settings")
    print("2. Navigate to Extensions > MCP Servers")
    print("3. Add server configuration:")
    
    cursor_config = {
        "name": "letta",
        "command": "letta-mcp",
        "args": ["run"],
        "env": {
            "LETTA_API_KEY": "${LETTA_API_KEY}"
        }
    }
    
    print(json.dumps(cursor_config, indent=2))
    print("\n✅ Cursor can now access Letta agents via CMD+K and chat")

def setup_replit():
    """Setup instructions for Replit"""
    print("\n🔄 Setting up Replit...")
    print("1. Create .replit file in your project root:")
    
    replit_config = """
[mcp]
servers = { letta = { command = "letta-mcp", args = ["run"] } }

[env]
LETTA_API_KEY = "${LETTA_API_KEY}"
"""
    
    print(replit_config)
    print("2. Install the MCP server in your Repl:")
    print("   pip install letta-mcp-server")
    print("\n✅ Replit workspace now has Letta agent access")

def setup_sourcegraph_cody():
    """Setup instructions for Sourcegraph Cody"""
    print("\n🔍 Setting up Sourcegraph Cody...")
    print("1. Configure OpenCtx in your VS Code settings:")
    
    cody_config = {
        "openctx.providers": {
            "https://openctx.org/providers/mcp": {
                "servers": generate_mcp_config()["mcpServers"]
            }
        }
    }
    
    print(json.dumps(cody_config, indent=2))
    print("\n✅ Sourcegraph Cody can now access Letta agents via OpenCtx")

def verify_setup():
    """Verify the setup works"""
    print("\n🔍 Verification Steps:")
    print("1. Ensure your LETTA_API_KEY environment variable is set")
    print("2. Test the server directly:")
    print("   letta-mcp run --test")
    print()
    print("3. In each client, try:")
    print("   - List agents: letta_list_agents")
    print("   - Send message: letta_send_message")
    print()
    print("4. Common issues:")
    print("   - API key not set: export LETTA_API_KEY=sk-let-your-key")
    print("   - Client restart needed after configuration")
    print("   - MCP support may need manual enabling")

def main():
    """Run multi-client setup"""
    print("🌐 Letta MCP Server - Multi-Client Setup")
    print("=" * 50)
    print("This script helps you configure Letta MCP Server for use across")
    print("multiple AI clients. The server works universally with any MCP client!")
    print()
    
    # Check if API key is available
    if not os.getenv('LETTA_API_KEY'):
        print("⚠️  Warning: LETTA_API_KEY environment variable not set")
        print("   Set it with: export LETTA_API_KEY=sk-let-your-key")
        print()
    
    # Setup each client
    setup_claude_desktop()
    setup_vs_code_copilot()
    setup_cursor()
    setup_replit()
    setup_sourcegraph_cody()
    
    verify_setup()
    
    print("\n🎉 Multi-client setup complete!")
    print("You can now use Letta agents from any of these AI clients:")
    print("• Claude Desktop")
    print("• GitHub Copilot (VS Code)")
    print("• Cursor")
    print("• Replit")
    print("• Sourcegraph Cody")
    print("• Any other MCP-compatible client")

if __name__ == "__main__":
    main()