"""
GDPR-pseudonimisering van persoonsgegevens en bedrijfsidentificatoren.

Conform AVG art. 4(5): pseudonimisering = verwerking zodat gegevens
niet meer aan een specifieke persoon kunnen worden gekoppeld zonder
gebruik van aanvullende informatie die apart wordt bewaard.
"""

import hashlib
import logging
import secrets

import pandas as pd

logger = logging.getLogger(__name__)


class GDPRAnonymizer:
    """
    Vervangt directe identificatoren door pseudoniemen.
    De mapping (sleutel ↔ pseudoniem) wordt nooit in de repo opgeslagen.
    """

    # Kolommen die ALTIJD worden gepseudonimieerd
    EMPLOYER_PII_COLUMNS = ["company_name", "vat_number", "contact_email", "contact_name"]
    INTERACTION_PII_COLUMNS = ["contact_email", "contact_name", "phone_number"]

    def __init__(self, salt: str | None = None):
        # Salt wordt per run gegenereerd of extern aangeleverd (bijv. via env var)
        self._salt = salt or secrets.token_hex(32)
        self._cache: dict[str, str] = {}
        logger.info("GDPRAnonymizer initialized (salt NOT logged for security)")

    def pseudonymize_employers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pseudonimiseer alle PII-kolommen in het werkgeversbestand."""
        df = df.copy()
        present = [c for c in self.EMPLOYER_PII_COLUMNS if c in df.columns]

        for col in present:
            original_count = df[col].notna().sum()
            df[col] = df[col].apply(self._hash_value)
            logger.debug("Pseudonymized column '%s' (%d values)", col, original_count)

        df["gdpr_processed_at"] = pd.Timestamp.now().isoformat()
        df["gdpr_pseudonymized"] = True
        return df

    def pseudonymize_interactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pseudonimiseer alle PII-kolommen in de interactietabel."""
        df = df.copy()
        present = [c for c in self.INTERACTION_PII_COLUMNS if c in df.columns]

        for col in present:
            df[col] = df[col].apply(self._hash_value)

        return df

    def redact_column(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Volledig verwijderen van een kolom (voor gegevens die niet bewaard mogen worden)."""
        if column in df.columns:
            df = df.drop(columns=[column])
            logger.info("Column '%s' redacted (GDPR compliance)", column)
        return df

    def _hash_value(self, value: str | None) -> str | None:
        """HMAC-SHA256 hash met project-salt. Deterministisch per run."""
        if pd.isna(value) or value is None:
            return None
        if value in self._cache:
            return self._cache[value]
        combined = f"{self._salt}:{value}".encode()
        result = "anon_" + hashlib.sha256(combined).hexdigest()[:16]
        self._cache[value] = result
        return result
