"""
Generate Caldera FDE Presentation Deck (.pptx)
Generates an 8-slide executive presentation on:
'Factored by Design vs. Reacted by Reflex: The Caldera FDE Lesson'
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Colors
    BG_COLOR = RGBColor(15, 23, 42)      # #0F172A
    CARD_BG = RGBColor(30, 41, 59)       # #1E293B
    TEXT_MAIN = RGBColor(248, 250, 252)  # #F8FAFC
    TEXT_MUTED = RGBColor(148, 163, 184)# #94A3B8
    ACCENT_GREEN = RGBColor(16, 185, 129)# #10B981
    ACCENT_BLUE = RGBColor(56, 189, 248) # #38BDF8
    ACCENT_AMBER = RGBColor(245, 158, 11)# #F59E0B
    ACCENT_ROSE = RGBColor(244, 63, 94)  # #F43F5E
    CARD_BORDER = RGBColor(51, 65, 85)   # #334155

    def set_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1)
        else:
            card.line.fill.background()
        return card

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    # Badge
    b1 = add_card(s1, Inches(1.0), Inches(1.0), Inches(3.2), Inches(0.4), bg_color=RGBColor(6, 78, 59), border_color=ACCENT_GREEN)
    tf_b1 = b1.text_frame
    tf_b1.text = "CALDERA THERAPEUTICS · TEAM 2"
    tf_b1.paragraphs[0].font.size = Pt(11)
    tf_b1.paragraphs[0].font.bold = True
    tf_b1.paragraphs[0].font.color.rgb = ACCENT_GREEN
    tf_b1.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Title
    txBox = s1.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(11.333), Inches(2.2))
    tf = txBox.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "Factored by Design"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_MAIN

    p2 = tf.add_paragraph()
    p2.text = "vs. Reacted by Reflex"
    p2.font.size = Pt(44)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_BLUE

    p3 = tf.add_paragraph()
    p3.text = "The Forward Deployed Engineering (FDE) Architecture & Governance Defense"
    p3.font.size = Pt(18)
    p3.font.color.rgb = TEXT_MUTED

    # 3 Summary Cards
    card_w = Inches(3.5)
    card_h = Inches(2.2)
    top_y = Inches(4.2)

    # Card 1
    c1 = add_card(s1, Inches(1.0), top_y, card_w, card_h)
    tf_c1 = c1.text_frame
    tf_c1.word_wrap = True
    p = tf_c1.paragraphs[0]
    p.text = "11:00 AM · CISO AUDIT"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p = tf_c1.add_paragraph()
    p.text = "Prompt Injection & EDC Barrier"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p = tf_c1.add_paragraph()
    p.text = "Decided passive tokenization at 09:15. Document text is passive payload, never executable instructions. Pydantic schema firewall actively drops EDC."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    # Card 2
    c2 = add_card(s1, Inches(4.9), top_y, card_w, card_h)
    tf_c2 = c2.text_frame
    tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]
    p.text = "13:00 PM · SPONSOR FOMO"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf_c2.add_paragraph()
    p.text = "Competitor Risk-Scoring Claim"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p = tf_c2.add_paragraph()
    p.text = "Reframed via ADR-001: Competitor carries an uninspected 21 CFR Part 11 / GxP liability. Our unranked system stays outside the 12-month CSV audit freeze."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    # Card 3
    c3 = add_card(s1, Inches(8.8), top_y, card_w, card_h)
    tf_c3 = c3.text_frame
    tf_c3.word_wrap = True
    p = tf_c3.paragraphs[0]
    p.text = "15:00 PM · VENDOR 500"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ROSE
    p = tf_c3.add_paragraph()
    p.text = "11/20 Outage & Denominators"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p = tf_c3.add_paragraph()
    p.text = "Overrode 5x retry loop. Enforced mandatory denominator disclosure: '3 of 6 reports - PARTIAL' and statutory warning: Absence of evidence is not evidence of absence."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: Junior vs FDE Mindset
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)

    txBox = s2.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "FOUNDATIONAL PARADIGM"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "The Scramble Loop vs. The Absorbing Boundary"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    # 2 Comparison Columns
    col_w = Inches(5.4)
    col_h = Inches(4.6)

    # Column Left: Reactive
    col1 = add_card(s2, Inches(1.0), Inches(2.0), col_w, col_h, bg_color=RGBColor(38, 20, 26), border_color=ACCENT_ROSE)
    tf_col1 = col1.text_frame
    tf_col1.word_wrap = True
    p = tf_col1.paragraphs[0]
    p.text = "THE JUNIOR REFLEX: REACTIVE PATCHING"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ROSE
    items_left = [
        ("✕ Happy Path Assumption:", "Assumes APIs return 200 OK, clients know what they want, and regulations are ignorable."),
        ("✕ Surprise as Interruption:", "Treats security questions, vendor errors, and sponsor anxieties as rude surprises."),
        ("✕ Emergency Scrambling:", "Patches symptoms at runtime: adds hasty regexes, infinite retry loops, and unvalidated pseudo-scores."),
        ("✕ The Cost:", "Compromises system boundaries, introduces fatal false reassurance, and causes 9-12 month regulatory stalls.")
    ]
    for title, desc in items_left:
        p = tf_col1.add_paragraph()
        p.text = f"{title} {desc}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MUTED

    # Column Right: FDE
    col2 = add_card(s2, Inches(6.9), Inches(2.0), col_w, col_h, bg_color=RGBColor(15, 39, 35), border_color=ACCENT_GREEN)
    tf_col2 = col2.text_frame
    tf_col2.word_wrap = True
    p = tf_col2.paragraphs[0]
    p.text = "THE FDE DISCIPLINE: ANTICIPATORY ARCHITECTURE"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    items_right = [
        ("✓ Hostile Reality by Design:", "Assumes from 09:15 that external vendors will fail, regulations bite, and clients experience FOMO."),
        ("✓ Scope Discipline as Shield:", "Spent the first 45 minutes locking what NOT to build (no predictive scores, no patient PHI)."),
        ("✓ Pre-Compiled Shock Absorbers:", "Pydantic schema firewalls, decoupled graph stages, and explicit metadata contracts."),
        ("✓ Empirical Git Audit Trail:", "Every treated risk in risk-register.md is tied to a passing test. Empty intentions score zero.")
    ]
    for title, desc in items_right:
        p = tf_col2.add_paragraph()
        p.text = f"{title} {desc}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 3: Curveball 1 Deep Dive (CISO)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)

    txBox = s3.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "11:00 AM · CISO SECURITY AUDIT"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p = tf.add_paragraph()
    p.text = "Curveball 1: Prompt Injection & Patient EDC Boundary"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    # Question Box
    q_box = add_card(s3, Inches(1.0), Inches(2.0), Inches(11.333), Inches(1.1), bg_color=RGBColor(45, 35, 20), border_color=ACCENT_AMBER)
    tf_q = q_box.text_frame
    tf_q.word_wrap = True
    p = tf_q.paragraphs[0]
    p.text = "CISO AUDIT INQUIRY (DUE 14:00):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p = tf_q.add_paragraph()
    p.text = "\"Hospital reports are authored by third-party monitors. What stops prompt injection? And prove you are not ingesting Electronic Data Capture (EDC) patient records.\""
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_MAIN

    # 2 Answer Boxes
    a1 = add_card(s3, Inches(1.0), Inches(3.4), Inches(5.5), Inches(3.2))
    tf_a1 = a1.text_frame
    tf_a1.word_wrap = True
    p = tf_a1.paragraphs[0]
    p.text = "1. Passive Tokenization (Prompt Injection Defense)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf_a1.add_paragraph()
    p.text = "• We never embed raw document text into executable LLM instructions.\n• Candidate sentences are tokenized as purely passive string data stored in immutable SourceCitation objects.\n• You cannot execute prompt injections on a system that does not interpret input documents as instructions.\n• Documented in threat-model.md under ISO 42001 A.8."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    a2 = add_card(s3, Inches(6.8), Inches(3.4), Inches(5.5), Inches(3.2))
    tf_a2 = a2.text_frame
    tf_a2.word_wrap = True
    p = tf_a2.paragraphs[0]
    p.text = "2. Code-Level Schema Barrier (EDC Privacy Defense)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf_a2.add_paragraph()
    p.text = "• Pydantic models in src/models.py actively validate input keys and raise ValidationError if patient fields (subject_id, edc_id, lab_values) appear.\n• Restricted payloads are dropped before processing.\n• Empirical Proof: tests/test_controls.py::test_edc_boundary_enforced passes in CI.\n• Mapped to ISO 42001 A.7 in risk-register.md (R-07)."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 4: Curveball 2 Deep Dive (Sponsor FOMO)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)

    txBox = s4.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "13:00 PM · SCOPE & REGULATORY DEFENSE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "Curveball 2: Sponsor FOMO & Defending the GxP Boundary"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    # Question Box
    q_box = add_card(s4, Inches(1.0), Inches(2.0), Inches(11.333), Inches(1.1), bg_color=RGBColor(25, 35, 55), border_color=ACCENT_BLUE)
    tf_q = q_box.text_frame
    tf_q.word_wrap = True
    p = tf_q.paragraphs[0]
    p.text = "SPONSOR CHALLENGE (13:00):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf_q.add_paragraph()
    p.text = "\"A competitor at a conference claims they have an AI predictive risk-scoring model running across their hospitals for 8 months! Why are you giving me less?\""
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_MAIN

    # Level 5 Reframe
    ref = add_card(s4, Inches(1.0), Inches(3.4), Inches(11.333), Inches(1.4), bg_color=RGBColor(20, 30, 45), border_color=ACCENT_GREEN)
    tf_ref = ref.text_frame
    tf_ref.word_wrap = True
    p = tf_ref.paragraphs[0]
    p.text = "THE LEVEL 5 FDE REFRAME (DELIVERED TO SPONSOR):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf_ref.add_paragraph()
    p.text = "\"The competitor hasn't beaten us; they are sitting on an uninspected regulatory time bomb. In clinical trials, an automated risk score triggers 21 CFR Part 11 / GxP Computerized System Validation (CSV), requiring 9 to 12 months of legal audits. If an FDA inspector asks how a site was chosen and they show an unvalidated AI score, it triggers an immediate Form 483 violation. We built an inspection-ready reading assistant that can be deployed today.\""
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MAIN

    # 2 Bottom Cards
    b1 = add_card(s4, Inches(1.0), Inches(5.1), Inches(5.5), Inches(1.6))
    tf_b1 = b1.text_frame
    tf_b1.word_wrap = True
    p = tf_b1.paragraphs[0]
    p.text = "Locked at 09:15 via ADR-001"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p = tf_b1.add_paragraph()
    p.text = "We anticipated this exact regulatory trap before writing code. 'Surfacing, Not Predicting' was our founding charter."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    b2 = add_card(s4, Inches(6.8), Inches(5.1), Inches(5.5), Inches(1.6))
    tf_b2 = b2.text_frame
    tf_b2.word_wrap = True
    p = tf_b2.paragraphs[0]
    p.text = "Zero-Score Code Contract"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p = tf_b2.add_paragraph()
    p.text = "test_zero_scoring_or_ranking asserts no numeric scores, tiers, or priority fields exist. Governed by risk R-01 in risk-register.md."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 5: Curveball 3 Deep Dive (Drop 3 eTMF)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)

    txBox = s5.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "15:00 PM · DROP 3 OF 3 EXTERNAL OUTAGE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ROSE
    p = tf.add_paragraph()
    p.text = "Curveball 3: eTMF 500 Outage & Denominator Honesty"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    # Bite Box
    bite_box = add_card(s5, Inches(1.0), Inches(2.0), Inches(11.333), Inches(1.3), bg_color=RGBColor(45, 20, 25), border_color=ACCENT_ROSE)
    tf_bite = bite_box.text_frame
    tf_bite.word_wrap = True
    p = tf_bite.paragraphs[0]
    p.text = "WHERE THIS BITES (DROP 3 PROMPT):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ROSE
    p = tf_bite.add_paragraph()
    p.text = "\"A grouping view built on 11 of 20 reports looks identical to one built on 20. A clinical reviewer would draw conclusions from the gaps. 'Three visits mention this' is a different statement when you could only read half the visits.\""
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_MAIN

    # 3 Response Pillars
    pw = Inches(3.5)
    ph = Inches(3.3)
    py = Inches(3.6)

    p1_card = add_card(s5, Inches(1.0), py, pw, ph)
    tf_p1 = p1_card.text_frame
    tf_p1.word_wrap = True
    p = tf_p1.paragraphs[0]
    p.text = "1. Rejected Retry Loop"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ROSE
    p = tf_p1.add_paragraph()
    p.text = "AI proposed a 5x retry loop. We overrode it in the review log.\n\nA retry loop freezes CRA workflows and masks the outage. When an outage is regional, retries will never fix it. Defensible systems degrade gracefully."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    p2_card = add_card(s5, Inches(4.9), py, pw, ph)
    tf_p2 = p2_card.text_frame
    tf_p2.word_wrap = True
    p = tf_p2.paragraphs[0]
    p.text = "2. Statutory Warning"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p = tf_p2.add_paragraph()
    p.text = "Review packet forces an unavoidable amber warning:\n\n'ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE: Conclusions regarding clean site conduct cannot be drawn for unretrieved visits.'"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    p3_card = add_card(s5, Inches(8.8), py, pw, ph)
    tf_p3 = p3_card.text_frame
    tf_p3.word_wrap = True
    p = tf_p3.paragraphs[0]
    p.text = "3. Denominator Disclosure"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf_p3.add_paragraph()
    p.text = "Displays exact coverage denominators across all headers:\n\n• Packet: 11 of 20 reports\n• Site 101: 3 of 6 reports - PARTIAL\n\nVerified by test_partial_etmf_outage_coverage_disclosure under R-04."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 6: The 3 Architectural Shock Absorbers
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)

    txBox = s6.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "SYSTEM ARCHITECTURE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "The 3 Pre-Existing Shock Absorbers"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    sw = Inches(3.5)
    sh = Inches(4.5)
    sy = Inches(2.2)

    s1_box = add_card(s6, Inches(1.0), sy, sw, sh)
    tf_s1 = s1_box.text_frame
    tf_s1.word_wrap = True
    p = tf_s1.paragraphs[0]
    p.text = "01"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf_s1.add_paragraph()
    p.text = "Schema Firewalls"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p = tf_s1.add_paragraph()
    p.text = "• Pydantic models at boundaries enforce immutable field types.\n• Prohibits risk scores and priority tiers.\n• Actively rejects EDC patient identifiers.\n• Requires document_id, page_number, and verbatim_sentence on every observation.\n\nEvidence: src/models.py"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    s2_box = add_card(s6, Inches(4.9), sy, sw, sh)
    tf_s2 = s2_box.text_frame
    tf_s2.word_wrap = True
    p = tf_s2.paragraphs[0]
    p.text = "02"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf_s2.add_paragraph()
    p.text = "State Graph Pipeline"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p = tf_s2.add_paragraph()
    p.text = "• Decoupled pipeline stages allow isolated failure containment.\n• Regional gate drops Site 404 before parsing.\n• Extraction runs deterministically.\n• Degradation handler outputs stateful operational metadata (reports_expected, reports_retrieved).\n\nEvidence: src/pipeline/triage_graph.py"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    s3_box = add_card(s6, Inches(8.8), sy, sw, sh)
    tf_s3 = s3_box.text_frame
    tf_s3.word_wrap = True
    p = tf_s3.paragraphs[0]
    p.text = "03"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = RGBColor(168, 85, 247)
    p = tf_s3.add_paragraph()
    p.text = "Empirical Risk Register"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p = tf_s3.add_paragraph()
    p.text = "• Every risk in risk-register.md is tied to a real test in /tests.\n• Status 'Treated' is forbidden without code evidence.\n• 9 automated tests passing in CI.\n• ISO 42001 objectives (A.2 - A.10) verified by test assertions.\n\nEvidence: docs/governance/risk-register.md"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: The 3 Enduring FDE Lessons
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)

    txBox = s7.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "RETROSPECTIVE & WISDOM"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "The 3 Enduring FDE Lessons"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    lw = Inches(11.333)
    lh = Inches(1.3)

    # Lesson 1
    l1 = add_card(s7, Inches(1.0), Inches(2.2), lw, lh)
    tf_l1 = l1.text_frame
    tf_l1.word_wrap = True
    p = tf_l1.paragraphs[0]
    p.text = "1. BOUNDARIES OVER FEATURES"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf_l1.add_paragraph()
    p.text = "The quality of enterprise AI is defined not by what it hallucinates or generates, but by what its perimeter actively refuses to ingest or output. We rejected predictive scores, patient PHI, and unverified sovereign regions before reading a single report."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # Lesson 2
    l2 = add_card(s7, Inches(1.0), Inches(3.7), lw, lh)
    tf_l2 = l2.text_frame
    tf_l2.word_wrap = True
    p = tf_l2.paragraphs[0]
    p.text = "2. REJECTION OVER ACCRETION"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf_l2.add_paragraph()
    p.text = "When a stakeholder panics or a competitor boasts, junior engineers add features; FDEs reinforce guardrails. Saying 'No' to risk scores saved Caldera 9–12 months of GxP validation delay."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # Lesson 3
    l3 = add_card(s7, Inches(1.0), Inches(5.2), lw, lh)
    tf_l3 = l3.text_frame
    tf_l3.word_wrap = True
    p = tf_l3.paragraphs[0]
    p.text = "3. DENOMINATOR HONESTY"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p = tf_l3.add_paragraph()
    p.text = "In clinical trials, partial data that looks complete is deadlier than a total crash. Defensible degradation requires surfacing the denominator so human monitors never draw false reassurance from missing visits."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 8: Trainer Defense Matrix
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)

    txBox = s8.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "TRAINER EVALUATION MATRIX"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RGBColor(168, 85, 247)
    p = tf.add_paragraph()
    p.text = "Trainer Defense Cheat Sheet"
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    dw = Inches(11.333)
    dh = Inches(1.1)

    qa1 = add_card(s8, Inches(1.0), Inches(2.1), dw, dh)
    tf_qa1 = qa1.text_frame
    tf_qa1.word_wrap = True
    p = tf_qa1.paragraphs[0]
    p.text = "Trainer: \"Did you anticipate the 15:00 API failure or react to it?\""
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p = tf_qa1.add_paragraph()
    p.text = "Your Answer: \"We anticipated it in our data model and pipeline architecture. At 09:15 we established that external vendor APIs fail. Our schema had reports_expected and reports_retrieved from day one. When Drop 3 hit, we proved the partial state with test_partial_etmf_outage_coverage_disclosure.\""
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MAIN

    qa2 = add_card(s8, Inches(1.0), Inches(3.4), dw, dh)
    tf_qa2 = qa2.text_frame
    tf_qa2.word_wrap = True
    p = tf_qa2.paragraphs[0]
    p.text = "Trainer: \"Why not just retry the 500 error 5 times with backoff?\""
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ROSE
    p = tf_qa2.add_paragraph()
    p.text = "Your Answer: \"Because a retry loop freezes CRA workflows and masks the outage. When an outage is regional, retries won't fix it. The correct FDE design is graceful degradation with mandatory denominator disclosure so reviewers know exactly which visits are missing.\""
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MAIN

    qa3 = add_card(s8, Inches(1.0), Inches(4.7), dw, dh)
    tf_qa3 = qa3.text_frame
    tf_qa3.word_wrap = True
    p = tf_qa3.paragraphs[0]
    p.text = "Trainer: \"How did your design prevent prompt injection without an LLM guardrail?\""
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf_qa3.add_paragraph()
    p.text = "Your Answer: \"By architectural choice: deterministic tokenization and passive extraction. The document text is strictly passive payload data inside a Pydantic object, never embedded into an executable prompt instruction. You cannot inject instructions into an engine that doesn't execute text as instructions.\""
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MAIN

    # Footer banner
    foot = add_card(s8, Inches(1.0), Inches(6.0), dw, Inches(0.6), bg_color=RGBColor(16, 185, 129), border_color=None)
    tf_foot = foot.text_frame
    p = tf_foot.paragraphs[0]
    p.text = "ALL 9 TESTS PASSING IN CI · REPOSITORY: 86sunbot/caldera-monitoring-triage · STATUS: INSPECTION READY"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(15, 23, 42)
    p.alignment = PP_ALIGN.CENTER

    output_path = "docs/Caldera_FDE_Factored_by_Design_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_deck()
