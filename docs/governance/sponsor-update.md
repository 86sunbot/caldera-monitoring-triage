# Caldera Therapeutics · 13:00 Sponsor Update (One-Pager & Script)
### Deliverable for Drop 2: VP Clinical Operations Check-In
**Speaker**: Lead Forward Deployed Engineer (One speaker, 5 minutes, no slides)  
**Recipient**: VP Clinical Operations  
**Artifact Location**: `docs/governance/sponsor-update.md`  
**Target Score**: Level 5 (Surfaces unrecognised regulatory exposure, delivers the uncomfortable truth, and secures executive decision)

---

## 1. Appendix B · Sponsor Update One-Pager

| Section | Your Content |
| :--- | :--- |
| **Where we are** | Thin slice running end-to-end against 20 clinical monitoring visit reports from eTMF. Ingests reports, extracts candidate signals with exact page/sentence citations, enforces a pre-processing regional compliance gate, and groups recurring issues by site and theme. |
| **What changed since yesterday** | Defended the GxP boundary against predictive risk scoring. Addressed the competitor claim: a peer company running unvalidated risk scores for 8 months is carrying severe unrecognised regulatory exposure under 21 CFR Part 11 / ICH E6(R2). Our surfacing architecture delivers immediate operational triage without triggering 9–12 months of Computerized System Validation (CSV). |
| **Risk 1 — what it is, what it costs, what we are doing** | **Cross-Border Data Sovereignty (R-02)**: Ingesting reports from two restricted trial regions without data transfer agreements risks GDPR/local fines and study audit findings. *Cost*: Regulatory enforcement or localized trial suspension. *Action*: Automated pre-ingestion gate drops and logs restricted reports; documents held in staging. |
| **Risk 2 — what it is, what it costs, what we are doing** | **Scanned Paper Report Coverage (R-06)**: 8% of historical monitoring visit reports are scanned images without digital text. *Cost*: Temporary blind spot on legacy trial sites unless manually triaged. *Action*: Explicitly deferred OCR from today's 5-hour slice; routed to manual CRA review; Phase 2 OCR backlog item created. |
| **What we need from you** | 1. **Executive Decision**: Confirm that Caldera will not chase predictive scoring in Phase 1, preserving our non-GxP timeline and inspection safety.<br>2. **DPO Introduction**: Direct connection to your Data Privacy Officer today to establish data transfer pathways for the two restricted trial regions. |
| **What happens next** | Repository frozen at 16:00. At 16:15 close-out, we demo the live triage execution across 20 reports, walking the risk register and proving zero scoring and 100% sentence provenance. |

---

## 2. Five-Minute Spoken Delivery Script (Do Not Read Aloud — Speak From This)

### [0:00 – 0:45] Where We Are Against What We Agreed
> *"Thank you for the five minutes. We are exactly where we agreed to be: we have a working, end-to-end slice running right now on our machines. It ingests 20 real-world clinical monitoring reports from eTMF, extracts operational observations with 100% verbatim sentence and page provenance, and groups them by site so your clinical monitors can spot multi-visit trends in seconds rather than reading 40-page PDFs."*

### [0:45 – 2:00] What Has Changed Since Yesterday (The Competitor Comparison)
> *"I understand your hesitation after hearing about your peer's risk-scoring model running for eight months. I need to tell you an uncomfortable truth about what they have versus what we are building:*  
>  
> *The thing you asked for on Monday is not the thing we are building, and here is why that is better for you.*  
>  
> *In our industry, if an automated model assigns a predictive risk score to a trial site to guide monitoring frequency or audit triage, regulatory agencies—under 21 CFR Part 11 and ICH E6(R2)—classify that algorithm as a computerized system governing trial data integrity. That mandates formal Computerized System Validation (CSV): prospective IQ/OQ/PQ protocols, algorithmic repeatability audits, and change controls taking 9 to 12 months.*  
>  
> *If your peer has had a risk-scoring model running for eight months across their portfolio without a completed GxP CSV package, they haven't outpaced us—they are sitting on an uninspected regulatory liability. In an FDA or EMA audit, when an inspector asks: 'What validated algorithm determined that this site was low risk?', an unvalidated score results in an immediate Form 483 observation or trial hold.*  
>  
> *What we are building is not 'less'. It is smarter. By surfacing candidate observations with exact page citations and zero black-box scoring, the qualified CRA remains the sole decision authority. That keeps this system outside the GxP validated estate, meaning you get working operational triage this quarter—100% inspection-ready—with zero regulatory exposure."*

### [2:00 – 3:30] What Is At Risk (Named in Business Terms)
> *"Four hours into this build, we are carrying two specific risks:*  
>  
> *First: **Data Sovereignty (Risk R-02)**. Four reports in our dataset come from two regions with strict cross-border data export prohibitions. Processing their text outside those jurisdictions risks significant GDPR and local privacy fines. What we are doing: our system includes an automated gate that drops and logs those documents before a single word is parsed. The cost to you is a temporary blind spot on those two sites until legal agreements are in place.*  
>  
> *Second: **Scanned Reports (Risk R-06)**. Approximately 8% of historical monitoring reports are scanned paper PDFs. What we are doing: we explicitly descoped OCR from today's five-hour build. The cost is that those scanned reports require manual CRA review today, which we have scheduled for our Phase 2 OCR sprint."*

### [3:30 – 4:15] What We Need From You (The Specific Asks)
> *"To maintain momentum, we need two specific decisions from you today:*  
> 1. *Affirm our non-predictive scope. Resist the peer pressure for risk scoring so we protect Caldera's inspection posture and keep our delivery date.*  
> 2. *Connect us with your Data Privacy Officer this afternoon so we can resolve the transfer restrictions on those two regions."*

### [4:15 – 5:00] What Happens Next
> *"Our repository freezes at 16:00. At 16:15, we will demo the live system running end-to-end across the 20 reports, show you the audit logs proving the restricted sites were safely held, and walk you through the risk register. Thank you."*
