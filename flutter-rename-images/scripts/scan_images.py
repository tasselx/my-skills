#!/usr/bin/env python3
"""Scan a directory for image files and generate a thumbnail contact sheet.

Usage:
    python scan_images.py <directory> [--output <contact_sheet.png>] [--cols <N>] [--thumb <size>]

Outputs:
    1. Prints a numbered JSON list of image files to stdout.
    2. Generates a contact sheet PNG with all thumbnails labeled by index number.
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".svg"}

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def scan_images(directory: str) -> List[Dict]:
    entries = []
    for f in sorted(Path(directory).iterdir()):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            entries.append({
                "index": len(entries),
                "filename": f.name,
                "extension": f.suffix.lower(),
                "size_bytes": f.stat().st_size,
            })
    return entries


def make_contact_sheet(
    directory: str,
    entries: List[Dict],
    output_path: str,
    cols: int = 6,
    thumb_size: int = 120,
) -> Optional[str]:
    drawable = [e for e in entries if e["extension"] != ".svg"]
    if not drawable:
        return None

    label_height = 24
    cell_w = thumb_size + 8
    cell_h = thumb_size + label_height + 8
    rows = math.ceil(len(drawable) / cols)
    sheet_w = cols * cell_w + 8
    sheet_h = rows * cell_h + 8
    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except (OSError, IOError):
            font = ImageFont.load_default()

    for i, entry in enumerate(drawable):
        col = i % cols
        row = i // cols
        x = col * cell_w + 4
        y = row * cell_h + 4

        img_path = Path(directory) / entry["filename"]
        try:
            img = Image.open(img_path)
            img.thumbnail((thumb_size, thumb_size), Image.LANCZOS)

            bg = Image.new("RGBA", (thumb_size, thumb_size), (245, 245, 245, 255))
            offset_x = (thumb_size - img.size[0]) // 2
            offset_y = (thumb_size - img.size[1]) // 2
            if img.mode == "RGBA":
                bg.paste(img, (offset_x, offset_y), img)
            else:
                bg.paste(img, (offset_x, offset_y))
            sheet.paste(bg.convert("RGB"), (x, y))
        except Exception:
            draw.rectangle([x, y, x + thumb_size, y + thumb_size], fill=(200, 200, 200))
            draw.text((x + 4, y + 4), "ERR", fill=(255, 0, 0), font=font)

        draw.rectangle([x - 1, y - 1, x + thumb_size + 1, y + thumb_size + 1], outline=(200, 200, 200))

        label = f"[{entry['index']}]"
        draw.text((x + 4, y + thumb_size + 2), label, fill=(0, 0, 0), font=font)

    sheet.save(output_path, "PNG")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Scan images and generate contact sheet")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--output", default=None, help="Contact sheet output path")
    parser.add_argument("--cols", type=int, default=6, help="Columns in contact sheet")
    parser.add_argument("--thumb", type=int, default=120, help="Thumbnail size in pixels")
    args = parser.parse_args()

    directory = os.path.expanduser(args.directory)
    if not os.path.isdir(directory):
        print(f"ERROR: {directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    entries = scan_images(directory)
    if not entries:
        print("No image files found.", file=sys.stderr)
        sys.exit(1)

    output = args.output or os.path.join(directory, ".contact_sheet.png")
    sheet_path = make_contact_sheet(directory, entries, output, args.cols, args.thumb)

    result = {"images": entries, "total": len(entries)}
    if sheet_path:
        result["contact_sheet"] = sheet_path

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
