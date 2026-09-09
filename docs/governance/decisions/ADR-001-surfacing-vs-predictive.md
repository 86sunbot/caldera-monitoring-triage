# ADR-001: Selection of Surfacing Architecture Over Predictive Scoring

### Status
Accepted (Ratified in Part 1 Architecture Defence)

### Context & Problem Statement
Caldera Therapeutics leadership originally requested an AI system capable of "predictive risk scoring" across clinical trial sites using monitoring visit reports. However, deploying a predictive risk score would trigger classification under the **GxP-regulated Computerized System Validation (CSV / 21 CFR Part 11)** regime. Formal GxP CSV requires prospective validation protocols, installation/operational/performance qualifications (IQ/OQ/PQ), and vendor audits, taking 9 to 12 months.

### Decision
Caldera will implement a **surfacing system**, explicitly rejecting all predictive risk scores, automated prioritization, or machine-asserted protocol deviations.
1. The system extracts candidate observations with verbatim page and sentence citations.
2. The system groups observations by site and theme.
3. The output is delivered to qualified Clinical Research Associates (CRAs) as an unranked informational aid.
4. Output schemas strictly prohibit numeric scores or severity tiers (`tests/test_controls.py::test_zero_scoring_or_ranking`).

### Consequences
- **Positive**: Remains outside the GxP-validated estate; can be delivered and deployed within the current quarter.
- **Positive**: Eliminates risk of black-box model hallucinating regulatory findings.
- **Negative / Trade-off**: Monitors must apply their own judgment to assess severity; requires active stakeholder alignment at the 13:00 sponsor check-in.
