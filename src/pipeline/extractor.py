"""
Observation Extractor for Clinical Monitoring Visit Reports.
Extracts candidate signals with strict verbatim grounding (ISO 42001 A.8).
Prohibits cross-document summarization or predictive score generation.
"""

import re
import uuid
from typing import List
from src.models import MonitoringReport, CandidateObservation, SourceCitation


# Standardized clinical monitoring observation themes
THEME_PATTERNS = {
    "Informed Consent": [
        r"\bconsent\b", r"\bre-consent\b", r"\bicf\b", r"\bassent\b", r"\bsigned prior to\b"
    ],
    "Investigational Product & Accountability": [
        r"\bdrug accountability\b", r"\binvestigational product\b", r"\bdispensing log\b",
        r"\breturned kits?\b", r"\bexpiry date\b", r"\bip storage\b"
    ],
    "Temperature Monitoring": [
        r"\btemperature excursion\b", r"\bfridge log\b", r"\bthermometer calibration\b",
        r"\btemperature out of range\b"
    ],
    "Staff Training & Delegation": [
        r"\bdelegation of authority\b", r"\bgcp certificate\b", r"\bstaff turnover\b",
        r"\btraining log missing\b"
    ],
    "Safety & Adverse Events": [
        r"\bsae reconciliation\b", r"\bsafety reporting timeline\b", r"\bdelayed reporting\b"
    ]
}


class ClinicalObservationExtractor:
    """
    Extracts candidate signals from digital monitoring report text.
    Supports Google AI Studio (Gemini) when configured, with seamless
    fallback to deterministic regex extraction.
    """

    def __init__(self, ai_studio_client=None, prefer_ai_studio: bool = False):
        self.ai_studio_client = ai_studio_client
        self.prefer_ai_studio = prefer_ai_studio

    def extract_from_report(self, report: MonitoringReport) -> List[CandidateObservation]:
        # 1. Try Google AI Studio if enabled and configured
        if self.prefer_ai_studio and self.ai_studio_client and self.ai_studio_client.is_configured():
            try:
                return self.ai_studio_client.extract_candidates(report)
            except Exception as err:
                # Log degradation and fall back to deterministic engine
                print(f"[AI Studio Degradation Warning] Falling back to deterministic extractor: {err}")

        # 2. Deterministic Regex Extraction (Default / Fallback)
        observations: List[CandidateObservation] = []

        for page_num, page_text in report.pages.items():
            sentences = re.split(r"(?<=[.!?])\s+", page_text.strip())
            for sentence in sentences:
                sentence_clean = sentence.strip()
                if not sentence_clean:
                    continue

                for theme, patterns in THEME_PATTERNS.items():
                    if any(re.search(pat, sentence_clean, re.IGNORECASE) for pat in patterns):
                        obs = CandidateObservation(
                            observation_id=f"OBS-{uuid.uuid4().hex[:8].upper()}",
                            site_id=report.site_id,
                            visit_date=report.visit_date,
                            theme=theme,
                            citation=SourceCitation(
                                document_id=report.document_id,
                                page_number=page_num,
                                verbatim_sentence=sentence_clean
                            )
                        )
                        observations.append(obs)
                        break

        return observations
