#!/usr/bin/env python3
"""Convert an input image into a pixelated image."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - runtime environment dependency
    raise SystemExit(
        "Pillow is required. Install it with: pip install pillow"
    ) from exc


try:
    _RESAMPLING = Image.Resampling
except AttributeError:  # Pillow < 9.1
    _RESAMPLING = Image


def pixelate_image(input_path: Path, output_path: Path, pixel_size: int) -> None:
    if pixel_size <= 0:
        raise ValueError("pixel_size must be greater than 0")

    with Image.open(input_path) as source:
        image = source.convert("RGB")
        width, height = image.size
        reduced_size = (max(1, width // pixel_size), max(1, height // pixel_size))
        pixelated = image.resize(reduced_size, _RESAMPLING.BILINEAR).resize(
            (width, height), _RESAMPLING.NEAREST
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pixelated.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert image files such as JPG/PNG into pixel-art style images."
    )
    parser.add_argument("input", type=Path, help="Path to the input image (jpg/png/...) ")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path for output image (default: <input_stem>_pixel.png)",
    )
    parser.add_argument(
        "-p",
        "--pixel-size",
        type=int,
        default=12,
        help="Pixel block size (default: 12)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input.exists():
        print(f"Input file does not exist: {args.input}", file=sys.stderr)
        return 1

    output_path = args.output or args.input.with_name(f"{args.input.stem}_pixel.png")

    try:
        pixelate_image(args.input, output_path, args.pixel_size)
    except Exception as exc:  # noqa: BLE001
        print(f"Conversion failed: {exc}", file=sys.stderr)
        return 1

    print(f"Pixel image created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
