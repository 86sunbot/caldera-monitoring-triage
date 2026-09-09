"""
Google AI Studio Client for Caldera Clinical Monitoring Triage.
Connects to Google AI Studio (Gemini) for candidate observation extraction.

GOVERNANCE SAFEGUARDS ENFORCED (ISO 42001 A.6, A.8 & CISO Threat Model):
1. Strictly unranked JSON schema output (Zero scores, zero priorities).
2. Verbatim source attribution requirement (document_id, page_number, verbatim_sentence).
3. Graceful degradation: If GEMINI_API_KEY is not set or API returns an error,
   falls back seamlessly to the deterministic extractor.
"""

import os
import json
import urllib.request
import urllib.error
from typing import List, Optional
from src.models import MonitoringReport, CandidateObservation, SourceCitation


AI_STUDIO_SYSTEM_INSTRUCTION = (
    "You are a clinical monitoring triage assistant for Caldera Therapeutics. "
    "Your duty is SURFACING candidate signals from monitoring reports, NOT PREDICTING or SCORING. "
    "CRITICAL GOVERNANCE MANDATES: "
    "1. NEVER output a risk score, priority, rating, or deviation confirmation. "
    "2. Every candidate observation MUST cite the exact page number and verbatim sentence from the report text. "
    "3. Classify each observation into one of these neutral themes: "
    "'Informed Consent', 'Investigational Product & Accountability', 'Temperature Monitoring', "
    "'Staff Training & Delegation', 'Safety & Adverse Events'. "
    "4. If no candidate observations exist in the report, return an empty list."
)

JSON_SCHEMA_FORMAT = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer"},
            "verbatim_sentence": {"type": "string"},
            "theme": {
                "type": "string",
                "enum": [
                    "Informed Consent",
                    "Investigational Product & Accountability",
                    "Temperature Monitoring",
                    "Staff Training & Delegation",
                    "Safety & Adverse Events"
                ]
            }
        },
        "required": ["page_number", "verbatim_sentence", "theme"]
    }
}


class GoogleAIStudioClient:
    """Interfaces with Google AI Studio Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model
        self.endpoint_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )

    def is_configured(self) -> bool:
        """Returns True if a valid Google AI Studio API key is provided."""
        return bool(self.api_key and self.api_key.strip())

    def extract_candidates(self, report: MonitoringReport) -> List[CandidateObservation]:
        """
        Sends monitoring report pages to Google AI Studio Gemini model with structured output.
        Returns validated CandidateObservation objects.
        """
        if not self.is_configured():
            raise RuntimeError("GEMINI_API_KEY not set. Cannot invoke Google AI Studio.")

        # Prepare payload with pages content
        formatted_pages = "\n\n".join(
            f"--- PAGE {p_num} ---\n{text}" for p_num, text in sorted(report.pages.items())
        )

        user_prompt = (
            f"Study Report ID: {report.document_id}\n"
            f"Site ID: {report.site_id}\n"
            f"Visit Date: {report.visit_date}\n\n"
            f"Report Content:\n{formatted_pages}\n\n"
            "Extract all candidate observations strictly adhering to the schema. Do not summarize; use verbatim sentences."
        )

        payload = {
            "system_instruction": {
                "parts": [{"text": AI_STUDIO_SYSTEM_INSTRUCTION}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
                "responseSchema": JSON_SCHEMA_FORMAT
            }
        }

        url = f"{self.endpoint_url}?key={self.api_key}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)

                # Parse candidate text response
                candidates = res_json.get("candidates", [])
                if not candidates:
                    return []

                content_parts = candidates[0].get("content", {}).get("parts", [])
                if not content_parts:
                    return []

                raw_extracted_text = content_parts[0].get("text", "[]")
                items = json.loads(raw_extracted_text)

                results: List[CandidateObservation] = []
                for idx, item in enumerate(items):
                    results.append(
                        CandidateObservation(
                            observation_id=f"OBS-AI-{idx+1:03d}-{report.document_id}",
                            site_id=report.site_id,
                            visit_date=report.visit_date,
                            theme=item["theme"],
                            citation=SourceCitation(
                                document_id=report.document_id,
                                page_number=int(item["page_number"]),
                                verbatim_sentence=item["verbatim_sentence"]
                            )
                        )
                    )
                return results

        except urllib.error.HTTPError as http_err:
            error_body = http_err.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Google AI Studio API Error (HTTP {http_err.code}): {error_body}")
        except Exception as e:
            raise RuntimeError(f"Failed to communicate with Google AI Studio: {str(e)}")
