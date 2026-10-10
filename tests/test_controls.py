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
        "reports_expected",
        "reports_retrieved",
        "is_partial_dataset",
        "data_completeness_warning",
        "processed_sites",
        "exclusions",
        "degradation_notices"
    }
    assert set(TriageOutput.model_fields.keys()) == allowed_fields
    # Explicit check: strictly forbidden to contain scores or ranks
    for field in TriageOutput.model_fields.keys():
        assert "score" not in field.lower()
        assert "rank" not in field.lower()
        assert "priority" not in field.lower()


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


def test_ai_studio_client_fallback_when_unconfigured():
    """
    EVIDENCE FOR AI STUDIO RESILIENCE & ISO 42001 A.10:
    Proves that if Google AI Studio is preferred but unconfigured (no API key),
    the system logs a warning and falls back safely to the deterministic regex engine.
    """
    from src.clients.ai_studio_client import GoogleAIStudioClient
    from src.pipeline.extractor import ClinicalObservationExtractor

    unconfigured_client = GoogleAIStudioClient(api_key="")
    assert unconfigured_client.is_configured() is False

    extractor = ClinicalObservationExtractor(
        ai_studio_client=unconfigured_client,
        prefer_ai_studio=True
    )

    sample_doc = [{
        "document_id": "MVR-AI-FALLBACK-01",
        "site_id": "SITE-101",
        "visit_date": "2024-03-01",
        "monitor_name": "Verifier CRA",
        "pages": {
            "1": "Delegation of authority log missing study coordinator signature."
        }
    }]
    pipeline = MonitoringTriagePipeline(extractor=extractor)
    output = pipeline.run(sample_doc)

    assert len(output.processed_sites) == 1
    site = output.processed_sites[0]
    assert site.themes[0].theme == "Staff Training & Delegation"
    assert "Delegation of authority" in site.themes[0].observations[0].citation.verbatim_sentence


def test_citation_validation_rejects_invalid_quotes_and_wrong_page_attribution(monkeypatch):
    """
    REGRESSION TEST FOR ISO 42001 A.8 CITATION GROUNDING:
    Verifies that both GoogleAIStudioClient.extract_candidates and SourceCitation.verify_against_report:
    1. Accept a verbatim quote attributed to the exact page where it appears.
    2. Reject a fabricated or paraphrased quote not present verbatim in the source page.
    3. Reject an empty or whitespace-only quote.
    4. Reject a verbatim quote when attributed to the wrong page number (e.g. text on page 1 cited as page 2 or page 99).
    5. Reject a verbatim quote when attributed to the wrong document_id.
    """
    import io
    import json
    import urllib.request
    from pydantic import ValidationError
    from src.models import MonitoringReport, SourceCitation
    from src.clients.ai_studio_client import GoogleAIStudioClient

    report = MonitoringReport(
        document_id="MVR-GROUNDING-01",
        site_id="SITE-101",
        visit_date="2024-05-10",
        monitor_name="Verifier CRA",
        pages={
            1: "Informed consent form was signed prior to any study procedures.",
            2: "Investigational product dispensing log was reviewed with the site pharmacist.",
        },
    )

    # 1. Direct SourceCitation.verify_against_report checks
    valid_citation = SourceCitation(
        document_id="MVR-GROUNDING-01",
        page_number=1,
        verbatim_sentence="Informed consent form was signed prior to any study procedures.",
    )
    assert valid_citation.verify_against_report(report) is True

    # Paraphrased / fabricated quote on valid page -> False
    paraphrased_citation = SourceCitation(
        document_id="MVR-GROUNDING-01",
        page_number=1,
        verbatim_sentence="Patient signed the consent form before procedures began.",
    )
    assert paraphrased_citation.verify_against_report(report) is False

    # Empty / whitespace quote -> False
    empty_citation = SourceCitation(
        document_id="MVR-GROUNDING-01",
        page_number=1,
        verbatim_sentence="   ",
    )
    assert empty_citation.verify_against_report(report) is False

    # Verbatim quote from Page 1 misattributed to Page 2 -> False
    wrong_page_citation = SourceCitation(
        document_id="MVR-GROUNDING-01",
        page_number=2,
        verbatim_sentence="Informed consent form was signed prior to any study procedures.",
    )
    assert wrong_page_citation.verify_against_report(report) is False

    # Verbatim quote from Page 1 misattributed to non-existent Page 99 -> False
    nonexistent_page_citation = SourceCitation(
        document_id="MVR-GROUNDING-01",
        page_number=99,
        verbatim_sentence="Informed consent form was signed prior to any study procedures.",
    )
    assert nonexistent_page_citation.verify_against_report(report) is False

    # Verbatim quote from Page 1 misattributed to wrong document_id -> False
    wrong_doc_citation = SourceCitation(
        document_id="MVR-OTHER-99",
        page_number=1,
        verbatim_sentence="Informed consent form was signed prior to any study procedures.",
    )
    assert wrong_doc_citation.verify_against_report(report) is False

    # SourceCitation immutability check (frozen=True)
    with pytest.raises(ValidationError):
        valid_citation.verbatim_sentence = "Tampered quote"

    # 2. GoogleAIStudioClient end-to-end filtering of mocked LLM output
    mock_llm_items = [
        # Valid: exact quote on page 1
        {
            "page_number": 1,
            "verbatim_sentence": "Informed consent form was signed prior to any study procedures.",
            "theme": "Informed Consent",
        },
        # Invalid quote: paraphrased text on page 1
        {
            "page_number": 1,
            "verbatim_sentence": "The ICF was signed before study procedures.",
            "theme": "Informed Consent",
        },
        # Invalid page attribution: exact quote from page 1 attributed to page 2
        {
            "page_number": 2,
            "verbatim_sentence": "Informed consent form was signed prior to any study procedures.",
            "theme": "Informed Consent",
        },
        # Invalid page attribution: exact quote from page 2 attributed to non-existent page 5
        {
            "page_number": 5,
            "verbatim_sentence": "Investigational product dispensing log was reviewed with the site pharmacist.",
            "theme": "Investigational Product & Accountability",
        },
    ]

    fake_response_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": json.dumps(mock_llm_items)}]
                }
            }
        ]
    }

    class DummyHTTPResponse(io.BytesIO):
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    def fake_urlopen(req, timeout=30):
        return DummyHTTPResponse(json.dumps(fake_response_payload).encode("utf-8"))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    client = GoogleAIStudioClient(api_key="test-synthetic-key")
    extracted = client.extract_candidates(report)

    assert len(extracted) == 1
    assert extracted[0].citation.page_number == 1
    assert extracted[0].citation.verbatim_sentence == "Informed consent form was signed prior to any study procedures."


