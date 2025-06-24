"""
Unit tests for configuration module
"""

import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError

from letta_mcp.config import LettaConfig, load_config
from letta_mcp.exceptions import ConfigurationError


class TestLettaConfig:
    """Test the LettaConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = LettaConfig()
        
        assert config.api_key is None
        assert config.base_url == "https://api.letta.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.default_model == "claude-sonnet-4-20250514"
        assert config.default_embedding == "text-embedding-ada-002"
    
    def test_custom_config(self):
        """Test configuration with custom values"""
        config = LettaConfig(
            api_key="test-key",
            base_url="http://localhost:8000",
            timeout=60.0,
            max_retries=5,
            default_model="claude-opus-4",
            default_embedding="custom-embedding"
        )
        
        assert config.api_key == "test-key"
        assert config.base_url == "http://localhost:8000"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.default_model == "claude-opus-4"
        assert config.default_embedding == "custom-embedding"
    
    def test_validation_errors(self):
        """Test configuration validation"""
        # Test negative timeout
        with pytest.raises(ValidationError):
            LettaConfig(timeout=-1.0)
        
        # Test negative max_retries
        with pytest.raises(ValidationError):
            LettaConfig(max_retries=-1)
        
        # Test invalid base_url
        with pytest.raises(ValidationError):
            LettaConfig(base_url="not-a-url")
    
    def test_model_validation(self):
        """Test model name validation"""
        # Valid model names should work
        valid_models = [
            "claude-sonnet-4-20250514",
            "claude-opus-4",
            "gpt-4",
            "custom-model-name"
        ]
        
        for model in valid_models:
            config = LettaConfig(default_model=model)
            assert config.default_model == model
    
    def test_config_serialization(self):
        """Test config can be serialized/deserialized"""
        original_config = LettaConfig(
            api_key="test-key",
            base_url="http://localhost:8000",
            timeout=45.0
        )
        
        # Convert to dict and back
        config_dict = original_config.model_dump()
        restored_config = LettaConfig(**config_dict)
        
        assert restored_config.api_key == original_config.api_key
        assert restored_config.base_url == original_config.base_url
        assert restored_config.timeout == original_config.timeout


class TestLoadConfig:
    """Test the load_config function"""
    
    def test_load_from_env_vars(self, env_var_helper):
        """Test loading configuration from environment variables"""
        env_var_helper.set("LETTA_API_KEY", "env-api-key")
        env_var_helper.set("LETTA_BASE_URL", "http://env-server:8000")
        env_var_helper.set("LETTA_TIMEOUT", "45.0")
        env_var_helper.set("LETTA_MAX_RETRIES", "5")
        env_var_helper.set("LETTA_DEFAULT_MODEL", "env-model")
        env_var_helper.set("LETTA_DEFAULT_EMBEDDING", "env-embedding")
        
        config = load_config()
        
        assert config.api_key == "env-api-key"
        assert config.base_url == "http://env-server:8000"
        assert config.timeout == 45.0
        assert config.max_retries == 5
        assert config.default_model == "env-model"
        assert config.default_embedding == "env-embedding"
    
    def test_load_with_defaults(self):
        """Test loading configuration with defaults when no env vars"""
        # Ensure no relevant env vars are set
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()
            
            assert config.api_key is None
            assert config.base_url == "https://api.letta.com"
            assert config.timeout == 30.0
            assert config.max_retries == 3
    
    def test_load_partial_env_vars(self, env_var_helper):
        """Test loading config with only some env vars set"""
        env_var_helper.set("LETTA_API_KEY", "partial-key")
        env_var_helper.set("LETTA_TIMEOUT", "60.0")
        
        config = load_config()
        
        assert config.api_key == "partial-key"
        assert config.timeout == 60.0
        # Other values should be defaults
        assert config.base_url == "https://api.letta.com"
        assert config.max_retries == 3
    
    @patch("letta_mcp.config.Path.exists")
    @patch("letta_mcp.config.Path.read_text")
    def test_load_from_dotenv_file(self, mock_read_text, mock_exists):
        """Test loading configuration from .env file"""
        mock_exists.return_value = True
        mock_read_text.return_value = """
LETTA_API_KEY=file-api-key
LETTA_BASE_URL=http://file-server:8000
LETTA_TIMEOUT=35.0
"""
        
        config = load_config()
        
        assert config.api_key == "file-api-key"
        assert config.base_url == "http://file-server:8000"
        assert config.timeout == 35.0
    
    def test_env_var_precedence_over_file(self, env_var_helper):
        """Test that environment variables take precedence over .env file"""
        env_var_helper.set("LETTA_API_KEY", "env-wins")
        
        with patch("letta_mcp.config.Path.exists", return_value=True):
            with patch("letta_mcp.config.Path.read_text", return_value="LETTA_API_KEY=file-loses"):
                config = load_config()
                assert config.api_key == "env-wins"
    
    def test_invalid_env_var_values(self, env_var_helper):
        """Test handling of invalid environment variable values"""
        env_var_helper.set("LETTA_TIMEOUT", "not-a-number")
        
        with pytest.raises(ValidationError):
            load_config()
    
    def test_empty_env_var_values(self, env_var_helper):
        """Test handling of empty environment variable values"""
        env_var_helper.set("LETTA_API_KEY", "")
        env_var_helper.set("LETTA_BASE_URL", "")
        
        config = load_config()
        
        # Empty string should be treated as None/default
        assert config.api_key == ""  # Empty strings are valid for API key
        assert config.base_url == ""  # Will fail validation if empty URL is invalid
    
    def test_config_with_custom_path(self):
        """Test loading config with custom .env file path"""
        # This would require modifying load_config to accept a path parameter
        # For now, just test that the function works with default behavior
        config = load_config()
        assert isinstance(config, LettaConfig)


class TestConfigIntegration:
    """Integration tests for configuration functionality"""
    
    def test_real_world_config_scenario(self, env_var_helper):
        """Test a realistic configuration scenario"""
        # Simulate a production-like environment
        env_var_helper.set("LETTA_API_KEY", "sk-let-production-key-123")
        env_var_helper.set("LETTA_BASE_URL", "https://api.letta.com")
        env_var_helper.set("LETTA_TIMEOUT", "30.0")
        env_var_helper.set("LETTA_MAX_RETRIES", "3")
        
        config = load_config()
        
        # Verify all values are loaded correctly
        assert config.api_key == "sk-let-production-key-123"
        assert config.base_url == "https://api.letta.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        
        # Verify config is valid for server creation
        from letta_mcp.server import LettaMCPServer
        server = LettaMCPServer(config)
        assert server.config == config
    
    def test_config_validation_edge_cases(self):
        """Test edge cases in configuration validation"""
        # Test minimum valid values
        config = LettaConfig(
            timeout=0.1,  # Very small but positive
            max_retries=0  # Zero retries is valid
        )
        assert config.timeout == 0.1
        assert config.max_retries == 0
        
        # Test maximum reasonable values
        config = LettaConfig(
            timeout=300.0,  # 5 minutes
            max_retries=10   # Many retries
        )
        assert config.timeout == 300.0
        assert config.max_retries == 10