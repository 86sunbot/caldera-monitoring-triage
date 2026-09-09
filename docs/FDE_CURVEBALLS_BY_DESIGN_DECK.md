# Factored by Design vs. Reacted by Reflex
## The Caldera Therapeutics FDE Architecture & Governance Defense
> **Team 2 · Health & Life Sciences Studio · Forward Deployed Engineering (FDE) Sprint**  
> **Core Inquiry**: *"Did we factor curveballs into the design, or did we merely react to them?"*  
> **Target Audience**: Trainers, Mentors, Evaluators, and Engineering Leadership

---

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             THE FDE CORE THESIS                                  │
│                                                                                  │
│   "Junior engineering teams build for the happy path and scramble to patch       │
│    surprises. Forward Deployed Engineers treat regulatory traps, CISO audits,   │
│    and vendor outages as predictable properties of enterprise reality.          │
│                                                                                  │
│    Every curveball today hit a pre-existing architectural shock absorber."       │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧭 Executive Summary Matrix: Designed vs. Reacted

| Curveball Event | The Reactive Reflex (What Most Teams Do) | Our Anticipatory Design (What We Locked at 09:15) | Empirical Proof in Repository |
| :--- | :--- | :--- | :--- |
| **Curveball 1 (11:00)**<br>CISO Audit: Prompt Injection & Patient Data (EDC) | Scramble to write prompt guards, add regex filters, rewrite LLM prompts at the last minute. | **Passive Tokenization & Schema Firewalls:** Decided at 09:15 that LLM would never execute text as instructions; Pydantic schema actively rejects patient identifiers. | `src/models.py:L23-L43`<br>`tests/test_controls.py::test_edc_boundary_enforced`<br>`docs/governance/threat-model.md` |
| **Curveball 2 (13:00)**<br>Sponsor FOMO: Competitor's 8-month predictive risk model | Cave to stakeholder pressure, slap a pseudo-score ("High/Med/Low" or 8.5/10) to appease client. | **Pre-Locked GxP Boundary:** Locked ADR-001 (*Surfacing, Not Predicting*) before writing code to prevent a 9–12 month CSV validation freeze. Delivered a Level 5 regulatory reframe. | `docs/governance/decisions/ADR-001-surfacing-vs-predictive.md`<br>`docs/governance/sponsor-update.md`<br>`tests/test_controls.py::test_zero_scoring_or_ranking` |
| **Curveball 3 (15:00)**<br>Drop 3: eTMF 500 Outage (11 of 20 reports retrieved) | Put in an infinite 5x retry loop that crashes CRA shift, or silently show 11 reports without disclosing missing data. | **Stateful Degradation & Denominator Disclosure:** Graph state machine tracks expected vs. retrieved counts, surfaces statutory completeness warning, and isolates missing sites. | `src/pipeline/triage_graph.py:L115-L165`<br>`tests/test_curveball_degradation.py::test_partial_etmf_outage_coverage_disclosure`<br>`docs/governance/risk-register.md (R-04)` |

---

## 🎬 Slide-by-Slide Presentation Deck

### Slide 1: Title & The Core Question
- **Headline**: Factored by Design vs. Reacted by Reflex: The Caldera FDE Lesson
- **Sub-headline**: How defensive architecture and scope discipline turned 3 sprint curveballs into non-events.
- **Presenter Spoken Hook**:  
  > *"When the trainer asks whether we designed for curveballs or reacted to them, the answer is foundational to what Forward Deployed Engineering actually means. If you write code assuming external APIs never fail, clients never panic, and security never asks hard questions, you aren't building enterprise software—you're building a hackathon prototype. Every curveball we faced was absorbed by a boundary we drafted before 10:00 AM."*

---

### Slide 2: The Junior Mindset vs. The FDE Mindset
- **Visual Contrast**:
  - **The Reactive Engineer (The "Scramble Loop")**:
    ```
    Happy Path Code ➔ Surprise Event ➔ Panic Patch ➔ Broken Abstraction ➔ Technical Debt
    ```
  - **The Forward Deployed Engineer (The "Absorbing Boundary")**:
    ```
    Domain Threat Model ➔ Boundary Contracts ➔ Event Strikes ➔ Boundary Holds ➔ Auditable Proof
    ```
