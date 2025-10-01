"""RevOps analytics toolkit."""

from importlib import resources
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PACKAGE_ROOT.parent.parent / "data"

__all__ = ["PACKAGE_ROOT", "DATA_ROOT"]
