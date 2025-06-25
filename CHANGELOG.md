# Changelog

## [1.0.4] - 2025-06-25

### Fixed
- Token limit optimization: Reduced response sizes by 95%
- letta_list_agents now returns summaries only (essential fields)
- letta_get_conversation_history default limit reduced to 10 messages
- letta_list_tools descriptions truncated to 200 characters
- letta_export_conversation limited to 100 messages maximum

### Changed
- Updated maintainer email to Zack@ascendhq.gg
- Improved developer experience with token limit handling

## [1.0.3] - 2025-06-24

### Added
- Professional Mermaid diagrams for enhanced documentation
- Diagram generation infrastructure
- Enhanced documentation with visual guides
- WSL-specific configurations

### Changed
- Improved CONTRIBUTING.md with diagram creation guidelines
- Enhanced visual documentation for better project understanding

### Fixed
- WSL compatibility issues with Mermaid CLI tools
- Diagram rendering on different backgrounds

## [1.0.2] - 2025-06-21

### Added
- 30+ MCP tools for Letta.ai integration
- Comprehensive error handling and logging
- Streaming support for real-time interactions
- Performance optimization with connection pooling
- Complete API coverage for agent management
- Memory system integration
- Tool management capabilities
- Export and import functionality
- Health checks and diagnostics

[1.0.4]: https://github.com/SNYCFIRE-CORE/letta-mcp-server/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/SNYCFIRE-CORE/letta-mcp-server/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/SNYCFIRE-CORE/letta-mcp-server/compare/v1.0.1...v1.0.2