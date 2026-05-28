# Analytics Roadmap

> Prioriteitenmatrix voor de analytics werking — rekening houdend met budget, security, GDPR, schaalbaarheid en technische haalbaarheid.

---

## Hoe werkt deze roadmap?

Elk initiatief wordt beoordeeld op vier assen:

| As | Beschrijving | Schaal |
|---|---|---|
| **Business impact** | Strategische waarde voor segmentstrategie & dienstverlening | 1–5 |
| **Technische haalbaarheid** | Beschikbare data, tooling en expertise | 1–5 |
| **GDPR-risico** | Verwerkingsgrond, dataminimalisatie, bewaarbeleid | Laag / Midden / Hoog |
| **Schaalbaarheid** | Werkt dit nog bij 10× datahoeveelheid? | Ja / Deels / Nee |

---

## Q3 2026 — Foundation

### ✅ Segmentatiepipeline (Python + K-Means)
- **Impact:** 5 | **Haalbaarheid:** 5 | **GDPR:** Laag | **Schaalbaar:** Ja
- RFM-segmentatie op werkgeversportfolio operationeel
- Maandelijkse herberekening via scheduler

### ✅ Power BI Operationeel Dashboard
- **Impact:** 5 | **Haalbaarheid:** 4 | **GDPR:** Laag | **Schaalbaar:** Ja
- Dagelijkse refresh, segmentoverzicht, churnrisico per account manager
- Uitgerold naar alle consultants

### 🔄 Datakwaliteitsmonitoring
- **Impact:** 4 | **Haalbaarheid:** 4 | **GDPR:** Laag | **Schaalbaar:** Ja
- Geautomatiseerde checks bij elke data-inname
- Alert bij anomalieën (missing data > 5%, onverwachte outliers)

---

## Q4 2026 — Verdieping

### 📋 Predictief Churnmodel
- **Impact:** 5 | **Haalbaarheid:** 3 | **GDPR:** Midden | **Schaalbaar:** Deels
- Logistische regressie op historische interactiedata
- Vereist: minimum 18 maanden history + labeled churn-events
- **Risico:** beperkte trainingsdata voor kleine segmenten → fallback op rule-based score
- **GDPR:** verwerkingsgrond = gerechtvaardigd belang, impactanalyse vereist

### 📋 CRM-integratie (Salesforce / HubSpot)
- **Impact:** 4 | **Haalbaarheid:** 3 | **GDPR:** Midden | **Schaalbaar:** Ja
- Bi-directionele sync: analytics → CRM-score, CRM-activiteiten → analytics
- Vereist API-authenticatie en data mapping met IT-afdeling

### 📋 Self-Service Analytics Portaal
- **Impact:** 3 | **Haalbaarheid:** 4 | **GDPR:** Laag | **Schaalbaar:** Ja
- Power BI Embedded of Fabric voor niet-technische gebruikers
- Row-level security per consultant (ziet alleen eigen accounts)

---

## H1 2027 — Innovatie

### 💡 Natural Language Querying op data
- **Impact:** 4 | **Haalbaarheid:** 2 | **GDPR:** Hoog | **Schaalbaar:** Deels
- "Welke werkgevers in Gent hebben >60 churnrisico?" via LLM-interface
- **Vereist:** data residency clauses, DPA met LLM-provider, security review
- **Beslissing:** parkeren tot AVG-guidance over AI-verwerking duidelijker is

### 💡 Marktbenchmarking via externe databronnen
- **Impact:** 4 | **Haalbaarheid:** 3 | **GDPR:** Laag | **Schaalbaar:** Ja
- NACE-sectordata, Statbel arbeidsmarktcijfers, RSZ-publicaties
- Contextualiseer eigen segmentprestaties t.o.v. markt

### 💡 Automatische anomaly detection
- **Impact:** 3 | **Haalbaarheid:** 3 | **GDPR:** Laag | **Schaalbaar:** Ja
- Isolatie Forest op interactiepatronen
- Alert bij ongewone pieken/dalingen per consultant of regio

---

## Wat niet te doen (bewuste keuzes)

| Idee | Reden van uitsluiting |
|---|---|
| Realtime streaming pipeline | Kosten vs. baten: dagelijkse batch volstaat |
| Gezichtsherkenning of stemanalyse | GDPR high-risk verwerking, geen businesscase |
| Externe social media scraping | Juridisch grijs gebied, reputatierisico |
| Eén monolithisch data warehouse | Vendor lock-in risico; modulaire aanpak gekozen |

---

## Beslissingsmatrix: prioriteitsstelling

```
Hoge impact, makkelijk → EERST doen (segmentatie, dashboard)
Hoge impact, moeilijk  → Plannen & risico's mitigeren (churnmodel)
Lage impact, makkelijk → Alleen als er capaciteit is
Lage impact, moeilijk  → Niet doen
```

---

*Laatste update: Q2 2026 | Eigenaar: Data Analytics Team | Review: kwartaalbasis*
