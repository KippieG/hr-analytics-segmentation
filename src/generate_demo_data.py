"""
Synthetische datagenerator — realistische demo-data zonder echte persoonsgegevens.

Genereert:
  - employers.csv      (1000 werkgevers met bedrijfskenmerken)
  - interactions.csv   (8000+ contactmomenten over 24 maanden)

Sectoren en profielen zijn gebaseerd op de Belgische arbeidsmarkt.
Alle namen/emails zijn volledig fictief.
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Belgische context
SECTORS = {
    "tech":           0.20,
    "healthcare":     0.18,
    "manufacturing":  0.16,
    "retail":         0.14,
    "finance":        0.12,
    "construction":   0.10,
    "logistics":      0.10,
}

COMPANY_SIZES = {
    "micro":   0.35,   # 1–9 werknemers
    "small":   0.30,   # 10–49
    "medium":  0.25,   # 50–249
    "large":   0.10,   # 250+
}

REGIONS = {
    "Antwerpen": 0.25,
    "Oost-Vlaanderen": 0.18,
    "West-Vlaanderen": 0.15,
    "Vlaams-Brabant": 0.14,
    "Limburg": 0.10,
    "Brussel": 0.10,
    "Wallonië": 0.08,
}

INTERACTION_TYPES = ["call", "email", "meeting", "event", "linkedin"]
STATUSES = ["Active", "Active", "Active", "Inactive", "Prospect"]  # gewogen


def _weighted_choice(options: dict) -> str:
    keys = list(options.keys())
    weights = list(options.values())
    return random.choices(keys, weights=weights, k=1)[0]


def _revenue_potential(size: str, sector: str) -> float:
    base = {"micro": 5_000, "small": 20_000, "medium": 75_000, "large": 200_000}[size]
    multiplier = {"tech": 1.4, "healthcare": 1.2, "finance": 1.3,
                  "manufacturing": 1.1, "retail": 0.9, "construction": 1.0, "logistics": 1.0}
    noise = np.random.normal(1.0, 0.15)
    return round(base * multiplier.get(sector, 1.0) * max(noise, 0.5), 2)


def generate_employers(n: int = 1000) -> pd.DataFrame:
    """Genereer n fictieve werkgevers."""
    records = []
    for i in range(1, n + 1):
        sector = _weighted_choice(SECTORS)
        size = _weighted_choice(COMPANY_SIZES)
        founded_year = random.randint(1980, 2022)

        records.append({
            "employer_id": f"EMP{i:05d}",
            "company_name": f"Bedrijf {i} NV",          # later gepseudonimieerd
            "vat_number": f"BE0{random.randint(100_000_000, 999_999_999)}",
            "sector": sector,
            "company_size": size,
            "region": _weighted_choice(REGIONS),
            "founded_year": founded_year,
            "employee_count": {
                "micro": random.randint(1, 9),
                "small": random.randint(10, 49),
                "medium": random.randint(50, 249),
                "large": random.randint(250, 2000),
            }[size],
            "revenue_potential": _revenue_potential(size, sector),
            "status": random.choice(STATUSES),
            "contact_name": f"Contact {i}",              # later gepseudonimieerd
            "contact_email": f"contact{i}@bedrijf{i}.be",
            "acquisition_date": (
                datetime(founded_year, 1, 1)
                + timedelta(days=random.randint(0, 365))
            ).strftime("%Y-%m-%d"),
        })

    return pd.DataFrame(records)


def generate_interactions(employers: pd.DataFrame, avg_per_employer: float = 8.0) -> pd.DataFrame:
    """
    Genereer interactiehistorie.
    Champions krijgen veel contactmomenten, Lost-kandidaten weinig.
    """
    records = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    for _, employer in employers.iterrows():
        # Simuleer realistische verdeling: sommige werkgevers weinig contact
        n_interactions = max(1, int(np.random.exponential(avg_per_employer)))

        # Meer recente contacten voor actieve werkgevers
        if employer["status"] == "Active":
            recency_bias = 0.7  # 70% kans op contact in laatste 180 dagen
        elif employer["status"] == "Prospect":
            recency_bias = 0.4
        else:
            recency_bias = 0.1

        for _ in range(n_interactions):
            if random.random() < recency_bias:
                days_ago = random.randint(0, 180)
            else:
                days_ago = random.randint(180, 730)

            interaction_date = end_date - timedelta(days=days_ago)

            records.append({
                "interaction_id": f"INT{len(records) + 1:07d}",
                "employer_id": employer["employer_id"],
                "interaction_date": interaction_date.strftime("%Y-%m-%d"),
                "interaction_type": random.choice(INTERACTION_TYPES),
                "outcome": random.choice(["positive", "neutral", "negative", "no_response"]),
                "follow_up_required": random.choice([True, False]),
                "consultant_id": f"CONS{random.randint(1, 15):03d}",
            })

    df = pd.DataFrame(records)

    # Voeg last_contact_date toe aan werkgevers op basis van interacties
    last_contact = (
        df.groupby("employer_id")["interaction_date"]
        .max()
        .reset_index()
        .rename(columns={"interaction_date": "last_contact_date"})
    )

    return df, last_contact


def save_demo_data(output_dir: str = "data/raw") -> None:
    """Genereer en sla synthetische demo-data op."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("Generating employers...")
    employers = generate_employers(n=1000)

    print("Generating interactions...")
    interactions, last_contact = generate_interactions(employers)

    # Voeg last_contact toe aan employers
    employers = employers.merge(last_contact, on="employer_id", how="left")

    # Frequency laatste 12 maanden
    cutoff = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    freq_12m = (
        interactions[interactions["interaction_date"] >= cutoff]
        .groupby("employer_id")
        .size()
        .reset_index(name="frequency_12m")
    )
    employers = employers.merge(freq_12m, on="employer_id", how="left")
    employers["frequency_12m"] = employers["frequency_12m"].fillna(0).astype(int)

    employers.to_csv(output_path / "employers.csv", index=False)
    interactions.to_csv(output_path / "interactions.csv", index=False)

    print(f"✅ Generated {len(employers)} employers and {len(interactions)} interactions")
    print(f"   Saved to: {output_path.resolve()}")


if __name__ == "__main__":
    save_demo_data()
