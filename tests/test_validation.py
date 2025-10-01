from __future__ import annotations

import pytest

from revops.validation import (
    validate_benchmarks_df,
    validate_marketing_df,
    validate_pipeline_df,
    validate_revenue_df,
)


def test_marketing_validation(marketing_df):
    validate_marketing_df(marketing_df)


def test_pipeline_validation(pipeline_df):
    validate_pipeline_df(pipeline_df)


def test_revenue_validation(revenue_df):
    validate_revenue_df(revenue_df)


def test_benchmark_validation():
    from revops.data import get_benchmarks_df

    validate_benchmarks_df(get_benchmarks_df())
