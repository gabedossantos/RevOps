from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataPaths:
    marketing: Path
    pipeline: Path
    revenue: Path
    benchmarks: Path


DEFAULT_DATA_PATHS = DataPaths(
    marketing=Path(__file__).resolve().parent.parent.parent / "marketing_channels.csv",
    pipeline=Path(__file__).resolve().parent.parent.parent / "pipeline_deals.csv",
    revenue=Path(__file__).resolve().parent.parent.parent / "revenue_customers.csv",
    benchmarks=Path(__file__).resolve().parent.parent.parent / "benchmarks.csv",
)
