"""
Pipeline orchestrator — voert de volledige analytics pipeline uit in volgorde.

Gebruik:
    python -m src.main
    python -m src.main --env staging
    python -m src.main --skip-validation
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.analysis.segment_profiles import SegmentProfiler
from src.ingestion.loader import DataLoader
from src.transformation.segmentation import EmployerSegmentation
from src.validation.data_quality import DataQualityValidator

# Logs map aanmaken voor logging opstart
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/pipeline_{datetime.now():%Y%m%d_%H%M}.log"),
    ],
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HR Analytics Segmentation Pipeline")
    parser.add_argument("--env", choices=["dev", "staging", "prod"], default="dev")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--n-segments", type=int, default=4)
    return parser.parse_args()


def run_pipeline(args: argparse.Namespace) -> None:
    logger.info("=" * 60)
    logger.info("HR Analytics Pipeline gestart | env=%s", args.env)
    logger.info("=" * 60)

    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # STAP 1: Inladen
    # ------------------------------------------------------------------
    logger.info("[1/4] Data inladen...")
    loader = DataLoader(raw_dir, processed_dir)
    employers = loader.load_employers()
    interactions = loader.load_interactions()

    # ------------------------------------------------------------------
    # STAP 2: Validatie
    # ------------------------------------------------------------------
    if not args.skip_validation:
        logger.info("[2/4] Datakwaliteit valideren...")
        validator = DataQualityValidator()
        emp_report = validator.validate_employers(employers)
        int_report = validator.validate_interactions(interactions)

        if not emp_report.passed:
            logger.error("Employers validatie MISLUKT — pipeline gestopt.")
            logger.error("Fouten: %d | Waarschuwingen: %d", emp_report.error_count, emp_report.warning_count)
            sys.exit(1)

        if not int_report.passed:
            logger.warning("Interactions validatie heeft waarschuwingen — pipeline gaat door.")
    else:
        logger.warning("[2/4] Validatie overgeslagen (--skip-validation)")

    # ------------------------------------------------------------------
    # STAP 3: Segmentatie
    # ------------------------------------------------------------------
    logger.info("[3/4] Segmentatie uitvoeren (%d segmenten)...", args.n_segments)
    segmenter = EmployerSegmentation(n_segments=args.n_segments)
    employers_segmented = segmenter.fit_transform(employers)

    output_path = processed_dir / f"employers_segmented_{datetime.now():%Y%m%d}.csv"
    employers_segmented.to_csv(output_path, index=False)
    logger.info("Gesegmenteerde data opgeslagen: %s", output_path)

    # ------------------------------------------------------------------
    # STAP 4: Profiling & rapport
    # ------------------------------------------------------------------
    logger.info("[4/4] Segmentprofielen genereren...")
    profiler = SegmentProfiler()
    profiles = profiler.generate(employers_segmented)

    profiles_path = processed_dir / "segment_profiles.csv"
    profiles.to_csv(profiles_path, index=False)

    logger.info("=" * 60)
    logger.info("Pipeline succesvol afgerond")
    logger.info("Resultaten:\n%s", profiles.to_string(index=False))
    logger.info("=" * 60)

    loader.save_ingestion_report()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args)
