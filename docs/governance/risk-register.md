# Caldera Therapeutics · Clinical Monitoring Triage Risk Register

### Risk Evaluation Scale
- **Likelihood**: Low (Rare / Unlikely) · Medium (Occasional) · High (Frequent / Probable)
- **Impact (Client Terms)**:
  - **Catastrophic**: Direct harm to clinical trial participants, suspension of trial license by EMA/FDA, or regulatory inspection finding.
  - **Major**: Data sovereignty / cross-border transfer fine under GDPR, or 9–12 month project stall due to unvalidated GxP deployment.
  - **Moderate**: Clinical monitor time wasted (20+ CRA hours) reconciling false signals or re-evaluating clean sites.
  - **Minor**: Localized triage delay (<4 hours) during transient network outages.

---

### Live Risk Register

| ID | Risk (Cause & Consequence) | Owner | Likelihood / Impact | Treatment | Control | Evidence (Repo File / Test / PR) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R-01** | Scope drift introduces numeric risk scores or ranking, causing the system to be classified as GxP-regulated software and halting clinical rollout for 9–12 months of CSV. | Lead Clinical QA Manager | Medium / Major | **Avoid** | Prohibit numeric scoring and ranking fields in data models and pipeline output schemas. | `src/models.py:L40` and `tests/test_controls.py::test_zero_scoring_or_ranking` | **Treated** |
| **R-02** | Reports from sovereign jurisdictions are ingested without cross-border transfer agreements, exposing Caldera to GDPR / territorial regulatory enforcement. | VP Data Privacy & Compliance | High / Major | **Reduce** | Automated pre-ingestion check against Site Registry. Restricted sites dropped and logged before content extraction. | `src/pipeline/triage_graph.py:L60-L93` and `tests/test_controls.py::test_region_restriction_gate_fires` | **Treated** |
| **R-03** | Observation extracts lose page/sentence provenance during pipeline grouping, preventing a CRA from verifying the claim against the original eTMF PDF. | Lead Clinical Monitor | Medium / Moderate | **Reduce** | Strict Pydantic models requiring immutable `document_id`, `page_number`, and `verbatim_sentence` for every candidate observation. | `src/models.py:L26-L37` and `tests/test_controls.py::test_verbatim_sentence_and_page_provenance` | **Treated** |
| **R-04** | Upstream eTMF Document API experiences partial or complete outage (HTTP 500), leading clinical reviewer to draw false reassurance from missing reports (e.g. interpreting unretrieved visits as clean site conduct) or causing triage crash. *(Curveball 3 - Drop 3 of 3)* | Clinical IT Systems Lead / Lead Clinical Monitor | High / Major | **Reduce** | Graceful partial retrieval handling (no crashing/infinite loops), mandatory coverage denominator disclosure (`reports_retrieved` of `reports_expected`), per-site coverage tracking, and prominent "ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE" completeness warning. | `src/pipeline/triage_graph.py:L115-L165`, `src/models.py:L60-L75`, and `tests/test_curveball_degradation.py::test_partial_etmf_outage_coverage_disclosure` | **Treated** |
| **R-05** | Lack of an overarching corporate AI governance policy across Caldera Therapeutics slows cross-functional sign-off. | VP Clinical Operations | High / Moderate | **Accept** | Client-level dependency not in the engineering pod's scope. Documented as external delivery dependency in ISO 42001 mapping. | `docs/governance/iso42001-mapping.md (Objective A.2)` | **Accepted** |
| **R-06** | Historical 8% scanned paper monitoring visit reports cannot be parsed by digital text extractor, omitting legacy site observations. | Clinical Systems Arch | Medium / Moderate | **Accept** | Scanned PDFs explicitly deferred from today's 5-hour slice. Scanned documents flagged for manual CRA review. | `README.md (Section 2 Deferrals)` | **Accepted** |
| **R-07** | Accidental ingestion of Electronic Data Capture (EDC) subject-level clinical data or PHI violates clinical trial firewalls and patient privacy regulations. | Lead Clinical Data Manager | High / Catastrophic | **Avoid** | Code-level schema barrier actively rejecting EDC fields and patient-level identifiers. | `src/models.py:L23-L43` and `tests/test_controls.py::test_edc_boundary_enforced` | **Treated** |
