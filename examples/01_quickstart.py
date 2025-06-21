#!/usr/bin/env python3
"""
Letta MCP Server - Quick Start Example

This example shows how to:
1. List available agents
2. Send a message to an agent
3. View agent memory
4. Update agent memory
"""

import asyncio
import os
from letta_mcp import create_server, LettaConfig

async def main():
    # Create server with config from environment
    config = LettaConfig.from_env()
    server = create_server(config)
    
    print("🚀 Letta MCP Server - Quick Start Example")
    print(f"📍 Connected to: {config.base_url}")
    print("-" * 50)
    
    # Get the tool functions
    letta_list_agents = server.mcp._tools["letta_list_agents"]["handler"]
    letta_send_message = server.mcp._tools["letta_send_message"]["handler"]
    letta_get_memory = server.mcp._tools["letta_get_memory"]["handler"]
    letta_update_memory = server.mcp._tools["letta_update_memory"]["handler"]
    
    # 1. List agents
    print("\n1. Listing available agents...")
    agents_result = await letta_list_agents()
    
    if agents_result["success"]:
        print(f"Found {agents_result['count']} agents:")
        for agent in agents_result["agents"][:3]:  # Show first 3
            print(f"  - {agent['name']} (ID: {agent['id']})")
            print(f"    Model: {agent.get('model', 'Unknown')}")
            print(f"    Tools: {len(agent.get('tools', []))} tools")
        
        if agents_result["count"] > 3:
            print(f"  ... and {agents_result['count'] - 3} more")
    else:
        print(f"❌ Error: {agents_result['error']}")
        return
    
    # 2. Send a message to the first agent
    if agents_result["agents"]:
        agent = agents_result["agents"][0]
        agent_id = agent["id"]
        agent_name = agent["name"]
        
        print(f"\n2. Sending message to '{agent_name}'...")
        message = "Hello! Can you tell me about yourself and what you can help with?"
        
        message_result = await letta_send_message(
            agent_id=agent_id,
            message=message
        )
        
        if message_result["success"]:
            print(f"💬 You: {message}")
            print(f"🤖 {agent_name}: {message_result['response']}")
            
            if message_result["tool_calls"]:
                print("\n📋 Tool calls made:")
                for tool in message_result["tool_calls"]:
                    print(f"  - {tool['name']}")
        else:
            print(f"❌ Error: {message_result['error']}")
        
        # 3. View agent memory
        print(f"\n3. Viewing memory for '{agent_name}'...")
        memory_result = await letta_get_memory(agent_id=agent_id)
        
        if memory_result["success"]:
            print("📝 Memory blocks:")
            for label, block in memory_result["memory_blocks"].items():
                print(f"\n  [{label}]")
                print(f"  {block['value'][:100]}..." if len(block['value']) > 100 else f"  {block['value']}")
        else:
            print(f"❌ Error: {memory_result['error']}")
        
        # 4. Update memory (example: updating human block)
        print(f"\n4. Updating 'human' memory block...")
        new_human_memory = "The user is a developer exploring Letta MCP integration. They are interested in building AI agents."
        
        update_result = await letta_update_memory(
            agent_id=agent_id,
            block_label="human",
            value=new_human_memory
        )
        
        if update_result["success"]:
            print(f"✅ Successfully updated 'human' memory block")
            print(f"   New value: {new_human_memory}")
        else:
            print(f"❌ Error: {update_result['error']}")
    
    print("\n✨ Quick start complete!")
    print("\nNext steps:")
    print("- Try creating a new agent with letta_create_agent")
    print("- Explore streaming with letta_send_message(stream=True)")
    print("- Check out more examples in the examples/ directory")

if __name__ == "__main__":
    # Ensure API key is set
    if not os.getenv("LETTA_API_KEY"):
        print("❌ Error: LETTA_API_KEY environment variable not set")
        print("Please set it to your Letta API key:")
        print("  export LETTA_API_KEY=sk-let-...")
    else:
        asyncio.run(main())