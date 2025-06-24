# Letta MCP Server Test Suite

This directory contains a comprehensive test suite for the Letta MCP Server, providing 90%+ code coverage with unit, integration, end-to-end, and performance tests.

## 🏗️ Test Architecture

### Test Types

```
tests/
├── unit/           # Unit tests (isolated, mocked)
├── integration/    # Integration tests (real API)
├── e2e/           # End-to-end workflow tests
├── performance/   # Performance benchmarks
└── conftest.py    # Shared fixtures and configuration
```

### Test Pyramid

```
    /\     Performance Tests (Real API, Benchmarks)
   /  \    
  /____\   E2E Tests (Complete Workflows)
 /      \  
/________\ Integration Tests (Real Letta API)
\_________/
 Unit Tests (Fast, Isolated, Mocked)
```

## 🚀 Quick Start

### Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

2. **For integration/performance tests** (optional):
   ```bash
   export LETTA_API_KEY="sk-let-your-api-key-here"
   ```

### Running Tests

```bash
# Quick validation
python tests/run_tests.py validate

# Fast unit tests only
python tests/run_tests.py unit

# All tests with real API validation
python tests/run_tests.py all

# Performance benchmarks
python tests/run_tests.py performance
```

## 📊 Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests using mocks. **No external dependencies.**

- **`test_config.py`**: Configuration loading, validation, environment variables
- **`test_utils.py`**: Utility functions, message parsing, agent ID validation
- **`test_server.py`**: Server initialization, tool registration, error handling

```bash
# Run unit tests with coverage
pytest tests/unit/ --cov=src/letta_mcp --cov-report=html
```

**Coverage Target**: 95%+ for all unit tests

### Integration Tests (`tests/integration/`)

Tests against the **real Letta API** using live AXLE agent.

- **`test_real_api.py`**: Live API validation, real agent interactions, error handling

```bash
# Enable integration tests
export RUN_INTEGRATION_TESTS=1
pytest tests/integration/ -v
```

**Requirements**:
- Valid `LETTA_API_KEY` environment variable
- Network connectivity to `api.letta.com`
- AXLE agent (`agent-01c2ef52-be32-401d-8d8f-edc561b39cbe`) accessible

### End-to-End Tests (`tests/e2e/`)

Complete user workflow scenarios.

- **`test_workflows.py`**: Multi-step scenarios, automotive analysis workflows, error recovery

```bash
pytest tests/e2e/ -v
```

**Scenarios Tested**:
- New user agent setup workflow
- Automotive dealer analysis workflow  
- Agent customization workflow
- Multi-agent coordination
- Error recovery patterns

### Performance Tests (`tests/performance/`)

Benchmarks and performance validation.

- **`test_benchmarks.py`**: Response times, throughput, memory usage, scalability

```bash
# Enable performance tests
export RUN_PERFORMANCE_TESTS=1
pytest tests/performance/ -v
```

**Benchmarks**:
- Response time targets (health check < 2s, operations < 3s)
- Concurrent request handling (10+ simultaneous)
- Memory stability over time
- Scalability under increasing load

## 🔧 Test Configuration

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `RUN_INTEGRATION_TESTS=1` | Enable integration tests | For real API tests |
| `RUN_PERFORMANCE_TESTS=1` | Enable performance tests | For benchmarks |
| `RUN_STRESS_TESTS=1` | Enable stress tests | For extended load testing |
| `LETTA_API_KEY` | Letta API authentication | For real API access |

### Pytest Configuration

Configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--tb=short", 
    "--cov=letta_mcp",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--asyncio-mode=auto",
]
```

### Coverage Configuration

```toml
[tool.coverage.run]
source = ["src/letta_mcp"]
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
```

## 📈 Test Fixtures

### Key Fixtures (from `conftest.py`)

#### Configuration Fixtures
- `mock_config`: Mock configuration for unit tests
- `real_config`: Real configuration for integration tests

#### Server Fixtures  
- `mock_server`: Mocked server instance
- `real_server`: Real server instance with API connection

#### Client Fixtures
- `mock_client`: FastMCP client with mocked server
- `real_client`: FastMCP client with real API connection

#### Data Fixtures
- `sample_agent_data`: Mock agent response data
- `sample_memory_blocks`: Mock memory block data
- `sample_message_response`: Mock conversation data

#### Utility Fixtures
- `mock_http_response`: Factory for creating mock HTTP responses
- `performance_timer`: Timer for performance measurements
- `env_var_helper`: Environment variable management

## 🎯 Testing Best Practices

### Unit Tests
- **Mock external dependencies**: Use `unittest.mock` for HTTP calls
- **Test edge cases**: Empty responses, malformed data, network errors
- **Fast execution**: All unit tests should complete in < 30 seconds
- **Deterministic**: No reliance on external state or timing

### Integration Tests
- **Real API validation**: Test actual Letta API responses
- **Graceful degradation**: Handle API errors appropriately
- **Rate limiting aware**: Respect API limits and implement backoff
- **Environment agnostic**: Work in any environment with valid credentials

### Performance Tests
- **Realistic scenarios**: Test patterns that match real usage
- **Statistical significance**: Multiple samples for timing measurements
- **Resource monitoring**: Track CPU, memory, and network usage
- **Regression prevention**: Fail if performance degrades significantly

## 🚦 CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: python tests/run_tests.py unit
      - uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    env:
      LETTA_API_KEY: ${{ secrets.LETTA_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: python tests/run_tests.py integration
```

### Test Commands Reference

```bash
# Validate environment
python tests/run_tests.py validate

# Unit tests only
python tests/run_tests.py unit

# Integration tests (requires API key)
python tests/run_tests.py integration

# End-to-end workflows  
python tests/run_tests.py e2e

# Performance benchmarks (requires API key)
python tests/run_tests.py performance

# Quick smoke test
python tests/run_tests.py quick

# Coverage report
python tests/run_tests.py coverage

# All tests (interactive prompts for API tests)
python tests/run_tests.py all

# All tests, skip optional suites
python tests/run_tests.py all --skip-integration --skip-performance
```

## 🔍 Debugging Test Failures

### Common Issues

1. **Import Errors**
   ```bash
   # Install in development mode
   pip install -e .
   ```

2. **Integration Test Failures**
   ```bash
   # Check API key
   echo $LETTA_API_KEY
   
   # Test API connectivity manually
   curl -H "Authorization: Bearer $LETTA_API_KEY" https://api.letta.com/v1/agents
   ```

3. **Performance Test Failures**
   ```bash
   # Check network connectivity
   ping api.letta.com
   
   # Run with verbose output
   pytest tests/performance/ -v -s
   ```

4. **Coverage Issues**
   ```bash
   # Generate detailed coverage report
   pytest tests/unit/ --cov=src/letta_mcp --cov-report=html
   open htmlcov/index.html
   ```

### Verbose Debugging

```bash
# Maximum verbosity
pytest tests/ -vvv -s --tb=long

# Stop on first failure
pytest tests/ -x

# Run specific test
pytest tests/unit/test_server.py::TestLettaMCPServer::test_server_initialization -v
```

## 📋 Coverage Reports

After running tests with coverage:

```bash
# Terminal report
pytest tests/unit/ --cov=src/letta_mcp --cov-report=term-missing

# HTML report (detailed)
pytest tests/unit/ --cov=src/letta_mcp --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest tests/unit/ --cov=src/letta_mcp --cov-report=xml
```

## 🎯 Coverage Targets

| Component | Target | Current |
|-----------|---------|---------|
| `config.py` | 95% | - |
| `utils.py` | 95% | - |
| `server.py` | 90% | - |
| `models.py` | 85% | - |
| `exceptions.py` | 90% | - |
| **Overall** | **90%** | - |

## 🚀 Contributing Tests

When adding new features:

1. **Add unit tests** for new functions/classes
2. **Update integration tests** for new API endpoints  
3. **Add e2e scenarios** for new workflows
4. **Include performance tests** for new operations
5. **Update fixtures** as needed for new data structures

### Test Naming Convention

```python
# Unit tests
def test_{function_name}_{scenario}()
def test_{function_name}_with_{condition}()
def test_{function_name}_when_{situation}()

# Integration tests  
def test_{operation}_with_real_api()

# E2E tests
def test_{workflow_name}_workflow()

# Performance tests
def test_{operation}_response_time()
def test_{operation}_throughput()
```

## 🔗 Related Documentation

- [Main README](../README.md) - Project overview
- [API Reference](../docs/API_REFERENCE.md) - Tool and resource documentation  
- [Architecture](../docs/ARCHITECTURE.md) - System design
- [Contributing](../CONTRIBUTING.md) - Development guidelines

---

**Test Coverage Status**: 🎯 Targeting 90%+ with comprehensive real API validation

**Last Updated**: June 24, 2025