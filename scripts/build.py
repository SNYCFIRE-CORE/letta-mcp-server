#!/usr/bin/env python3
"""
Build script for Letta MCP Server package.

This script handles building distribution packages (wheel and source distribution)
with proper validation and error checking.
"""

import subprocess
import sys
import shutil
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


def main():
    """Main build process."""
    print("🚀 Building Letta MCP Server package...")
    
    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"📁 Project root: {project_root}")
    
    # Clean previous builds
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    if dist_dir.exists():
        print("🧹 Cleaning previous dist/ directory...")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print("🧹 Cleaning previous build/ directory...")
        shutil.rmtree(build_dir)
    
    # Check if we have setuptools-scm and git
    if not run_command("python -m pip show setuptools-scm", "Checking setuptools-scm", project_root):
        print("📦 Installing setuptools-scm...")
        if not run_command("python -m pip install setuptools-scm", "Installing setuptools-scm", project_root):
            return False
    
    # Check git repository status
    if not run_command("git status", "Checking git status", project_root):
        print("⚠️  Warning: Not in a git repository or git not available")
        print("   setuptools-scm may use fallback version")
    
    # Install build tools
    print("📦 Installing build dependencies...")
    if not run_command("python -m pip install --upgrade build twine", "Installing build tools", project_root):
        return False
    
    # Build the package
    print("🔨 Building package...")
    if not run_command("python -m build", "Building distributions", project_root):
        return False
    
    # Validate the built packages
    print("🔍 Validating built packages...")
    if not run_command("python -m twine check dist/*", "Validating packages", project_root):
        return False
    
    # List built files
    print("📦 Built packages:")
    dist_files = list(dist_dir.glob("*"))
    for file in dist_files:
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"   📁 {file.name} ({size_mb:.2f} MB)")
    
    # Test import
    print("🧪 Testing package import...")
    try:
        # Try to install and import the wheel
        wheel_files = list(dist_dir.glob("*.whl"))
        if wheel_files:
            wheel_file = wheel_files[0]
            if not run_command(
                f"python -m pip install --force-reinstall {wheel_file}",
                f"Installing {wheel_file.name}",
                project_root
            ):
                return False
            
            if not run_command(
                "python -c \"import letta_mcp; print(f'✅ Import successful! Version: {letta_mcp.__version__}')\"",
                "Testing import",
                project_root
            ):
                return False
    except Exception as e:
        print(f"⚠️  Warning: Could not test import: {e}")
    
    print("✅ Build completed successfully!")
    print(f"📦 Distribution files are in: {dist_dir}")
    print("\n🚀 Next steps:")
    print("   • Test: python scripts/test_install.py")
    print("   • Upload to TestPyPI: python scripts/upload.py --test")
    print("   • Upload to PyPI: python scripts/upload.py --production")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)