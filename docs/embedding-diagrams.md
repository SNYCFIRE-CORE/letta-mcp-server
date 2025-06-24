# Embedding Diagrams in Documentation

This guide shows how to properly embed the Letta MCP Server diagrams in various documentation contexts.

## GitHub README.md

For the main README, use relative paths to SVG files:

```markdown
## 🏗️ Architecture

The Letta MCP Server acts as a bridge between Claude's MCP ecosystem and Letta's powerful agent platform:

![Letta MCP Server Architecture](diagrams/output/architecture.svg)

### Key Components:
- **Connection Pooling**: Maintains 10 persistent connections for optimal performance
- **Error Handling**: Automatic retry with exponential backoff
- **Streaming Support**: Real-time response streaming for better UX
```

## PyPI Long Description

For PyPI, use absolute URLs to PNG files (better compatibility):

```markdown
## Architecture

![Letta MCP Server Architecture](https://raw.githubusercontent.com/SNYCFIRE-CORE/letta-mcp-server/main/diagrams/output/architecture.png)
```

## Documentation Sites (MkDocs, Sphinx, etc.)

### MkDocs Material

```markdown
## System Architecture

<figure markdown>
  ![Architecture](../diagrams/output/architecture.svg){ width="100%" }
  <figcaption>Letta MCP Server bridges Claude and Letta.ai ecosystems</figcaption>
</figure>
```

### Sphinx

```rst
System Architecture
===================

.. figure:: /_static/diagrams/architecture.svg
   :width: 100%
   :alt: Letta MCP Server Architecture
   :align: center

   Letta MCP Server bridges Claude and Letta.ai ecosystems
```

## Blog Posts and Articles

### Dev.to / Medium

```markdown
![Letta MCP Server Architecture](https://raw.githubusercontent.com/SNYCFIRE-CORE/letta-mcp-server/main/diagrams/output/architecture.png)

*Figure 1: The Letta MCP Server architecture showing the bridge between Claude and Letta.ai*
```

### HTML Embedding

```html
<div class="diagram-container">
  <img src="https://raw.githubusercontent.com/SNYCFIRE-CORE/letta-mcp-server/main/diagrams/output/architecture.svg" 
       alt="Letta MCP Server Architecture diagram showing Claude Desktop/Code connecting through MCP protocol to Letta MCP Server, which manages connection pooling, error handling, and streaming to the Letta.ai platform"
       width="100%" 
       loading="lazy">
  <p class="caption">Figure 1: System Architecture Overview</p>
</div>
```

## Social Media

### Twitter/X

When sharing on Twitter, use the PNG versions with proper alt text:

```
🚀 Excited to share the architecture of Letta MCP Server - the first production-ready bridge between @AnthropicAI's Claude and @LettaAI!

✅ 4x performance improvement
✅ Connection pooling
✅ Auto-retry & error handling
✅ Real-time streaming

[Attach: architecture.png]
```

### LinkedIn

```
Just released Letta MCP Server v1.0.2! 🎉

Key architectural highlights:
• Seamless integration between Claude and Letta.ai
• 10x connection pool for optimal performance
• Intelligent error handling with exponential backoff
• Real-time streaming support

Check out the architecture diagram below to see how we achieved 4-5x performance improvements over direct API calls.

#AI #OpenSource #MCP #Claude #LettaAI
```

## Accessibility Best Practices

### 1. Always Include Alt Text

```markdown
![System architecture diagram showing Claude Desktop and Claude Code connecting to Letta MCP Server via MCP Protocol. The server includes connection pooling, error handling, and streaming components that interface with the Letta.ai API, which manages agent registry, memory store, and tool manager for multiple agents](diagrams/output/architecture.svg)
```

### 2. Provide Text Descriptions

After embedding a diagram, include a text description:

```markdown
![Installation Flow](diagrams/output/installation-flow.svg)

The installation process follows these steps:
1. Check Python 3.9+ installation
2. Install via pip: `pip install letta-mcp-server`
3. Configure using either automatic (`letta-mcp configure`) or manual method
4. Enter your Letta API key
5. Restart Claude
6. Test with `letta_list_agents` tool
```

### 3. Use Semantic HTML

```html
<figure role="img" aria-labelledby="arch-caption">
  <img src="diagrams/output/architecture.svg" 
       alt="Detailed architecture diagram">
  <figcaption id="arch-caption">
    Figure 1: Letta MCP Server bridges Claude's MCP ecosystem with Letta's agent platform,
    providing connection pooling, error handling, and streaming capabilities.
  </figcaption>
</figure>
```

## Performance Considerations

### 1. Lazy Loading

```html
<img src="diagrams/output/architecture.svg" 
     loading="lazy"
     alt="Architecture diagram">
```

### 2. Responsive Images

```html
<picture>
  <source media="(max-width: 768px)" 
          srcset="diagrams/output/architecture-mobile.svg">
  <img src="diagrams/output/architecture.svg" 
       alt="Architecture diagram">
</picture>
```

### 3. CDN Usage

For high-traffic sites, consider using a CDN:

```markdown
![Architecture](https://cdn.jsdelivr.net/gh/SNYCFIRE-CORE/letta-mcp-server@main/diagrams/output/architecture.svg)
```

## Examples by Diagram Type

### Architecture Diagram
Best for: README, documentation sites, technical blog posts

### Installation Flow
Best for: Quick start guides, getting started sections

### Tool Catalog
Best for: API reference, feature overviews

### Performance Comparison
Best for: Blog posts, benchmarking sections, marketing materials

### Error Handling Flow
Best for: Troubleshooting guides, technical documentation

### Memory Lifecycle
Best for: Advanced usage guides, architectural deep dives

---

Remember: The goal is to make complex concepts immediately understandable through visual representation while maintaining accessibility for all users.