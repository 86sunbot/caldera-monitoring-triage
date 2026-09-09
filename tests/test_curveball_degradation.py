"""
Curveball 3 Resilience Test (15:00 Dependency Degradation).
EVIDENCE FOR R-04 & ISO 42001 A.10 (Third-Party Relationships).

Verifies that when upstream external dependencies (eTMF / Site Registry)
return HTTP 500 server errors, the system:
1. Does not enter an infinite retry loop or crash.
2. Degrades gracefully and produces defensible output.
3. Transparently discloses the degradation to the human clinical reviewer.
"""

from src.clients.etmf_client import ETMFClient
from src.clients.site_registry import SiteRegistryClient
from src.pipeline.triage_graph import MonitoringTriagePipeline


def test_graceful_degradation_on_etmf_500():
    """
    Simulates eTMF Document API returning HTTP 500.
    System must fail safe, mark system_status as DEGRADED, and issue user notice.
    """
    failing_etmf = ETMFClient(simulate_500=True)
    pipeline = MonitoringTriagePipeline(etmf_client=failing_etmf)

    output = pipeline.run([{"dummy": "data"}])

    assert output.system_status == "DEGRADED"
    assert len(output.degradation_notices) == 1
    assert "UPSTREAM FAILURE: eTMF Document API encountered error" in output.degradation_notices[0]
    assert len(output.processed_sites) == 0


def test_graceful_degradation_on_site_registry_500():
    """
    Simulates Site Registry API returning HTTP 500.
    System must fail-closed on unverified regions, hold documents in staging,
    and alert the reviewer without crashing the entire batch.
    """
    failing_registry = SiteRegistryClient(simulate_500=True)
    pipeline = MonitoringTriagePipeline(site_registry=failing_registry)

    sample_doc = [{
        "document_id": "MVR-REG-FAIL-001",
        "site_id": "SITE-101",
        "visit_date": "2024-04-01",
        "monitor_name": "Resilience CRA",
        "pages": {"1": "Test content"}
    }]

    output = pipeline.run(sample_doc)

    assert output.system_status == "DEGRADED"
    assert len(output.degradation_notices) == 1
    assert "COMPLIANCE GATE DEGRADED: Site Registry lookup failed" in output.degradation_notices[0]
    # Fail-closed: document is held in exclusions rather than ingested unsafely
    assert len(output.exclusions) == 1
    assert "Fail-closed hold" in output.exclusions[0].reason
    assert len(output.processed_sites) == 0


def test_partial_etmf_outage_coverage_disclosure():
    """
    EVIDENCE FOR DROP 3 (15:00 eTMF API Outage) & RISK R-04:
    Simulates eTMF returning HTTP 500 for a subset of studies (11 of 20 reports retrieved).
    Proves:
    1. System does not crash or infinite-retry.
    2. Review packet marks system_status as DEGRADED and is_partial_dataset as True.
    3. Mandatory data completeness warning is emitted cautioning against false reassurance.
    4. Per-site coverage ratio (e.g. '3 of 6 reports') discloses the denominator.
    """
    import json
    from pathlib import Path

    fixture_path = Path("data/sample_reports/twenty_reports.json")
    with open(fixture_path, "r") as f:
        raw_reports = json.load(f)

    assert len(raw_reports) == 20

    # Simulate 11 of 20 successful retrievals before eTMF 500 errors occur
    partial_etmf = ETMFClient(simulate_partial_500=True, successful_doc_limit=11)
    pipeline = MonitoringTriagePipeline(etmf_client=partial_etmf)

    output = pipeline.run(raw_reports)

    # 1. Defensible degradation status
    assert output.system_status == "DEGRADED"
    assert output.is_partial_dataset is True
    assert output.reports_expected == 20
    assert output.reports_retrieved == 11

    # 2. Honest user communication (Casebook requirement)
    assert output.data_completeness_warning is not None
    assert "ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE" in output.data_completeness_warning
    assert "11 of 20 reports" in output.data_completeness_warning

    # 3. Denominator disclosure per site
    assert len(output.processed_sites) >= 1
    site_101 = next(s for s in output.processed_sites if s.site_id == "SITE-101")
    assert site_101.total_reports_expected == 6
    assert site_101.coverage_ratio is not None
    assert "of 6 reports" in site_101.coverage_ratio
