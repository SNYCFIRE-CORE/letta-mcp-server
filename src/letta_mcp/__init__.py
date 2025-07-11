"""
Letta MCP Server - Bridge Claude and Letta.ai agents with one line of code.
"""

try:
    from ._version import __version__
except ImportError:
    # _version.py is generated by setuptools-scm
    __version__ = "0.0.0"

__author__ = "SNYCFIRE-CORE"
__email__ = "Zack@ascendhq.gg"

from .server import LettaMCPServer, create_server, run_server
from .config import LettaConfig, load_config
from .exceptions import LettaMCPError, ConfigurationError, APIError
from .models import AgentInfo, MemoryBlock, ToolInfo, Message

__all__ = [
    "LettaMCPServer",
    "create_server", 
    "run_server",
    "LettaConfig",
    "load_config",
    "LettaMCPError",
    "ConfigurationError", 
    "APIError",
    "AgentInfo",
    "MemoryBlock",
    "ToolInfo",
    "Message",
]