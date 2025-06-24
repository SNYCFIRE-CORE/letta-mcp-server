#!/usr/bin/env python3
"""
Upload script for Letta MCP Server package to PyPI.

This script handles uploading to both TestPyPI and production PyPI
with proper authentication and error handling.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description, cwd=None):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False


def check_dist_files(project_root):
    """Check that distribution files exist."""
    dist_dir = project_root / "dist"
    if not dist_dir.exists():
        print("❌ Error: dist/ directory not found. Run 'python scripts/build.py' first.")
        return False
    
    dist_files = list(dist_dir.glob("*"))
    if not dist_files:
        print("❌ Error: No distribution files found. Run 'python scripts/build.py' first.")
        return False
    
    print("📦 Found distribution files:")
    for file in dist_files:
        print(f"   📁 {file.name}")
    
    return True


def setup_pypirc(test_mode=False):
    """Setup .pypirc configuration file."""
    home_dir = Path.home()
    pypirc_path = home_dir / ".pypirc"
    
    if test_mode:
        config_content = """[distutils]
index-servers =
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = # Add your TestPyPI API token here
"""
        print("🔧 TestPyPI configuration needed in ~/.pypirc:")
        print("   1. Get API token from https://test.pypi.org/manage/account/#api-tokens")
        print("   2. Add token to ~/.pypirc file")
    else:
        config_content = """[distutils]
index-servers =
    pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = # Add your PyPI API token here
"""
        print("🔧 PyPI configuration needed in ~/.pypirc:")
        print("   1. Get API token from https://pypi.org/manage/account/#api-tokens")
        print("   2. Add token to ~/.pypirc file")
    
    if not pypirc_path.exists():
        print(f"📝 Creating {pypirc_path}...")
        with open(pypirc_path, 'w') as f:
            f.write(config_content)
        print("✅ .pypirc file created. Please add your API token.")
        return False
    
    return True


def upload_to_testpypi(project_root):
    """Upload package to TestPyPI."""
    print("🧪 Uploading to TestPyPI...")
    
    if not setup_pypirc(test_mode=True):
        return False
    
    cmd = "python -m twine upload --repository testpypi dist/*"
    if not run_command(cmd, "Uploading to TestPyPI", project_root):
        return False
    
    print("✅ Upload to TestPyPI successful!")
    print("🔗 Check your package at: https://test.pypi.org/project/letta-mcp-server/")
    print("\n🧪 Test installation:")
    print("   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ letta-mcp-server")
    
    return True


def upload_to_pypi(project_root):
    """Upload package to production PyPI."""
    print("🚀 Uploading to production PyPI...")
    
    # Double-check this is what the user wants
    response = input("⚠️  Are you sure you want to upload to PRODUCTION PyPI? This cannot be undone! (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Upload cancelled.")
        return False
    
    if not setup_pypirc(test_mode=False):
        return False
    
    cmd = "python -m twine upload dist/*"
    if not run_command(cmd, "Uploading to PyPI", project_root):
        return False
    
    print("🎉 Upload to PyPI successful!")
    print("🔗 Check your package at: https://pypi.org/project/letta-mcp-server/")
    print("\n📦 Installation command:")
    print("   pip install letta-mcp-server")
    
    return True


def main():
    """Main upload process."""
    parser = argparse.ArgumentParser(description="Upload Letta MCP Server to PyPI")
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Upload to TestPyPI instead of production PyPI"
    )
    parser.add_argument(
        "--production", 
        action="store_true", 
        help="Upload to production PyPI"
    )
    
    args = parser.parse_args()
    
    if not args.test and not args.production:
        print("❌ Error: Specify either --test or --production")
        parser.print_help()
        return False
    
    if args.test and args.production:
        print("❌ Error: Cannot specify both --test and --production")
        return False
    
    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"📁 Project root: {project_root}")
    
    # Check distribution files exist
    if not check_dist_files(project_root):
        return False
    
    # Install twine if needed
    if not run_command("python -m pip show twine", "Checking twine installation", project_root):
        print("📦 Installing twine...")
        if not run_command("python -m pip install twine", "Installing twine", project_root):
            return False
    
    # Validate packages first
    print("🔍 Validating packages before upload...")
    if not run_command("python -m twine check dist/*", "Validating packages", project_root):
        return False
    
    # Upload to appropriate repository
    if args.test:
        return upload_to_testpypi(project_root)
    else:
        return upload_to_pypi(project_root)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)