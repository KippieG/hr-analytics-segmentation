"""Unit tests voor DataQualityValidator."""

import pandas as pd
import pytest

from src.validation.data_quality import DataQualityValidator, ValidationReport, ValidationResult


@pytest.fixture
def validator() -> DataQualityValidator:
    return DataQualityValidator()


@pytest.fixture
def valid_employers() -> pd.DataFrame:
    n = 15
    return pd.DataFrame({
        "employer_id": [f"EMP{i:03d}" for i in range(n)],
        "company_size": (["small", "medium", "large", "micro", "small"] * 3)[:n],
        "status": (["Active", "Inactive", "Prospect"] * 5)[:n],
        "last_contact_date": ["2025-01-01"] * n,
        "revenue_potential": [20000.0 + i * 1000 for i in range(n)],
    })


@pytest.fixture
def valid_interactions() -> pd.DataFrame:
    return pd.DataFrame({
        "interaction_id": [f"INT{i:04d}" for i in range(15)],
        "employer_id": [f"EMP{i:03d}" for i in range(15)],
        "interaction_date": ["2025-01-01"] * 15,
        "interaction_type": ["call", "email", "meeting", "event", "linkedin"] * 3,
    })


class TestValidationReport:

    def test_passed_when_no_errors(self):
        report = ValidationReport(dataset_name="Test", total_rows=10)
        report.results.append(ValidationResult("check", passed=True, details="OK", severity="error"))
        assert report.passed is True

    def test_failed_when_error_present(self):
        report = ValidationReport(dataset_name="Test", total_rows=10)
        report.results.append(ValidationResult("check", passed=False, details="Fout", severity="error"))
        assert report.passed is False

    def test_warnings_dont_fail_report(self):
        report = ValidationReport(dataset_name="Test", total_rows=10)
        report.results.append(ValidationResult("check", passed=False, details="Waarschuwing", severity="warning"))
        assert report.passed is True

    def test_error_count(self):
        report = ValidationReport(dataset_name="Test", total_rows=10)
        report.results.append(ValidationResult("c1", passed=False, details="x", severity="error"))
        report.results.append(ValidationResult("c2", passed=False, details="x", severity="warning"))
        assert report.error_count == 1
        assert report.warning_count == 1

    def test_summary_contains_status(self):
        report = ValidationReport(dataset_name="Employers", total_rows=100)
        assert "Employers" in report.summary()
        assert "100" in report.summary()


class TestValidateEmployers:

    def test_passes_with_valid_data(self, validator, valid_employers):
        report = validator.validate_employers(valid_employers)
        assert report.passed

    def test_fails_on_null_employer_id(self, validator, valid_employers):
        valid_employers.loc[0, "employer_id"] = None
        report = validator.validate_employers(valid_employers)
        assert not report.passed

    def test_fails_on_duplicate_employer_id(self, validator, valid_employers):
        valid_employers.loc[1, "employer_id"] = valid_employers.loc[0, "employer_id"]
        report = validator.validate_employers(valid_employers)
        assert not report.passed

    def test_fails_on_invalid_company_size(self, validator, valid_employers):
        valid_employers.loc[0, "company_size"] = "giant"
        report = validator.validate_employers(valid_employers)
        assert not report.passed

    def test_fails_on_invalid_status(self, validator, valid_employers):
        valid_employers.loc[0, "status"] = "Unknown"
        report = validator.validate_employers(valid_employers)
        assert not report.passed

    def test_fails_on_future_date(self, validator, valid_employers):
        valid_employers.loc[0, "last_contact_date"] = "2099-01-01"
        report = validator.validate_employers(valid_employers)
        assert not report.passed

    def test_warning_on_missing_last_contact_date(self, validator, valid_employers):
        valid_employers.loc[0, "last_contact_date"] = None
        report = validator.validate_employers(valid_employers)
        assert report.warning_count >= 1

    def test_warning_on_negative_revenue(self, validator, valid_employers):
        valid_employers.loc[0, "revenue_potential"] = -100.0
        report = validator.validate_employers(valid_employers)
        assert report.warning_count >= 1

    def test_fails_on_too_few_rows(self, validator):
        df = pd.DataFrame({
            "employer_id": ["EMP001"],
            "company_size": ["small"],
            "status": ["Active"],
            "last_contact_date": ["2025-01-01"],
            "revenue_potential": [20000.0],
        })
        report = validator.validate_employers(df)
        assert not report.passed

    def test_handles_missing_optional_column(self, validator, valid_employers):
        df = valid_employers.drop(columns=["last_contact_date"])
        report = validator.validate_employers(df)
        assert isinstance(report, ValidationReport)

    def test_value_set_check_missing_column(self, validator):
        """Dekt de branch in _check_value_set wanneer de kolom ontbreekt."""
        df = pd.DataFrame({"employer_id": [f"EMP{i}" for i in range(15)]})
        result = validator._check_value_set(df, "company_size", {"small", "medium"})
        assert not result.passed

    def test_positive_values_check_missing_column(self, validator):
        """Dekt de branch in _check_positive_values wanneer de kolom ontbreekt."""
        df = pd.DataFrame({"employer_id": ["EMP001"]})
        result = validator._check_positive_values(df, "revenue_potential")
        assert result.passed  # ontbrekende kolom = geen fout


class TestValidateInteractions:

    def test_passes_with_valid_data(self, validator, valid_interactions):
        report = validator.validate_interactions(valid_interactions)
        assert report.passed

    def test_fails_on_null_interaction_id(self, validator, valid_interactions):
        valid_interactions.loc[0, "interaction_id"] = None
        report = validator.validate_interactions(valid_interactions)
        assert not report.passed

    def test_fails_on_null_employer_id(self, validator, valid_interactions):
        valid_interactions.loc[0, "employer_id"] = None
        report = validator.validate_interactions(valid_interactions)
        assert not report.passed

    def test_fails_on_duplicate_interaction_id(self, validator, valid_interactions):
        valid_interactions.loc[1, "interaction_id"] = valid_interactions.loc[0, "interaction_id"]
        report = validator.validate_interactions(valid_interactions)
        assert not report.passed

    def test_fails_on_invalid_interaction_type(self, validator, valid_interactions):
        valid_interactions.loc[0, "interaction_type"] = "carrier_pigeon"
        report = validator.validate_interactions(valid_interactions)
        assert not report.passed

    def test_fails_on_future_interaction_date(self, validator, valid_interactions):
        valid_interactions.loc[0, "interaction_date"] = "2099-12-31"
        report = validator.validate_interactions(valid_interactions)
        assert not report.passed
