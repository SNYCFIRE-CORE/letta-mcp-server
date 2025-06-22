# Contributing to Letta MCP Server

Thank you for your interest in contributing to the Letta MCP Server! This project represents the first production-ready bridge between Claude's MCP ecosystem and Letta's stateful agents, and we welcome contributions from the community.

## 🎯 Project Vision

Our mission is to democratize access to stateful AI agents by providing seamless integration between Claude and Letta.ai. We believe that powerful AI capabilities should be accessible to all developers, not just those working with specific platforms.

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ or Python 3.8+
- Claude Desktop or Claude Code installed
- Basic understanding of MCP (Model Context Protocol)
- Familiarity with REST APIs and async programming

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/letta-mcp-server.git
   cd letta-mcp-server
   ```

2. **Install Dependencies**
   ```bash
   npm install
   # or for Python development
   pip install -e ".[dev]"
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Add your Letta API key
   LETTA_API_KEY=sk-let-your-key-here
   ```

4. **Run Tests**
   ```bash
   npm test
   # or
   pytest
   ```

5. **Start Development Server**
   ```bash
   npm run dev
   # or
   python -m letta_mcp.server
   ```

## 📋 How to Contribute

### Types of Contributions We Welcome

**🔧 Code Contributions**
- Bug fixes and performance improvements
- New MCP tool implementations
- Enhanced error handling and logging
- Documentation improvements
- Test coverage expansion

**📚 Documentation**
- API documentation and examples
- Troubleshooting guides
- Use case tutorials
- Integration guides for other platforms

**🧪 Testing & Quality Assurance**
- Manual testing across different environments
- Automated test suite expansion
- Performance benchmarking
- Security vulnerability assessment

**🎨 Community & Ecosystem**
- Example applications and demos
- Blog posts and tutorials
- Conference presentations
- Community support and mentoring

### Contribution Process

1. **Check Existing Issues**
   - Browse our [issue tracker](https://github.com/SNYCFIRE-CORE/letta-mcp-server/issues)
   - Look for issues labeled `good-first-issue` or `help-wanted`
   - Comment on issues you'd like to work on

2. **Create an Issue (if needed)**
   - For bugs: Use the bug report template
   - For features: Use the feature request template
   - For questions: Use the discussion template

3. **Fork and Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

4. **Make Your Changes**
   - Follow our coding standards (see below)
   - Include tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

5. **Submit Pull Request**
   - Use our pull request template
   - Provide clear description of changes
   - Link to related issues
   - Request review from maintainers

## 🎨 Coding Standards

### Code Style

**TypeScript/JavaScript:**
- Use Prettier for formatting (config provided)
- Follow ESLint rules (config provided)
- Use meaningful variable and function names
- Prefer async/await over promises

**Python:**
- Follow PEP 8 style guidelines
- Use Black for code formatting
- Type hints required for public APIs
- Docstrings for all public functions

### API Design Principles

1. **Consistency**: Follow established patterns in the codebase
2. **Error Handling**: Provide meaningful error messages and proper HTTP status codes
3. **Documentation**: All public APIs must be documented with examples
4. **Testing**: New features require corresponding tests
5. **Performance**: Consider memory usage and response times

### Commit Message Format

```
type(scope): short description

Longer description if needed, explaining what changed and why.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Build process or auxiliary tool changes

### Example Commit Messages

```
feat(api): add streaming support for agent conversations

Implement Server-Sent Events (SSE) for real-time conversation streaming.
This enables more responsive user experiences in Claude when interacting
with Letta agents.

Fixes #45
```

```
fix(auth): handle expired API keys gracefully

Previously, expired Letta API keys would cause server crashes. Now we
catch authentication errors and return proper HTTP 401 responses with
helpful error messages.

Fixes #67
```

## 🧪 Testing Guidelines

### Test Categories

**Unit Tests**
- Individual function and method testing
- Mock external dependencies
- Fast execution (< 100ms per test)
- High coverage requirements (>90%)

