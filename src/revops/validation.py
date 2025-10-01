from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd
from pydantic import BaseModel, ValidationError


class MarketingRow(BaseModel):
    date: str
    channel: str
    campaign: str
    segment: str
    geo: str
    spend: float
    impressions: int
    clicks: int
    leads: int
    MQLs: int
    SQLs: int
    opportunities: int
    closed_won: int
    CAC: float
    CPL: float
    CTR: float
    CVR_stagewise: float
    ROI: float


class PipelineRow(BaseModel):
    deal_id: str
    account: str
    segment: str
    owner: str
    stage: str
    amount: float
    created_at: str
    expected_close: str
    last_stage_change: str
    days_in_stage: int
    probability: float
    expected_value: float
    status: str
    source_channel: str


class RevenueRow(BaseModel):
    customer_id: str
    account: str
    segment: str
    plan: str
    start_date: str
    mrr: float
    new_mrr: float
    expansion_mrr: float
    contraction_mrr: float
    churned_flag: bool
    churn_date: Optional[str]
    churn_reason: Optional[str]
    arpa: float
    nrr: float


class BenchmarkRow(BaseModel):
    benchmark_id: str
    metric_type: str
    category: str
    subcategory: str
    target_value: float
    min_value: float
    max_value: float
    unit: str
    description: str


def _validate_columns(df: pd.DataFrame, model: type[BaseModel]) -> None:
    missing = set(model.model_fields) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")


def _validate_sample(df: pd.DataFrame, model: type[BaseModel]) -> None:
    if df.empty:
        raise ValueError("DataFrame is empty")
    sample = {
        key: None if pd.isna(value) else value
        for key, value in df.iloc[0].to_dict().items()
    }
    try:
        model.model_validate(sample)
    except ValidationError as exc:
        raise ValueError(f"Schema validation failed: {exc}") from exc


def validate_marketing_df(df: pd.DataFrame) -> None:
    _validate_columns(df, MarketingRow)
    _validate_sample(df, MarketingRow)


def validate_pipeline_df(df: pd.DataFrame) -> None:
    _validate_columns(df, PipelineRow)
    _validate_sample(df, PipelineRow)


def validate_revenue_df(df: pd.DataFrame) -> None:
    _validate_columns(df, RevenueRow)
    _validate_sample(df, RevenueRow)


def validate_benchmarks_df(df: pd.DataFrame) -> None:
    _validate_columns(df, BenchmarkRow)
    _validate_sample(df, BenchmarkRow)


__all__ = [
    "validate_marketing_df",
    "validate_pipeline_df",
    "validate_revenue_df",
    "validate_benchmarks_df",
]
