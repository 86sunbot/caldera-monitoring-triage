# Caldera Therapeutics — Monitoring Report Triage System
### Forward Deployed Engineering (FDE) Challenge Build Sprint · Team 2

[![Google AI Studio](https://img.shields.io/badge/Google%20AI%20Studio-Applet%20Live%20Link-teal?logo=google)](https://aistudio.google.com/apps/cc4ffde2-8a28-4c34-92e3-09e9b1bb805a?showAssistant=true&project=metal-contact-364103&showPreview=true)

🔗 **Quick Access**: [Launch Caldera Clinical Monitoring Triage in Google AI Studio](https://aistudio.google.com/apps/cc4ffde2-8a28-4c34-92e3-09e9b1bb805a?showAssistant=true&project=metal-contact-364103&showPreview=true)

> **Operating Philosophy**: *Surfacing, Not Predicting.*  
> This system ingests clinical monitoring visit reports, extracts candidate observations with verbatim source attribution (document ID, page number, sentence), groups them by site and theme, and presents an unranked review packet to a human clinical reviewer.

---

## 1. Today's Scoped Slice (Locked at 09:15)

In accordance with FDE scope discipline, this repository builds a single **thin path that runs end-to-end**:

1. **Ingress**: Digital text ingestion across a sample of 20 clinical monitoring visit reports from eTMF.
2. **Pre-Processing Compliance Gate**: Automated check against the `Site Registry`. Documents originating from region-restricted jurisdictions are dropped **before** content extraction and recorded in an auditable exclusion log.
3. **Observation Extraction**: Extraction of candidate operational and protocol observations with immutable source attribution:
   - `document_id`
   - `page_number`
   - `verbatim_sentence`
4. **Grouping**: Observations grouped by `site_id` and categorized into standard clinical monitoring `theme`s, explicitly presenting a **same-theme-across-visits view** for recurring signals at a given site.
5. **Reviewer Packet Assembly**: Structured reviewer packet (JSON and plain-text markdown) presented to human clinical monitors.
6. **Graceful Degradation (Curveball 3 resilience)**: Resilient fallback handling when upstream dependencies (eTMF / Site Registry) experience service degradation (500s), reporting partial results without crashing.

---

## 2. Explicitly NOT Building Today (Recorded Deferrals)

Every deferral is an intentional architectural decision, not an oversight:

| Deferred Item | Why It Is Excluded | Governance / Business Justification |
| :--- | :--- | :--- |
| **Predictive Risk Scoring / Ranking** | "If it looks like a score, it is a score." | A predictive risk score places the system inside the **GxP-validated estate (21 CFR Part 11 / Computerized System Validation)**, requiring 9–12 months of formal validation that kills the sponsor's timeline. |
| **Subject-Level Clinical Data** | Not needed for operational monitoring triage. | Avoids ingesting protected health information (PHI/HIPAA/GDPR Special Category Data) from the Electronic Data Capture (EDC) or safety databases. |
| **OCR for Scanned Documents (8%)** | Time-boxed 5-hour build constraint. | Digital text only in this slice. Scanned PDFs are flagged and routed to manual processing (tracked as **R-06**). |
| **Cross-Study Inference** | Inappropriate statistical aggregation. | Inferences across disparate clinical protocols risk introducing false analogies across differing therapeutic endpoints. |
| **Automated Regulatory Decisions** | Human-in-the-loop compliance mandate. | The system never asserts that a clinical protocol deviation has occurred. Only a qualified clinical reviewer can make that determination. |

---

## 3. Repository Architecture

```
caldera-monitoring-triage/
├── README.md                          # Scoped slice & deferral log
├── pyproject.toml                     # Python packaging & dependencies
├── requirements.txt                   # Pip requirements
├── .github/
│   ├── pull_request_template.md       # Mandatory governance questions on every PR
│   └── workflows/ci.yml               # Automated CI for tests & governance integrity
├── src/
│   ├── __init__.py
│   ├── config.py                      # System configuration
│   ├── models.py                      # Pydantic schemas enforcing provenance & no scores
│   ├── clients/
│   │   ├── etmf_client.py             # Mock eTMF Document API (with 500 error simulation)
│   │   └── site_registry.py           # Site jurisdiction & region-restriction service
│   ├── pipeline/
│   │   ├── triage_graph.py            # End-to-end pipeline: gate -> extract -> group -> packet
│   │   └── extractor.py               # Deterministic signal extractor
│   └── main.py                        # CLI runner
├── tests/
│   ├── test_pipeline_slice.py         # End-to-end execution test
│   ├── test_controls.py               # Proves governance controls fire (cited in risk register)
│   └── test_curveball_degradation.py  # Proves graceful degradation on 500 errors
├── data/
│   └── sample_reports/                # 20 synthetic monitoring visit reports
└── docs/
    └── governance/
        ├── risk-register.md           # Live risk register with repo evidence citations
        ├── iso42001-mapping.md        # Mapping AI management objectives (A.2 to A.10)
        ├── threat-model.md            # CISO 14:00 excerpt (STRIDE + AI attack surfaces)
        ├── impact-assessment.md       # Error asymmetry analysis (A.5)
        ├── sponsor-update.md          # 13:00 5-minute sponsor update script
        └── decisions/
            ├── ADR-001-surfacing-vs-predictive.md
            └── ADR-002-region-restriction-boundary.md
```

---

## 4. Working with AI Assistance (Review Log)

In accordance with sprint requirements, all AI-generated code and documentation have been interrogated and reviewed:

- **AI Proposal**: Initially, the assistant suggested adding a `"severity_level": "HIGH / MEDIUM / LOW"` field to candidate observations.
- **Human Review Decision**: **Rejected.** Under Caldera's governance charter, adding a severity tier is a pseudo-score that risks drifting into GxP validation territory. Observations remain strictly unranked with neutral theme categorizations.
- **AI Proposal**: The assistant proposed retrying external API calls 5 times with exponential backoff for the 15:00 curveball.
- **Human Review Decision**: **Overridden.** A retry loop is not a degradation strategy. The pipeline was modified to catch 500s immediately, log the dependency failure to the audit trail, and assemble a partial review packet with an explicit notice to the clinical reviewer.
