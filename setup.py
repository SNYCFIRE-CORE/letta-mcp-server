"""
Setup configuration for Letta MCP Server
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version
version_file = this_directory / "src" / "letta_mcp" / "__init__.py"
version_line = [line for line in version_file.read_text().split("\n") if line.startswith("__version__")][0]
version = version_line.split('"')[1]

setup(
    name="letta-mcp-server",
    version=version,
    author="SNYCFIRE-CORE",
    author_email="support@letta-mcp.dev",
    description="Bridge Claude and Letta.ai agents with one line of code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SNYCFIRE-CORE/letta-mcp-server",
    project_urls={
        "Bug Tracker": "https://github.com/SNYCFIRE-CORE/letta-mcp-server/issues",
        "Documentation": "https://github.com/SNYCFIRE-CORE/letta-mcp-server/docs",
        "Source Code": "https://github.com/SNYCFIRE-CORE/letta-mcp-server",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "fastmcp>=0.2.0",
        "httpx>=0.27.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "tenacity>=8.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings[python]>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "letta-mcp=letta_mcp.cli:main",
            "letta-mcp-server=letta_mcp.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    keywords=[
        "letta",
        "mcp",
        "claude",
        "ai",
        "agents",
        "llm",
        "model-context-protocol",
        "fastmcp",
        "memgpt",
    ],
)