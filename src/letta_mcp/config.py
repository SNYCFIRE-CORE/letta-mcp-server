"""
Configuration management for Letta MCP Server
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from .exceptions import ConfigurationError

@dataclass
class LettaConfig:
    """Configuration for Letta MCP Server"""
    
    # API Configuration
    api_key: Optional[str] = None
    base_url: str = "https://api.letta.com"
    
    # Default Models
    default_model: str = "openai/gpt-4o-mini"
    default_embedding: str = "openai/text-embedding-3-small"
    
    # Performance Settings
    timeout: int = 60
    max_retries: int = 3
    connection_pool_size: int = 10
    
    # Feature Flags
    enable_streaming: bool = True
    enable_auto_retry: bool = True
    enable_request_logging: bool = False
    enable_performance_metrics: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "LettaConfig":
        """Create config from environment variables"""
        return cls(
            api_key=os.getenv("LETTA_API_KEY"),
            base_url=os.getenv("LETTA_BASE_URL", "https://api.letta.com"),
            default_model=os.getenv("LETTA_DEFAULT_MODEL", "openai/gpt-4o-mini"),
            default_embedding=os.getenv("LETTA_DEFAULT_EMBEDDING", "openai/text-embedding-3-small"),
            timeout=int(os.getenv("LETTA_TIMEOUT", "60")),
            max_retries=int(os.getenv("LETTA_MAX_RETRIES", "3")),
            connection_pool_size=int(os.getenv("LETTA_POOL_SIZE", "10")),
            enable_streaming=os.getenv("LETTA_ENABLE_STREAMING", "true").lower() == "true",
            enable_auto_retry=os.getenv("LETTA_ENABLE_AUTO_RETRY", "true").lower() == "true",
            enable_request_logging=os.getenv("LETTA_ENABLE_REQUEST_LOGGING", "false").lower() == "true",
            enable_performance_metrics=os.getenv("LETTA_ENABLE_METRICS", "true").lower() == "true",
            log_level=os.getenv("LETTA_LOG_LEVEL", "INFO"),
            log_file=os.getenv("LETTA_LOG_FILE")
        )
    
    @classmethod
    def from_yaml(cls, path: Path) -> "LettaConfig":
        """Load config from YAML file"""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Handle nested structure
            letta_config = data.get('letta', {})
            defaults = data.get('defaults', {})
            performance = data.get('performance', {})
            features = data.get('features', {})
            logging = data.get('logging', {})
            
            # Expand environment variables
            api_key = letta_config.get('api_key', '')
            if api_key.startswith('${') and api_key.endswith('}'):
                var_name = api_key[2:-1]
                api_key = os.getenv(var_name)
            
            return cls(
                api_key=api_key or os.getenv("LETTA_API_KEY"),
                base_url=letta_config.get('base_url', cls.base_url),
                default_model=defaults.get('model', cls.default_model),
                default_embedding=defaults.get('embedding', cls.default_embedding),
                timeout=performance.get('timeout', cls.timeout),
                max_retries=performance.get('max_retries', cls.max_retries),
                connection_pool_size=performance.get('connection_pool_size', cls.connection_pool_size),
                enable_streaming=features.get('streaming', cls.enable_streaming),
                enable_auto_retry=features.get('auto_retry', cls.enable_auto_retry),
                enable_request_logging=features.get('request_logging', cls.enable_request_logging),
                enable_performance_metrics=features.get('performance_metrics', cls.enable_performance_metrics),
                log_level=logging.get('level', cls.log_level),
                log_file=logging.get('file', cls.log_file)
            )
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {path}: {e}")
    
    def validate(self):
        """Validate the configuration"""
        if self.base_url == "https://api.letta.com" and not self.api_key:
            raise ConfigurationError(
                "LETTA_API_KEY is required for Letta Cloud. "
                "Set it via environment variable or config file."
            )
        
        if self.timeout < 1:
            raise ConfigurationError("Timeout must be at least 1 second")
        
        if self.max_retries < 0:
            raise ConfigurationError("Max retries cannot be negative")
        
        if self.connection_pool_size < 1:
            raise ConfigurationError("Connection pool size must be at least 1")

def get_config_path() -> Optional[Path]:
    """Get the path to the config file"""
    # Check multiple locations
    locations = [
        Path.home() / ".letta-mcp" / "config.yaml",
        Path.home() / ".letta-mcp" / "config.yml",
        Path.cwd() / "letta-mcp.yaml",
        Path.cwd() / "letta-mcp.yml",
        Path.cwd() / ".letta-mcp.yaml",
        Path.cwd() / ".letta-mcp.yml"
    ]
    
    for path in locations:
        if path.exists():
            return path
    
    return None

def load_config() -> LettaConfig:
    """Load configuration from file or environment"""
    # Try to load from file first
    config_path = get_config_path()
    
    if config_path:
        try:
            config = LettaConfig.from_yaml(config_path)
        except Exception:
            # Fall back to environment
            config = LettaConfig.from_env()
    else:
        # Load from environment
        config = LettaConfig.from_env()
    
    # Validate
    config.validate()
    
    return config

def create_default_config(path: Optional[Path] = None) -> Path:
    """Create a default configuration file"""
    if path is None:
        path = Path.home() / ".letta-mcp" / "config.yaml"
    
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Default config content
    config_content = """# Letta MCP Server Configuration

letta:
  # API key for Letta Cloud (or use environment variable LETTA_API_KEY)
  api_key: ${LETTA_API_KEY}
  
  # Base URL for Letta API
  # For Letta Cloud: https://api.letta.com
  # For self-hosted: http://localhost:8283
  base_url: https://api.letta.com

defaults:
  # Default model for new agents
  model: openai/gpt-4o-mini
  
  # Default embedding model
  embedding: openai/text-embedding-3-small

performance:
  # Request timeout in seconds
  timeout: 60
  
  # Maximum number of retries for failed requests
  max_retries: 3
  
  # HTTP connection pool size
  connection_pool_size: 10

features:
  # Enable streaming responses
  streaming: true
  
  # Enable automatic retry on failure
  auto_retry: true
  
  # Enable request/response logging (verbose)
  request_logging: false
  
  # Enable performance metrics collection
  performance_metrics: true

logging:
  # Log level: DEBUG, INFO, WARNING, ERROR
  level: INFO
  
  # Optional log file path
  # file: ~/.letta-mcp/server.log
"""
    
    with open(path, 'w') as f:
        f.write(config_content)
    
    return path