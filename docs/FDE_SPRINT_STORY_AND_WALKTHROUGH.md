# Caldera Therapeutics · Clinical Monitoring Triage
## The Complete FDE Challenge Build Sprint Story & Walkthrough Guide
> **Written in Plain English for Developers, Mentors, and Stakeholders**  
> **Team 2 · Health & Life Sciences Studio · Challenge Build Sprint**

---

## 📖 Executive Summary (The 30-Second Story)

In a clinical trial, doctors test new experimental medicines on human patients across multiple hospitals. Monitors regularly visit these hospitals and write long 40-page inspection reports. 

The client originally asked: *"Build an AI that predicts risk scores and ranks hospitals."*  
**The problem:** In medicine, software that calculates automated "risk scores" triggers strict legal regulations (**21 CFR Part 11 / GxP**) requiring **9 to 12 months of formal validation audits** before anyone can touch it.

**What we delivered instead:** A **"Surfacing, Not Predicting"** reading assistant:
1. It reads the 40-page reports from the electronic file storage (**eTMF**).
2. It blocks reports from restricted countries before parsing to obey data privacy laws.
3. It finds compliance observations and extracts the **exact sentence** with the **exact page number**.
4. It groups findings by hospital, highlighting recurring issues across visits in seconds.
5. It **strictly forbids risk scores**, keeping the software safe from 12-month legal delays.
6. It runs live in **Google AI Studio** with built-in resilience against server outages.

---

## 👣 Step 1: The Client, The Problem, and The Legal Trap

### 1. Who is the Client?
The client is **Caldera Therapeutics**, a biotechnology company testing new medicines across hospitals.

### 2. The Daily Pain Point
Human monitors visit hospital trial sites and write 40-page **Monitoring Visit Reports (MVRs)** detailing safety checks (consent forms, drug storage temperatures, staff training). These reports are stored in a digital file cabinet called the **eTMF** (*electronic Trial Master File*). Monitors are drowning in paperwork, reading hundreds of 40-page PDFs just to find recurring mistakes.

### 3. What the Client Asked For (And the Legal Trap)
The client's VP of Clinical Operations asked:
> *"Build an AI that reads these reports and gives each hospital a predictive risk score (e.g. 'High Risk' or '8/10')."*

#### Why this was a legal trap (Jargon Translated):
- **GxP** (*Good Practice regulations*): International medical laws protecting patient safety and trial honesty.
- **21 CFR Part 11**: A strict US Food & Drug Administration (FDA) law stating that software making clinical trial decisions or calculating trial risk scores must be formally audited and certified.
- **Computerized System Validation (CSV)**: The 9-to-12-month formal process of running hundreds of verification tests and signing piles of legal paperwork.

**The Bottom Line:** If our AI calculates a risk score, regulators declare it a regulated medical decision-maker, delaying deployment by **9 to 12 months**.

### 4. What We Agreed to Build (The "Ratified Ask")
As Forward Deployed Engineers, we reframed the scope to **"Surfacing, Not Predicting"**:
- An intelligent reading helper that highlights real compliance sentences with exact page numbers.
- **Zero scores, zero rankings, zero automated deviation calls.**
- Qualified human monitors make 100% of the decisions.
- Because it is an informational reading tool without scores, it **stays outside the 12-month legal delay** and can be used immediately.

---

## 🛡️ Step 2: Ground Rules & Scope Discipline Before Writing Code

In the FDE Operating Model, you set the guardrails **before** writing code:

### 1. The README Rule (Documenting Non-Goals)
Before writing line 1 of Python, we locked our scope in [README.md](../README.md):
- **NO Predictive Scores:** Avoids the 12-month GxP CSV audit trap.
- **NO Patient Health Records:** We do not touch patient names, medical history, or lab tests (from hospital databases called **EDC**). We only read hospital conduct notes.
- **NO Scanned Paper Reports (Deferred):** About 8% of historical reports are scanned paper pictures. We explicitly deferred building optical character recognition (**OCR**) to Phase 2 rather than wasting 3 hours of sprint time.

### 2. The Live Risk Register (Proof Over Promises)
We created [docs/governance/risk-register.md](risk-register.md) tracking 7 risks (**R-01 through R-07**). 
Under sprint rules, **a risk cannot be marked 'Treated' without naming a real test or code file in the repository**. Empty intentions score zero; empirical evidence scores maximum marks.

---

## ⚙️ Step 3: How the Code Works (The 4-Stage Assembly Line)

Our application slice in `/src` operates like a clean assembly line:

```
[ 20 Reports from eTMF ]
           │
           ▼
┌──────────────────────────────────────┐
│  STAGE 1: The Regional Border Guard  │ ➔ If country is restricted (Site 404):
│  (Data Sovereignty Gate)             │    DROP file & record in Audit Log!
└──────────────────────────────────────┘
           │ (Eligible reports only)
           ▼
┌──────────────────────────────────────┐
│  STAGE 2: The Sentence Highlighter   │ ➔ Finds important sentences.
│  (Observation Extractor)             │    Saves exact page & exact words!
└──────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  STAGE 3: The Pattern Organizer      │ ➔ Groups by Hospital & Theme.
│  (Same-Theme-Across-Visits View)     │    Shows: "Hospital 101 did this 6 times!"
└──────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  STAGE 4: The Reviewer Packet        │ ➔ Delivered to human doctor/monitor.
│  (Unranked, Clean Output)            │    Zero scores. 100% human decision.
└──────────────────────────────────────┘
```

1. **Stage 1: The Regional Border Guard (`src/pipeline/triage_graph.py`)**  
   Certain countries forbid exporting hospital data. Before parsing any text, the code queries the `Site Registry`. All 4 reports from **`SITE-404`** (located in a restricted country) are immediately dropped into the audit exclusion log without ever touching the AI engine.