def test_pipeline_drops_unverified_citations_from_custom_extractor():
    """
    REGRESSION TEST FOR PIPELINE CITATION GATE:
    Verifies that MonitoringTriagePipeline.run filters out any observation returned by an
    extractor whose citation fails verify_against_report (e.g., wrong page or wrong document_id).
    """
    class FaultyExtractor:
        def extract_from_report(self, report):
            return [
                # Valid observation on page 1
                CandidateObservation(
                    observation_id="OBS-VALID-1",
                    site_id=report.site_id,
                    visit_date=report.visit_date,
                    theme="Temperature Monitoring",
                    citation=SourceCitation(
                        document_id=report.document_id,
                        page_number=1,
                        verbatim_sentence="Fridge log showed a temperature excursion on Tuesday.",
                    ),
                ),
                # Misattributed page (sentence is on page 1, cited as page 2)
                CandidateObservation(
                    observation_id="OBS-WRONG-PAGE",
                    site_id=report.site_id,
                    visit_date=report.visit_date,
                    theme="Temperature Monitoring",
                    citation=SourceCitation(
                        document_id=report.document_id,
                        page_number=2,
                        verbatim_sentence="Fridge log showed a temperature excursion on Tuesday.",
                    ),
                ),
                # Fabricated quote not in report
                CandidateObservation(
                    observation_id="OBS-FABRICATED",
                    site_id=report.site_id,
                    visit_date=report.visit_date,
                    theme="Temperature Monitoring",
                    citation=SourceCitation(
                        document_id=report.document_id,
                        page_number=1,
                        verbatim_sentence="Freezer failed completely for 48 hours.",
                    ),
                ),
            ]

    sample_doc = [{
        "document_id": "MVR-PIPE-GATE-01",
        "site_id": "SITE-101",
        "visit_date": "2024-06-01",
        "monitor_name": "Verifier CRA",
        "pages": {
            "1": "Fridge log showed a temperature excursion on Tuesday.",
            "2": "All routine laboratory kits were accounted for.",
        },
    }]

    pipeline = MonitoringTriagePipeline(extractor=FaultyExtractor())
    output = pipeline.run(sample_doc)

    assert len(output.processed_sites) == 1
    site = output.processed_sites[0]
    assert len(site.themes) == 1
    observations = site.themes[0].observations
    assert len(observations) == 1
    assert observations[0].observation_id == "OBS-VALID-1"
