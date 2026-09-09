"""
Data models for Caldera Therapeutics Monitoring Report Triage System.

CRITICAL GOVERNANCE CONSTRAINT (Team 2 Brief):
Surfacing, not predicting.
The models below strictly enforce:
1. Verbatim source provenance (document ID, page, and sentence).
2. Zero predictive scores, tiers, or automated deviation assertions.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, model_validator


class MonitoringReport(BaseModel):
    """Raw clinical monitoring visit report ingested from eTMF."""
    document_id: str = Field(..., description="Unique document ID in the eTMF")
    site_id: str = Field(..., description="Clinical trial site identifier (e.g. SITE-101)")
    visit_date: str = Field(..., description="Date of the monitoring visit (YYYY-MM-DD)")
    monitor_name: str = Field(..., description="Clinical Research Associate (CRA) name")
    pages: Dict[int, str] = Field(..., description="Page number to text content mapping")

    @model_validator(mode="before")
    @classmethod
    def enforce_edc_boundary(cls, data: dict):
        """
        GOVERNANCE CONTROL (CISO Question 2 & ISO 42001 A.7):
        EDC Boundary Enforcement.
        Rejects any attempt to pass Electronic Data Capture (EDC) subject-level
        clinical data (e.g. lab results, adverse event terms, subject identifiers).
        """
        edc_forbidden_keys = [
            "edc_id", "subject_dob", "subject_initials", "randomization_code",
            "lab_results", "adverse_event_term", "concomitant_meds", "crf_data"
        ]
        for key in data.keys():
            if any(forbidden in key.lower() for forbidden in edc_forbidden_keys):
                raise ValueError(
                    f"EDC Boundary Violation: Ingestion of EDC field '{key}' is strictly forbidden. "
                    "System only ingests eTMF monitoring visit reports, not subject-level clinical data."
                )
        return data


class SourceCitation(BaseModel):
    """Verbatim grounding citation for auditability (ISO 42001 A.8)."""
    document_id: str
    page_number: int
    verbatim_sentence: str


class CandidateObservation(BaseModel):
    """
    Candidate observation surfaced from monitoring text.
    Must contain verbatim citation and assigned theme.
    NEVER contains a score, rank, or deviation assertion.
    """
    observation_id: str
    site_id: str
    visit_date: str
    theme: str = Field(..., description="Neutral observation category (e.g. Informed Consent, Drug Accountability)")
    citation: SourceCitation

    @model_validator(mode="before")
    @classmethod
    def check_forbidden_fields(cls, data: dict):
        """Governance enforcement: prohibit any score, rank, or priority field."""
        forbidden_keywords = ["score", "risk_level", "priority", "severity", "rank", "deviation_confirmed"]
        for key in data.keys():
            if any(forbidden in key.lower() for forbidden in forbidden_keywords):
                raise ValueError(
                    f"Governance Violation: Field '{key}' is forbidden. "
                    "System must remain outside GxP CSV boundary (Surfacing, not predicting)."
                )
        return data


class SameThemeAcrossVisitsView(BaseModel):
    """Aggregates multiple observations under the same theme for a site across distinct visits."""
    theme: str
    observations: List[CandidateObservation]
    distinct_visit_count: int


class SiteReviewPacket(BaseModel):
    """Reviewer-facing packet for a single trial site."""
    site_id: str
    country: str
    total_reports_processed: int
    themes: List[SameThemeAcrossVisitsView]


class ExclusionRecord(BaseModel):
    """Audit log record for dropped documents (ISO 42001 A.7 Data Control)."""
    document_id: str
    site_id: str
    country: str
    reason: str
    timestamp: str


class TriageOutput(BaseModel):
    """Final output bundle for clinical reviewers."""
    system_status: str = Field(..., description="NORMAL or DEGRADED")
    disclaimer: str = (
        "CALDERA CLINICAL OPS TRIAGE AID: "
        "Informational surfacing only. Not a predictive score, not a regulatory deviation record. "
        "All clinical actions require human evaluation by an authorized clinical monitor."
    )
    processed_sites: List[SiteReviewPacket]
    exclusions: List[ExclusionRecord]
    degradation_notices: List[str] = Field(default_factory=list)
