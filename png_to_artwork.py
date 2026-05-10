#!/usr/bin/env python3
"""
PNG → Pixel Art JSON Converter
================================
Chuyển đổi ảnh PNG bất kỳ thành JSON pixel data cho coloring book app.

CÁCH DÙNG:
    python3 png_to_artwork.py <input.png> [options]

VÍ DỤ:
    python3 png_to_artwork.py cat.png
    python3 png_to_artwork.py cat.png --grid 32 --colors 20 --id artwork_01 --title "Cute Cat" --category animal
    python3 png_to_artwork.py folder/*.png --output artworks.json   # batch convert

OPTIONS:
    --grid      Grid size (default: 32). Ảnh sẽ resize về NxN pixels. Càng lớn càng chi tiết.
                Gợi ý: 24 (đơn giản), 32 (cân bằng), 48 (chi tiết), 64 (rất chi tiết)
    --colors    Số màu tối đa trong palette (default: 20, max: 64)
    --id        ID của artwork (default: tên file)
    --title     Tên hiển thị (default: tên file)
    --category  Category: animal/flowers/trending/popular/fantasy/space/ocean (default: popular)
    --preview   Tên ảnh preview trong asset (default: img_home1)
    --output    File JSON output (default: artworks.json)
    --append    Thêm vào file JSON hiện có thay vì tạo mới
    --preview-png   Xuất ảnh preview để kiểm tra kết quả

LƯU Ý VỀ ẢNH ĐẦU VÀO:
    - PNG với nền trắng hoặc transparent đều OK
    - Ảnh square (vuông) cho kết quả tốt nhất
    - Ảnh có màu sắc rõ ràng, contrast cao sẽ đẹp hơn
    - Tránh ảnh có quá nhiều gradient mịn (sẽ bị posterize)
"""

import json
import sys
import os
import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageOps
except ImportError:
    print("Lỗi: Cần cài Pillow trước: pip install Pillow")
    sys.exit(1)


def quantize_image(img: Image.Image, n_colors: int) -> tuple[Image.Image, list[str]]:
    """Quantize image to N colors, returns quantized image + hex palette."""
    # Convert to RGBA để xử lý transparency
    img_rgba = img.convert("RGBA")
    
    # Replace transparent pixels with white
    background = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
    background.paste(img_rgba, mask=img_rgba.split()[3])
    img_rgb = background.convert("RGB")
    
    # Slight sharpening for better edge definition
    img_rgb = img_rgb.filter(ImageFilter.SHARPEN)
    
    # Quantize using median cut
    quantized = img_rgb.quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT, dither=0)
    
    # Extract palette
    palette_raw = quantized.getpalette()  # flat list [R,G,B, R,G,B, ...]
    hex_palette = []
    used_indices = set(quantized.getdata())
    
    # Only include used colors
    index_remap = {}
    for old_idx in sorted(used_indices):
        r = palette_raw[old_idx * 3]
        g = palette_raw[old_idx * 3 + 1]
        b = palette_raw[old_idx * 3 + 2]
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        new_idx = len(hex_palette)
        index_remap[old_idx] = new_idx
        hex_palette.append(hex_color)
    
    return quantized, hex_palette, index_remap


def image_to_artwork(
    image_path: str,
    grid_size: int = 32,
    n_colors: int = 20,
    artwork_id: str = None,
    title: str = None,
    category: str = "popular",
    preview_image: str = "img_home1",
) -> dict:
    """Convert a PNG image to artwork JSON dict."""
    
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {image_path}")
    
    # Auto-generate ID and title from filename if not provided
    stem = path.stem
    if artwork_id is None:
        artwork_id = stem.lower().replace(" ", "_")
    if title is None:
        title = stem.replace("_", " ").replace("-", " ").title()
    
    print(f"  📂 Đọc ảnh: {path.name}")
    img = Image.open(image_path)
    print(f"  📐 Kích thước gốc: {img.width}×{img.height}, mode: {img.mode}")
    
    # Resize to grid_size x grid_size using high-quality downsampling
    img_resized = img.resize(
        (grid_size, grid_size),
        Image.Resampling.LANCZOS
    )
    print(f"  🔲 Resize về: {grid_size}×{grid_size}")
    
    # Quantize colors
    actual_colors = min(n_colors, 64)
    quantized, hex_palette, index_remap = quantize_image(img_resized, actual_colors)
    print(f"  🎨 Palette: {len(hex_palette)} màu")
    
    # Extract cells
    cells = []
    raw_data = list(quantized.getdata())
    for pixel in raw_data:
        cells.append(index_remap[pixel])
    
    # Validate
    assert len(cells) == grid_size * grid_size, f"Expected {grid_size*grid_size} cells, got {len(cells)}"
    assert max(cells) < len(hex_palette), f"Cell index {max(cells)} >= palette size {len(hex_palette)}"
    
    print(f"  ✅ Cells: {len(cells)}, max_index: {max(cells)}, palette: {len(hex_palette)}")
    
    return {
        "id": artwork_id,
        "title": title,
        "category": category,
        "previewImage": preview_image,
        "gridWidth": grid_size,
        "gridHeight": grid_size,
        "palette": hex_palette,
        "cells": cells,
    }


