from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional

import pandas as pd


@dataclass(frozen=True)
class FilterSet:
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    segments: Optional[Iterable[str]] = None
    channels: Optional[Iterable[str]] = None
    geo: Optional[Iterable[str]] = None

    def apply(self, df: pd.DataFrame, *, date_column: str = "date") -> pd.DataFrame:
        filtered = df.copy()

        if date_column in filtered.columns:
            filtered[date_column] = pd.to_datetime(filtered[date_column]).dt.date

        if self.start_date:
            filtered = filtered[filtered[date_column] >= self.start_date]
        if self.end_date:
            filtered = filtered[filtered[date_column] <= self.end_date]
        if self.segments:
            filtered = filtered[filtered["segment"].isin(self.segments)]
        if self.channels and "channel" in filtered.columns:
            filtered = filtered[filtered["channel"].isin(self.channels)]
        if self.geo and "geo" in filtered.columns:
            filtered = filtered[filtered["geo"].isin(self.geo)]

        return filtered


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


__all__ = ["FilterSet", "_safe_divide"]
