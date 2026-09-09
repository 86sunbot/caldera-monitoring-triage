"""
Governance Control Verification Tests.
CITATIONS:
- risk-register.md (R-01, R-02, R-03)
- iso42001-mapping.md (A.6, A.7, A.8)

Every test in this file serves as empirical repository evidence that a governance control fires.
"""

import pytest
from src.models import CandidateObservation, SourceCitation, TriageOutput
from src.clients.site_registry import SiteRegistryClient
from src.pipeline.triage_graph import MonitoringTriagePipeline


def test_region_restriction_gate_fires():
    """
    EVIDENCE FOR R-02 & ISO 42001 A.7 (Data Control):
    Proves that documents originating from region-restricted jurisdictions
    are rejected before content extraction and recorded in the audit exclusion log.
    Specifically verifies that the model/extractor is NEVER invoked for restricted files.
    """
    registry = SiteRegistryClient()
    is_restricted, country, reason = registry.is_region_restricted("SITE-404")
    assert is_restricted is True
    assert country == "RESTRICTED_REGION_X"
    assert "Data sovereignty restriction" in reason

    # Pipeline integration: verify document is dropped without processing
    sample_restricted_doc = [{
        "document_id": "MVR-RESTRICTED-001",
        "site_id": "SITE-404",
        "visit_date": "2024-01-01",
        "monitor_name": "Auditor Test",
        "pages": {"1": "This text must never be parsed or extracted."}
    }]
    
    # Spy on extractor to prove it is NEVER invoked on restricted docs
    class SpyExtractor:
        def __init__(self):
            self.invoked = False
        def extract_from_report(self, report):
            self.invoked = True
            return []

    spy = SpyExtractor()
    pipeline = MonitoringTriagePipeline(site_registry=registry, extractor=spy)
    output = pipeline.run(sample_restricted_doc)

    assert len(output.exclusions) == 1
    assert output.exclusions[0].document_id == "MVR-RESTRICTED-001"
    assert output.exclusions[0].site_id == "SITE-404"
    assert len(output.processed_sites) == 0
    # Technical guarantee: extractor/model was never called
    assert spy.invoked is False


def test_edc_boundary_enforced():
    """
    EVIDENCE FOR CISO QUESTION 2 & ISO 42001 A.7:
    Proves that the ingestion schema actively rejects Electronic Data Capture (EDC)
    subject-level clinical data, enforcing the architectural boundary in code.
    """
    from src.models import MonitoringReport

    # Passing subject-level EDC data must raise validation error
    with pytest.raises(ValueError, match="EDC Boundary Violation"):
        MonitoringReport(
            document_id="MVR-FAIL",
            site_id="SITE-101",
            visit_date="2024-01-01",
            monitor_name="Auditor Test",
            pages={"1": "Clean page"},
            subject_initials="J.D.",  # EDC clinical field
            lab_results="ALT 45 U/L"   # EDC clinical field
        )


def test_zero_scoring_or_ranking():
    """
    EVIDENCE FOR R-01 & ISO 42001 A.6 (AI Life Cycle Boundary):
    Proves that the system strictly produces no predictive risk score,
    no severity ranking, and no automated deviation assertion, keeping it
    outside the GxP 21 CFR Part 11 Computerized System Validation boundary.
    """
    # 1. Pydantic validation rejects any pseudo-score attempt
    with pytest.raises(ValueError, match="Governance Violation"):
        CandidateObservation(
            observation_id="OBS-FAIL",
            site_id="SITE-101",
            visit_date="2024-01-01",
            theme="Informed Consent",
            citation=SourceCitation(
                document_id="DOC-1",
                page_number=1,
                verbatim_sentence="Test sentence."
            ),
            risk_level="HIGH"  # Attempting to sneak a score in
        )

    # 2. Assert output schema contains no ranking or score fields
    allowed_fields = {
        "system_status",
        "disclaimer",
        "processed_sites",
        "exclusions",
        "degradation_notices"
    }
    assert set(TriageOutput.model_fields.keys()) == allowed_fields


def test_verbatim_sentence_and_page_provenance():
    """
    EVIDENCE FOR R-03 & ISO 42001 A.8 (Transparency & Traceability):
    Proves that every candidate observation retains verbatim text citation,
    exact page number, and source document ID for reviewer inspection.
    """
    sample_doc = [{
        "document_id": "MVR-VERIFY-01",
        "site_id": "SITE-101",
        "visit_date": "2024-03-01",
        "monitor_name": "Verifier CRA",
        "pages": {
            "4": "Fridge log indicated a temporary temperature excursion of +12C over the weekend."
        }
    }]
    pipeline = MonitoringTriagePipeline()
    output = pipeline.run(sample_doc)

    assert len(output.processed_sites) == 1
    site = output.processed_sites[0]
    assert len(site.themes) == 1
    obs = site.themes[0].observations[0]

    assert obs.citation.document_id == "MVR-VERIFY-01"
    assert obs.citation.page_number == 4
    assert obs.citation.verbatim_sentence == "Fridge log indicated a temporary temperature excursion of +12C over the weekend."
