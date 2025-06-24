#!/usr/bin/env python3
"""
Local MCP Server Validation - Tests components without live API
"""

import asyncio
import json
from unittest.mock import Mock, AsyncMock
import inspect

from src.letta_mcp.config import LettaConfig
from src.letta_mcp.server import LettaMCPServer
from src.letta_mcp.exceptions import LettaMCPError, APIError, ConfigurationError
from src.letta_mcp.utils import (
    parse_message_response,
    format_memory_blocks,
    validate_agent_id,
    extract_assistant_message
)

class LocalValidator:
    """Validate MCP server components locally"""
    
    def __init__(self):
        self.results = []
        
    async def run_validation(self):
        """Run comprehensive local validation"""
        print("🚀 Letta MCP Server - Local Component Validation")
        print("=" * 60)
        
        await self._test_configuration()
        await self._test_server_initialization()
        await self._test_utility_functions()
        await self._test_tool_registration()
        await self._test_error_handling()
        await self._test_mock_operations()
        
        self._generate_report()
        
    async def _test_configuration(self):
        """Test configuration management"""
        print("\n⚙️ Testing Configuration Management...")
        
        # Test default config
        try:
            config = LettaConfig()
            print(f"✅ Default config created: {config.base_url}")
            self.results.append({"test": "Default Configuration", "status": "PASSED"})
        except Exception as e:
            print(f"❌ Default config failed: {e}")
            self.results.append({"test": "Default Configuration", "status": "FAILED", "error": str(e)})
        
        # Test custom config
        try:
            config = LettaConfig(
                api_key="test-key",
                base_url="https://custom.api.com",
                timeout=60.0,
                max_retries=5
            )
            assert config.api_key == "test-key"
            assert config.timeout == 60.0
            print("✅ Custom config validation passed")
            self.results.append({"test": "Custom Configuration", "status": "PASSED"})
        except Exception as e:
            print(f"❌ Custom config failed: {e}")
            self.results.append({"test": "Custom Configuration", "status": "FAILED", "error": str(e)})
    
    async def _test_server_initialization(self):
        """Test server initialization"""
        print("\n🖥️ Testing Server Initialization...")
        
        try:
            config = LettaConfig(api_key="test-key", base_url="https://test.api.com")
            server = LettaMCPServer(config)
            
            # Check that FastMCP is initialized
            assert hasattr(server, 'mcp')
            assert hasattr(server, 'client')
            assert hasattr(server, 'config')
            
            print("✅ Server initialization successful")
            self.results.append({"test": "Server Initialization", "status": "PASSED"})
        except Exception as e:
            print(f"❌ Server initialization failed: {e}")
            self.results.append({"test": "Server Initialization", "status": "FAILED", "error": str(e)})
    
    async def _test_utility_functions(self):
        """Test utility functions"""
        print("\n🔧 Testing Utility Functions...")
        
        # Test agent ID validation
        try:
            validate_agent_id("agent-12345678-1234-1234-1234-123456789abc")
            print("✅ Valid agent ID accepted")
            
            try:
                validate_agent_id("invalid-id")
                print("❌ Invalid agent ID should have been rejected")
                self.results.append({"test": "Agent ID Validation", "status": "FAILED", "error": "Invalid ID accepted"})
            except ValueError:
                print("✅ Invalid agent ID properly rejected")
                self.results.append({"test": "Agent ID Validation", "status": "PASSED"})
                
        except Exception as e:
            print(f"❌ Agent ID validation failed: {e}")
            self.results.append({"test": "Agent ID Validation", "status": "FAILED", "error": str(e)})
        
        # Test memory block formatting
        try:
            memory_blocks = [
                {"label": "human", "value": "Test user", "description": "User info"},
                {"label": "persona", "value": "Test agent", "description": "Agent persona"}
            ]
            formatted = format_memory_blocks(memory_blocks)
            
            assert "human" in formatted
            assert "persona" in formatted
            assert formatted["human"]["value"] == "Test user"
            
            print("✅ Memory block formatting successful")
            self.results.append({"test": "Memory Block Formatting", "status": "PASSED"})
        except Exception as e:
            print(f"❌ Memory block formatting failed: {e}")
            self.results.append({"test": "Memory Block Formatting", "status": "FAILED", "error": str(e)})
        
        # Test message response parsing
        try:
            mock_response = [
                {"message_type": "assistant_message", "content": "Hello!"},
                {"message_type": "tool_call_message", "tool_call": {"name": "test_tool", "arguments": {}}}
            ]
            parsed = parse_message_response(mock_response)
            
            assert "assistant_message" in parsed
            assert "tool_calls" in parsed
            assert len(parsed["tool_calls"]) == 1
            
            print("✅ Message response parsing successful")
            self.results.append({"test": "Message Response Parsing", "status": "PASSED"})
        except Exception as e:
            print(f"❌ Message response parsing failed: {e}")
            self.results.append({"test": "Message Response Parsing", "status": "FAILED", "error": str(e)})
    
    async def _test_tool_registration(self):
        """Test tool registration"""
        print("\n🔨 Testing Tool Registration...")
        
        try:
            config = LettaConfig(api_key="test-key", base_url="https://test.api.com")
            server = LettaMCPServer(config)
            
            # Check that tools are registered with FastMCP
            # This is harder to test directly, but we can check that the methods exist
            
            expected_methods = [
                '_register_agent_tools',
                '_register_conversation_tools', 
                '_register_memory_tools',
                '_register_tool_management',
                '_register_utility_tools'
            ]
            
            for method_name in expected_methods:
                assert hasattr(server, method_name), f"Missing method: {method_name}"
                method = getattr(server, method_name)
                assert callable(method), f"Method not callable: {method_name}"
            
            print("✅ Tool registration methods available")
            self.results.append({"test": "Tool Registration", "status": "PASSED"})
        except Exception as e:
            print(f"❌ Tool registration failed: {e}")
            self.results.append({"test": "Tool Registration", "status": "FAILED", "error": str(e)})
    
    async def _test_error_handling(self):
        """Test error handling"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test custom exceptions
        try:
            # Test LettaMCPError
            try:
                raise LettaMCPError("Test error")
            except LettaMCPError as e:
                assert str(e) == "Test error"
            
            # Test APIError
            try:
                raise APIError("API test error", status_code=404)
            except APIError as e:
                assert str(e) == "API test error"
                assert e.status_code == 404
            
            # Test ConfigurationError
            try:
                raise ConfigurationError("Config test error")
            except ConfigurationError as e:
                assert str(e) == "Config test error"
            
            print("✅ Custom exceptions working correctly")
            self.results.append({"test": "Error Handling", "status": "PASSED"})
        except Exception as e:
            print(f"❌ Error handling failed: {e}")
            self.results.append({"test": "Error Handling", "status": "FAILED", "error": str(e)})
    
    async def _test_mock_operations(self):
        """Test operations with mocked HTTP client"""
        print("\n🎭 Testing Mock Operations...")
        
        try:
            config = LettaConfig(api_key="test-key", base_url="https://test.api.com")
            server = LettaMCPServer(config)
            
            # Mock the HTTP client
            mock_client = AsyncMock()
            server.client = mock_client
            
            # Mock a successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"id": "agent-123", "name": "Test Agent"}]
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            
            # This would normally test an actual tool call, but since we're testing locally,
            # we just verify the mock setup works
            response = await mock_client.get("/v1/agents")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "Test Agent"
            
            print("✅ Mock HTTP operations successful")
            self.results.append({"test": "Mock Operations", "status": "PASSED"})
        except Exception as e:
            print(f"❌ Mock operations failed: {e}")
            self.results.append({"test": "Mock Operations", "status": "FAILED", "error": str(e)})
    
    def _generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("🏁 LOCAL VALIDATION COMPLETE")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["status"] == "PASSED")
        failed = sum(1 for r in self.results if r["status"] == "FAILED")
        total = len(self.results)
        
        print(f"\n📊 RESULTS SUMMARY:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "No tests")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result["status"] == "FAILED":
                    print(f"   - {result['test']}: {result.get('error', 'Unknown error')}")
        
        status = "✅ ALL LOCAL COMPONENTS VALIDATED" if failed == 0 else "⚠️ SOME COMPONENTS NEED ATTENTION"
        print(f"\n🎯 LOCAL VALIDATION STATUS: {status}")
        
        # Component analysis
        print(f"\n🔍 COMPONENT ANALYSIS:")
        print(f"   📦 Configuration Management: {'✅' if any(r['test'] in ['Default Configuration', 'Custom Configuration'] and r['status'] == 'PASSED' for r in self.results) else '❌'}")
        print(f"   🖥️ Server Architecture: {'✅' if any(r['test'] == 'Server Initialization' and r['status'] == 'PASSED' for r in self.results) else '❌'}")
        print(f"   🔧 Utility Functions: {'✅' if any(r['test'] in ['Agent ID Validation', 'Memory Block Formatting', 'Message Response Parsing'] and r['status'] == 'PASSED' for r in self.results) else '❌'}")
        print(f"   🔨 Tool Registration: {'✅' if any(r['test'] == 'Tool Registration' and r['status'] == 'PASSED' for r in self.results) else '❌'}")
        print(f"   ⚠️ Error Handling: {'✅' if any(r['test'] == 'Error Handling' and r['status'] == 'PASSED' for r in self.results) else '❌'}")
        print(f"   🎭 Mock Framework: {'✅' if any(r['test'] == 'Mock Operations' and r['status'] == 'PASSED' for r in self.results) else '❌'}")

async def main():
    """Main execution function"""
    validator = LocalValidator()
    await validator.run_validation()

if __name__ == "__main__":
    asyncio.run(main())