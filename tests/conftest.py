"""pytest configuration and shared fixtures."""

import pytest
from pathlib import Path

SAMPLES_DIR = Path(__file__).parent.parent / "samples"
GCD_FILE = SAMPLES_DIR / "GUPDATE.GCD"


@pytest.fixture(scope="session")
def gcd_path() -> Path:
    """Path to the sample GCD file. Skips tests if file is absent (CI)."""
    if not GCD_FILE.exists():
        pytest.skip("samples/GUPDATE.GCD not present — local-only tests")
    return GCD_FILE
