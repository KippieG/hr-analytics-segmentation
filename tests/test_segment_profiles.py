"""Unit tests voor SegmentProfiler."""

import pandas as pd
import numpy as np
import pytest

from src.analysis.segment_profiles import SegmentProfiler
from src.transformation.segmentation import EmployerSegmentation


@pytest.fixture
def segmented_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 80
    df = pd.DataFrame({
        "employer_id": [f"EMP{i:05d}" for i in range(n)],
        "last_contact_date": pd.date_range("2024-01-01", periods=n, freq="3D").strftime("%Y-%m-%d"),
        "frequency_12m": rng.integers(0, 20, n),
        "revenue_potential": rng.uniform(5_000, 200_000, n).round(2),
        "company_size": rng.choice(["micro", "small", "medium", "large"], n),
        "sector": rng.choice(["tech", "healthcare", "retail"], n),
        "status": rng.choice(["Active", "Inactive"], n),
    })
    seg = EmployerSegmentation(n_segments=4, random_state=42)
    return seg.fit_transform(df)


class TestSegmentProfiler:

    def test_returns_dataframe(self, segmented_df):
        profiler = SegmentProfiler()
        result = profiler.generate(segmented_df)
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns_present(self, segmented_df):
        profiler = SegmentProfiler()
        result = profiler.generate(segmented_df)
        for col in ["segment_name", "count", "avg_rfm_score", "avg_priority_score", "avg_revenue_potential"]:
            assert col in result.columns

    def test_row_counts_sum_to_total(self, segmented_df):
        profiler = SegmentProfiler()
        result = profiler.generate(segmented_df)
        assert result["count"].sum() == len(segmented_df)

    def test_at_most_four_segments(self, segmented_df):
        profiler = SegmentProfiler()
        result = profiler.generate(segmented_df)
        assert len(result) <= 4

    def test_sorted_by_rfm_score_descending(self, segmented_df):
        profiler = SegmentProfiler()
        result = profiler.generate(segmented_df)
        scores = result["avg_rfm_score"].tolist()
        assert scores == sorted(scores, reverse=True)