def render_preview(artwork: dict, output_path: str, scale: int = 10):
    """Render artwork back to PNG for visual verification."""
    gw = artwork["gridWidth"]
    gh = artwork["gridHeight"]
    palette = artwork["palette"]
    cells = artwork["cells"]
    
    img = Image.new("RGB", (gw * scale, gh * scale), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    for y in range(gh):
        for x in range(gw):
            ci = cells[y * gw + x]
            hx = palette[ci]
            r = int(hx[1:3], 16)
            g = int(hx[3:5], 16)
            b = int(hx[5:7], 16)
            draw.rectangle(
                [x * scale, y * scale, x * scale + scale - 1, y * scale + scale - 1],
                fill=(r, g, b)
            )
    
    img.save(output_path)
    print(f"  🖼  Preview saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert PNG images to pixel art JSON for coloring book app",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("images", nargs="+", help="PNG file(s) to convert")
    parser.add_argument("--grid", type=int, default=32, help="Grid size (default: 32)")
    parser.add_argument("--colors", type=int, default=20, help="Max colors in palette (default: 20)")
    parser.add_argument("--id", dest="artwork_id", default=None, help="Artwork ID")
    parser.add_argument("--title", default=None, help="Artwork title")
    parser.add_argument("--category", default="popular", help="Category")
    parser.add_argument("--preview", default="img_home1", help="Preview image asset name")
    parser.add_argument("--output", default="artworks.json", help="Output JSON file")
    parser.add_argument("--append", action="store_true", help="Append to existing JSON")
    parser.add_argument("--preview-png", action="store_true", help="Export preview PNG")
    parser.add_argument("--scale", type=int, default=10, help="Preview PNG scale (default: 10)")
    
    args = parser.parse_args()
    
    # Load existing data if appending
    existing_artworks = []
    if args.append and os.path.exists(args.output):
        with open(args.output) as f:
            data = json.load(f)
            existing_artworks = data.get("artworks", [])
        print(f"📦 Loaded {len(existing_artworks)} existing artworks from {args.output}")
    
    new_artworks = []
    preview_images = ["img_home1", "img_home2", "img_home3"]
    
    for i, image_path in enumerate(args.images):
        print(f"\n[{i+1}/{len(args.images)}] Converting: {image_path}")
        try:
            # For batch, auto-assign preview images
            preview = args.preview
            if len(args.images) > 1:
                preview = preview_images[i % 3]
            
            artwork = image_to_artwork(
                image_path=image_path,
                grid_size=args.grid,
                n_colors=args.colors,
                artwork_id=args.artwork_id if len(args.images) == 1 else None,
                title=args.title if len(args.images) == 1 else None,
                category=args.category,
                preview_image=preview,
            )
            new_artworks.append(artwork)
            
            # Export preview PNG
            if args.preview_png:
                preview_path = Path(image_path).stem + "_preview.png"
                render_preview(artwork, preview_path, scale=args.scale)
                
        except Exception as e:
            print(f"  ❌ Lỗi: {e}")
            continue
    
    # Save JSON
    all_artworks = existing_artworks + new_artworks
    output_data = {
        "version": 1,
        "artworks": all_artworks
    }
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(new_artworks)} new artworks → {args.output}")
    print(f"   Total artworks: {len(all_artworks)}")


if __name__ == "__main__":
    main()