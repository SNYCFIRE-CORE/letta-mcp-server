#!/usr/bin/env python3
"""
Test runner script for Letta MCP Server

This script provides convenient commands for running different test suites.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle the result"""
    print(f"\n{'='*60}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ {description or 'Command'} failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ {description or 'Command'} completed successfully")
        return True


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests"""
    cmd = ["python", "-m", "pytest", "tests/unit/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src/letta_mcp", "--cov-report=term-missing", "--cov-report=html"])
    
    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose=False):
    """Run integration tests (requires real API)"""
    # Set environment variable for integration tests
    env = os.environ.copy()
    env["RUN_INTEGRATION_TESTS"] = "1"
    
    cmd = ["python", "-m", "pytest", "tests/integration/"]
    
    if verbose:
        cmd.append("-v")
    
    print("\n⚠️  Integration tests require a valid Letta API key!")
    print("Make sure LETTA_API_KEY is set in your environment.")
    
    result = subprocess.run(cmd, capture_output=False, env=env)
    
    if result.returncode != 0:
        print(f"\n❌ Integration tests failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ Integration tests completed successfully")
        return True


def run_e2e_tests(verbose=False):
    """Run end-to-end tests"""
    cmd = ["python", "-m", "pytest", "tests/e2e/"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "End-to-End Tests")


def run_performance_tests(verbose=False):
    """Run performance tests (requires real API)"""
    env = os.environ.copy()
    env["RUN_PERFORMANCE_TESTS"] = "1"
    env["RUN_INTEGRATION_TESTS"] = "1"  # Performance tests need real API
    
    cmd = ["python", "-m", "pytest", "tests/performance/"]
    
    if verbose:
        cmd.append("-v")
    
    print("\n⚠️  Performance tests require a valid Letta API key!")
    print("These tests will make many API calls and may take several minutes.")
    
    result = subprocess.run(cmd, capture_output=False, env=env)
    
    if result.returncode != 0:
        print(f"\n❌ Performance tests failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ Performance tests completed successfully")
        return True


def run_all_tests(verbose=False, skip_integration=False, skip_performance=False):
    """Run all test suites"""
    results = []
    
    # Unit tests with coverage
    results.append(run_unit_tests(verbose=verbose, coverage=True))
    
    # End-to-end tests
    results.append(run_e2e_tests(verbose=verbose))
    
    # Integration tests (optional)
    if not skip_integration:
        print("\n" + "="*60)
        print("INTEGRATION TESTS")
        print("="*60)
        response = input("Run integration tests? Requires Letta API key (y/N): ")
        if response.lower() in ['y', 'yes']:
            results.append(run_integration_tests(verbose=verbose))
        else:
            print("Skipping integration tests")
    
    # Performance tests (optional)
    if not skip_performance:
        print("\n" + "="*60)
        print("PERFORMANCE TESTS")
        print("="*60)
        response = input("Run performance tests? Requires Letta API key and takes time (y/N): ")
        if response.lower() in ['y', 'yes']:
            results.append(run_performance_tests(verbose=verbose))
        else:
            print("Skipping performance tests")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


def run_quick_test():
    """Run a quick smoke test"""
    print("\n🚀 Running quick smoke test...")
    
    # Just run a few key unit tests
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/test_config.py::TestLettaConfig::test_default_config",
        "tests/unit/test_utils.py::TestValidateAgentId::test_valid_agent_ids",
        "tests/unit/test_server.py::TestLettaMCPServer::test_server_initialization",
        "-v"
    ]
    
    return run_command(cmd, "Quick Smoke Test")


def check_coverage():
    """Check test coverage"""
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/",
        "--cov=src/letta_mcp",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-fail-under=80"
    ]
    
    return run_command(cmd, "Coverage Check")


def lint_tests():
    """Lint test files"""
    cmd = ["python", "-m", "flake8", "tests/"]
    return run_command(cmd, "Lint Tests")


def type_check_tests():
    """Type check test files"""
    cmd = ["python", "-m", "mypy", "tests/", "--ignore-missing-imports"]
    return run_command(cmd, "Type Check Tests")


def validate_test_environment():
    """Validate that the test environment is properly set up"""
    print("\n🔍 Validating test environment...")
    
    issues = []
    
    # Check if pytest is available
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__} is available")
    except ImportError:
        issues.append("pytest is not installed")
    
    # Check if fastmcp is available
    try:
        import fastmcp
        print(f"✅ fastmcp is available")
    except ImportError:
        issues.append("fastmcp is not installed")
    
    # Check if our source code is available
    try:
        from letta_mcp.server import LettaMCPServer
        print("✅ letta_mcp source code is available")
    except ImportError:
        issues.append("letta_mcp source code is not available (run 'pip install -e .')")
    
    # Check API key for integration tests
    api_key = os.getenv("LETTA_API_KEY")
    if api_key:
        print(f"✅ LETTA_API_KEY is set (...{api_key[-10:]})")
    else:
        print("⚠️  LETTA_API_KEY is not set (required for integration/performance tests)")
    
    # Check test files exist
    test_files = [
        "tests/unit/test_config.py",
        "tests/unit/test_utils.py", 
        "tests/unit/test_server.py",
        "tests/integration/test_real_api.py",
        "tests/e2e/test_workflows.py",
        "tests/performance/test_benchmarks.py"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ {test_file} exists")
        else:
            issues.append(f"{test_file} is missing")
    
    if issues:
        print("\n❌ Environment validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("\n✅ Test environment is properly configured!")
        return True


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Test runner for Letta MCP Server")
    parser.add_argument(
        "command", 
        choices=[
            "unit", "integration", "e2e", "performance", 
            "all", "quick", "coverage", "lint", "typecheck", "validate"
        ],
        help="Test command to run"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--skip-integration", action="store_true", help="Skip integration tests in 'all'")
    parser.add_argument("--skip-performance", action="store_true", help="Skip performance tests in 'all'")
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = False
    
    if args.command == "unit":
        success = run_unit_tests(verbose=args.verbose, coverage=True)
    elif args.command == "integration":
        success = run_integration_tests(verbose=args.verbose)
    elif args.command == "e2e":
        success = run_e2e_tests(verbose=args.verbose)
    elif args.command == "performance":
        success = run_performance_tests(verbose=args.verbose)
    elif args.command == "all":
        success = run_all_tests(
            verbose=args.verbose, 
            skip_integration=args.skip_integration,
            skip_performance=args.skip_performance
        )
    elif args.command == "quick":
        success = run_quick_test()
    elif args.command == "coverage":
        success = check_coverage()
    elif args.command == "lint":
        success = lint_tests()
    elif args.command == "typecheck":
        success = type_check_tests()
    elif args.command == "validate":
        success = validate_test_environment()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()