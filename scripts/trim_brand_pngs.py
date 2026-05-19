"""Trim transparent borders and normalize brand PNG dimensions for Home Assistant."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

BRAND = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "hijri_calendar"
    / "brand"
)

ICON_FILES: tuple[tuple[str, int], ...] = (
    ("icon.png", 256),
    ("icon@2x.png", 512),
    ("dark_icon.png", 256),
    ("dark_icon@2x.png", 512),
)

LOGO_FILES: tuple[tuple[str, int], ...] = (
    ("logo.png", 256),
    ("logo@2x.png", 512),
    ("dark_logo.png", 256),
    ("dark_logo@2x.png", 512),
)


def _trim(image: Image.Image) -> Image.Image:
    """Crop to the tightest bounding box around non-transparent pixels."""
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    bbox = image.getbbox()
    if bbox is None:
        return image
    return image.crop(bbox)


def _fit_square(image: Image.Image, size: int) -> Image.Image:
    """Scale trimmed artwork to fit a square canvas (maximize size, centered)."""
    trimmed = _trim(image)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    width, height = trimmed.size
    scale = min(size / width, size / height)
    new_w = max(1, round(width * scale))
    new_h = max(1, round(height * scale))
    resized = trimmed.resize((new_w, new_h), Image.Resampling.LANCZOS)
    offset = ((size - new_w) // 2, (size - new_h) // 2)
    canvas.paste(resized, offset, resized)
    return canvas


def _fit_logo_height(image: Image.Image, height: int) -> Image.Image:
    """Scale trimmed artwork so the shortest side equals the target height."""
    trimmed = _trim(image)
    width, img_height = trimmed.size
    scale = height / img_height
    new_w = max(1, round(width * scale))
    return trimmed.resize((new_w, height), Image.Resampling.LANCZOS)


def _log(message: str) -> None:
    """Write a status line to stderr."""
    sys.stderr.write(f"{message}\n")


def main() -> int:
    """Trim icon and logo PNGs under the integration brand directory."""
    for filename, size in ICON_FILES:
        path = BRAND / filename
        if not path.is_file():
            _log(f"skip missing {path}")
            continue
        _fit_square(Image.open(path), size).save(path, optimize=True)
        _log(f"trimmed {filename} -> {size}x{size}")

    for filename, height in LOGO_FILES:
        path = BRAND / filename
        if not path.is_file():
            _log(f"skip missing {path}")
            continue
        result = _fit_logo_height(Image.open(path), height)
        result.save(path, optimize=True)
        _log(f"trimmed {filename} -> {result.size[0]}x{height}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
