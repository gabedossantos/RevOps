from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from revops import data


@pytest.fixture(scope="session")
def marketing_df():
    return data.get_marketing_df().copy()


@pytest.fixture(scope="session")
def pipeline_df():
    return data.get_pipeline_df().copy()


@pytest.fixture(scope="session")
def revenue_df():
    return data.get_revenue_df().copy()


@pytest.fixture(autouse=True)
def _clear_cache():
    yield
    data.clear_caches()
