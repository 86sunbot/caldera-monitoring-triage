# Caldera Therapeutics · Clinical Monitoring Triage Impact Assessment (ISO 42001 A.5)

This document formalizes the impact assessment for the Clinical Monitoring Triage system, specifically addressing the **fundamental asymmetry between error types** in clinical trial oversight.

---

## 1. Interested Parties & Stakeholders

| Stakeholder Group | Primary Interest | Vulnerability |
| :--- | :--- | :--- |
| **Clinical Trial Participants** | Patient safety, ethical treatment, valid informed consent, receipt of properly stored investigational product. | Vulnerable to protocol non-compliance, uncalibrated temperature storage, or delayed adverse event reporting. |
| **Clinical Research Associates (CRAs)** | Efficient workload management, clear visibility into recurring site trends. | Vulnerable to alert fatigue from low-signal false alarms. |
| **Site Staff & Investigators** | Reputation, operational compliance, clear regulatory standing. | Vulnerable to unjustified scrutiny or damaged sponsor relationships resulting from false accusations. |
| **Caldera Clinical Quality Assurance** | Inspection readiness with EMA/FDA, GxP boundary integrity. | Vulnerable to audit citations if unvalidated AI makes regulatory decisions. |

---

## 2. Asymmetry of Error Types

In a clinical trial environment, **false negatives and false positives do not carry equal risk**:

```
+---------------------------------------------------------------------------------------+
| ERROR TYPE 1: MISSED OBSERVATION (False Negative)                                    |
| Who it harms: Trial Participants (High Harm)                                         |
| Impact:                                                                              |
|   If an expired thermometer, missing re-consent, or recurring drug accountability    |
|   error is missed across 3 visits, patient safety is directly jeopardized.           |
|   Regulatory consequence: Major audit finding, potential study hold by FDA/EMA.      |
+---------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------+
| ERROR TYPE 2: FALSE SIGNAL SURFACED (False Positive)                                 |
| Who it harms: CRA / Site Staff (Operational Inconvenience)                            |
| Impact:                                                                              |
|   A benign mention is flagged under a theme. The CRA clicks the verbatim sentence,   |
|   reads it in 15 seconds, and dismisses it.                                          |
|   Harm is limited to minor operational friction (~15 seconds of monitor time).       |
+---------------------------------------------------------------------------------------+
```

### Strategic Architectural Conclusion:
> **The triage system is intentionally calibrated to maximize recall over precision.**  
> Surfacing a candidate signal for human review has near-zero safety downside, whereas omitting a signal directly threatens trial participants. However, to prevent monitor alert fatigue, candidate signals must always provide the exact verbatim sentence and page number so dismissal takes seconds.

---

## 3. The GxP Boundary as an Impact Safeguard

By classifying this system as a **surfacing aid** rather than an **automated predictive scoring engine**:
- It produces **no regulatory records**.
- It makes **no automated deviation calls**.
- It remains strictly outside the **GxP 21 CFR Part 11 / Computerized System Validation (CSV)** boundary, ensuring that human clinical judgment remains the sole decision authority.