- **Key Talking Points**:
  1. *Enterprise systems are hostile environments*: Vendors fail, regulations bite, and stakeholders get anxious.
  2. *Design is what you refuse to allow*: In clinical healthcare, an unvalidated feature is not a bonus—it is a legal liability.
  3. *Our 09:15 charter*: We spent our first 45 minutes defining what we would **NOT** build (no predictive scores, no patient PHI, no scanned paper PDFs).

---

### Slide 3: Curveball 1 — The CISO Security Audit (11:00 AM)
- **The Event**: The CISO demands proof against prompt injection from unvetted site monitors and guarantees that patient-level Electronic Data Capture (EDC) data is not ingested.
- **Did We React?**  
  *No.* We did not change our parser or add emergency sanitizer code.
- **How It Was Factored in Design**:
  1. **Passive Tokenization Architecture**: In our initial system design, report text is treated purely as string data in immutable Pydantic containers (`SourceCitation`), never formatted into executable system instructions.
  2. **Schema-Level Exclusion**: `src/models.py` was defined with explicit schema validators that throw validation errors if EDC fields (`patient_id`, `subject_initials`, `lab_value`) appear.
  3. **The Evidence**: `tests/test_controls.py::test_edc_boundary_enforced` was already written to prove that feeding patient data causes the system to drop the payload.
- **Presenter Line**:  
  > *"When the CISO questioned us at 11:00, we didn't have to rewrite our pipeline. We opened `test_controls.py`, showed our automated test passing, and mapped it to ISO 42001 Section A.7. The security control was already compiled in code."*

---

### Slide 4: Curveball 2 — The Sponsor's Conference FOMO (1:00 PM)
- **The Event**: The VP of Clinical Operations hears a competitor has had an AI risk-scoring model running across trial sites for 8 months and questions why we aren't delivering predictive risk scores.
- **Did We React?**  
  *No.* A reactive team would have added a quick "Risk: 8.2 / 10" badge to the UI to please the client. We held the line.
- **How It Was Factored in Design**:
  1. **ADR-001 (Surfacing vs. Predicting)**: Locked at 09:15. We recognized that introducing a predictive score pushes the system inside **21 CFR Part 11 / GxP Computerized System Validation (CSV)**, triggering 9 to 12 months of legal audits before clinical use.
  2. **The Level 5 Reframe**: We educated the sponsor that their competitor is carrying an uninspected regulatory time bomb. If an FDA inspector asks how a trial site was selected for audit and the sponsor cites an unvalidated AI score, it results in an immediate Form 483 inspection finding.
  3. **Zero-Score Code Barrier**: `src/models.py` and `tests/test_controls.py::test_zero_scoring_or_ranking` strictly prohibit ranking fields.
- **Presenter Line**:  
  > *"Our job as FDEs is not to say 'yes' to every client urge—it is to protect the client from deploying uninspected regulatory debt. We designed the GxP boundary at 09:15, and at 13:00 we defended it."*

---

### Slide 5: Curveball 3 — Drop 3 of 3: eTMF 500 Outage & Denominator Disclosure (3:00 PM)
- **The Event**: The vendor's eTMF API fails with HTTP 500 for a subset of studies. Only 11 of 20 reports can be retrieved.
- **Where This Bites**: A grouping view built on 11 reports looks identical to one on 20. A clinical monitor seeing zero observations for a site draws false reassurance that the hospital is clean, when in reality half the reports were never retrieved!
- **Did We React?**  
  *We rejected the AI assistant's proposal to put a 5x retry loop.* A retry loop freezes CRA workflows and crashes when an upstream vendor is degraded.
- **How It Was Factored in Design**:
  1. **State-Machine Pipeline**: Our pipeline architecture (`MonitoringTriagePipeline`) was built from the start to output rich operational metadata (`system_status`, `reports_expected`, `reports_retrieved`, `is_partial_dataset`).
  2. **Mandatory Denominator Disclosure**: Instead of silently masking the 9 failed documents, the pipeline calculates exact denominators (`Coverage: 3 of 6 reports - PARTIAL`) and surfaces an amber warning banner:
     *"ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE: Conclusions regarding clean site conduct cannot be drawn for unretrieved visits."*
  3. **Empirical Risk Audit**: Mapped to risk **R-04** in `docs/governance/risk-register.md` and verified by `tests/test_curveball_degradation.py::test_partial_etmf_outage_coverage_disclosure`.
