# HR Analytics — Employer Segmentation

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Power BI](https://img.shields.io/badge/Power%20BI-DAX-yellow.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-K--Means-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

End-to-end pipeline that segments an employer portfolio using **RFM scoring + K-Means clustering**, with a Power BI operational dashboard for account managers and consultants.

---

## Overview

The pipeline classifies every employer in a portfolio into one of four actionable segments:

| Segment | Description | Recommended action |
|---|---|---|
| **Champions** | Most valuable, highly active employers | Retain — proactive contact, exclusive services |
| **Potentials** | Regular contact, not yet fully leveraged | Develop — identify upsell opportunities |
| **At Risk** | Previously active, recently quieter | Reactivate — initiate personal re-contact |
| **Lost** | No recent interaction | Evaluate — win-back campaign or write off |

---

## Architecture

```
data/raw/
├── employers.csv          # CRM export: employer master data
└── interactions.csv       # Contact history

src/
├── ingestion/
│   ├── loader.py          # CSV loading + ingestion report
│   └── gdpr_anonymizer.py # PII pseudonymisation before processing
├── transformation/
│   └── segmentation.py    # RFM computation + K-Means clustering
├── validation/
│   └── data_quality.py    # Schema checks, null thresholds, outlier flags
├── analysis/
│   └── segment_profiles.py # Aggregated segment statistics
└── main.py                # Pipeline orchestrator

powerbi/
├── measures/kpi_measures.dax  # DAX measures (KPIs, churn, time intelligence)
└── semantic_model.md          # Table schema and relationships

docs/
├── analytics_roadmap.md   # Prioritised initiative roadmap (Q3 2026 → H1 2027)
└── gdpr_register.md       # Processing register and retention policy

tests/
└── test_segmentation.py
```

---

## Pipeline steps

```
[1] Load      → employers + interactions from data/raw/
[2] Validate  → schema, nulls, referential integrity
[3] Segment   → RFM scores → MinMax normalisation → K-Means (n=4)
[4] Profile   → aggregated stats per segment → data/processed/
```

---

## Getting started

**Requirements:** Python 3.11+

```bash
pip install -r requirements.txt

# Generate synthetic demo data
python -m src.generate_demo_data

# Run the full pipeline
python -m src.main

# Options
python -m src.main --env staging --n-segments 4
python -m src.main --skip-validation
```

**Run tests:**

```bash
pytest                          # all tests
pytest --cov=src --cov-report=term-missing
```

---

## DAX examples (Power BI)

**Churn Risk Score (0–100):**
```dax
[Churn Risk Score] =
VAR DaysSinceContact =
    DATEDIFF(CALCULATE(MAX(Interactions[InteractionDate])), TODAY(), DAY)
VAR FrequencyLast12M =
    CALCULATE(
        COUNTROWS(Interactions),
        DATESINPERIOD(Interactions[InteractionDate], TODAY(), -12, MONTH)
    )
VAR NormRecency    = MIN(DIVIDE(DaysSinceContact, 365), 1)
VAR NormFrequency  = 1 - MIN(DIVIDE(FrequencyLast12M, 24), 1)
RETURN
    ROUND((NormRecency * 0.6 + NormFrequency * 0.4) * 100, 0)
```

**Segment label with traffic-light indicator:**
```dax
[Segment Prioriteit Label] =
SWITCH(
    TRUE(),
    [Churn Risk Score] < 20 && [Totaal Omzetpotentieel] > 50000, "🟢 Champion",
    [Churn Risk Score] < 40,                                      "🔵 Potential",
    [Churn Risk Score] < 70,                                      "🟡 At Risk",
                                                                  "🔴 Lost"
)
```

---

## GDPR

- All PII fields are pseudonymised via `gdpr_anonymizer.py` before processing.
- No personal data is written to `data/processed/`.
- Processing register and retention schedule: `docs/gdpr_register.md`.
- Legal basis: legitimate interest (B2B employer relationship management).

---

## Roadmap

| Phase | Initiatives |
|---|---|
| Q3 2026 (done) | Segmentation pipeline, Power BI dashboard, data quality monitoring |
| Q4 2026 | Predictive churn model, CRM integration, self-service analytics portal |
| H1 2027 | NL querying, market benchmarking, anomaly detection |

Full details: [`docs/analytics_roadmap.md`](docs/analytics_roadmap.md)

---

## Dependencies

| Package | Purpose |
|---|---|
| pandas | Data manipulation |
| scikit-learn | K-Means, MinMaxScaler |
| numpy | Numerical operations |
| pytest / coverage | Testing |
| ruff / mypy | Linting and type checking |

---

## License

MIT
