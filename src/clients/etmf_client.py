"""
Client for electronic Trial Master File (eTMF) Document API.
Handles ingestion of monitoring visit reports.
Supports failure injection to test 15:00 curveball graceful degradation.
"""

from typing import List, Dict, Any
from src.models import MonitoringReport


class ETMFClient:
    """Mock eTMF client retrieving monitoring reports."""

    def __init__(
        self,
        simulate_500: bool = False,
        simulate_partial_500: bool = False,
        successful_doc_limit: int = 11,
    ):
        self.simulate_500 = simulate_500
        self.simulate_partial_500 = simulate_partial_500
        self.successful_doc_limit = successful_doc_limit

    def fetch_reports(self, raw_reports_data: List[Dict[str, Any]]) -> List[MonitoringReport]:
        """
        Retrieves monitoring visit reports from eTMF.
        If simulate_500 is True, raises complete server error.
        If simulate_partial_500 is True, retrieves up to successful_doc_limit (e.g. 11 of 20),
        and raises simulated 500 errors for subsequent documents.
        """
        if self.simulate_500:
            raise RuntimeError("HTTP 500: eTMF Document Gateway Internal Server Error")

        reports = []
        for idx, item in enumerate(raw_reports_data):
            if self.simulate_partial_500 and idx >= self.successful_doc_limit:
                # Subsequent study retrievals fail with 500
                continue
            reports.append(MonitoringReport(**item))
        return reports
