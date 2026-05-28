# 🏢 HR Analytics & Employer Segmentation

> **Een end-to-end data analytics project dat laat zien hoe ruwe werkgeversdata wordt omgezet naar strategische segmentinzichten — inclusief Python datapipeline, semantisch model en Power BI DAX-measures.**

---

## 📌 Projectoverzicht

Dit project simuleert een realistisch analytics-vraagstuk voor een HR-dienstverlener:

> *"Welke werkgevers hebben het hoogste groeipotentieel, en hoe pas ik mijn dienstverlening aan per segment?"*

Het toont de volledige keten van **ruwe data → dataproduct → strategisch inzicht**, inclusief aandacht voor GDPR, datakwaliteit en schaalbaarheid.

### Waarom dit project?

| Business vraag | Analytische oplossing |
|---|---|
| Welke werkgevers groeien snelst? | RFM-segmentatie + groeicoëfficiënt |
| Hoe verdelen we onze consultants? | Segment-priority score per account |
| Waar liggen de churns? | Predictieve churn-indicator op basis van engagement |
| Hoe rapporteren we naar management? | Power BI semantic model + DAX measures |

---

## 🏗️ Architectuur

```
raw data (CSV/API)
      │
      ▼
┌─────────────────┐
│  Ingestion Layer │  ← bronvalidatie, schema checks, GDPR-pseudonimisering
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transformation  │  ← cleaning, feature engineering, segmentlogica
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Semantic Model  │  ← dimensioneel model (ster-schema), business definities
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Power BI Layer │  ← DAX measures, KPI-berekeningen, dashboard-logica
└────────┬────────┘
         │
         ▼
   Management rapport / Operationeel dashboard
```

---

## 📂 Projectstructuur

```
hr-analytics-segmentation/
│
├── data/
│   ├── raw/                    # Ruwe brondata (niet ingecheckt, zie .gitignore)
│   ├── processed/              # Getransformeerde dataset
│   └── external/               # NACE-codes, regiodata, benchmarks
│
├── src/
│   ├── ingestion/
│   │   ├── loader.py           # Inladen en valideren van bronbestanden
│   │   └── gdpr_anonymizer.py  # Pseudonimisering conform AVG/GDPR
│   ├── transformation/
│   │   ├── cleaner.py          # Data cleaning pipeline
│   │   ├── feature_engineering.py  # Segmentatievariabelen bouwen
│   │   └── segmentation.py     # RFM + K-Means segmentatie
│   ├── analysis/
│   │   ├── segment_profiles.py # Segmentkarakteristieken & statistieken
│   │   └── churn_indicator.py  # Churnscore berekening
│   └── validation/
│       ├── data_quality.py     # Great Expectations checks
│       └── schema_validator.py # Pandera schema validatie
│
├── powerbi/
│   ├── measures/
│   │   ├── kpi_measures.dax    # Kernmaatstaven (revenue, groei, churn)
│   │   ├── segmentation.dax    # Segmentlogica in DAX
│   │   └── time_intelligence.dax  # YTD, MoM, rollende gemiddelden
│   └── semantic_model.md       # Documentatie van het datamodel
│
├── tests/
│   ├── test_cleaner.py
│   ├── test_segmentation.py
│   └── test_data_quality.py
│
├── docs/
│   ├── analytics_roadmap.md    # Prioriteitenmatrix & technische haalbaarheid
│   ├── data_dictionary.md      # Businessdefinities van alle velden
│   └── gdpr_register.md        # Verwerkingsregister (demo)
│
├── .github/
│   └── workflows/
│       └── ci.yml              # Automatische tests bij elke push
│
├── notebooks/
│   └── 01_exploratory_analysis.ipynb  # EDA met visualisaties
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 🚀 Aan de slag

### Vereisten

- Python 3.11+
- Power BI Desktop (voor `.pbix` visualisatie)

### Installatie

```bash
git clone https://github.com/jouwgebruikersnaam/hr-analytics-segmentation.git
cd hr-analytics-segmentation

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Pipeline uitvoeren

