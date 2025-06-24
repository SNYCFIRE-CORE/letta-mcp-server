#!/usr/bin/env python3
"""
Simple Letta API Test - Direct HTTP Testing
"""

import asyncio
import httpx
import json
import time

# Configuration
API_KEY = "sk-let-MTVhMWI3YmYtNWEzMi00NDQ5LWJiMzAtNTAwZTE5NGQ4N2FjOmEwZjc1NzQwLTU2NjAtNDI0Ny04YThkLTVlM2MyZDNhYjUyNA=="
AXLE_AGENT_ID = "agent-01c2ef52-be32-401d-8d8f-edc561b39cbe"
BASE_URL = "https://api.letta.com"

async def test_letta_api():
    """Test direct API connectivity"""
    print("🚀 Testing Direct Letta API Connection")
    print(f"📡 Base URL: {BASE_URL}")
    print(f"🤖 AXLE Agent: {AXLE_AGENT_ID}")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        
        # Test 1: Health Check (List agents)
        print("\n🔍 Test 1: Health Check (List Agents)")
        try:
            response = await client.get(f"{BASE_URL}/v1/agents", params={"limit": 5})
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                agents = response.json()
                print(f"   ✅ SUCCESS: Found {len(agents)} agents")
                for agent in agents[:2]:  # Show first 2
                    print(f"      - {agent.get('name', 'Unknown')} ({agent.get('id', 'No ID')})")
            else:
                print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
        
        # Test 2: Get AXLE Agent
        print("\n🤖 Test 2: Get AXLE Agent Details")
        try:
            response = await client.get(f"{BASE_URL}/v1/agents/{AXLE_AGENT_ID}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                agent = response.json()
                print(f"   ✅ SUCCESS: AXLE Agent Details")
                print(f"      Name: {agent.get('name', 'Unknown')}")
                print(f"      Model: {agent.get('model', 'Unknown')}")
                print(f"      Tools: {len(agent.get('tools', []))}")
                print(f"      Memory Blocks: {len(agent.get('memory_blocks', []))}")
            else:
                print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
        
        # Test 3: Get AXLE Memory
        print("\n🧠 Test 3: Get AXLE Memory Blocks")
        try:
            response = await client.get(f"{BASE_URL}/v1/agents/{AXLE_AGENT_ID}/memory-blocks")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                memory_blocks = response.json()
                print(f"   ✅ SUCCESS: Found {len(memory_blocks)} memory blocks")
                for block in memory_blocks:
                    label = block.get('label', 'Unknown')
                    value_len = len(block.get('value', ''))
                    print(f"      - {label}: {value_len} characters")
            else:
                print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
        
        # Test 4: Send Message to AXLE
        print("\n💬 Test 4: Send Message to AXLE")
        try:
            start_time = time.time()
            message_data = {
                "messages": [{"role": "user", "content": "Hello AXLE! This is a quick integration test. Please respond briefly."}],
                "stream_steps": False,
                "stream_tokens": False
            }
            
            response = await client.post(f"{BASE_URL}/v1/agents/{AXLE_AGENT_ID}/messages", json=message_data)
            end_time = time.time()
            
            print(f"   Status: {response.status_code}")
            print(f"   Response Time: {end_time - start_time:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS: Message sent and received")
                
                # Extract assistant response
                assistant_response = ""
                if isinstance(result, list):
                    for msg in result:
                        if msg.get("message_type") == "assistant_message":
                            assistant_response = msg.get("content", "")
                            break
                
                if assistant_response:
                    print(f"   AXLE Response: {assistant_response[:100]}...")
                else:
                    print(f"   Raw Response: {str(result)[:200]}...")
            else:
                print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
        
        # Test 5: Get Tools
        print("\n🔧 Test 5: List Available Tools")
        try:
            response = await client.get(f"{BASE_URL}/v1/tools")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                tools = response.json()
                print(f"   ✅ SUCCESS: Found {len(tools)} tools")
                
                # Look for firecrawl tools
                firecrawl_tools = [tool for tool in tools if 'firecrawl' in tool.get('name', '').lower()]
                print(f"   Firecrawl Tools: {len(firecrawl_tools)}")
                
                # Show some tool names
                for tool in tools[:5]:
                    print(f"      - {tool.get('name', 'Unknown')}")
            else:
                print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
        
        # Test 6: Get Conversation History
        print("\n📜 Test 6: Get AXLE Conversation History")
        try:
            response = await client.get(f"{BASE_URL}/v1/agents/{AXLE_AGENT_ID}/messages", params={"limit": 5})
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                messages = response.json()
                print(f"   ✅ SUCCESS: Found {len(messages)} recent messages")
                
                # Count message types
                user_msgs = sum(1 for msg in messages if msg.get("message_type") == "user_message")
                assistant_msgs = sum(1 for msg in messages if msg.get("message_type") == "assistant_message")
                tool_msgs = sum(1 for msg in messages if msg.get("message_type") == "tool_call_message")
                
                print(f"      User Messages: {user_msgs}")
                print(f"      Assistant Messages: {assistant_msgs}")
                print(f"      Tool Messages: {tool_msgs}")
            else:
                print(f"   ❌ FAILED: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Direct API Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_letta_api())