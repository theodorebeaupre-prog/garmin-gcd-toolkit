"""Compatibility wrapper for local execution.

This keeps `python -m gcd_tool.cli` working even if the editable install path
is not injected correctly by the local virtualenv.
"""

from src.gcd_tool import __version__

__all__ = ["__version__"]
