"""
Unit tests voor de segmentatielogica.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.transformation.segmentation import EmployerSegmentation, SEGMENT_DEFINITIONS


@pytest.fixture
def sample_employers() -> pd.DataFrame:
    """Minimale testdataset met bekende eigenschappen."""
    n = 100
    rng = np.random.default_rng(42)

    return pd.DataFrame({
        "employer_id": [f"EMP{i:05d}" for i in range(1, n + 1)],
        "last_contact_date": [
            (datetime.now() - timedelta(days=int(d))).strftime("%Y-%m-%d")
            for d in rng.integers(1, 700, n)
        ],
        "frequency_12m": rng.integers(0, 20, n),
        "revenue_potential": rng.uniform(5_000, 200_000, n).round(2),
        "company_size": rng.choice(["micro", "small", "medium", "large"], n),
        "sector": rng.choice(["tech", "healthcare", "retail"], n),
        "status": rng.choice(["Active", "Inactive", "Prospect"], n),
    })


class TestEmployerSegmentation:

    def test_output_has_segment_columns(self, sample_employers):
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(sample_employers)

        required_columns = ["segment_name", "segment_id", "rfm_score", "priority_score"]
        for col in required_columns:
            assert col in result.columns, f"Verwachte kolom ontbreekt: {col}"

    def test_all_rows_get_segment(self, sample_employers):
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(sample_employers)
        assert result["segment_name"].notna().all(), "Niet alle rijen hebben een segment"

    def test_segment_names_valid(self, sample_employers):
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(sample_employers)
        valid_names = {s.name for s in SEGMENT_DEFINITIONS.values()}
        assert set(result["segment_name"].unique()).issubset(valid_names)

    def test_priority_score_range(self, sample_employers):
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(sample_employers)
        assert result["priority_score"].between(0, 100).all(), \
            "Prioriteitsscore buiten [0, 100] bereik"

    def test_rfm_score_range(self, sample_employers):
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(sample_employers)
        assert result["rfm_score"].between(0, 1).all(), \
            "RFM-score buiten [0, 1] bereik"

    def test_row_count_preserved(self, sample_employers):
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(sample_employers)
        assert len(result) == len(sample_employers), \
            "Aantal rijen is veranderd na segmentatie"

    def test_segment_profiles(self, sample_employers):
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(sample_employers)
        profiles = seg.get_segment_profiles(result)

        assert len(profiles) <= 4, "Meer segmenten dan verwacht"
        assert "count" in profiles.columns
        assert "avg_priority_score" in profiles.columns
        assert profiles["count"].sum() == len(sample_employers)

    def test_deterministic_output(self, sample_employers):
        """Zelfde input → zelfde output (reproduceerbaarheid)."""
        seg1 = EmployerSegmentation(n_segments=4, random_state=42)
        seg2 = EmployerSegmentation(n_segments=4, random_state=42)
        r1 = seg1.fit_transform(sample_employers.copy())
        r2 = seg2.fit_transform(sample_employers.copy())
        pd.testing.assert_series_equal(r1["segment_name"], r2["segment_name"])

    def test_high_recency_gets_high_churn_risk(self, sample_employers):
        """Werkgevers met lang geen contact hebben hogere prioriteitsscore."""
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(sample_employers)

        high_recency = result.nlargest(10, "recency_days")["priority_score"].mean()
        low_recency = result.nsmallest(10, "recency_days")["priority_score"].mean()
        assert high_recency > low_recency, \
            "Werkgevers met meer dagen geen contact zouden hogere prioriteit moeten hebben"
