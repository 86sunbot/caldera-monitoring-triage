"""
Client for electronic Trial Master File (eTMF) Document API.
Handles ingestion of monitoring visit reports.
Supports failure injection to test 15:00 curveball graceful degradation.
"""

from typing import List, Dict, Any
from src.models import MonitoringReport


class ETMFClient:
    """Mock eTMF client retrieving monitoring reports."""

    def __init__(self, simulate_500: bool = False):
        self.simulate_500 = simulate_500

    def fetch_reports(self, raw_reports_data: List[Dict[str, Any]]) -> List[MonitoringReport]:
        """
        Retrieves monitoring visit reports from eTMF.
        If simulate_500 is True, raises an external HTTP 500 server error.
        """
        if self.simulate_500:
            raise RuntimeError("HTTP 500: eTMF Document Gateway Internal Server Error")

        reports = []
        for item in raw_reports_data:
            reports.append(MonitoringReport(**item))
        return reports
