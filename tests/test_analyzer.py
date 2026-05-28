"""Tests for record payload analyzer helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from gcd_tool.analyzer import (
    calculate_entropy,
    classify_type_0x01,
    detect_containers,
    is_arm_thumb,
)


GUPDATE_GCD = Path(__file__).parent.parent / "samples" / "GUPDATE.GCD"


def test_calculate_entropy_edge_cases() -> None:
    assert calculate_entropy(b"") == 0.0
    assert calculate_entropy(b"\x00" * 128) == 0.0
    assert calculate_entropy(bytes(range(256))) > 7.5


def test_is_arm_thumb_on_known_pattern() -> None:
    thumb_like = b"\x10\xb5\x00\xf0\x70\x47\x00\xbd" * 16
    assert is_arm_thumb(thumb_like) > 0.4


def test_detect_containers_synthetic() -> None:
    blob = bytearray(1024)
    blob[16:20] = b"PK\x03\x04"
    blob[100:104] = b"\x7fELF"
    blob[512 + 0x1FE : 512 + 0x200] = b"\x55\xAA"

    hits = detect_containers(bytes(blob))

    assert hits["zip"] == [16]
    assert hits["elf"] == [100]
    assert hits["fat_boot_sector"] == [512]


def test_classify_type_0x01_samples() -> None:
    if not GUPDATE_GCD.exists():
        pytest.skip("samples/GUPDATE.GCD not present — local-only tests")

    data = GUPDATE_GCD.read_bytes()
    offset = 0x18F81F
    payload_start = offset + 9
    payload_size = 2_447_711
    payload = data[payload_start : payload_start + payload_size]

    result = classify_type_0x01(payload, offset)

    assert "type" in result
    assert "confidence" in result
    assert "details" in result
