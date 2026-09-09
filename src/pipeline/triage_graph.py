"""
LangGraph-aligned pipeline graph for Caldera Monitoring Report Triage.
Stages:
1. Ingress & Gating (Region-restriction pre-check)
2. Extraction (Verbatim citations only)
3. Grouping (By site and theme, producing same-theme-across-visits view)
4. Packet Assembly (Strictly unranked, human-in-the-loop review packet)
5. Graceful Degradation (Catches 500s, reports partial batch + transparent notices)
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collections import defaultdict

from src.models import (
    MonitoringReport,
    CandidateObservation,
    SameThemeAcrossVisitsView,
    SiteReviewPacket,
    ExclusionRecord,
    TriageOutput,
)
from src.clients.etmf_client import ETMFClient
from src.clients.site_registry import SiteRegistryClient
from src.pipeline.extractor import ClinicalObservationExtractor


class MonitoringTriagePipeline:
    """Orchestrates the monitoring report triage workflow."""

    def __init__(
        self,
        etmf_client: Optional[ETMFClient] = None,
        site_registry: Optional[SiteRegistryClient] = None,
        extractor: Optional[ClinicalObservationExtractor] = None,
    ):
        self.etmf_client = etmf_client or ETMFClient()
        self.site_registry = site_registry or SiteRegistryClient()
        self.extractor = extractor or ClinicalObservationExtractor()

    def run(self, raw_reports_data: List[Dict[str, Any]]) -> TriageOutput:
        """
        Executes the triage pipeline.
        Gracefully handles external API 500 failures (Curveball 3).
        """
        system_status = "NORMAL"
        degradation_notices: List[str] = []
        exclusions: List[ExclusionRecord] = []
        reports: List[MonitoringReport] = []

        # 1. Ingress via eTMF (Resilience Gate)
        try:
            reports = self.etmf_client.fetch_reports(raw_reports_data)
        except RuntimeError as err:
            system_status = "DEGRADED"
            degradation_notices.append(
                f"UPSTREAM FAILURE: eTMF Document API encountered error: {str(err)}. "
                "Processing degraded; unable to retrieve newly published reports."
            )
            return TriageOutput(
                system_status=system_status,
                processed_sites=[],
                exclusions=[],
                degradation_notices=degradation_notices,
            )

        # 2. Regional Compliance Gate (ISO 42001 A.7 Data Control)
        eligible_reports: List[MonitoringReport] = []
        for report in reports:
            try:
                is_restricted, country, justification = self.site_registry.is_region_restricted(report.site_id)
            except RuntimeError as err:
                # Curveball 3: Upstream Site Registry 500 error
                system_status = "DEGRADED"
                degradation_notices.append(
                    f"COMPLIANCE GATE DEGRADED: Site Registry lookup failed for {report.site_id} ({str(err)}). "
                    "Fail-closed policy activated: document held in staging pending regional compliance verification."
                )
                exclusions.append(
                    ExclusionRecord(
                        document_id=report.document_id,
                        site_id=report.site_id,
                        country="UNKNOWN",
                        reason=f"Fail-closed hold: Site Registry service returned 500 ({str(err)})",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                )
                continue

            if is_restricted:
                # Pre-processing drop: document text is NEVER parsed
                exclusions.append(
                    ExclusionRecord(
                        document_id=report.document_id,
                        site_id=report.site_id,
                        country=country,
                        reason=justification,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                )
            else:
                eligible_reports.append(report)

        # 3. Candidate Observation Extraction (Verbatim citations)
        observations_by_site: Dict[str, List[CandidateObservation]] = defaultdict(list)
        site_reports_count: Dict[str, set] = defaultdict(set)

        for report in eligible_reports:
            site_reports_count[report.site_id].add(report.document_id)
            extracted = self.extractor.extract_from_report(report)
            observations_by_site[report.site_id].extend(extracted)

        # 4. Grouping: By site & theme, generating same-theme-across-visits view
        processed_sites: List[SiteReviewPacket] = []
        for site_id, observations in observations_by_site.items():
            country = self.site_registry.get_site_country(site_id)
            theme_map: Dict[str, List[CandidateObservation]] = defaultdict(list)

            for obs in observations:
                theme_map[obs.theme].append(obs)

            theme_views: List[SameThemeAcrossVisitsView] = []
            for theme_name, obs_list in theme_map.items():
                distinct_visits = len({obs.visit_date for obs in obs_list})
                theme_views.append(
                    SameThemeAcrossVisitsView(
                        theme=theme_name,
                        observations=obs_list,
                        distinct_visit_count=distinct_visits,
                    )
                )

            # Sort themes alphabetically (STRICTLY NO RANKING OR SCORES)
            theme_views.sort(key=lambda t: t.theme)

            processed_sites.append(
                SiteReviewPacket(
                    site_id=site_id,
                    country=country,
                    total_reports_processed=len(site_reports_count[site_id]),
                    themes=theme_views,
                )
            )

        # Sort sites deterministically by site_id
        processed_sites.sort(key=lambda s: s.site_id)

        # 5. Assemble and return Reviewer Packet
        return TriageOutput(
            system_status=system_status,
            processed_sites=processed_sites,
            exclusions=exclusions,
            degradation_notices=degradation_notices,
        )
