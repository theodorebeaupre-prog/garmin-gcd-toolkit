"""Record walker for Garmin .GCD files.

Phase 2 only confirms the 9-byte record header and a partial length model:
- types 0x4C and 0x67 use FieldB as a LE uint16 payload length
- types 0xDC and 0x64 do not yet have a confirmed inline length encoding

For unknown-length record types, we recover by scanning forward for the next
top-level marker. This is intentionally conservative and may be refined in
Phase 3 as more type-specific structure becomes known.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterator

from gcd_tool.parser import GCD_MARKER, GCD_RECORD_HEADER

KNOWN_LENGTH_TYPES = {0x4C, 0x67}
RECORD_HEADER_SIZE = 9


@dataclass(frozen=True)
class GCDRecord:
    offset: int
    type: int
    field_a: bytes
    field_b: bytes
    payload_size: int


def _find_next_marker(handle: BinaryIO, start_offset: int) -> int | None:
    """Scan forward for the next top-level record marker."""
    handle.seek(0, 2)
    file_size = handle.tell()
    if start_offset >= file_size:
        return None

    handle.seek(start_offset)
    window = handle.read(file_size - start_offset)
    rel = window.find(GCD_MARKER)
    if rel == -1:
        return None
    return start_offset + rel


def _read_record_header(handle: BinaryIO, offset: int) -> tuple[int, bytes, bytes] | None:
    """Read and parse a 9-byte record header at the given offset."""
    handle.seek(0, 2)
    file_size = handle.tell()
    if offset + RECORD_HEADER_SIZE > file_size:
        return None

    handle.seek(offset)
    blob = handle.read(RECORD_HEADER_SIZE)
    try:
        parsed = GCD_RECORD_HEADER.parse(blob)
    except Exception:
        return None

    return int(parsed.type), bytes(parsed.field_a), bytes(parsed.field_b)


def iter_records(path: str | Path, start_offset: int = 0x1000) -> Iterator[GCDRecord]:
    """Yield GCD records from a file, recovering sync when possible."""
    file_path = Path(path)

    with file_path.open("rb") as handle:
        handle.seek(0, 2)
        file_size = handle.tell()

        current = start_offset
        while current < file_size:
            header = _read_record_header(handle, current)
            if header is None:
                next_marker = _find_next_marker(handle, current + 1)
                if next_marker is None:
                    break
                current = next_marker
                continue

            record_type, field_a, field_b = header

            if record_type in KNOWN_LENGTH_TYPES:
                payload_size = int.from_bytes(field_b, "little")
                next_offset = current + RECORD_HEADER_SIZE + payload_size
            else:
                # Length encoding for these types is still unknown in Phase 2.
                next_marker = _find_next_marker(handle, current + RECORD_HEADER_SIZE)
                if next_marker is None:
                    next_offset = file_size
                else:
                    next_offset = next_marker
                payload_size = next_offset - (current + RECORD_HEADER_SIZE)

            if payload_size < 0:
                next_marker = _find_next_marker(handle, current + 1)
                if next_marker is None:
                    break
                current = next_marker
                continue

            yield GCDRecord(
                offset=current,
                type=record_type,
                field_a=field_a,
                field_b=field_b,
                payload_size=payload_size,
            )

            if record_type == 0x67:
                break

            if next_offset <= current:
                next_marker = _find_next_marker(handle, current + 1)
                if next_marker is None:
                    break
                current = next_marker
                continue

            current = next_offset


def walk_file(path: str | Path, start_offset: int = 0x1000) -> list[GCDRecord]:
    """Return all walked records as a list."""
    return list(iter_records(path, start_offset=start_offset))
