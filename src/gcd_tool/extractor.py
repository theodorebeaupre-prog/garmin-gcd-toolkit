"""Resource extraction helpers for Garmin .GCD payloads.

Phase 3 confirms valid embedded PNG resources and gzip-signature hits inside
record payloads. Gzip hits are exported as raw candidates even when standard
decompression fails, because their true framing is still unknown.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from gcd_tool.walker import GCDRecord, walk_file

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
GZIP_MAGIC = b"\x1f\x8b"
PNG_IEND = b"IEND"


@dataclass(frozen=True)
class ExtractedResource:
    record_offset: int
    record_type: int
    kind: str
    absolute_offset: int
    path: Path
    size: int
    detected_mime: str


@dataclass(frozen=True)
class ExtractionSummary:
    resources: list[ExtractedResource]

    @property
    def png_count(self) -> int:
        return sum(1 for resource in self.resources if resource.kind == "png")

    @property
    def gzip_count(self) -> int:
        return sum(1 for resource in self.resources if resource.kind == "gzip")


def _record_payload_bounds(record: GCDRecord) -> tuple[int, int]:
    payload_start = record.offset + 9
    payload_end = payload_start + record.payload_size
    return payload_start, payload_end


def _record_matches_type_filter(record: GCDRecord, type_filter: set[int] | None) -> bool:
    return type_filter is None or record.type in type_filter


def _build_output_path(
    output_dir: Path,
    kind: str,
    record: GCDRecord,
    index: int,
    absolute_offset: int,
    suffix: str,
) -> Path:
    target_dir = output_dir / kind
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / (
        f"record_{record.type:02x}_{record.offset:x}_{index:03d}_at_{absolute_offset:x}.{suffix}"
    )


def _detect_mime(blob: bytes) -> str:
    if not blob:
        return "application/octet-stream"
    try:
        import magic

        return str(magic.from_buffer(blob, mime=True))
    except Exception:
        return "application/octet-stream"


def _iter_png_hits(payload: bytes, payload_start: int) -> Iterable[tuple[int, bytes]]:
    pos = 0
    while True:
        idx = payload.find(PNG_MAGIC, pos)
        if idx == -1:
            break
        iend = payload.find(PNG_IEND, idx + len(PNG_MAGIC))
        if iend == -1:
            pos = idx + 1
            continue
        end = iend + 8
        chunk = payload[idx:end]
        yield payload_start + idx, chunk
        pos = idx + len(PNG_MAGIC)


def _iter_gzip_hits(payload: bytes, payload_start: int) -> Iterable[tuple[int, bytes]]:
    pos = 0
    while True:
        idx = payload.find(GZIP_MAGIC, pos)
        if idx == -1:
            break
        next_idx = payload.find(GZIP_MAGIC, idx + 2)
        if next_idx == -1:
            chunk = payload[idx:]
        else:
            chunk = payload[idx:next_idx]
        yield payload_start + idx, chunk
        pos = idx + len(GZIP_MAGIC)


def extract_resources(
    gcd_path: str | Path,
    output_dir: str | Path,
    *,
    type_filter: set[int] | None = None,
    start_offset: int = 0x1000,
) -> ExtractionSummary:
    """Extract confirmed embedded resource types from a GCD file."""
    gcd_file = Path(gcd_path)
    out_dir = Path(output_dir)
    resources: list[ExtractedResource] = []

    data = gcd_file.read_bytes()
    records = walk_file(gcd_file, start_offset=start_offset)

    for record in records:
        if not _record_matches_type_filter(record, type_filter):
            continue

        payload_start, payload_end = _record_payload_bounds(record)
        payload = data[payload_start:payload_end]

        for index, (absolute_offset, chunk) in enumerate(_iter_png_hits(payload, payload_start)):
            target = _build_output_path(out_dir, "png", record, index, absolute_offset, "png")
            target.write_bytes(chunk)
            resources.append(
                ExtractedResource(
                    record_offset=record.offset,
                    record_type=record.type,
                    kind="png",
                    absolute_offset=absolute_offset,
                    path=target,
                    size=len(chunk),
                    detected_mime=_detect_mime(chunk),
                )
            )

        for index, (absolute_offset, chunk) in enumerate(_iter_gzip_hits(payload, payload_start)):
            target = _build_output_path(out_dir, "gzip", record, index, absolute_offset, "gz")
            target.write_bytes(chunk)
            resources.append(
                ExtractedResource(
                    record_offset=record.offset,
                    record_type=record.type,
                    kind="gzip",
                    absolute_offset=absolute_offset,
                    path=target,
                    size=len(chunk),
                    detected_mime=_detect_mime(chunk),
                )
            )

    return ExtractionSummary(resources=resources)
