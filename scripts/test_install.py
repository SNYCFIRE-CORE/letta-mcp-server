#!/usr/bin/env python3
"""
Test installation script for Letta MCP Server package.

This script tests the built package by installing it in a virtual environment
and verifying it works correctly.
"""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run_command(cmd, description, cwd=None, capture_output=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=capture_output,
            text=True,
            cwd=cwd
        )
        if result.stdout and capture_output:
            output = result.stdout.strip()
            if output:
                print(f"   {output}")
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False, ""


def test_package_installation():
    """Test package installation in a clean virtual environment."""
    print("🧪 Testing Letta MCP Server package installation...")
    
    # Get project root and check for distribution files
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    
    if not dist_dir.exists():
        print("❌ Error: dist/ directory not found. Run 'python scripts/build.py' first.")
        return False
    
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        print("❌ Error: No wheel files found. Run 'python scripts/build.py' first.")
        return False
    
    wheel_file = wheel_files[0]
    print(f"📦 Testing wheel: {wheel_file.name}")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        venv_path = temp_path / "test_env"
        
        print(f"📁 Creating test environment in: {venv_path}")
        
        # Create virtual environment
        print("🐍 Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        
        # Get activation commands based on platform
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        # Upgrade pip
        success, _ = run_command(
            f'"{pip_exe}" install --upgrade pip',
            "Upgrading pip in test environment"
        )
        if not success:
            return False
        
        # Install the wheel
        success, _ = run_command(
            f'"{pip_exe}" install "{wheel_file}"',
            f"Installing {wheel_file.name}"
        )
        if not success:
            return False
        
        # Test basic import
        success, version_output = run_command(
            f'"{python_exe}" -c "import letta_mcp; print(f\'Version: {{letta_mcp.__version__}}\')"',
            "Testing basic import"
        )
        if not success:
            return False
        
        # Test CLI commands exist
        success, _ = run_command(
            f'"{python_exe}" -c "import letta_mcp.cli; print(\'CLI module imported successfully\')"',
            "Testing CLI module import"
        )
        if not success:
            return False
        
        success, _ = run_command(
            f'"{python_exe}" -c "import letta_mcp.server; print(\'Server module imported successfully\')"',
            "Testing server module import"
        )
        if not success:
            return False
        
        # Test that entry points work
        try:
            # Check if CLI commands are available
            success, _ = run_command(
                f'"{python_exe}" -m pip show letta-mcp-server',
                "Checking installed package info"
            )
            if not success:
                print("⚠️  Warning: Could not get package info")
        except Exception as e:
            print(f"⚠️  Warning: Could not test entry points: {e}")
        
        # Test configuration loading
        success, _ = run_command(
            f'"{python_exe}" -c "from letta_mcp.config import LettaConfig; print(\'Config module works\')"',
            "Testing configuration module"
        )
        if not success:
            return False
        
        # Test exception classes
        success, _ = run_command(
            f'"{python_exe}" -c "from letta_mcp.exceptions import LettaMCPError; print(\'Exception classes work\')"',
            "Testing exception classes"
        )
        if not success:
            return False
        
        # Test models
        success, _ = run_command(
            f'"{python_exe}" -c "from letta_mcp.models import AgentInfo; print(\'Model classes work\')"',
            "Testing model classes"
        )
        if not success:
            return False
        
        print("✅ All installation tests passed!")
        return True


def test_from_testpypi():
    """Test installation from TestPyPI."""
    print("🧪 Testing installation from TestPyPI...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        venv_path = temp_path / "testpypi_env"
        
        print(f"📁 Creating TestPyPI test environment in: {venv_path}")
        
        # Create virtual environment
        venv.create(venv_path, with_pip=True)
        
        # Get activation commands based on platform
        if sys.platform == "win32":
            pip_exe = venv_path / "Scripts" / "pip.exe"
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            pip_exe = venv_path / "bin" / "pip"
            python_exe = venv_path / "bin" / "python"
        
        # Upgrade pip
        success, _ = run_command(
            f'"{pip_exe}" install --upgrade pip',
            "Upgrading pip"
        )
        if not success:
            return False
        
        # Install from TestPyPI
        success, _ = run_command(
            f'"{pip_exe}" install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ letta-mcp-server',
            "Installing from TestPyPI"
        )
        if not success:
            print("⚠️  Package not available on TestPyPI yet, or installation failed")
            return False
        
        # Test basic functionality
        success, _ = run_command(
            f'"{python_exe}" -c "import letta_mcp; print(f\'TestPyPI version: {{letta_mcp.__version__}}\')"',
            "Testing TestPyPI installation"
        )
        if not success:
            return False
        
        print("✅ TestPyPI installation test passed!")
        return True


def main():
    """Main test process."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Letta MCP Server package installation")
    parser.add_argument(
        "--testpypi",
        action="store_true",
        help="Test installation from TestPyPI instead of local wheel"
    )
    
    args = parser.parse_args()
    
    if args.testpypi:
        success = test_from_testpypi()
    else:
        success = test_package_installation()
    
    if success:
        print("\n🎉 All tests passed! Package is ready for distribution.")
        print("\n🚀 Next steps:")
        if not args.testpypi:
            print("   • Upload to TestPyPI: python scripts/upload.py --test")
            print("   • Test TestPyPI install: python scripts/test_install.py --testpypi")
            print("   • Upload to PyPI: python scripts/upload.py --production")
    else:
        print("\n❌ Tests failed. Please fix issues before distributing.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)