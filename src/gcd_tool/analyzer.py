"""Heuristic analyzers for Garmin .GCD record payloads."""

from __future__ import annotations

from collections import Counter
import math
from pathlib import Path
from typing import Any

from gcd_tool.walker import walk_file


def calculate_entropy(data: bytes) -> float:
    """Return Shannon entropy in bits per byte."""
    if not data:
        return 0.0

    counts = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return entropy


def _shannon_entropy(data: bytes) -> float:
    return calculate_entropy(data)


def is_arm_thumb(data: bytes) -> float:
    """Return a confidence score that the input resembles ARM Thumb code."""
    if len(data) < 2:
        return 0.0

    score = 0.0
    halfwords = [int.from_bytes(data[i : i + 2], "little") for i in range(0, len(data) - 1, 2)]
    total_halfwords = max(len(halfwords), 1)

    bx_lr_count = sum(1 for value in halfwords if value in {0x4770, 0x4778, 0x4770})
    score += min(0.30, bx_lr_count / total_halfwords * 8.0)

    thumb2_count = sum(1 for value in halfwords if 0xF000 <= value <= 0xFFFF)
    score += min(0.25, thumb2_count / total_halfwords * 0.75)

    push_count = sum(1 for value in halfwords if 0xB400 <= value <= 0xB5FF)
    score += min(0.20, push_count / total_halfwords * 4.0)

    stack_adj_count = sum(1 for value in halfwords if 0xB000 <= value <= 0xB0FF)
    score += min(0.10, stack_adj_count / total_halfwords * 3.0)

    entropy = _shannon_entropy(data[: min(len(data), 4096)])
    if 4.5 <= entropy <= 7.5:
        score += 0.15

    # Repeated all-zero/all-0xff data is less likely to be code.
    if data[:256].count(0x00) > 200 or data[:256].count(0xFF) > 200:
        score *= 0.5

    return max(0.0, min(1.0, score))


def detect_containers(data: bytes) -> dict[str, list[int]]:
    """Detect common embedded container signatures."""
    hits: dict[str, list[int]] = {
        "fat_boot_sector": [],
        "zip": [],
        "elf": [],
        "garmin": [],
    }

    # FAT boot sector marker: 0x55AA at offset +0x1FE of a candidate sector.
    for base in range(0, max(len(data) - 0x1FF, 0)):
        if data[base + 0x1FE : base + 0x200] == b"\x55\xAA":
            hits["fat_boot_sector"].append(base)

    start = 0
    while True:
        idx = data.find(b"PK\x03\x04", start)
        if idx == -1:
            break
        hits["zip"].append(idx)
        start = idx + 1

    start = 0
    while True:
        idx = data.find(b"\x7fELF", start)
        if idx == -1:
            break
        hits["elf"].append(idx)
        start = idx + 1

    for marker in (b"GRMN", b"GARMIN"):
        start = 0
        while True:
            idx = data.find(marker, start)
            if idx == -1:
                break
            hits["garmin"].append(idx)
            start = idx + 1

    return {name: sorted(set(offsets)) for name, offsets in hits.items() if offsets}


def classify_type_0x01(data: bytes, offset: int) -> dict[str, Any]:
    """Classify a type 0x01 payload using lightweight heuristics."""
    container_offsets = detect_containers(data)
    thumb_score = is_arm_thumb(data[: min(len(data), 65536)])
    entropy = _shannon_entropy(data[: min(len(data), 65536)])

    if container_offsets:
        return {
            "type": "container",
            "confidence": min(1.0, 0.6 + 0.1 * len(container_offsets)),
            "details": (
                f"Embedded container signatures found near record payload at 0x{offset:x}; "
                f"entropy={entropy:.2f}, thumb_score={thumb_score:.2f}"
            ),
            "container_offsets": container_offsets,
        }

    if thumb_score >= 0.55:
        return {
            "type": "arm_thumb",
            "confidence": thumb_score,
            "details": (
                f"Thumb-like opcode density detected near record payload at 0x{offset:x}; "
                f"entropy={entropy:.2f}"
            ),
            "container_offsets": None,
        }

    if entropy >= 7.0:
        return {
            "type": "binary_data",
            "confidence": min(0.95, entropy / 8.0),
            "details": (
                f"High-entropy binary data at 0x{offset:x}; "
                f"no strong container or Thumb indicators found"
            ),
            "container_offsets": None,
        }

    return {
        "type": "unknown",
        "confidence": max(0.1, thumb_score),
        "details": (
            f"Inconclusive classification for payload at 0x{offset:x}; "
            f"entropy={entropy:.2f}, thumb_score={thumb_score:.2f}"
        ),
        "container_offsets": None,
    }


def analyze_record_type(
    gcd_path: str | Path,
    record_type: int,
    *,
    start_offset: int = 0x1000,
) -> list[dict[str, Any]]:
    """Analyze every record of the requested type in a GCD file."""
    path = Path(gcd_path)
    data = path.read_bytes()
    records = walk_file(path, start_offset=start_offset)

    analyses: list[dict[str, Any]] = []
    for record in records:
        if record.type != record_type:
            continue
        payload_start = record.offset + 9
        payload_end = payload_start + record.payload_size
        payload = data[payload_start:payload_end]
        if record_type == 0x01:
            result = classify_type_0x01(payload, record.offset)
        else:
            result = {
                "type": "unknown",
                "confidence": 0.0,
                "details": f"No specialized analyzer implemented for type 0x{record_type:02x}",
                "container_offsets": None,
            }
        result["record_offset"] = record.offset
        result["payload_size"] = record.payload_size
        analyses.append(result)

    return analyses
