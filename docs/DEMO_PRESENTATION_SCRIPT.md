# Caldera Therapeutics · Clinical Monitoring Triage
## 🎤 10-Minute Demo Presentation Script & Workflow
> **Team 2 · Health & Life Sciences Studio · Challenge Build Sprint**  
> **Target Audience**: Mentors, Trainers, Pod Members, and Evaluators

---

## ⏱️ Visual Timeline

```
0:00 ──── 1:30 ──── 4:00 ──── 6:30 ──── 8:00 ──── 9:00 ──── 10:00
 │          │          │          │          │          │
 └─ Context └─ Live    └─ Curve-  └─ Risk    └─ Next    └─ Q&A
    & Hook     Demo       balls      Register   Steps
```

---

## 🖥️ Screen Setup Before You Begin
- **Tab 1 (Main Screen)**: Your **Google AI Studio Interactive Web UI**.
- **Tab 2 (Backup/Evidence)**: Your **GitHub repository** open to [`docs/governance/risk-register.md`](https://github.com/86sunbot/caldera-monitoring-triage/blob/main/docs/governance/risk-register.md).

---

## Part 1: The Hook & Context (0:00 – 1:30)
**Screen to Share:** Google AI Studio Web UI.

**What to Say:**
> *"Hello everyone. We are Team 2, representing Caldera Therapeutics in the Health & Life Sciences Studio.*  
>  
> *In clinical trials, human monitors visit hospitals and write 40-page reports detailing safety checks and drug storage. Monitors are drowning in paperwork reading hundreds of these 40-page PDFs.*  
>  
> *The client originally asked: **'Build an AI that predicts risk scores and ranks hospitals.'**  
> But we recognized the legal trap: under medical regulations (**21 CFR Part 11 / GxP**), an automated risk score triggers **9 to 12 months of legal validation audits** before anyone can touch it.*  
>  
> *Our core operating thesis today is **'Surfacing, Not Predicting'**. We built a human-in-the-loop reading assistant that extracts real compliance issues with 100% page and sentence citations. Because the human makes the decisions and there are zero scores, it stays outside the 12-month legal delay and can be used today."*

---

## Part 2: Live Demo — The 3 Proofs (1:30 – 4:00)
**Action:** Click the big green button: **`▶ Run Clinical Monitoring Triage`**.

### Point to Proof 1 on screen (The Regional Border Guard):
> *"First, look at this table: **Region-Restricted Document Exclusions**.  
> In international trials, certain countries forbid exporting hospital data. Before reading a single sentence, our pre-processing code gate checked the hospital registry, saw that `SITE-404` is in a restricted country, and dropped those 4 reports into this audit log. We enforce privacy compliance in code before text parsing even begins."*

### Point to Proof 2 on screen (Verbatim Provenance):
> *"Second, scroll down to `SITE-101`. Look at the findings:  
> Notice the **quotation marks** and the source line: `Document MVR-2024-001, Page 2`.  
> The AI did not summarize or make things up. If an FDA inspector audits Caldera tomorrow, the monitor doesn't have to guess—they open document MVR-2024-001, go to Page 2, and the exact sentence is right there on paper."*

### Point to Proof 3 on screen (Same-Theme-Across-Visits View):
> *"Third, look at this headline:  
> **'Theme: Informed Consent — Appeared across 6 distinct visits'**.  
> Site 101 had consent paperwork issues across 6 different visits from January to June. A human monitor reading 40-page reports one month at a time would miss this pattern. Our system clustered 240 pages of reading into a 5-second trend insight."*

---

## Part 3: Live Demo — Curveballs in Action (4:00 – 6:30)

### 1. Demonstrate Curveball 3 (Server 500 Outage — LIVE!):
**Action:** 
1. Check the box: **`Simulate eTMF Document API (HTTP 500)`**.
2. Click the green button: **`▶ Run Clinical Monitoring Triage`**.

**What to Say:**
> *"At 3:00 PM, an external server broke and started returning HTTP 500 errors. Most teams write an infinite retry loop that freezes and crashes.  
> Watch our screen: the status cleanly changes to **`System Status: DEGRADED`**. It warned the user, safely held unverified files in staging, and stayed online without crashing. A retry loop is not a degradation strategy; this is."*

*(Uncheck the box and click Run once more to return to green).*

### 2. Demonstrate Curveball 1 (CISO Security Audit):
**Action:** Click the gold button in the top right: **`Verify Governance Controls`**.

**What to Say:**
> *"The CISO asked: 'How do you stop prompt injection and protect patient data?'  
> When we click **Verify Governance Controls**, you can see our automated controls:  
> - **ISO 42001 A.7:** Our code actively detects and rejects personal patient medical data (EDC fields).  
> - **ISO 42001 A.8:** Candidate extraction uses deterministic sentence parsing, treating text strictly as passive data so prompt injection cannot execute."*

---

## Part 4: The Sponsor Story & Risk Register (6:30 – 8:00)
**Screen to Share:** Switch to your GitHub tab showing [`docs/governance/risk-register.md`](https://github.com/86sunbot/caldera-monitoring-triage/blob/main/docs/governance/risk-register.md).

**What to Say:**
> *"At 1:00 PM, our sponsor had FOMO because a competitor claimed to have an AI risk-scoring model running for 8 months.  
> We gave a Level 5 reframe: that competitor is sitting on an uninspected regulatory liability. If an FDA auditor asks them how a site was chosen, an unvalidated AI score results in an immediate Form 483 inspection warning. What we built for Caldera is safe, unranked, and inspection-ready today.*  
>  
> *In our risk register, every single risk marked as **Treated** (R-01 to R-07) points to a real test in our repository. We have 8 automated tests running in GitHub CI with 100% core coverage."*

---

## Part 5: Scope Discipline — What We Would Do Next (8:00 – 9:00)
**What to Say:**
> *"In the FDE Operating Model, a project is never 100% done on Day 1. Every deferral was a conscious decision with an audit trail:  
> 1. Today we processed digital text only. In Phase 2, we will build the OCR pipeline for the 8% scanned paper reports that we intentionally deferred today under risk **R-06**.  
> 2. We will work with Caldera's Data Privacy Officer to establish formal cross-border transfer agreements for the two restricted trial sites."*

---

## Part 6: Wrap-up & Q&A (9:00 – 10:00)
**What to Say:**
> *"To summarize: we didn't just write code—we delivered working software, defended the GxP boundary, beat all three curveballs, and proved every claim with automated tests.*  
>  
> *Thank you. We welcome any questions!"*

---

## 📋 Trainer Q&A Cheat Sheet

| If the Trainer Asks... | You Answer... |
| :--- | :--- |
| **"Why didn't you add High / Low risk tags?"** | *"Because in clinical trials, a risk tag is a pseudo-score under 21 CFR Part 11, triggering 9 to 12 months of legal validation delay. We leave prioritization to the human monitor."* |
| **"Where is the code proof for patient data rejection?"** | *"In `tests/test_controls.py`, test `test_edc_boundary_enforced`. It deliberately feeds patient data and proves the system blocks it."* |
| **"What did you do when the API failed at 15:00?"** | *"We returned status DEGRADED, held unverified files in staging, and tracked it as risk R-04 with tests in `tests/test_curveball_degradation.py`."* |
