"""
Data kwaliteitscontroles voor de analytics pipeline.

Filosofie: data quality checks zijn geen afterthought maar deel van de pipeline.
Elk rapport dat management bereikt is gevalideerd en gedocumenteerd.

Geïnspireerd op Great Expectations — lichtgewicht eigen implementatie
die dezelfde principes volgt zonder zware dependency.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    check_name: str
    passed: bool
    details: str
    severity: str = "error"  # "error" | "warning" | "info"
    affected_rows: int = 0


@dataclass
class ValidationReport:
    dataset_name: str
    total_rows: int
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results if r.severity == "error")

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if not r.passed and r.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for r in self.results if not r.passed and r.severity == "warning")

    def summary(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        return (
            f"{status} | {self.dataset_name} | "
            f"{self.total_rows} rows | "
            f"{self.error_count} errors | {self.warning_count} warnings"
        )


class DataQualityValidator:
    """
    Reeks kwaliteitschecks die worden uitgevoerd op elke dataset
    voor ze de transformatielaag ingaan.

    Checks zijn georganiseerd per categorie:
    - Volledigheid (null-checks)
    - Geldigheid (formaat, waardebereik)
    - Consistentie (referentiële integriteit, logische regels)
    - Tijdigheid (data niet te oud)
    """

    def validate_employers(self, df: pd.DataFrame) -> ValidationReport:
        report = ValidationReport(dataset_name="Employers", total_rows=len(df))

        report.results.extend([
            self._check_no_nulls(df, "employer_id", severity="error"),
            self._check_no_nulls(df, "company_size", severity="error"),
            self._check_no_nulls(df, "last_contact_date", severity="warning"),
            self._check_unique(df, "employer_id"),
            self._check_value_set(df, "company_size", {"micro", "small", "medium", "large"}),
            self._check_value_set(df, "status", {"Active", "Inactive", "Prospect"}),
            self._check_date_not_future(df, "last_contact_date"),
            self._check_date_not_too_old(df, "last_contact_date", max_age_days=730),
            self._check_positive_values(df, "revenue_potential", severity="warning"),
            self._check_row_count(df, min_rows=10, dataset_name="Employers"),
        ])

        self._log_report(report)
        return report

    def validate_interactions(self, df: pd.DataFrame) -> ValidationReport:
        report = ValidationReport(dataset_name="Interactions", total_rows=len(df))

        report.results.extend([
            self._check_no_nulls(df, "interaction_id", severity="error"),
            self._check_no_nulls(df, "employer_id", severity="error"),
            self._check_no_nulls(df, "interaction_date", severity="error"),
            self._check_unique(df, "interaction_id"),
            self._check_value_set(
                df, "interaction_type",
                {"call", "email", "meeting", "event", "linkedin"}
            ),
            self._check_date_not_future(df, "interaction_date"),
            self._check_referential_integrity(df, "employer_id", source_name="Interactions"),
        ])

        self._log_report(report)
        return report

    # ------------------------------------------------------------------
    # Generieke check-methoden
    # ------------------------------------------------------------------

    def _check_no_nulls(
        self, df: pd.DataFrame, column: str, severity: str = "error"
    ) -> ValidationResult:
        if column not in df.columns:
            return ValidationResult(
                check_name=f"column_exists:{column}",
                passed=False,
                details=f"Kolom '{column}' bestaat niet in de dataset.",
                severity="error",
            )
        null_count = df[column].isna().sum()
        return ValidationResult(
            check_name=f"no_nulls:{column}",
            passed=null_count == 0,
            details=f"{null_count} null-waarden gevonden in '{column}'." if null_count else "OK",
            severity=severity,
            affected_rows=int(null_count),
        )

    def _check_unique(self, df: pd.DataFrame, column: str) -> ValidationResult:
        duplicates = df[column].duplicated().sum()
        return ValidationResult(
            check_name=f"unique:{column}",
            passed=duplicates == 0,
            details=f"{duplicates} duplicaten in '{column}'." if duplicates else "OK",
            severity="error",
            affected_rows=int(duplicates),
        )

    def _check_value_set(
        self, df: pd.DataFrame, column: str, valid_values: set
    ) -> ValidationResult:
        if column not in df.columns:
            return ValidationResult(
                check_name=f"value_set:{column}", passed=False,
                details=f"Kolom '{column}' ontbreekt.", severity="error"
            )
        invalid = ~df[column].isin(valid_values)
        invalid_count = invalid.sum()
        invalid_sample = df.loc[invalid, column].unique()[:5].tolist()
        return ValidationResult(
            check_name=f"value_set:{column}",
            passed=invalid_count == 0,
            details=(
                f"{invalid_count} ongeldige waarden: {invalid_sample}" if invalid_count else "OK"
            ),
            severity="error",
            affected_rows=int(invalid_count),
        )

    def _check_date_not_future(self, df: pd.DataFrame, column: str) -> ValidationResult:
        if column not in df.columns:
            return ValidationResult(
                check_name=f"not_future:{column}", passed=True, details="Kolom niet aanwezig."
            )
        dates = pd.to_datetime(df[column], errors="coerce")
        future = (dates > pd.Timestamp.now()).sum()
        return ValidationResult(
            check_name=f"not_future:{column}",
            passed=future == 0,
            details=f"{future} datums in de toekomst." if future else "OK",
            severity="error",
            affected_rows=int(future),
        )

    def _check_date_not_too_old(
        self, df: pd.DataFrame, column: str, max_age_days: int = 730
    ) -> ValidationResult:
        if column not in df.columns:
            return ValidationResult(
                check_name=f"freshness:{column}", passed=True, details="Kolom niet aanwezig."
            )
        dates = pd.to_datetime(df[column], errors="coerce")
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=max_age_days)
        stale = (dates < cutoff).sum()
        return ValidationResult(
            check_name=f"freshness:{column}",
            passed=stale == 0,
            details=(
                f"{stale} rijen ouder dan {max_age_days} dagen (mogelijk verouderde data)."
                if stale else "OK"
            ),
            severity="warning",
            affected_rows=int(stale),
        )

    def _check_positive_values(
        self, df: pd.DataFrame, column: str, severity: str = "error"
    ) -> ValidationResult:
        if column not in df.columns:
            return ValidationResult(
                check_name=f"positive:{column}", passed=True, details="Kolom niet aanwezig."
            )
        non_positive = (df[column] <= 0).sum()
        return ValidationResult(
            check_name=f"positive:{column}",
            passed=non_positive == 0,
            details=f"{non_positive} niet-positieve waarden in '{column}'." if non_positive else "OK",
            severity=severity,
            affected_rows=int(non_positive),
        )

    def _check_row_count(
        self, df: pd.DataFrame, min_rows: int, dataset_name: str = ""
    ) -> ValidationResult:
        return ValidationResult(
            check_name=f"min_row_count:{dataset_name}",
            passed=len(df) >= min_rows,
            details=f"Slechts {len(df)} rijen (minimum: {min_rows})." if len(df) < min_rows else "OK",
            severity="error",
        )

    def _check_referential_integrity(
        self, df: pd.DataFrame, column: str, source_name: str = ""
    ) -> ValidationResult:
        """
        Placeholder: in productie vergelijkt dit met de primaire sleutels
        van de Employers-tabel om orphan records te detecteren.
        """
        return ValidationResult(
            check_name=f"ref_integrity:{column}",
            passed=True,
            details="Referentiële integriteitscheck: vereist join met Employers-tabel.",
            severity="info",
        )

    def _log_report(self, report: ValidationReport) -> None:
        logger.info(report.summary())
        for result in report.results:
            if not result.passed:
                level = logging.ERROR if result.severity == "error" else logging.WARNING
                logger.log(level, "[%s] %s: %s", result.severity.upper(), result.check_name, result.details)
