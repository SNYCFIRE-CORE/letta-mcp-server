#!/usr/bin/env python3
"""
Generate all Mermaid diagrams for the Letta MCP Server documentation.
This script converts .mmd files to both SVG and PNG formats with optimization.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DIAGRAMS_SRC = PROJECT_ROOT / "diagrams" / "src"
DIAGRAMS_OUTPUT = PROJECT_ROOT / "diagrams" / "output"
MERMAID_CONFIG = PROJECT_ROOT / "mermaid-config.json"
PUPPETEER_CONFIG = PROJECT_ROOT / "puppeteer-config.json"

# Ensure output directory exists
DIAGRAMS_OUTPUT.mkdir(parents=True, exist_ok=True)

def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a command and return the exit code, stdout, and stderr."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def generate_diagram(input_file: Path, output_format: str, scale: int = 2) -> bool:
    """Generate a diagram in the specified format."""
    output_file = DIAGRAMS_OUTPUT / f"{input_file.stem}.{output_format}"
    
    cmd = [
        "mmdc",
        "-i", str(input_file),
        "-o", str(output_file),
        "-c", str(MERMAID_CONFIG),
        "-p", str(PUPPETEER_CONFIG),
    ]
    
    if output_format == "png":
        cmd.extend(["-s", str(scale)])
    
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        print(f"✅ Generated: {output_file.name}")
        # Get file size
        size_kb = output_file.stat().st_size / 1024
        print(f"   Size: {size_kb:.1f} KB")
        return True
    else:
        print(f"❌ Failed to generate {output_file.name}")
        print(f"   Error: {stderr}")
        return False

def main():
    """Main function to generate all diagrams."""
    print("🎨 Letta MCP Server - Diagram Generation")
    print("=" * 50)
    
    # Find all .mmd files
    mmd_files = list(DIAGRAMS_SRC.glob("*.mmd"))
    
    if not mmd_files:
        print("❌ No .mmd files found in", DIAGRAMS_SRC)
        sys.exit(1)
    
    print(f"Found {len(mmd_files)} diagram(s) to generate")
    print()
    
    success_count = 0
    total_count = len(mmd_files) * 2  # SVG + PNG for each
    
    for mmd_file in mmd_files:
        print(f"\n📊 Processing: {mmd_file.name}")
        print("-" * 40)
        
        # Generate SVG
        if generate_diagram(mmd_file, "svg"):
            success_count += 1
        
        # Generate PNG with 2x scale for high DPI
        if generate_diagram(mmd_file, "png", scale=2):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✨ Generation complete: {success_count}/{total_count} files")
    
    # Create an index file
    create_index()
    
    return 0 if success_count == total_count else 1

def create_index():
    """Create an index.md file with all diagrams."""
    index_path = DIAGRAMS_OUTPUT / "index.md"
    
    diagrams = [
        ("architecture", "System Architecture", "Overview of how Letta MCP Server bridges Claude and Letta.ai"),
        ("installation-flow", "Installation Flow", "Step-by-step guide to get up and running in 60 seconds"),
        ("tool-catalog", "Tool Catalog", "Complete listing of all 19+ MCP tools organized by category"),
        ("performance-comparison", "Performance Comparison", "Visual benchmark showing 4-5x performance improvements"),
        ("error-handling", "Error Handling Flow", "Robust error handling and recovery mechanisms"),
        ("memory-lifecycle", "Memory Lifecycle", "How agent memory persists and is managed across sessions"),
        ("streaming-flow", "Streaming Flow", "Real-time streaming for better user experience")
    ]
    
    content = """# Letta MCP Server - Diagrams

These diagrams visualize the key concepts and architecture of the Letta MCP Server.

## Quick Navigation

"""
    
    for filename, title, description in diagrams:
        if (DIAGRAMS_OUTPUT / f"{filename}.svg").exists():
            content += f"### {title}\n"
            content += f"{description}\n\n"
            content += f"- [SVG (GitHub)](./{filename}.svg)\n"
            content += f"- [PNG (High-Res)](./{filename}.png)\n\n"
    
    content += """## Usage

### Embedding in Documentation

```markdown
<!-- For GitHub README -->
![System Architecture](diagrams/output/architecture.svg)

<!-- For PyPI or other platforms -->
![System Architecture](https://raw.githubusercontent.com/SNYCFIRE-CORE/letta-mcp-server/main/diagrams/output/architecture.png)
```

### Contributing

To modify or add diagrams:
1. Edit/create `.mmd` files in `diagrams/src/`
2. Run `python scripts/generate-diagrams.py`
3. Commit both source and output files

---

Generated with [Mermaid](https://mermaid.js.org/) and ❤️
"""
    
    index_path.write_text(content)
    print(f"\n📄 Created index: {index_path}")

if __name__ == "__main__":
    sys.exit(main())