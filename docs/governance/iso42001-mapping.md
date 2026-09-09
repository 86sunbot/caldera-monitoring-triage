# Caldera Therapeutics · ISO/IEC 42001:2023 Mapping

This document provides Caldera's alignment to the ISO/IEC 42001:2023 Annex A control objectives for the Clinical Monitoring Triage system. 

In accordance with FDE governance discipline, this mapping presents **honest assessments backed by repo evidence**, rather than aspirational assertions.

---

| Objective | Theme | Status | Evidence or Defensible Justification for Exclusion |
| :--- | :--- | :--- | :--- |
| **A.2** | **AI Policy** | **Not applicable today** | Client-level organizational policy. Caldera corporate AI policy is an external organizational dependency outside the engineering pod's delivery boundary; tracked as **R-05** in the risk register. |
| **A.3** | **Internal Organisation** | **Addressed** | Named operational roles defined: Lead Clinical QA Manager owns GxP boundary; VP Data Privacy owns cross-border transfer rules; Lead Clinical Monitor owns triage packet review. |
| **A.4** | **Resources for AI Systems** | **Addressed** | Infrastructure dependencies documented: eTMF Document API (document ingress), Site Registry (jurisdiction lookup), Python 3.11 execution runtime. |
| **A.5** | **Impact Assessment** | **Addressed** | Formal assessment of error asymmetry (missed observation vs. false observation) documented in [`docs/governance/impact-assessment.md`](impact-assessment.md). |
| **A.6** | **AI System Life Cycle** | **Addressed** | System explicitly architected to remain outside the GxP-validated estate (21 CFR Part 11). Proved by test preventing scoring/ranking: `tests/test_controls.py::test_zero_scoring_or_ranking` and `docs/governance/decisions/ADR-001-surfacing-vs-predictive.md`. |
| **A.7** | **Data for AI Systems** | **Addressed** | Jurisdiction and provenance control enforced. Pre-ingestion region check drops and logs restricted sites: `tests/test_controls.py::test_region_restriction_gate_fires` and `src/pipeline/triage_graph.py:L60-L93`. Scanned 8% deferred under R-06. |
| **A.8** | **Information for Interested Parties** | **Addressed** | System output carries full provenance (document ID, page, verbatim sentence) and an explicit human-in-the-loop triage disclaimer. Proved by `tests/test_controls.py::test_verbatim_sentence_and_page_provenance`. |
| **A.9** | **Use of AI Systems** | **Addressed** | System produces triage review packets for human clinical monitors only. The system never asserts a protocol deviation has occurred; all clinical determinations remain human accountabilities. |
| **A.10** | **Third-Party Relationships** | **Addressed** | Third-party eTMF and registry dependencies isolated behind client interfaces. Graceful degradation on 500 outages verified by `tests/test_curveball_degradation.py::test_graceful_degradation_on_etmf_500`. |
