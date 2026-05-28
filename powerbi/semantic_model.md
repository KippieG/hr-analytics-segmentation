# Semantisch Model — HR Analytics

> Documentatie van het datamodel dat de basis vormt voor alle Power BI rapporten.
> Dit is de "single source of truth" voor businessdefinities.

---

## Modeloverzicht (Ster-schema)

```
                    ┌─────────────┐
                    │  DimDate    │
                    │  (Kalender) │
                    └──────┬──────┘
                           │
┌──────────────┐    ┌──────▼──────┐    ┌──────────────┐
│ DimConsultant│────│ FactInteract│────│  DimEmployer │
│              │    │    ions     │    │              │
└──────────────┘    └──────┬──────┘    └──────┬───────┘
                           │                  │
                    ┌──────▼──────┐    ┌──────▼───────┐
                    │ DimOutcome  │    │ DimSegment   │
                    │             │    │              │
                    └─────────────┘    └──────────────┘
```

---

## Tabeldefinities

### FactInteractions (Feitentabel)

| Kolom | Type | Beschrijving | Voorbeeld |
|---|---|---|---|
| `interaction_id` | Text | Primaire sleutel | INT0000001 |
| `employer_id` | Text | FK → DimEmployer | EMP00042 |
| `consultant_id` | Text | FK → DimConsultant | CONS003 |
| `interaction_date` | Date | FK → DimDate | 2026-03-15 |
| `interaction_type` | Text | FK → DimOutcome | meeting |
| `outcome` | Text | Resultaat contactmoment | positive |
| `follow_up_required` | Boolean | Opvolgactie nodig? | TRUE |

### DimEmployer (Werkgeverdimensie)

| Kolom | Type | Beschrijving | Voorbeeld |
|---|---|---|---|
| `employer_id` | Text | Primaire sleutel | EMP00042 |
| `sector` | Text | NACE-hoofdsector | tech |
| `company_size` | Text | Grootteklasse | medium |
| `region` | Text | Belgische provincie | West-Vlaanderen |
| `status` | Text | Relatiestatus | Active |
| `revenue_potential` | Decimal | Geschat jaarpotentieel (€) | 75.000 |
| `segment_name` | Text | RFM-segment | Champions |
| `priority_score` | Decimal | Opvolgurgentie 0–100 | 23.4 |
| `rfm_score` | Decimal | Gewogen RFM-score 0–1 | 0.847 |

### DimSegment (Segmentdimensie)

| Kolom | Type | Beschrijving |
|---|---|---|
| `segment_id` | Integer | PK |
| `segment_name` | Text | Champions / Potentials / At Risk / Lost |
| `priority` | Integer | Prioriteitsvolgorde (1 = hoogst) |
| `color_hex` | Text | Kleurcode voor rapport |
| `recommended_action` | Text | Aanbevolen actie voor consultant |

---

## Businessdefinities (Glossarium)

| Term | Definitie | Eigenaar |
|---|---|---|
| **Actieve werkgever** | Status = "Active" EN minstens 1 interactie afgelopen 12 maanden | Account Management |
| **Churnrisico** | Score ≥ 70 op Churn Risk Score measure | Data Team |
| **Interactie** | Elk gedocumenteerd contactmoment (call, email, meeting, event, LinkedIn) | Consultants |
| **Omzetpotentieel** | Geschatte jaarlijkse omzet uit plaatsingen, gebaseerd op bedrijfsgrootte × sectorcoëfficiënt | Finance |
| **Segmentatie** | RFM-gebaseerde clustering, maandelijks herberekend op de 1e van de maand | Data Team |
| **Prioriteitsscore** | Gecombineerde urgentiescore 0–100 voor opvolgvolgorde consultant | Account Management |

---

## Berekende kolommen vs. Measures

**Vuistregel:** Gebruik measures voor aggregaties, berekende kolommen voor rijattributen.

| Type | Gebruik voor | Voorbeeld |
|---|---|---|
| Berekende kolom | Statische rijattributen, filters, slicers | `segment_name`, `priority_label` |
| Measure | Aggregaties, tijdsintelligentie, ratio's | `[Churn Risk Score]`, `[MoM Groei %]` |

---

## Refreshschema

| Dataset | Frequentie | Tijdstip | Methode |
|---|---|---|---|
| Interacties | Dagelijks | 06:00 | Incrementeel (nieuwe rijen) |
| Werkgeversdata | Wekelijks | Zondag 02:00 | Volledig |
| Segmentatie | Maandelijks | 1e dag 04:00 | Volledig herberekend |
| Kalender | Jaarlijks | 1 januari | Manueel |

---

*Versie: 1.2 | Laatste update: Q2 2026 | Eigenaar: Data Analytics Team*
