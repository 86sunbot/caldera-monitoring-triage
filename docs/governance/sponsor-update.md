# Caldera Therapeutics · 13:00 Sponsor Update (One-Pager & Script)
### Audience: VP Clinical Operations (Role-played by Pod Mentor) · Format: 5 Minutes, Spoken, No Slides

> **Mentor Role-Play Context**: The VP Clinical Operations accepted yesterday's reframe to "surfacing", but this morning spoke with a peer at another pharma company who claimed they have *"the predictive risk score thing running already"*. Expect the VP to challenge you: *"Why aren't we building the predictive model?"*

---

## 5-Minute Spoken Delivery Script

### 0:00 – 0:45 | Where We Are Against What We Agreed
> *"Good afternoon. Today we are delivering the core monitoring report triage engine for Caldera's active studies. Right now, the system successfully ingests monitoring visit reports, extracts candidate operational signals with exact page and sentence references, and groups them by site so your clinical monitors can immediately see recurring issues across visits without reading 40-page PDFs front-to-back."*

### 0:45 – 2:00 | What Has Changed Since Yesterday (Addressing the "Predictive" Peer)
> *"I want to address something directly. You may hear from peers at other sponsors that they are 'running predictive risk scoring'. Here is why the surfacing system we are building today is better for Caldera:*  
> *If we assign a predictive risk score—like flagging a site as 'High Risk' or predicting protocol non-compliance—that score enters the **GxP-validated estate under 21 CFR Part 11**. That immediately triggers 9 to 12 months of Computerized System Validation, IQ/OQ/PQ audits, and regulatory scrutiny before a single monitor can touch it.*  
> *What we are building stays strictly outside the GxP validation boundary. It makes no automated calls, applies no black-box scores, and leaves the clinical decision with your qualified monitors. That is how we get working triage into your monitors' hands this quarter instead of next year."*

### 2:00 – 3:30 | What Is At Risk (Clear & Business-Specific)
> *"We are managing two specific risks right now:*  
> 1. **Data Sovereignty Risk (R-02)**: *Four reports in our test sample originate from sites in restricted overseas jurisdictions. Ingesting their text without executed data transfer agreements creates regulatory exposure under cross-border data transfer laws. We have implemented an automated pre-ingestion gate that drops and logs these reports rather than processing them unsafely.*  
> 2. **Scanned PDF Coverage (R-06)**: *Approximately 8% of historical monitoring reports are scanned paper copies. Today's build processes digital text only; OCR is deferred. Those scanned files will be routed to manual CRA review until our Phase 2 OCR pipeline is online."*

### 3:30 – 4:15 | What We Need From You (The Specific Ask)
> *"We need two specific actions from you:*  
> 1. **A formal sign-off** that Caldera's deployment strategy is 'surfacing triage for monitors' and will not seek predictive scoring in Phase 1, protecting our non-GxP timeline.  
> 2. **An introduction to your Data Privacy Officer** to confirm the list of authorized trial site countries so our automated jurisdiction gate reflects your legal agreements."*

### 4:15 – 5:00 | What Happens Next
> *"By 16:00 today, our repository will be frozen with a working end-to-end slice running across 20 reports, complete with an automated test suite proving zero scoring and 100% sentence provenance. At 16:15, we will demo the live triage packet showing a recurring informed consent signal at Site 101."*

---

## Appendix B Table Summary (For the Record)

| Section | Your Content |
| :--- | :--- |
| **Where we are** | Working end-to-end slice ingesting 20 reports, extracting candidate observations with page/sentence citations, and grouping by site and theme. |
| **What changed since yesterday** | Defended the GxP boundary: explicitly rejected predictive risk scores to protect the 3-month launch timeline vs. a 12-month CSV cycle. |
| **Risk 1 — what it is, cost, mitigation** | **Data Sovereignty (R-02)**: Cross-border transfer fines; pre-processing gate drops restricted sites into audit log. |
| **Risk 2 — what it is, cost, mitigation** | **Scanned PDF Gap (R-06)**: 8% of documents unparsed; explicitly deferred OCR and routed to manual CRA review. |
| **What we need from you** | 1. Affirmation of the non-predictive scope. 2. Intro to DPO for approved site country list. |
| **What happens next** | Code freeze at 16:00; live execution demo at 16:15 showing recurring cross-visit signals at Site 101. |
