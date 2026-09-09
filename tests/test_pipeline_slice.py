"""
End-to-End slice execution test for Caldera Monitoring Report Triage.
Verifies thin slice runs end-to-end against the 20-report corpus.
"""

import json
from pathlib import Path
from src.pipeline.triage_graph import MonitoringTriagePipeline


def test_end_to_end_triage_slice():
    # Load 20-report fixture
    fixture_path = Path("data/sample_reports/twenty_reports.json")
    with open(fixture_path, "r") as f:
        raw_reports = json.load(f)

    assert len(raw_reports) == 20

    pipeline = MonitoringTriagePipeline()
    output = pipeline.run(raw_reports)

    # 1. Pipeline status
    assert output.system_status == "NORMAL"
    assert "CALDERA CLINICAL OPS TRIAGE AID" in output.disclaimer

    # 2. Regional Gate Verification (Site-404 must be dropped)
    assert len(output.exclusions) == 4
    for exclusion in output.exclusions:
        assert exclusion.site_id == "SITE-404"
        assert exclusion.country == "RESTRICTED_REGION_X"
        assert "Data sovereignty restriction" in exclusion.reason

    # 3. Eligible site processing (SITE-101, SITE-102, SITE-103)
    site_ids = [site.site_id for site in output.processed_sites]
    assert "SITE-101" in site_ids
    assert "SITE-102" in site_ids
    assert "SITE-103" in site_ids
    assert "SITE-404" not in site_ids

    # 4. Same-theme-across-visits view verification for SITE-101
    site_101 = next(s for s in output.processed_sites if s.site_id == "SITE-101")
    assert site_101.total_reports_processed == 6

    # Verify Informed Consent appears across multiple visits
    ic_theme = next((t for t in site_101.themes if t.theme == "Informed Consent"), None)
    assert ic_theme is not None
    assert ic_theme.distinct_visit_count >= 3
    assert len(ic_theme.observations) >= 4

    # 5. Reviewer-facing packet output integrity
    assert len(output.processed_sites) == 3
