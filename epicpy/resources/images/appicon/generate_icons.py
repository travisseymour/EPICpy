#!/usr/bin/env python3
"""Generate icon sizes from appicon.png."""

from pathlib import Path

from PIL import Image

SIZES = [16, 24, 32, 48, 64, 128, 256, 512]


def main():
    script_dir = Path(__file__).parent
    source = script_dir / "appicon.png"

    if not source.exists():
        print(f"Source image not found: {source}")
        return

    img = Image.open(source)
    print(f"Loaded {source.name} ({img.width}x{img.height})")

    for size in SIZES:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        output = script_dir / f"icon_{size}.png"
        resized.save(output, "PNG")
        print(f"Created {output.name}")

    print("Done!")


if __name__ == "__main__":
    main()
