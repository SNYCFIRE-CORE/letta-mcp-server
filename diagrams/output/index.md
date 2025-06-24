# Letta MCP Server - Diagrams

These diagrams visualize the key concepts and architecture of the Letta MCP Server.

## Quick Navigation

### System Architecture
Overview of how Letta MCP Server bridges Claude and Letta.ai

- [SVG (GitHub)](./architecture.svg)
- [PNG (High-Res)](./architecture.png)

### Installation Flow
Step-by-step guide to get up and running in 60 seconds

- [SVG (GitHub)](./installation-flow.svg)
- [PNG (High-Res)](./installation-flow.png)

### Tool Catalog
Complete listing of all 19+ MCP tools organized by category

- [SVG (GitHub)](./tool-catalog.svg)
- [PNG (High-Res)](./tool-catalog.png)

### Performance Comparison
Visual benchmark showing 4-5x performance improvements

- [SVG (GitHub)](./performance-comparison.svg)
- [PNG (High-Res)](./performance-comparison.png)

### Error Handling Flow
Robust error handling and recovery mechanisms

- [SVG (GitHub)](./error-handling.svg)
- [PNG (High-Res)](./error-handling.png)

### Memory Lifecycle
How agent memory persists and is managed across sessions

- [SVG (GitHub)](./memory-lifecycle.svg)
- [PNG (High-Res)](./memory-lifecycle.png)

### Streaming Flow
Real-time streaming for better user experience

- [SVG (GitHub)](./streaming-flow.svg)
- [PNG (High-Res)](./streaming-flow.png)

## Usage

### Embedding in Documentation

```markdown
<!-- For GitHub README -->
![System Architecture](diagrams/output/architecture.svg)

<!-- For PyPI or other platforms -->
![System Architecture](https://raw.githubusercontent.com/SNYCFIRE-CORE/letta-mcp-server/main/diagrams/output/architecture.png)
```

### Contributing

To modify or add diagrams:
1. Edit/create `.mmd` files in `diagrams/src/`
2. Run `python scripts/generate-diagrams.py`
3. Commit both source and output files

---

Generated with [Mermaid](https://mermaid.js.org/) and ❤️
