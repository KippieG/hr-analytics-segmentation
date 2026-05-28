# GDPR Verwerkingsregister (Demo)

> Conform AVG Art. 30 — Register van verwerkingsactiviteiten.
> Dit document is een **demonstratie** van hoe een verwerkingsregister eruitziet. Geen echte persoonsgegevens aanwezig.

---

## Verwerkingsactiviteit 1: Werkgeverssegmentatie

| Veld | Waarde |
|---|---|
| **Naam verwerking** | Segmentatie werkgeversportfolio |
| **Doel** | Strategische prioritering van account management o.b.v. RFM-profiel |
| **Verwerkingsgrond** | Gerechtvaardigd belang (art. 6.1.f AVG) |
| **Categorieën betrokkenen** | Contactpersonen bij werkgevers (B2B) |
| **Categorieën gegevens** | Naam, e-mail, telefoonnummer contactpersoon; bedrijfsnaam, BTW-nummer |
| **Ontvangers** | Interne consultants (via Power BI, row-level security) |
| **Doorgifte derde landen** | Nee |
| **Bewaartermijn** | 24 maanden na laatste interactie |
| **Technische maatregelen** | Pseudonimisering vóór verwerking, versleutelde opslag, toegangslogging |
| **Organisatorische maatregelen** | Need-to-know principe, jaarlijkse security awareness training |

---

## Verwerkingsactiviteit 2: Interactiehistorie

| Veld | Waarde |
|---|---|
| **Naam verwerking** | Logging contactmomenten consultant ↔ werkgever |
| **Doel** | Kwaliteitsbewaking dienstverlening, churnpreventie |
| **Verwerkingsgrond** | Gerechtvaardigd belang (art. 6.1.f AVG) |
| **Categorieën betrokkenen** | Contactpersonen bij werkgevers |
| **Categorieën gegevens** | Interactiedatum, type (call/email/meeting), outcome, consultant-ID |
| **Ontvangers** | Management, betrokken consultant |
| **Bewaartermijn** | 36 maanden |
| **Technische maatregelen** | Audit log bij elke toegang, pseudonimisering contact-ID's |

---

## Pseudonimiseringsaanpak

```
Ruwe data (met PII)
      │
      ▼ [src/ingestion/gdpr_anonymizer.py]
Pseudoniem via HMAC-SHA256 + project-salt
      │
      ▼
Verwerkte data (zonder directe identificatoren)
```

- De **mapping-tabel** (pseudoniem ↔ originele waarde) wordt **nooit in de repository** opgeslagen
- De **salt** wordt beheerd via omgevingsvariabele (`GDPR_SALT`), nooit hardcoded
- **Re-identificatie** is alleen mogelijk voor gemachtigde personen met toegang tot de salt

---

## Dataretentie & verwijdering

| Dataset | Bewaring | Verwijderingsproces |
|---|---|---|
| `data/raw/` | Niet in repo (`.gitignore`) | Lokaal: handmatig na inname |
| `data/processed/` | 24 maanden | Automatisch via retention script |
| Logs | 12 maanden | Log rotation via logrotate |
| Power BI rapport | Live (geen kopie) | N.v.t. |

---

*Eigenaar: Data Team | Review: jaarlijks of bij wijziging verwerkingsdoel*
