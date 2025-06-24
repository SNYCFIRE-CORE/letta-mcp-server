#!/usr/bin/env python3
"""
Final validation script for letta-mcp-server PyPI release
Comprehensive pre-release validation checklist
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_command(cmd, check=True, capture=True):
    """Run a command and return the result"""
    print(f"  → {cmd}")
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"    ❌ FAILED: {result.stderr}")
            return False
        return result
    else:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0

def check_build_system():
    """Validate build system configuration"""
    print("🔧 Checking build system configuration...")
    
    # Check pyproject.toml exists
    if not Path("pyproject.toml").exists():
        print("  ❌ pyproject.toml not found")
        return False
    print("  ✅ pyproject.toml exists")
    
    # Validate setuptools-scm version detection
    result = run_command("python -m setuptools_scm")
    if result:
        version = result.stdout.strip()
        print(f"  ✅ Version detected: {version}")
        return True
    return False

def check_dependencies():
    """Validate all dependencies are properly specified"""
    print("📦 Checking dependencies...")
    
    # Try importing all dependencies  
    deps = ["fastmcp", "httpx", "yaml", "dotenv", "tenacity", "pydantic"]
    for dep in deps:
        try:
            __import__(dep)
            print(f"  ✅ {dep} importable")
        except ImportError:
            print(f"  ❌ {dep} not available")
            return False
    
    return True

def check_package_structure():
    """Validate package structure"""
    print("📁 Checking package structure...")
    
    required_files = [
        "src/letta_mcp/__init__.py",
        "src/letta_mcp/server.py",
        "src/letta_mcp/cli.py",
        "src/letta_mcp/config.py",
        "src/letta_mcp/models.py",
        "src/letta_mcp/utils.py",
        "src/letta_mcp/exceptions.py",
        "README.md",
        "LICENSE",
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} missing")
            return False
    
    return True

def check_build_and_install():
    """Test package building and installation"""
    print("🏗️ Testing package build and installation...")
    
    # Clean previous builds
    if not run_command("rm -rf dist/*.tar.gz dist/*.whl", check=False):
        print("  ⚠️ Could not clean dist directory")
    
    # Build package
    if not run_command("python -m build"):
        return False
    print("  ✅ Package built successfully")
    
    # Validate with twine
    if not run_command("twine check dist/*"):
        return False
    print("  ✅ Package validation passed")
    
    # Test installation in temporary environment
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_path = Path(tmpdir) / "test_venv"
        
        # Create virtual environment
        if not run_command(f"python -m venv {venv_path}"):
            return False
        
        # Install package
        wheel_files = list(Path("dist").glob("*.whl"))
        if not wheel_files:
            print("  ❌ No wheel files found")
            return False
        
        wheel_file = wheel_files[0]
        pip_cmd = f"{venv_path}/bin/pip install {wheel_file}"
        if not run_command(pip_cmd):
            return False
        print("  ✅ Package installs successfully")
        
        # Test CLI commands
        letta_cmd = f"{venv_path}/bin/letta-mcp --help"
        if not run_command(letta_cmd, capture=False):
            return False
        print("  ✅ CLI commands work")
    
    return True

def check_metadata():
    """Validate package metadata"""
    print("📋 Checking package metadata...")
    
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    
    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    
    project = config.get("project", {})
    
    # Check required fields
    required_fields = ["name", "description", "authors", "classifiers", "dependencies"]
    for field in required_fields:
        if field in project:
            print(f"  ✅ {field}")
        else:
            print(f"  ❌ {field} missing")
            return False
    
    # Check classifiers include Python versions
    classifiers = project.get("classifiers", [])
    python_versions = [c for c in classifiers if "Programming Language :: Python ::" in c]
    if python_versions:
        print(f"  ✅ Python versions specified: {len(python_versions)}")
    else:
        print("  ❌ No Python version classifiers")
        return False
    
    return True

def main():
    """Run all validation checks"""
    print("🚀 letta-mcp-server PyPI Release Validation")
    print("=" * 50)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    checks = [
        ("Build System", check_build_system),
        ("Dependencies", check_dependencies), 
        ("Package Structure", check_package_structure),
        ("Metadata", check_metadata),
        ("Build & Install", check_build_and_install),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
            if result:
                print(f"✅ {name} validation passed\n")
            else:
                print(f"❌ {name} validation failed\n")
        except Exception as e:
            print(f"❌ {name} validation error: {e}\n")
            results.append((name, False))
    
    # Summary
    print("📊 Validation Summary")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ALL VALIDATIONS PASSED - READY FOR PYPI RELEASE!")
        return 0
    else:
        print("⚠️ VALIDATION ISSUES FOUND - PLEASE FIX BEFORE RELEASE")
        return 1

if __name__ == "__main__":
    sys.exit(main())