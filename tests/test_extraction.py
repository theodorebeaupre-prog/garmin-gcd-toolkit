"""Tests for Phase 3/4 extraction helpers."""

from pathlib import Path

import pytest

from gcd_tool.extractor import extract_resources


GUPDATE_GCD = Path(__file__).parent.parent / "samples" / "GUPDATE.GCD"


def test_extract_resources_all(tmp_path: Path) -> None:
    if not GUPDATE_GCD.exists():
        pytest.skip("samples/GUPDATE.GCD not present — local-only tests")

    summary = extract_resources(GUPDATE_GCD, tmp_path)

    assert summary.png_count == 20
    assert summary.gzip_count == 6
    pngs = [resource for resource in summary.resources if resource.kind == "png"]
    assert pngs
    assert pngs[0].path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_extract_resources_type_filter(tmp_path: Path) -> None:
    if not GUPDATE_GCD.exists():
        pytest.skip("samples/GUPDATE.GCD not present — local-only tests")

    summary = extract_resources(GUPDATE_GCD, tmp_path, type_filter={0x64})

    assert summary.png_count == 10
    assert summary.gzip_count == 1
    assert {resource.record_type for resource in summary.resources} == {0x64}


def test_extracted_png_contains_iend(tmp_path: Path) -> None:
    if not GUPDATE_GCD.exists():
        pytest.skip("samples/GUPDATE.GCD not present — local-only tests")

    summary = extract_resources(GUPDATE_GCD, tmp_path, type_filter={0x64})
    pngs = [resource for resource in summary.resources if resource.kind == "png"]
    assert pngs
    first_png = pngs[0].path.read_bytes()
    assert b"IEND" in first_png
