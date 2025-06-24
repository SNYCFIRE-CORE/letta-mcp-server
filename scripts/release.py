#!/usr/bin/env python3
"""
Release automation script for letta-mcp-server
Handles version management, building, and PyPI uploads
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"ERROR: Command failed with code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    return result

def get_current_version():
    """Get the current version from setuptools-scm"""
    result = run_command("python -m setuptools_scm")
    return result.stdout.strip()

def validate_package():
    """Validate the built packages"""
    print("Validating packages...")
    run_command("twine check dist/*")
    print("✅ Package validation passed")

def build_package():
    """Build the package"""
    print("Building package...")
    run_command("rm -rf dist/*.tar.gz dist/*.whl", check=False)
    run_command("python -m build")
    print("✅ Package built successfully")

def upload_to_pypi(repository="pypi", api_key=None):
    """Upload to PyPI or TestPyPI"""
    if not api_key:
        api_key = os.getenv("PYPI_API_KEY")
        if not api_key:
            print("ERROR: No API key provided. Set PYPI_API_KEY environment variable or use --api-key")
            sys.exit(1)
    
    env = os.environ.copy()
    env["TWINE_USERNAME"] = "__token__"
    env["TWINE_PASSWORD"] = api_key
    
    if repository == "testpypi":
        cmd = "twine upload --repository testpypi dist/*"
    else:
        cmd = "twine upload dist/*"
    
    print(f"Uploading to {repository}...")
    result = subprocess.run(cmd, shell=True, env=env)
    
    if result.returncode == 0:
        print(f"✅ Successfully uploaded to {repository}")
    else:
        print(f"❌ Upload to {repository} failed")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Release letta-mcp-server")
    parser.add_argument("--version", help="Show current version", action="store_true")
    parser.add_argument("--build", help="Build package only", action="store_true")
    parser.add_argument("--validate", help="Validate package only", action="store_true")
    parser.add_argument("--upload", choices=["testpypi", "pypi"], help="Upload to repository")
    parser.add_argument("--api-key", help="PyPI API key")
    parser.add_argument("--full-release", help="Full release: build + validate + upload to PyPI", action="store_true")
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    if args.version:
        version = get_current_version()
        print(f"Current version: {version}")
        return
    
    if args.build or args.full_release:
        build_package()
    
    if args.validate or args.full_release:
        validate_package()
    
    if args.upload:
        upload_to_pypi(args.upload, args.api_key)
    elif args.full_release:
        upload_to_pypi("pypi", args.api_key)

if __name__ == "__main__":
    main()