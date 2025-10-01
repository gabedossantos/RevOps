from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

import pandas as pd

from .config import DataPaths, DEFAULT_DATA_PATHS


@lru_cache(maxsize=1)
def _resolve_paths(paths: Optional[DataPaths] = None) -> DataPaths:
    return paths or DEFAULT_DATA_PATHS


def _load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Expected data file not found: {path}")
    return pd.read_csv(path)


@lru_cache(maxsize=4)
def get_marketing_df(paths: Optional[DataPaths] = None) -> pd.DataFrame:
    resolved = _resolve_paths(paths)
    return _load_csv(resolved.marketing)


@lru_cache(maxsize=4)
def get_pipeline_df(paths: Optional[DataPaths] = None) -> pd.DataFrame:
    resolved = _resolve_paths(paths)
    return _load_csv(resolved.pipeline)


@lru_cache(maxsize=4)
def get_revenue_df(paths: Optional[DataPaths] = None) -> pd.DataFrame:
    resolved = _resolve_paths(paths)
    return _load_csv(resolved.revenue)


@lru_cache(maxsize=4)
def get_benchmarks_df(paths: Optional[DataPaths] = None) -> pd.DataFrame:
    resolved = _resolve_paths(paths)
    return _load_csv(resolved.benchmarks)


def clear_caches() -> None:
    """Clear all cached loaders (useful for tests)."""

    get_marketing_df.cache_clear()  # type: ignore[attr-defined]
    get_pipeline_df.cache_clear()  # type: ignore[attr-defined]
    get_revenue_df.cache_clear()  # type: ignore[attr-defined]
    get_benchmarks_df.cache_clear()  # type: ignore[attr-defined]
    _resolve_paths.cache_clear()


__all__ = [
    "DataPaths",
    "DEFAULT_DATA_PATHS",
    "get_marketing_df",
    "get_pipeline_df",
    "get_revenue_df",
    "get_benchmarks_df",
    "clear_caches",
]
