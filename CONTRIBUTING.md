# 🤝 Contributing to Letta MCP Server

Thank you for your interest in contributing to the **first production-ready MCP server for Letta.ai**! This guide will help you understand our development workflow and contribution process.

## 🏗️ Development Workflow

### Branching Strategy

We use a **GitHub Flow + Release Branches** strategy for professional development:

```
main (production)     ←─────────── release/v1.0.0 ←─── develop (integration)
  ↓                                                        ↑
PyPI Auto-Release                                    feature/xyz-branch
  ↓                                                        ↑
GitHub Release                                       PR from contributors
```

### Branch Descriptions

**🏭 `main` - Production Branch**
- Always deployable, production-ready code
- Protected: Requires PR reviews + all status checks
- Auto-triggers: PyPI release, GitHub release, changelog
- **No direct commits allowed**

**🔧 `develop` - Integration Branch**
- Active development, where PRs get merged first
- Continuous integration testing
- Staging deployments for validation
- **Primary target for contributor PRs**

**🚀 `release/vX.Y.Z` - Release Preparation**
- Created from develop for final testing
- Version bumping, changelog finalization
- Release candidate testing
- Merges to main when ready

**⚡ `hotfix/xyz` - Emergency Fixes**
- Branches from main for critical issues
- Merges back to both main and develop
- Immediate PyPI releases

## 🚀 Quick Start for Contributors

### 1. Fork & Clone
```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/letta-mcp-server.git
cd letta-mcp-server
git remote add upstream https://github.com/SNYCFIRE-CORE/letta-mcp-server.git
```

### 2. Set Up Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create Feature Branch
```bash
# Always branch from develop
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

### 4. Make Changes & Test
```bash
# Run tests locally
pytest tests/ -v

# Run quality checks
black src/ tests/
ruff check src/ tests/
mypy src/letta_mcp/

