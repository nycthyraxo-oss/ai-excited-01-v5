#!/usr/bin/env python3
"""First Class — entry program for make.fun ai-excited-01.

Copies the entry image to the output directory the harness reads.
Standard library only; no network access; deterministic.
"""

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024


def validate_entry(path: Path) -> None:
    """Fail loudly unless the entry image meets the competition gate.

    Checks: the file exists, is a whole JPEG (SOI marker at the start,
    EOI marker at the end), is at most 1024x1024 pixels, and is at most
    1 MiB. A silent bad copy would be scored 0 by the gate; refusing
    to write it is strictly better.
    """
    if not path.is_file():
        raise SystemExit(f"entry image missing: {path}")
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit(
            f"entry image too large: {len(data)} bytes (max {MAX_BYTES})"
        )
    if not data.startswith(b"\xff\xd8") or not data.rstrip(b"\x00").endswith(
        b"\xff\xd9"
    ):
        raise SystemExit("entry image is not a whole JPEG (bad SOI/EOI markers)")
    width, height = jpeg_dimensions(data)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise SystemExit(
            f"entry image too large: {width}x{height} "
            f"(max {MAX_DIMENSION}x{MAX_DIMENSION})"
        )


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Read width/height from the first SOF marker of a JPEG byte string."""
    pos = 2
    while pos + 9 < len(data):
        if data[pos] != 0xFF:
            pos += 1
            continue
        marker = data[pos + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height = int.from_bytes(data[pos + 5 : pos + 7], "big")
            width = int.from_bytes(data[pos + 7 : pos + 9], "big")
            return width, height
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        length = int.from_bytes(data[pos + 2 : pos + 4], "big")
        pos += 2 + length
    raise SystemExit("entry image has no JPEG SOF marker (not a whole JPEG)")


def main() -> None:
    validate_entry(SOURCE)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, out_dir / "entry.png")


if __name__ == "__main__":
    main()