**Integration Tests**
- End-to-end MCP tool functionality
- Real Letta API interactions (test environment)
- Claude MCP client integration
- Network and timeout handling

**Performance Tests**
- Response time benchmarks
- Memory usage profiling
- Concurrent request handling
- Rate limit compliance

### Test Requirements

- All new features must include tests
- Bug fixes must include regression tests
- Tests should be deterministic and reliable
- Use descriptive test names explaining the scenario

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- tests/agent-management.test.js

# Run with coverage
npm run test:coverage

# Run integration tests
npm run test:integration
```

## 📖 Documentation Standards

### Code Documentation

**Functions and Methods:**
```typescript
/**
 * Creates a new Letta agent with specified configuration
 * @param config - Agent configuration object
 * @param config.name - Unique name for the agent
 * @param config.persona - Agent personality description
 * @param config.tools - Array of tool names to attach
 * @returns Promise resolving to agent object
 * @throws {LettaAPIError} When API request fails
 * @example
 * ```typescript
 * const agent = await createAgent({
 *   name: "sales-assistant",
 *   persona: "Helpful automotive sales expert",
 *   tools: ["web_search", "calculator"]
 * });
 * ```
 */
```

**API Endpoints:**
```markdown
### Create Agent

Creates a new stateful agent in Letta.

**Endpoint:** `POST /agents`

**Parameters:**
- `name` (string, required): Unique agent name
- `persona` (string, optional): Personality description
- `tools` (array, optional): Tool names to attach

**Response:**
```json
{
  "id": "agent-123",
  "name": "sales-assistant",
  "created_at": "2025-06-21T10:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:3000/mcp/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "sales-assistant", "persona": "Helpful expert"}'
```
```

### README and Guides

- Use clear, concise language
- Include working code examples
- Provide context and motivation
- Link to related documentation
- Keep examples up-to-date

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) and help us maintain a positive community.

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests, technical discussions
- **GitHub Discussions**: General questions, ideas, community chat
- **Discord**: Real-time collaboration and support (link in README)
- **Email**: Security vulnerabilities and private matters

### Getting Help

**For Development Questions:**
1. Check existing documentation and issues
2. Search GitHub discussions
3. Ask in Discord #development channel
4. Create a GitHub discussion

**For Bug Reports:**
1. Use the bug report template
2. Provide minimal reproduction case
3. Include environment details
4. Check if issue already exists

**For Feature Requests:**
1. Use the feature request template
2. Explain the use case and motivation
3. Consider implementation complexity
4. Be open to alternative solutions

## 🏆 Recognition

We believe in recognizing contributions to our community:

- **Contributors**: Listed in README and release notes
- **Major Features**: Highlighted in blog posts and social media
- **Community Leaders**: Invited to maintainer roles
- **Conference Speakers**: Support for presenting project work

### Contributor Levels

**Community Member**
- Occasional contributions
- Participates in discussions
- Helps other users

**Regular Contributor**
- Consistent contributions over time
- Mentors new contributors
- Helps with issue triage

**Core Contributor**
- Significant feature contributions
- Reviews pull requests
- Shapes project direction

**Maintainer**
- Commit access to repository
- Release management
- Project governance participation

## 🔒 Security

If you discover a security vulnerability, please do not open a public issue. Instead:

1. Email us at security@snycfire.com
2. Provide detailed description of the vulnerability
3. Include steps to reproduce (if possible)
4. Allow time for us to address the issue before public disclosure

We follow responsible disclosure practices and will acknowledge your contribution once the issue is resolved.

## 📝 License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE).

## ❓ Questions?

Still have questions? We're here to help:

- **Documentation**: Check our [docs folder](docs/)
- **Examples**: Browse [examples folder](examples/)
- **Discussions**: GitHub Discussions tab
- **Discord**: Real-time chat with the community
- **Email**: contribute@snycfire.com

Thank you for contributing to the future of AI agent development! Together, we're making stateful agents accessible to developers everywhere.

---

*This project is proudly open source and community-driven. Every contribution, no matter how small, makes a difference.*