2. **Stage 2: The Sentence Highlighter (`src/pipeline/extractor.py`)**  
   Scans eligible reports for real clinical themes (*Informed Consent*, *Medicine Storage*, *Temperature*, *Staff Training*). It extracts candidate observations with **immutable citations**: document ID, page number, and verbatim sentence.
3. **Stage 3: The Pattern Organizer (Same-Theme-Across-Visits)**  
   Groups findings by hospital and theme. For **`SITE-101`**, it instantly reveals that *Informed Consent documentation issues appeared across 6 distinct visits*, saving monitors hours of manual cross-referencing.
4. **Stage 4: Strict Anti-Scoring Guardrails (`src/models.py`)**  
   Pydantic code validators actively reject any fields named `score`, `priority`, or `risk_level`, and immediately block any subject-level patient health data (`edc_id`, `lab_results`).

---

## ⚾ Step 4: The 3 Curveballs & How We Beat Them

During the sprint, 3 surprise interruptions landed:

### Curveball 1 (11:00 AM) — The CISO Security Audit (Due by 14:00)
- **The Challenge:** The Chief Information Security Officer asks: *"Hospital reports are written by people we don't employ. What if someone embeds prompt-injection hacks? And prove you aren't touching patient medical data."*
- **Our Solution ([docs/governance/threat-model.md](threat-model.md)):**
  - Prompt Injection: Extraction uses deterministic sentence tokenization; text is treated strictly as passive data, never executed as commands.
  - Patient Data Barrier: Pointed to `test_edc_boundary_enforced` which actively rejects hospital patient data.
  - Inspection Status: Explained that the triage packet is an unarchived reading aid (like `Ctrl+F`), not a regulated GCP legal record.

### Curveball 2 (1:00 PM) — The Sponsor's Conference FOMO
- **The Challenge:** The VP of Clinical Operations says: *"A competitor at a conference said they've had a predictive risk-scoring AI running across their hospitals for 8 months! Why are you giving me less?"*
- **Our Solution ([docs/governance/sponsor-update.md](sponsor-update.md)):**
  - We gave a 5-minute Level 5 pitch: *"The competitor hasn't beaten us—**they are sitting on an uninspected regulatory time bomb**. If an FDA auditor asks how a site was chosen and they show an unvalidated AI score, it triggers an immediate violation warning (Form 483). What we built is safe, keeps us outside the 12-month GxP delay, and delivers working triage this quarter."*

### Curveball 3 (3:00 PM) — The Server 500 Outage
- **The Challenge:** An upstream external service starts returning `HTTP 500 Server Error`.
- **Our Solution ([tests/test_curveball_degradation.py](../../tests/test_curveball_degradation.py)):**
  - **Graceful Degradation:** Instead of crashing in an infinite retry loop, our code catches the 500, changes status to **`DEGRADED`**, displays a clear warning to the monitor, and enforces a **fail-closed** regional hold so unverified files are never leaked. Logged as **R-04** in the risk register.

---

## 🚀 Step 5: Verification, GitHub, and Google AI Studio

1. **Automated Testing:** 8 tests passing with 100% core coverage (`pytest tests/ -v`).
2. **GitHub Repository:** Full code and governance pack pushed to **[https://github.com/86sunbot/caldera-monitoring-triage](https://github.com/86sunbot/caldera-monitoring-triage)**.
3. **Live Google AI Studio UI:** Imported into Google AI Studio, rendering a live web application with:
   - One-click triage execution.
   - Built-in **Curveball 3 Simulator** checkboxes (simulate HTTP 500 on eTMF or Site Registry).
   - Real-time regional exclusion logs and same-theme visit views.

---

## 🎤 The 16:15 Close-Out Demo Playbook (10 Minutes)

When your mentors ask you to present:

1. **Show the Working Slice (3 mins):**
   - Open your live Google AI Studio app and click **Run Clinical Monitoring Triage**.
   - Show Site 404 dropped by the regional compliance gate.
   - Show Site 101 displaying recurring informed consent issues across 6 visits with exact page numbers.
2. **Show the Governance & Curveball Defense (4 mins):**
   - Open `risk-register.md`: *"Every single risk points to a real test in our repo, not promises."*
   - Check the **Simulate HTTP 500** checkbox in the UI and click Run: *"When the server failed at 15:00, we didn't retry and crash. We degraded gracefully and protected data sovereignty."*
3. **Name What You Would Do Next (3 mins):**
   - *"In Phase 2, we will build the OCR pipeline for the 8% scanned paper reports we deferred today, and work with the DPO on transfer agreements for the restricted sites."*

---

## 🗺️ Mapping to the 21-Stage AI FDE Operating Model

| Operating Model Phase | Stages Covered | What Caldera Therapeutics Delivered |
| :--- | :--- | :--- |
| **1. DISCOVER** | **01–04** | Field immersion into CRA workflows; triaged regulations to reject predictive risk scoring and avoid 9–12 months of GxP CSV. |
| **2. DEFINE** | **05–08** | Modeled domain in `models.py`; enforced EDC data firewall; authored ISO 42001 impact assessment; selected deterministic sentence extraction. |
| **3. DESIGN** | **09–13** | Designed Same-Theme-Across-Visits view; built regional compliance gate; authored CISO threat model; approved ADR-001 and ADR-002. |
| **4. DELIVER** | **14–17** | Built Python backend, CLI, and Web UI; verified with 8 automated tests; mapped ISO 42001 evidence; pushed to GitHub and Google AI Studio. |
| **5. OPERATE & IMPROVE** | **18–21** | Proved Curveball 3 resilience on 500 errors; delivered 13:00 sponsor pitch; enforced non-GxP lifecycle boundary; captured Phase 2 OCR backlog. |
