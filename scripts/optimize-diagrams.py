#!/usr/bin/env python3
"""
Optimize diagram file sizes for web delivery.
Uses svgo for SVG optimization and PIL for PNG optimization.
"""

import os
import subprocess
from pathlib import Path
from PIL import Image
import io

PROJECT_ROOT = Path(__file__).parent.parent
DIAGRAMS_OUTPUT = PROJECT_ROOT / "diagrams" / "output"

def optimize_svg(svg_path: Path) -> None:
    """Optimize SVG file using svgo if available."""
    try:
        # Check if svgo is installed
        subprocess.run(["svgo", "--version"], capture_output=True, check=True)
        
        original_size = svg_path.stat().st_size
        
        # Run svgo with optimizations
        subprocess.run([
            "svgo",
            str(svg_path),
            "-o", str(svg_path),
            "--multipass",
            "--pretty",
            "--precision=2"
        ], check=True)
        
        new_size = svg_path.stat().st_size
        reduction = (1 - new_size / original_size) * 100
        
        print(f"✅ {svg_path.name}: {original_size/1024:.1f}KB → {new_size/1024:.1f}KB ({reduction:.1f}% reduction)")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"⚠️  svgo not installed. Install with: npm install -g svgo")
        print(f"   Skipping optimization for {svg_path.name}")

def optimize_png(png_path: Path) -> None:
    """Optimize PNG file using PIL."""
    try:
        original_size = png_path.stat().st_size
        
        # Open and optimize
        img = Image.open(png_path)
        
        # Convert RGBA to RGB if no transparency is needed
        if img.mode == 'RGBA':
            # Check if alpha channel is all opaque
            alpha = img.split()[-1]
            if alpha.getextrema() == (255, 255):
                img = img.convert('RGB')
        
        # Save with optimization
        img.save(png_path, 'PNG', optimize=True, quality=95)
        
        new_size = png_path.stat().st_size
        reduction = (1 - new_size / original_size) * 100
        
        print(f"✅ {png_path.name}: {original_size/1024:.1f}KB → {new_size/1024:.1f}KB ({reduction:.1f}% reduction)")
    except Exception as e:
        print(f"❌ Error optimizing {png_path.name}: {e}")

def main():
    """Main function to optimize all diagrams."""
    print("🎯 Diagram Optimization")
    print("=" * 50)
    
    # Check for PIL
    try:
        import PIL
    except ImportError:
        print("❌ PIL not installed. Install with: pip install Pillow")
        return 1
    
    svg_files = list(DIAGRAMS_OUTPUT.glob("*.svg"))
    png_files = list(DIAGRAMS_OUTPUT.glob("*.png"))
    
    if svg_files:
        print("\n📊 Optimizing SVG files...")
        for svg_file in svg_files:
            optimize_svg(svg_file)
    
    if png_files:
        print("\n🖼️  Optimizing PNG files...")
        for png_file in png_files:
            optimize_png(png_file)
    
    print("\n✨ Optimization complete!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())