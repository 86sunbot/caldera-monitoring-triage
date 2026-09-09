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