```bash
# Stap 1: Data inladen & valideren
python src/ingestion/loader.py

# Stap 2: Cleaning & feature engineering
python src/transformation/cleaner.py
python src/transformation/feature_engineering.py

# Stap 3: Segmentatie uitvoeren
python src/transformation/segmentation.py

# Of alles in één keer:
python -m src.main
```

### Tests uitvoeren

```bash
pytest tests/ -v --cov=src --cov-report=html
```

---

## 📊 Segmentatielogica

De kern van dit project is een **RFM-gebaseerde segmentatie** gecombineerd met K-Means clustering:

| Dimensie | Definitie | Gewicht |
|---|---|---|
| **Recency** | Dagen sinds laatste interactie met dienstverlener | 30% |
| **Frequency** | Aantal contactmomenten afgelopen 12 maanden | 40% |
| **Monetary** | Geschatte omzetpotentieel op basis van bedrijfsgrootte | 30% |

### Segmenten

| Segment | Profiel | Prioriteit |
|---|---|---|
| 🟢 **Champions** | Hoge RFM, actief, groeiend | Top |
| 🔵 **Potentials** | Goede frequency, laag monetair | Hoog |
| 🟡 **At Risk** | Vroeger actief, nu stiller | Medium |
| 🔴 **Lost** | Geen recente interactie | Laag / reactivatie |

---

## 📐 Power BI DAX — Voorbeeldmeasures

```dax
-- Churn Risk Score (genormaliseerd 0-100)
Churn Risk Score =
VAR DaysSinceContact =
    DATEDIFF(MAX(Employers[LastContactDate]), TODAY(), DAY)
VAR FrequencyScore =
    DIVIDE(CALCULATE(COUNTROWS(Interactions)), 12)
VAR NormDays = MIN(DIVIDE(DaysSinceContact, 365), 1)
RETURN
    ROUND((NormDays * 0.6 + (1 - FrequencyScore) * 0.4) * 100, 0)
```

```dax
-- Segment Priority Index
Segment Priority Index =
SWITCH(
    TRUE(),
    [Churn Risk Score] < 20 && [Revenue Potential] > 50000, "Champion",
    [Churn Risk Score] < 40, "Potential",
    [Churn Risk Score] < 70, "At Risk",
    "Lost"
)
```

Volledige measures staan in [`powerbi/measures/`](./powerbi/measures/).

---

## 🔒 GDPR & Data Governance

- Alle persoonsgegevens worden **gepseudonimieerd** voor verwerking (`src/ingestion/gdpr_anonymizer.py`)
- Ruwe data staat **nooit** in de repository (`.gitignore` enforced)
- Verwerkingsregister gedocumenteerd in [`docs/gdpr_register.md`](./docs/gdpr_register.md)
- Data retention policy: verwerkte data maximaal 24 maanden bewaard

---

## 🗺️ Analytics Roadmap

Zie [`docs/analytics_roadmap.md`](./docs/analytics_roadmap.md) voor de volledige prioriteitenmatrix.

**Korte termijn (Q3 2026)**
- [x] Segmentatiepipeline operationeel
- [x] Power BI rapport voor account managers
- [ ] Automatische maandelijkse refresh via Fabric

**Middellange termijn (Q4 2026)**
- [ ] Predictief churnmodel (logistische regressie)
- [ ] Integratie met CRM-systeem
- [ ] Self-service analytics portaal

---

## 🛠️ Tech Stack

| Laag | Technologie |
|---|---|
| Data processing | Python (pandas, scikit-learn) |
| Data validatie | Great Expectations, Pandera |
| Visualisatie | Power BI, matplotlib, seaborn |
| DAX / Semantic model | Power BI Desktop / Fabric |
| Testing | pytest, pytest-cov |
| CI/CD | GitHub Actions |
| Versiebeheer | Git + pre-commit hooks |

---

## 📬 Contact

Vragen of feedback? Bereik me via [LinkedIn](https://linkedin.com/in/jouwprofiel) of open een GitHub Issue.

---

*Dit project is gebouwd als portfolio demonstratie. Alle data is synthetisch gegenereerd en bevat geen echte persoonsgegevens.*
