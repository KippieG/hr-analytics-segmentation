"""Segmentprofielen genereren voor management rapportage."""
import pandas as pd


class SegmentProfiler:
    def generate(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.groupby("segment_name").agg(
            count=("employer_id", "count"),
            avg_rfm_score=("rfm_score", "mean"),
            avg_priority_score=("priority_score", "mean"),
            avg_revenue_potential=("revenue_potential", "mean"),
        ).round(2).reset_index().sort_values("avg_rfm_score", ascending=False)
