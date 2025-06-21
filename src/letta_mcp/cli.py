#!/usr/bin/env python3
"""
CLI for Letta MCP Server
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from .config import create_default_config, load_config
from .server import run_server
from .__init__ import __version__

def add_to_claude_config(config_path: Path) -> bool:
    """Add Letta MCP server to Claude configuration"""
    try:
        # Read existing config
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Ensure mcpServers exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Add Letta configuration
        config["mcpServers"]["letta"] = {
            "command": sys.executable,
            "args": ["-m", "letta_mcp.server"],
            "env": {
                "LETTA_API_KEY": os.getenv("LETTA_API_KEY", "YOUR_API_KEY_HERE")
            }
        }
        
        # Write updated config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Error updating Claude config: {e}")
        return False

def find_claude_config() -> Optional[Path]:
    """Find Claude configuration file"""
    # Common locations
    locations = [
        # Windows
        Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
        # macOS
        Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        # Linux
        Path.home() / ".config" / "Claude" / "claude_desktop_config.json",
        # Claude Code (all platforms)
        Path.home() / ".claude" / "mcp_config.json",
    ]
    
    for path in locations:
        if path.exists():
            return path
    
    return None

def cmd_configure(args):
    """Configure Letta MCP Server"""
    print(f"🔧 Configuring Letta MCP Server v{__version__}")
    print()
    
    # Create default config
    config_path = Path.home() / ".letta-mcp" / "config.yaml"
    print(f"Creating configuration at: {config_path}")
    create_default_config(config_path)
    print("✅ Configuration file created")
    
    # Find and update Claude config
    claude_config = find_claude_config()
    if claude_config:
        print(f"\n📍 Found Claude config at: {claude_config}")
        if add_to_claude_config(claude_config):
            print("✅ Added Letta MCP server to Claude configuration")
            print("\n⚠️  Important: Set your LETTA_API_KEY environment variable:")
            print("  export LETTA_API_KEY=sk-let-...")
            print("\nThen restart Claude to use the Letta MCP server!")
        else:
            print("❌ Failed to update Claude configuration")
    else:
        print("\n⚠️  Could not find Claude configuration file")
        print("Please add the following to your Claude config manually:")
        print("""
{
  "mcpServers": {
    "letta": {
      "command": "python",
      "args": ["-m", "letta_mcp.server"],
      "env": {
        "LETTA_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
""")

def cmd_run(args):
    """Run the Letta MCP Server"""
    print(f"🚀 Starting Letta MCP Server v{__version__}")
    
    try:
        config = load_config()
        run_server(config, transport=args.transport)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def cmd_test(args):
    """Test connection to Letta API"""
    import asyncio
    from .server import create_server
    
    print(f"🧪 Testing Letta MCP Server v{__version__}")
    
    async def test():
        try:
            config = load_config()
            server = create_server(config)
            
            print(f"📍 Base URL: {config.base_url}")
            print(f"🔑 API Key: {'Set' if config.api_key else 'Not set'}")
            
            # Test health check
            health_check = server.mcp._tools["letta_health_check"]["handler"]
            result = await health_check()
            
            if result["success"]:
                print("\n✅ Connection successful!")
                print(f"   Status: {result['status']}")
                print(f"   API Version: {result.get('api_version', 'Unknown')}")
            else:
                print(f"\n❌ Connection failed: {result['error']}")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
    
    asyncio.run(test())

def cmd_tools(args):
    """List available MCP tools"""
    print(f"🛠️  Letta MCP Server Tools v{__version__}")
    print("\nAvailable tools:")
    
    tools = [
        ("Agent Management", [
            ("letta_list_agents", "List all available agents"),
            ("letta_create_agent", "Create a new agent"),
            ("letta_get_agent", "Get agent details"),
            ("letta_update_agent", "Update agent configuration"),
            ("letta_delete_agent", "Delete an agent"),
        ]),
        ("Conversations", [
            ("letta_send_message", "Send a message to an agent"),
            ("letta_get_conversation_history", "Get conversation history"),
            ("letta_export_conversation", "Export conversation"),
        ]),
        ("Memory Management", [
            ("letta_get_memory", "View agent memory blocks"),
            ("letta_update_memory", "Update memory block"),
            ("letta_create_memory_block", "Create custom memory block"),
            ("letta_search_memory", "Search conversation memory"),
        ]),
        ("Tools & Workflows", [
            ("letta_list_tools", "List available tools"),
            ("letta_get_agent_tools", "Get agent's tools"),
            ("letta_attach_tool", "Attach tool to agent"),
            ("letta_detach_tool", "Detach tool from agent"),
        ]),
        ("Utilities", [
            ("letta_health_check", "Check API connection"),
            ("letta_get_usage_stats", "Get usage statistics"),
        ]),
    ]
    
    for category, category_tools in tools:
        print(f"\n{category}:")
        for name, description in category_tools:
            print(f"  • {name}")
            print(f"    {description}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="letta-mcp",
        description="Letta MCP Server - Bridge Claude and Letta.ai agents"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Configure command
    configure_parser = subparsers.add_parser(
        "configure",
        help="Configure Letta MCP Server and add to Claude"
    )
    configure_parser.set_defaults(func=cmd_configure)
    
    # Run command
    run_parser = subparsers.add_parser(
        "run",
        help="Run the MCP server"
    )
    run_parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    run_parser.set_defaults(func=cmd_run)
    
    # Test command
    test_parser = subparsers.add_parser(
        "test",
        help="Test connection to Letta API"
    )
    test_parser.set_defaults(func=cmd_test)
    
    # Tools command
    tools_parser = subparsers.add_parser(
        "tools",
        help="List available MCP tools"
    )
    tools_parser.set_defaults(func=cmd_tools)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()