# Test installation
pip install -e .
letta-mcp --help
```

### 5. Submit Pull Request
- Push your branch to your fork
- Create PR targeting `develop` branch
- Fill out the PR template completely
- Ensure all CI checks pass

## 📋 Contribution Types

### 🐛 Bug Fixes
- Target: `develop` branch
- Requirements: Test case demonstrating the bug
- Include: Clear reproduction steps

### ✨ New Features
- Target: `develop` branch
- Requirements: Feature proposal discussion first
- Include: Tests, documentation, examples

### 📖 Documentation
- Target: `develop` branch
- Include: Spelling/grammar check
- Test: Verify all links work

### 🧪 Tests
- Target: `develop` branch
- Focus: Increase coverage, edge cases
- Include: Performance impact assessment

### 🎨 Examples
- Target: `develop` branch
- Requirements: Working, tested examples
- Include: Clear documentation

## ✅ Quality Standards

### Code Quality Requirements

**✅ All PRs Must Pass:**
- [ ] **Code formatting**: `black` and `ruff` checks
- [ ] **Type checking**: `mypy` validation
- [ ] **Security scanning**: `bandit` security analysis
- [ ] **Test coverage**: 85%+ coverage maintained
- [ ] **Documentation**: All public APIs documented
- [ ] **Examples**: Working code examples where applicable

### Testing Requirements

**✅ Test Categories:**
- **Unit Tests**: Fast, isolated, mocked dependencies
- **Integration Tests**: Real API interactions (where safe)
- **Performance Tests**: Benchmark critical operations
- **Cross-platform**: Windows, macOS, Linux compatibility

### Documentation Standards

**✅ Documentation Must Include:**
- Clear, concise explanations
- Working code examples
- Installation/setup instructions
- Troubleshooting common issues
- API reference completeness

## 🔄 Development Process

### Step 1: Planning
- Check existing issues for similar work
- Create issue for significant changes
- Discuss approach with maintainers
- Get approval before starting large features

### Step 2: Implementation
- Write tests first (TDD encouraged)
- Implement feature with clean, documented code
- Follow existing code patterns and style
- Add examples demonstrating usage

### Step 3: Validation
- Run full test suite locally
- Verify cross-platform compatibility
- Test installation from clean environment
- Validate documentation accuracy

### Step 4: Review Process
- Create PR with detailed description
- Respond to review feedback promptly
- Update tests/docs based on feedback
- Ensure CI passes completely

## 🛡️ Security Considerations

### Security-First Development
- **API Keys**: Never commit API keys or secrets
- **Dependencies**: Keep dependencies updated
- **Validation**: Validate all inputs thoroughly
- **Transport**: Use HTTPS/TLS for all communications

### PyPI Release Security
- **NEVER** commit PyPI tokens to any file
- **ALWAYS** use environment variables for credentials
- **AUDIT** every release: `./scripts/secure-upload.sh audit`
- **TEST** on TestPyPI first before production release
- **VERIFY** distribution contents don't contain secrets:
  ```bash
  tar -tzf dist/*.tar.gz | grep -E "(\.env|\.pypirc|token|secret)"
  ```
- **USE** the secure upload script: `./scripts/secure-upload.sh release`
- **FOLLOW** the SECURE_PYPI_UPLOAD_GUIDE in mem0

### Reporting Security Issues
- **Email**: security@snycfire.com
- **Do NOT** create public GitHub issues
- **Include**: Detailed reproduction steps
- **Response**: We'll respond within 24 hours
- **Token Exposure**: If a PyPI token is exposed, immediately:
  1. Revoke at https://pypi.org/manage/account/#api-tokens
  2. Generate new token
  3. Notify maintainers
  4. Audit all files for exposure

## 🎯 Performance Guidelines

### Performance Standards
- **Response Times**: < 2s for typical operations
- **Memory Usage**: Efficient connection pooling
- **Concurrency**: Thread-safe implementations
- **Caching**: Intelligent caching strategies

### Benchmarking
- Run performance tests before submitting
- Document any performance impacts
- Include benchmark results in PR description
- Test with realistic workloads

## 📊 Release Process

### How Releases Work
1. **Development**: Features merged to `develop`
2. **Release Preparation**: Create `release/vX.Y.Z` from `develop`
3. **Final Testing**: Comprehensive validation on release branch
4. **Production Release**: Merge release branch to `main`
5. **Automated Publishing**: GitHub Actions handles PyPI + releases

### Version Strategy
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Conventional Commits**: Used for automated changelog
- **Release Notes**: Auto-generated from commit history

### Technical Diagrams

We use Mermaid for all technical diagrams to ensure consistency and maintainability.

**Creating/Updating Diagrams:**

1. **Edit Source Files**: Modify `.mmd` files in `diagrams/src/`
   ```mermaid
   flowchart LR
       A[Start] --> B{Decision}
       B -->|Yes| C[Success]
       B -->|No| D[Try Again]
   ```

2. **Follow Style Guide**:
   - Primary color: `#2563eb` (Claude/MCP elements)
   - Secondary color: `#10b981` (Letta.ai elements)
   - Accent color: `#f59e0b` (highlights/performance)
   - Error color: `#ef4444` (error states)

3. **Generate Output Files**:
   ```bash
   cd letta-mcp-server-enhanced
   python scripts/generate-diagrams.py
   ```

4. **Verify Output**:
   - Check SVG files render correctly
   - Ensure PNG files are high-quality (2x DPI)
   - Keep file sizes under 500KB

5. **Update Documentation**:
   - Add new diagrams to `docs/diagrams.md`
   - Update README with diagram references
   - Include alt text for accessibility

**Diagram Types We Use:**
- **Flowcharts**: Installation flows, process diagrams
- **Sequence Diagrams**: API interactions, memory operations
- **State Diagrams**: Error handling, state machines
- **Mind Maps**: Tool catalogs, feature overviews
- **Architecture Diagrams**: System components, data flow

**Best Practices:**
- Keep diagrams focused on a single concept
- Use clear, concise labels
- Test on both light and dark backgrounds
- Consider mobile device rendering
- Always commit both source (.mmd) and output files

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers learn and contribute
- Focus on technical merit in discussions

### Communication Channels
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, showcase
- **Discord**: Real-time community chat
- **Email**: Private/security communications

### Recognition
- All contributors credited in releases
- Significant contributions highlighted
- Community recognition for helpful members
- Open source badges for profiles

## 📚 Resources

### Documentation
- [Letta.ai Documentation](https://docs.letta.com)
- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Python Packaging Guide](https://packaging.python.org)

### Development Tools
- **IDE Setup**: VSCode with Python extension recommended
- **Testing**: pytest with coverage reporting
- **Linting**: ruff for fast Python linting
- **Formatting**: black for consistent code style
- **Type Checking**: mypy for static analysis

### Getting Help
- Check existing issues and documentation first
- Ask questions in GitHub Discussions
- Join our Discord community
- Reach out to maintainers for complex issues

---

## 🎉 Thank You!

Your contributions help make the Letta MCP Server the best tool for connecting Claude and Letta.ai. Every contribution, no matter how small, makes a difference in the AI development community.

**Happy coding!** 🚀

---

*Last updated: June 2025*