- **Presenter Line**:  
  > *"The fatal mistake in healthcare is pretending partial data is complete data. We didn't just catch the 500; we forced the review packet to tell the truth about the missing denominator."*

---

### Slide 6: The Architectural Shock Absorbers
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CALDERA ARCHITECTURAL SHOCK ABSORBERS                    │
├────────────────────────┬───────────────────────────────┬────────────────────────┤
│ 1. SCHEMA FIREWALL     │ 2. STATE MACHINE GRAPH        │ 3. EMPIRICAL REGISTER  │
│                        │                               │                        │
│ Pydantic validation    │ Pipeline decoupled into       │ Every risk entry in    │
│ blocks:                │ discrete, stateful nodes:     │ `risk-register.md` is  │
│ - EDC patient fields   │ - Gate (drops Site 404)       │ paired with a passing  │
│ - Predictive scores    │ - Extract (verbatim quotes)   │ test file in `/tests`. │
│ - Uncited observations │ - Group (same-theme-visits)   │                        │
│                        │ - Packet (status & coverage)  │ No paper promises.     │
└────────────────────────┴───────────────────────────────┴────────────────────────┘
```

---

### Slide 7: The 3 Enduring FDE Lessons

#### 1. Boundaries Over Features
> *The excellence of an enterprise AI deployment is defined not by what it generates, but by what its boundaries reject.*  
> We rejected predictive scores, rejected patient PHI, and rejected restricted jurisdictions before reading a single report.

#### 2. Rejection Over Accretion
> *When a stakeholder panics or a competitor boasts, junior engineers add features; FDEs reinforce guardrails.*  
> Our refusal to add a risk score saved Caldera 9–12 months of regulatory validation delay.

#### 3. Denominator Honesty
> *In mission-critical domains, silent degradation is deadlier than a total crash.*  
> When external dependencies fail partially, defensible software must disclose the denominator to prevent human reviewers from drawing false reassurance from missing data.

---

### Slide 8: The Trainer Defense Cheat Sheet (Word-for-Word Answers)

| When the Trainer Asks... | Deliver This Exact FDE Answer |
| :--- | :--- |
| **"Did you anticipate the 15:00 API failure or react to it?"** | *"We anticipated it in our data model and pipeline architecture. At 09:15 we established that upstream eTMF and registry services are untrusted external dependencies. We designed our output schema with `system_status`, `reports_retrieved`, and `reports_expected` from day one. When Drop 3 hit, we didn't have to redesign anything—we just proved the partial state with `test_partial_etmf_outage_coverage_disclosure`."* |
| **"Why not just retry the 500 error 5 times?"** | *"Because in CRA shift workflows, an infinite retry loop freezes the user interface and masks an upstream outage. More importantly, when an outage is regional, retries won't fix it. The correct FDE design is graceful degradation with mandatory denominator disclosure so doctors know exactly what hasn't been read."* |
| **"How did your design stop prompt injection without an LLM guardrail?"** | *"By architectural choice: we used deterministic sentence tokenization and passive extraction. The document text is strictly passive payload data in a Pydantic object, never embedded into an executable prompt instruction. You cannot inject instructions into an engine that doesn't execute document text as instructions."* |
| **"What is the single biggest FDE lesson from today's sprint?"** | *"That in regulated enterprise AI, 'No' is the most valuable engineering decision you can make. Saying 'No' to predictive scores kept us out of a 12-month GxP freeze; saying 'No' to silent degradation protected patient trial integrity."* |

---

## 🔗 Repository Evidence Links
- **Risk Register**: [`docs/governance/risk-register.md`](governance/risk-register.md)
- **ADR-001 (Surfacing vs. Predicting)**: [`docs/governance/decisions/ADR-001-surfacing-vs-predictive.md`](governance/decisions/ADR-001-surfacing-vs-predictive.md)
- **Threat Model**: [`docs/governance/threat-model.md`](governance/threat-model.md)
- **Partial Degradation Test**: [`tests/test_curveball_degradation.py`](../tests/test_curveball_degradation.py)
- **EDC Firewall Test**: [`tests/test_controls.py`](../tests/test_controls.py)
