"""
Ingestion layer — brondata inladen, valideren en loggen.
Houdt rekening met GDPR, schaalbaarheid en datastandaarden.
"""

import logging
import hashlib
from pathlib import Path
from datetime import datetime

import pandas as pd
import pandera as pa

from src.ingestion.schema_definitions import employer_schema, interaction_schema
from src.ingestion.gdpr_anonymizer import GDPRAnonymizer

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Verantwoordelijk voor het inladen van bronbestanden met:
    - Schema-validatie (Pandera)
    - GDPR-pseudonimisering
    - Audit logging
    - Schaalbaarheid via chunked loading voor grote datasets
    """

    SUPPORTED_FORMATS = {".csv", ".parquet", ".xlsx"}

    def __init__(self, raw_data_dir: Path, processed_dir: Path):
        self.raw_dir = Path(raw_data_dir)
        self.processed_dir = Path(processed_dir)
        self.anonymizer = GDPRAnonymizer()
        self._ingestion_log: list[dict] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def load_employers(self, filename: str = "employers.csv") -> pd.DataFrame:
        """Laad en valideer werkgeversbestand."""
        path = self.raw_dir / filename
        df = self._load_file(path)

        logger.info("Validating employer schema for %s (%d rows)", filename, len(df))
        df = employer_schema.validate(df, lazy=True)

        df = self.anonymizer.pseudonymize_employers(df)
        self._log_ingestion(filename, len(df), "employers")

        return df

    def load_interactions(self, filename: str = "interactions.csv") -> pd.DataFrame:
        """Laad en valideer interactiegeschiedenis."""
        path = self.raw_dir / filename
        df = self._load_file(path)

        logger.info("Validating interaction schema for %s (%d rows)", filename, len(df))
        df = interaction_schema.validate(df, lazy=True)

        self._log_ingestion(filename, len(df), "interactions")
        return df

    def load_chunked(self, filename: str, chunk_size: int = 50_000) -> pd.DataFrame:
        """
        Chunked loader voor grote bestanden (>500k rijen).
        Vermijdt geheugenproblemen bij zware datasets.
        """
        path = self.raw_dir / filename
        chunks = []

        logger.info("Loading %s in chunks of %d", filename, chunk_size)
        for i, chunk in enumerate(pd.read_csv(path, chunksize=chunk_size)):
            chunk = self._basic_clean(chunk)
            chunks.append(chunk)
            logger.debug("Loaded chunk %d (%d rows)", i + 1, len(chunk))

        df = pd.concat(chunks, ignore_index=True)
        logger.info("Chunked load complete: %d total rows", len(df))
        return df

    def save_ingestion_report(self) -> Path:
        """Schrijf audit log naar processed map (GDPR verwerkingsregister)."""
        report_path = self.processed_dir / f"ingestion_log_{datetime.now():%Y%m%d_%H%M}.csv"
        pd.DataFrame(self._ingestion_log).to_csv(report_path, index=False)
        logger.info("Ingestion report saved to %s", report_path)
        return report_path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_file(self, path: Path) -> pd.DataFrame:
        if not path.exists():
            raise FileNotFoundError(f"Bronbestand niet gevonden: {path}")

        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Niet-ondersteund formaat: {suffix}")

        loaders = {
            ".csv": pd.read_csv,
            ".parquet": pd.read_parquet,
            ".xlsx": pd.read_excel,
        }
        df = loaders[suffix](path)
        logger.info("Loaded %s — %d rows, %d columns", path.name, len(df), len(df.columns))
        return df

    def _basic_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Minimale cleaning die altijd veilig is op ruwe data."""
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        df = df.drop_duplicates()
        return df

    def _log_ingestion(self, filename: str, row_count: int, data_type: str) -> None:
        self._ingestion_log.append({
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "data_type": data_type,
            "row_count": row_count,
            "checksum": self._file_checksum(self.raw_dir / filename),
        })

    @staticmethod
    def _file_checksum(path: Path) -> str:
        """MD5 checksum voor data-integriteitscontrole."""
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
