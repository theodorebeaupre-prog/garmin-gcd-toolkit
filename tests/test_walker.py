"""Tests for the Phase 2 GCD record walker."""

from pathlib import Path

import pytest

from gcd_tool.walker import walk_file


REMOTE_SW_GCD = Path(__file__).parent.parent / "samples" / "remotesw_090100.GCD"
GUPDATE_GCD = Path(__file__).parent.parent / "samples" / "GUPDATE.GCD"


@pytest.fixture(scope="session")
def remotesw_records() -> list:
    if not REMOTE_SW_GCD.exists():
        pytest.skip("samples/remotesw_090100.GCD not present — local-only tests")
    return walk_file(REMOTE_SW_GCD, start_offset=0x8)


def test_remotesw_record_count(remotesw_records: list) -> None:
    assert len(remotesw_records) == 4


def test_remotesw_types(remotesw_records: list) -> None:
    assert [record.type for record in remotesw_records] == [0xDC, 0x4C, 0x64, 0x67]


def test_remotesw_offsets(remotesw_records: list) -> None:
    assert [record.offset for record in remotesw_records] == [0x8, 0x6E, 0x1000, 0x9063]


def test_remotesw_payload_sizes(remotesw_records: list) -> None:
    assert [record.payload_size for record in remotesw_records] == [93, 3977, 32858, 0]


def test_remotesw_eof_type(remotesw_records: list) -> None:
    assert remotesw_records[-1].type == 0x67


def test_gupdate_starts_correctly() -> None:
    if not GUPDATE_GCD.exists():
        pytest.skip("samples/GUPDATE.GCD not present — local-only tests")
    records = walk_file(GUPDATE_GCD)
    assert records[0].offset == 0x1000
    assert records[0].type == 0x64
