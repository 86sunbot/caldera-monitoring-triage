# ADR-002: Pre-Ingestion Data Sovereignty & Regional Compliance Gate

### Status
Accepted

### Context & Problem Statement
Caldera Therapeutics runs multi-center international clinical trials. Certain sovereign jurisdictions (e.g. non-adequate data transfer regimes) prohibit transferring clinical trial documentation or site monitoring narratives outside local legal boundaries without executed transfer agreements. Ingesting text into a central pipeline without verification creates immediate regulatory non-compliance under GDPR and international privacy frameworks.

### Decision
We introduce an automated pre-ingestion compliance gate interfacing with the `Site Registry`:
1. Before any monitoring report text is parsed or processed, the site identifier is queried against the `Site Registry`.
2. If the site is flagged as region-restricted, the document is dropped **immediately**.
3. An `ExclusionRecord` is logged to the audit log containing timestamp, site ID, document ID, country, and justification.
4. The system operates on a **fail-closed** policy: if the `Site Registry` experiences an outage (HTTP 500), documents are held in staging rather than processed unsafely.

### Consequences
- **Positive**: Proves ISO 42001 A.7 data jurisdiction control to auditors.
- **Positive**: Prevents accidental ingestion of unauthorized foreign site data.
- **Evidence**: Verified by automated test `tests/test_controls.py::test_region_restriction_gate_fires`.
