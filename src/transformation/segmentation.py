"""
Werkgeverssegmentatie via RFM-scoring + K-Means clustering.

Businesslogica:
  - Recency:   hoe recent was het laatste contactmoment?
  - Frequency: hoe vaak heeft de werkgever interactie met de dienstverlener?
  - Monetary:  wat is het geschatte omzetpotentieel?

Output: elk werkgeversrecord krijgt een segment-label + prioriteitsscore.
"""

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)


@dataclass
class SegmentDefinition:
    name: str
    color: str
    priority: int
    description: str
    action: str


SEGMENT_DEFINITIONS: dict[int, SegmentDefinition] = {
    0: SegmentDefinition(
        name="Champions",
        color="#22c55e",
        priority=1,
        description="Meest waardevolle, actieve werkgevers",
        action="Behoud — proactief contact, exclusieve diensten",
    ),
    1: SegmentDefinition(
        name="Potentials",
        color="#3b82f6",
        priority=2,
        description="Regelmatig contact, nog niet volledig benut",
        action="Ontwikkelen — upsell kansen identificeren",
    ),
    2: SegmentDefinition(
        name="At Risk",
        color="#f59e0b",
        priority=3,
        description="Vroeger actief, recent stiller geworden",
        action="Reactiveren — persoonlijk hercontact initiëren",
    ),
    3: SegmentDefinition(
        name="Lost",
        color="#ef4444",
        priority=4,
        description="Geen recente interactie meer",
        action="Evalueren — win-back campagne of afschrijven",
    ),
}


class EmployerSegmentation:
    """
    Twee-staps segmentatie:
    1. RFM-scores berekenen en normaliseren (0–1)
    2. K-Means clustering op genormaliseerde RFM-ruimte
    """

    def __init__(self, n_segments: int = 4, random_state: int = 42):
        self.n_segments = n_segments
        self.random_state = random_state
        self.scaler = MinMaxScaler()
        self.kmeans = KMeans(
            n_clusters=n_segments,
            random_state=random_state,
            n_init=20,
            max_iter=500,
        )
        self._is_fitted = False

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Bereken RFM, fit K-Means en wijs segmenten toe."""
        logger.info("Starting segmentation for %d employers", len(df))

        df = df.copy()
        df = self._compute_rfm(df)
        df = self._normalize_rfm(df)
        df = self._assign_clusters(df)
        df = self._map_segments(df)
        df = self._compute_priority_score(df)

        self._is_fitted = True
        self._log_segment_summary(df)
        return df

    def get_segment_profiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Geaggregeerde statistieken per segment — input voor management rapport."""
        if "segment_name" not in df.columns:
            raise ValueError("Roep eerst fit_transform() aan.")

        profile = df.groupby("segment_name").agg(
            count=("employer_id", "count"),
            avg_recency_days=("recency_days", "mean"),
            avg_frequency=("frequency_12m", "mean"),
            avg_revenue_potential=("revenue_potential", "mean"),
            avg_priority_score=("priority_score", "mean"),
            pct_of_total=("employer_id", lambda x: len(x) / len(df) * 100),
        ).round(1).reset_index()

        profile = profile.sort_values("avg_priority_score", ascending=False)
        return profile

    # ------------------------------------------------------------------
    # Private pipeline stappen
    # ------------------------------------------------------------------

    def _compute_rfm(self, df: pd.DataFrame) -> pd.DataFrame:
        """Bereken de drie RFM-dimensies."""
        reference_date = pd.Timestamp.now()

        df["last_contact_date"] = pd.to_datetime(df["last_contact_date"])
        df["recency_days"] = (reference_date - df["last_contact_date"]).dt.days

        # Frequency: aantal interacties afgelopen 12 maanden (uit aparte kolom of berekend)
        if "frequency_12m" not in df.columns:
            df["frequency_12m"] = df.get("total_interactions", 1)

        # Monetary: omzetpotentieel op basis van bedrijfsgrootte × sector-coëfficiënt
        if "revenue_potential" not in df.columns:
            df["revenue_potential"] = self._estimate_revenue_potential(df)

        return df

    def _estimate_revenue_potential(self, df: pd.DataFrame) -> pd.Series:
        """
        Eenvoudig potentiaalmodel: bedrijfsgrootte × sectorgewicht.
        In productie: vervangen door historisch omzetmodel of CRM-data.
        """
        size_map = {"micro": 5_000, "small": 20_000, "medium": 75_000, "large": 200_000}
        sector_multiplier = {"tech": 1.4, "healthcare": 1.2, "retail": 0.9, "manufacturing": 1.1}

        base = df.get("company_size", "small").map(size_map).fillna(20_000)
        multiplier = df.get("sector", "tech").map(sector_multiplier).fillna(1.0)
        return (base * multiplier).round(0)

    def _normalize_rfm(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliseer RFM naar [0,1] interval. Recency wordt omgekeerd (lager = beter)."""
        rfm_cols = ["recency_days", "frequency_12m", "revenue_potential"]
        scaled = self.scaler.fit_transform(df[rfm_cols])

        df["r_score"] = 1 - scaled[:, 0]  # Omgekeerd: minder dagen = hogere score
        df["f_score"] = scaled[:, 1]
        df["m_score"] = scaled[:, 2]

        # Gewogen RFM-totaalscore
        df["rfm_score"] = (
            df["r_score"] * 0.30
            + df["f_score"] * 0.40
            + df["m_score"] * 0.30
        ).round(4)

        return df

    def _assign_clusters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit K-Means op RFM-scoreruimte."""
        X = df[["r_score", "f_score", "m_score"]].values
        df["cluster"] = self.kmeans.fit_predict(X)
        return df

    def _map_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Koppel cluster-nummers aan businesssegmenten op basis van gemiddelde rfm_score.
        Dit maakt de segmentnamen stabiel ongeacht K-Means label-volgorde.
        """
        cluster_means = df.groupby("cluster")["rfm_score"].mean().sort_values(ascending=False)
        rank_to_segment = {
            cluster: segment_id
            for segment_id, cluster in enumerate(cluster_means.index)
        }

        df["segment_id"] = df["cluster"].map(rank_to_segment)
        df["segment_name"] = df["segment_id"].map(
            lambda s: SEGMENT_DEFINITIONS[s].name
        )
        df["segment_priority"] = df["segment_id"].map(
            lambda s: SEGMENT_DEFINITIONS[s].priority
        )
        df["segment_action"] = df["segment_id"].map(
            lambda s: SEGMENT_DEFINITIONS[s].action
        )
        return df

    def _compute_priority_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prioriteitsscore 0–100 voor account managers:
        hoge score = meest dringende opvolging nodig.
        """
        df["priority_score"] = (
            (1 - df["rfm_score"]) * 0.5          # Laag rfm = hogere urgentie
            + (df["recency_days"] / 365).clip(0, 1) * 0.3
            + (1 - df["f_score"]) * 0.2
        ).clip(0, 1).mul(100).round(1)

        return df

    def _log_segment_summary(self, df: pd.DataFrame) -> None:
        summary = df.groupby("segment_name").size()
        logger.info("Segmentation complete:\n%s", summary.to_string())
