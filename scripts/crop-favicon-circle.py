#!/usr/bin/env python3
"""Crop favicon.svg and favicon.ico into circles."""

import os
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

PUBLIC_DIR = "public"
SIZE = 512

def create_circular_mask(size):
    """Create a circular mask."""
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, size - 1, size - 1], fill=255)
    return mask

def render_svg_to_png(svg_path, output_size=SIZE):
    """Render SVG to PNG using cairosvg or return None if unavailable."""
    try:
        import cairosvg
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            cairosvg.svg2png(url=svg_path, write_to=tmp.name, output_width=output_size)
            return tmp.name
    except ImportError:
        print(f"  ⚠ cairosvg not installed. Install with: pip install cairosvg")
        return None

def crop_to_circle(image_path, output_path, is_svg=False):
    """Open image, crop to circle, save."""
    print(f"Processing {os.path.basename(image_path)}...")

    # Handle SVG by rendering first
    if is_svg:
        temp_png = render_svg_to_png(image_path)
        if not temp_png:
            return False
        image_path = temp_png

    try:
        # Open and convert to RGBA
        img = Image.open(image_path).convert("RGBA")
        img.thumbnail((SIZE, SIZE), Image.Resampling.LANCZOS)

        # Pad to square if needed
        if img.size[0] != img.size[1]:
            square = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
            offset = ((SIZE - img.size[0]) // 2, (SIZE - img.size[1]) // 2)
            square.paste(img, offset)
            img = square
        else:
            # Ensure it's the target size
            if img.size != (SIZE, SIZE):
                img = img.resize((SIZE, SIZE), Image.Resampling.LANCZOS)

        # Apply circular mask
        mask = create_circular_mask(img.size[0])  # Use actual image size
        img.putalpha(mask)

        # Save
        img.save(output_path)
        print(f"  ✓ Created {os.path.basename(output_path)}")
        return True
    finally:
        # Cleanup temp file if it was created
        if is_svg and os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    print("Creating circular favicons...\n")

    svg_path = os.path.join(PUBLIC_DIR, "favicon.svg")
    ico_path = os.path.join(PUBLIC_DIR, "favicon.ico")

    success = True

    # SVG → PNG circle
    if os.path.exists(svg_path):
        if not crop_to_circle(svg_path, os.path.join(PUBLIC_DIR, "favicon-circle-svg.png"), is_svg=True):
            success = False

    # ICO → PNG circle
    if os.path.exists(ico_path):
        crop_to_circle(ico_path, os.path.join(PUBLIC_DIR, "favicon-circle-ico.png"))

    print("\nGenerated:")
    if os.path.exists(svg_path):
        print("  - public/favicon-circle-svg.png")
    if os.path.exists(ico_path):
        print("  - public/favicon-circle-ico.png")

    if not success:
        sys.exit(1)
