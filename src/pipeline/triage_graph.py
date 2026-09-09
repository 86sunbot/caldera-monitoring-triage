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

        # Calculate expected report counts per site
        reports_expected = len(raw_reports_data)
        site_expected_count: Dict[str, int] = defaultdict(int)
        for raw in raw_reports_data:
            s_id = raw.get("site_id", "UNKNOWN")
            site_expected_count[s_id] += 1

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
                reports_expected=reports_expected,
                reports_retrieved=0,
                is_partial_dataset=True,
                data_completeness_warning=(
                    "CRITICAL: Complete eTMF Document Gateway outage (HTTP 500). Zero documents retrieved."
                ),
                processed_sites=[],
                exclusions=[],
                degradation_notices=degradation_notices,
            )

        reports_retrieved = len(reports)
        is_partial_dataset = reports_retrieved < reports_expected
        data_completeness_warning = None

        if is_partial_dataset:
            system_status = "DEGRADED"
            missing_count = reports_expected - reports_retrieved
            degradation_notices.append(
                f"VENDOR SERVICE NOTICE: eTMF Document API degraded (HTTP 500). "
                f"Partial retrieval: {reports_retrieved} of {reports_expected} reports retrieved ({missing_count} failed)."
            )
            data_completeness_warning = (
                f"⚠️ DEGRADED REVIEW PACKET (PARTIAL DATASET): Only {reports_retrieved} of {reports_expected} reports "
                "were retrieved due to upstream vendor HTTP 500 errors. "
                "ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE: Conclusions regarding clean site conduct "
                "or lack of deviations cannot be drawn for unretrieved monitoring visits."
            )

        # 2. Regional Compliance Gate (ISO 42001 A.7 Data Control)
        eligible_reports: List[MonitoringReport] = []
        for report in reports:
            try:
                is_restricted, country, justification = self.site_registry.is_region_restricted(report.site_id)
            except RuntimeError as err:
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

            processed_count = len(site_reports_count[site_id])
            expected_count = site_expected_count.get(site_id, processed_count)
            is_site_partial = processed_count < expected_count

            processed_sites.append(
                SiteReviewPacket(
                    site_id=site_id,
                    country=country,
                    total_reports_processed=processed_count,
                    total_reports_expected=expected_count,
                    coverage_ratio=f"{processed_count} of {expected_count} reports",
                    is_partial_coverage=is_site_partial,
                    themes=theme_views,
                )
            )

        # Sort sites deterministically by site_id
        processed_sites.sort(key=lambda s: s.site_id)

        # 5. Assemble and return Reviewer Packet
        return TriageOutput(
            system_status=system_status,
            reports_expected=reports_expected,
            reports_retrieved=reports_retrieved,
            is_partial_dataset=is_partial_dataset,
            data_completeness_warning=data_completeness_warning,
            processed_sites=processed_sites,
            exclusions=exclusions,
            degradation_notices=degradation_notices,
        )
