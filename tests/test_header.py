"""Phase 1 smoke tests — verify magic and file accessibility."""

from pathlib import Path


GCD_MAGIC = b"GARMINd\x00"


def test_gcd_magic(gcd_path: Path) -> None:
    with open(gcd_path, "rb") as f:
        magic = f.read(8)
    assert magic == GCD_MAGIC, f"Unexpected magic bytes: {magic!r}"


def test_gcd_file_size(gcd_path: Path) -> None:
    size = gcd_path.stat().st_size
    assert size == 50_201_232, f"Unexpected file size: {size}"
