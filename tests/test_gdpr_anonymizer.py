"""Unit tests voor GDPRAnonymizer."""

import pandas as pd
import pytest

from src.ingestion.gdpr_anonymizer import GDPRAnonymizer


@pytest.fixture
def anonymizer() -> GDPRAnonymizer:
    return GDPRAnonymizer(salt="test-salt-fixed")


@pytest.fixture
def employer_df() -> pd.DataFrame:
    return pd.DataFrame({
        "employer_id": ["EMP001", "EMP002"],
        "company_name": ["Bedrijf A NV", "Bedrijf B BV"],
        "vat_number": ["BE0123456789", "BE0987654321"],
        "contact_email": ["a@bedrijf.be", "b@bedrijf.be"],
        "contact_name": ["Jan Janssen", "Piet Pieters"],
        "sector": ["tech", "retail"],
    })


class TestPseudonymizeEmployers:

    def test_pii_columns_are_hashed(self, anonymizer, employer_df):
        result = anonymizer.pseudonymize_employers(employer_df)
        assert result["company_name"].str.startswith("anon_").all()
        assert result["contact_email"].str.startswith("anon_").all()
        assert result["contact_name"].str.startswith("anon_").all()

    def test_non_pii_columns_unchanged(self, anonymizer, employer_df):
        result = anonymizer.pseudonymize_employers(employer_df)
        assert list(result["employer_id"]) == ["EMP001", "EMP002"]
        assert list(result["sector"]) == ["tech", "retail"]

    def test_gdpr_flags_added(self, anonymizer, employer_df):
        result = anonymizer.pseudonymize_employers(employer_df)
        assert "gdpr_processed_at" in result.columns
        assert result["gdpr_pseudonymized"].all()

    def test_original_df_not_mutated(self, anonymizer, employer_df):
        original_name = employer_df["company_name"].iloc[0]
        anonymizer.pseudonymize_employers(employer_df)
        assert employer_df["company_name"].iloc[0] == original_name

    def test_deterministic_within_run(self, anonymizer, employer_df):
        r1 = anonymizer.pseudonymize_employers(employer_df)
        r2 = anonymizer.pseudonymize_employers(employer_df)
        pd.testing.assert_series_equal(r1["company_name"], r2["company_name"])

    def test_different_salts_produce_different_hashes(self, employer_df):
        a1 = GDPRAnonymizer(salt="salt-one")
        a2 = GDPRAnonymizer(salt="salt-two")
        r1 = a1.pseudonymize_employers(employer_df)
        r2 = a2.pseudonymize_employers(employer_df)
        assert r1["company_name"].iloc[0] != r2["company_name"].iloc[0]

    def test_missing_pii_column_does_not_crash(self, anonymizer):
        df = pd.DataFrame({"employer_id": ["EMP001"], "sector": ["tech"]})
        result = anonymizer.pseudonymize_employers(df)
        assert "employer_id" in result.columns


class TestPseudonymizeInteractions:

    def test_interaction_pii_hashed(self, anonymizer):
        df = pd.DataFrame({
            "interaction_id": ["INT001"],
            "contact_email": ["test@example.com"],
            "contact_name": ["Jan"],
        })
        result = anonymizer.pseudonymize_interactions(df)
        assert result["contact_email"].iloc[0].startswith("anon_")
        assert result["contact_name"].iloc[0].startswith("anon_")

    def test_interaction_id_unchanged(self, anonymizer):
        df = pd.DataFrame({
            "interaction_id": ["INT001"],
            "contact_email": ["test@example.com"],
        })
        result = anonymizer.pseudonymize_interactions(df)
        assert result["interaction_id"].iloc[0] == "INT001"


class TestRedactColumn:

    def test_column_is_removed(self, anonymizer):
        df = pd.DataFrame({"a": [1], "b": [2]})
        result = anonymizer.redact_column(df, "a")
        assert "a" not in result.columns
        assert "b" in result.columns

    def test_missing_column_does_not_crash(self, anonymizer):
        df = pd.DataFrame({"a": [1]})
        result = anonymizer.redact_column(df, "nonexistent")
        assert "a" in result.columns


class TestHashValue:

    def test_none_returns_none(self, anonymizer):
        assert anonymizer._hash_value(None) is None

    def test_hash_starts_with_anon(self, anonymizer):
        result = anonymizer._hash_value("test")
        assert result.startswith("anon_")

    def test_cache_hit(self, anonymizer):
        r1 = anonymizer._hash_value("cached_value")
        r2 = anonymizer._hash_value("cached_value")
        assert r1 == r2
        assert "cached_value" in anonymizer._cache
