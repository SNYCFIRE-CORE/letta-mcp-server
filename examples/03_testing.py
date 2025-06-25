#!/usr/bin/env python3
"""
Testing Your Setup

This example shows how to test your Letta MCP Server installation
and verify everything is working correctly.
"""

import os
import subprocess
import sys

def check_installation():
    """Check if letta-mcp-server is installed"""
    try:
        import letta_mcp
        print("✅ letta-mcp-server package found")
        return True
    except ImportError:
        print("❌ letta-mcp-server not installed")
        print("   Run: pip install letta-mcp-server")
        return False

def check_api_key():
    """Check if API key is configured"""
    api_key = os.getenv('LETTA_API_KEY')
    if not api_key:
        print("❌ LETTA_API_KEY not set")
        print("   Run: export LETTA_API_KEY=sk-let-your-key")
        return False
    
    if not api_key.startswith('sk-let-'):
        print("⚠️  API key doesn't match expected format (sk-let-...)")
        return False
    
    print("✅ API key configured correctly")
    return True

def test_server():
    """Test the MCP server directly"""
    try:
        # Try to run the server in test mode
        result = subprocess.run(
            [sys.executable, '-m', 'letta_mcp.cli', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ MCP server responds correctly")
            return True
        else:
            print("❌ MCP server error")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  MCP server timed out (may still work)")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def suggest_next_steps():
    """Suggest next steps for the user"""
    print("\n📋 Next Steps:")
    print("1. Open Claude Desktop")
    print("2. Try these MCP tools:")
    print("   • letta_list_agents")
    print("   • letta_send_message")
    print("   • letta_get_memory")
    print()
    print("3. If tools don't appear:")
    print("   • Restart Claude Desktop")
    print("   • Check configuration with: letta-mcp configure")
    print("   • Verify API key is correct")

def main():
    """Run setup tests"""
    print("🧪 Letta MCP Server - Setup Testing")
    print("=" * 45)
    print()
    
    all_good = True
    
    print("🔍 Checking installation...")
    if not check_installation():
        all_good = False
    
    print("\n🔑 Checking API key...")
    if not check_api_key():
        all_good = False
    
    print("\n🚀 Testing server...")
    if not test_server():
        all_good = False
    
    print("\n" + "=" * 45)
    if all_good:
        print("🎉 All tests passed! Your setup looks good.")
        suggest_next_steps()
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    print("\n📚 Need help? Check the documentation:")
    print("   https://github.com/SNYCFIRE-CORE/letta-mcp-server")

if __name__ == "__main__":
    main()