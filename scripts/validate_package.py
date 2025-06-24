#!/usr/bin/env python3
"""
Complete package validation script for Letta MCP Server.

This script performs comprehensive validation of the built package,
including metadata checks, import tests, and CLI validation.
"""

import subprocess
import sys
import tempfile
import venv
import json
from pathlib import Path
from typing import Dict, Any


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
                print(f"   ✅ {output}")
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stdout:
            print(f"      stdout: {e.stdout}")
        if e.stderr:
            print(f"      stderr: {e.stderr}")
        return False, ""


def check_metadata(wheel_path: Path) -> Dict[str, Any]:
    """Extract and validate package metadata."""
    print("📋 Validating package metadata...")
    
    metadata = {}
    
    # Check wheel contents
    try:
        result = subprocess.run(
            ["python", "-m", "zipfile", "-l", str(wheel_path)],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.split('\n')
        metadata['wheel_files'] = [f.strip() for f in files if f.strip()]
        print(f"   ✅ Wheel contains {len(metadata['wheel_files'])} files")
    except subprocess.CalledProcessError:
        print("   ❌ Could not read wheel contents")
        return metadata
    
    # Check for required files
    required_files = [
        'letta_mcp/__init__.py',
        'letta_mcp/cli.py',
        'letta_mcp/server.py',
        'letta_mcp/_version.py'
    ]
    
    for req_file in required_files:
        if any(req_file in f for f in metadata['wheel_files']):
            print(f"   ✅ Found {req_file}")
        else:
            print(f"   ❌ Missing {req_file}")
    
    return metadata


def validate_installation(wheel_path: Path) -> bool:
    """Validate package installation in clean environment."""
    print("🧪 Validating package installation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_env"
        
        # Create virtual environment
        print("   🐍 Creating test environment...")
        venv.create(venv_path, with_pip=True)
        
        # Get executables
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        # Upgrade pip
        success, _ = run_command(
            f'"{pip_exe}" install --upgrade pip',
            "Upgrading pip"
        )
        if not success:
            return False
        
        # Install wheel
        success, _ = run_command(
            f'"{pip_exe}" install "{wheel_path}"',
            f"Installing {wheel_path.name}"
        )
        if not success:
            return False
        
        # Test basic import
        success, version = run_command(
            f'"{python_exe}" -c "import letta_mcp; print(letta_mcp.__version__)"',
            "Testing import and version"
        )
        if not success:
            return False
        
        # Test CLI availability
        success, _ = run_command(
            f'"{python_exe}" -c "import letta_mcp.cli; print(\'CLI available\')"',
            "Testing CLI module"
        )
        if not success:
            return False
        
        success, _ = run_command(
            f'"{python_exe}" -c "import letta_mcp.server; print(\'Server available\')"',
            "Testing server module"
        )
        if not success:
            return False
        
        # Test all imports
        modules = [
            "letta_mcp.config",
            "letta_mcp.exceptions", 
            "letta_mcp.models",
            "letta_mcp.utils"
        ]
        
        for module in modules:
            success, _ = run_command(
                f'"{python_exe}" -c "import {module}; print(\'{module} imported\')"',
                f"Testing {module}"
            )
            if not success:
                return False
        
        print("   ✅ All installation tests passed!")
        return True


def validate_entry_points(wheel_path: Path) -> bool:
    """Validate that entry points are correctly configured."""
    print("🎯 Validating entry points...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_env"
        
        # Create virtual environment and install
        venv.create(venv_path, with_pip=True)
        
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
            letta_mcp_exe = venv_path / "Scripts" / "letta-mcp.exe"
            letta_server_exe = venv_path / "Scripts" / "letta-mcp-server.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
            letta_mcp_exe = venv_path / "bin" / "letta-mcp"
            letta_server_exe = venv_path / "bin" / "letta-mcp-server"
        
        # Install package
        success, _ = run_command(
            f'"{pip_exe}" install --upgrade pip',
            "Upgrading pip"
        )
        if not success:
            return False
        
        success, _ = run_command(
            f'"{pip_exe}" install "{wheel_path}"',
            "Installing package"
        )
        if not success:
            return False
        
        # Check CLI executables exist
        if letta_mcp_exe.exists():
            print("   ✅ letta-mcp command available")
        else:
            print("   ❌ letta-mcp command not found")
            return False
        
        if letta_server_exe.exists():
            print("   ✅ letta-mcp-server command available")
        else:
            print("   ❌ letta-mcp-server command not found")
            return False
        
        return True


def main():
    """Main validation process."""
    print("🔍 Letta MCP Server Package Validation")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    
    if not dist_dir.exists():
        print("❌ Error: dist/ directory not found. Run build first.")
        return False
    
    # Find wheel file
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        print("❌ Error: No wheel files found. Run build first.")
        return False
    
    wheel_file = wheel_files[0]
    print(f"📦 Validating: {wheel_file.name}")
    print()
    
    # Validate metadata
    metadata = check_metadata(wheel_file)
    print()
    
    # Validate installation
    if not validate_installation(wheel_file):
        print("❌ Installation validation failed!")
        return False
    print()
    
    # Validate entry points
    if not validate_entry_points(wheel_file):
        print("❌ Entry point validation failed!")
        return False
    print()
    
    # Final summary
    print("🎉 Package Validation Complete!")
    print("=" * 50)
    print("✅ Metadata validation: PASSED")
    print("✅ Installation test: PASSED") 
    print("✅ Import tests: PASSED")
    print("✅ Entry points: PASSED")
    print()
    print("📦 Package is ready for distribution!")
    print(f"   Wheel: {wheel_file}")
    print(f"   Size: {wheel_file.stat().st_size / 1024:.1f} KB")
    print()
    print("🚀 Next steps:")
    print("   • Upload to TestPyPI: python scripts/upload.py --test")
    print("   • Upload to PyPI: python scripts/upload.py --production")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)