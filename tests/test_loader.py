"""Unit tests voor DataLoader en schema_definitions."""

import pandas as pd
import pytest
from pathlib import Path

from src.ingestion.loader import DataLoader
from src.ingestion.schema_definitions import employer_schema, interaction_schema, VALID_SECTORS, VALID_SIZES


@pytest.fixture
def tmp_dirs(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    return raw_dir, processed_dir


@pytest.fixture
def sample_employers_csv(tmp_dirs) -> Path:
    raw_dir, _ = tmp_dirs
    df = pd.DataFrame({
        "employer_id": [f"EMP{i:03d}" for i in range(20)],
        "company_name": [f"Bedrijf {i}" for i in range(20)],
        "company_size": ["small"] * 20,
        "status": ["Active"] * 20,
        "sector": ["tech"] * 20,
        "revenue_potential": [20000.0] * 20,
        "last_contact_date": ["2025-01-01"] * 20,
        "frequency_12m": [5] * 20,
        "contact_name": [f"Naam {i}" for i in range(20)],
        "contact_email": [f"email{i}@test.be" for i in range(20)],
        "vat_number": [f"BE{i:010d}" for i in range(20)],
    })
    path = raw_dir / "employers.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def sample_interactions_csv(tmp_dirs) -> Path:
    raw_dir, _ = tmp_dirs
    df = pd.DataFrame({
        "interaction_id": [f"INT{i:04d}" for i in range(30)],
        "employer_id": [f"EMP{i % 20:03d}" for i in range(30)],
        "interaction_date": ["2025-03-01"] * 30,
        "interaction_type": ["call"] * 30,
        "outcome": ["positive"] * 30,
        "follow_up_required": [True] * 30,
        "consultant_id": ["CONS001"] * 30,
    })
    path = raw_dir / "interactions.csv"
    df.to_csv(path, index=False)
    return path


class TestSchemaDefinitions:

    def test_valid_sectors_not_empty(self):
        assert len(VALID_SECTORS) > 0

    def test_valid_sizes_contains_expected(self):
        assert {"micro", "small", "medium", "large"} == VALID_SIZES

    def test_employer_schema_is_defined(self):
        assert employer_schema is not None

    def test_interaction_schema_is_defined(self):
        assert interaction_schema is not None


class TestDataLoader:

    def test_load_employers_returns_dataframe(self, tmp_dirs, sample_employers_csv):
        raw_dir, processed_dir = tmp_dirs
        loader = DataLoader(raw_dir, processed_dir)
        df = loader.load_employers()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 20

    def test_load_employers_pseudonymizes_pii(self, tmp_dirs, sample_employers_csv):
        raw_dir, processed_dir = tmp_dirs
        loader = DataLoader(raw_dir, processed_dir)
        df = loader.load_employers()
        assert df["company_name"].str.startswith("anon_").all()
        assert df["contact_email"].str.startswith("anon_").all()

    def test_load_interactions_returns_dataframe(self, tmp_dirs, sample_interactions_csv):
        raw_dir, processed_dir = tmp_dirs
        loader = DataLoader(raw_dir, processed_dir)
        df = loader.load_interactions()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 30

    def test_file_not_found_raises(self, tmp_dirs):
        raw_dir, processed_dir = tmp_dirs
        loader = DataLoader(raw_dir, processed_dir)
        with pytest.raises(FileNotFoundError):
            loader.load_employers("nonexistent.csv")

    def test_unsupported_format_raises(self, tmp_dirs):
        raw_dir, processed_dir = tmp_dirs
        (raw_dir / "data.txt").write_text("test")
        loader = DataLoader(raw_dir, processed_dir)
        with pytest.raises(ValueError):
            loader._load_file(raw_dir / "data.txt")

    def test_save_ingestion_report(self, tmp_dirs, sample_employers_csv, sample_interactions_csv):
        raw_dir, processed_dir = tmp_dirs
        loader = DataLoader(raw_dir, processed_dir)
        loader.load_employers()
        loader.load_interactions()
        report_path = loader.save_ingestion_report()
        assert report_path.exists()
        report_df = pd.read_csv(report_path)
        assert len(report_df) == 2
        assert "filename" in report_df.columns
        assert "checksum" in report_df.columns

    def test_chunked_load(self, tmp_dirs, sample_employers_csv):
        raw_dir, processed_dir = tmp_dirs
        loader = DataLoader(raw_dir, processed_dir)
        df = loader.load_chunked("employers.csv", chunk_size=7)
        assert len(df) == 20

    def test_basic_clean_normalizes_columns(self, tmp_dirs):
        raw_dir, processed_dir = tmp_dirs
        loader = DataLoader(raw_dir, processed_dir)
        df = pd.DataFrame({"Column One": [1], "Column Two": [2]})
        cleaned = loader._basic_clean(df)
        assert "column_one" in cleaned.columns
        assert "column_two" in cleaned.columns

    def test_file_checksum_is_deterministic(self, tmp_dirs, sample_employers_csv):
        raw_dir, processed_dir = tmp_dirs
        h1 = DataLoader._file_checksum(sample_employers_csv)
        h2 = DataLoader._file_checksum(sample_employers_csv)
        assert h1 == h2
        assert len(h1) == 32  # MD5 hex digest


class TestSegmentationWithoutOptionalColumns:
    """Dekt de RFM-branches waarbij frequency_12m en revenue_potential ontbreken."""

    def test_fit_transform_without_frequency_column(self):
        from datetime import datetime, timedelta
        import numpy as np
        from src.transformation.segmentation import EmployerSegmentation

        rng = np.random.default_rng(0)
        n = 60
        df = pd.DataFrame({
            "employer_id": [f"EMP{i:05d}" for i in range(n)],
            "last_contact_date": [
                (datetime.now() - timedelta(days=int(d))).strftime("%Y-%m-%d")
                for d in rng.integers(1, 500, n)
            ],
            "company_size": rng.choice(["small", "medium", "large"], n),
            "sector": rng.choice(["tech", "retail"], n),
            "total_interactions": rng.integers(1, 15, n),
        })
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(df)
        assert "frequency_12m" in result.columns
        assert result["segment_name"].notna().all()

    def test_fit_transform_without_revenue_column(self):
        from datetime import datetime, timedelta
        import numpy as np
        from src.transformation.segmentation import EmployerSegmentation

        rng = np.random.default_rng(1)
        n = 60
        df = pd.DataFrame({
            "employer_id": [f"EMP{i:05d}" for i in range(n)],
            "last_contact_date": [
                (datetime.now() - timedelta(days=int(d))).strftime("%Y-%m-%d")
                for d in rng.integers(1, 500, n)
            ],
            "frequency_12m": rng.integers(1, 10, n),
            "company_size": rng.choice(["small", "medium"], n),
            "sector": rng.choice(["tech", "healthcare"], n),
        })
        seg = EmployerSegmentation(n_segments=4)
        result = seg.fit_transform(df)
        assert "revenue_potential" in result.columns
        assert result["segment_name"].notna().all()
