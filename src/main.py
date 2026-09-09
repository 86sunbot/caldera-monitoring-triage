"""
CLI entry point for Caldera Monitoring Report Triage.
Executes triage over input reports and produces structured reviewer packets.
"""

import json
import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path for direct CLI execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.triage_graph import MonitoringTriagePipeline


def format_markdown_packet(triage_output) -> str:
    """Formats the reviewer-facing packet as clean human-readable markdown."""
    lines = []
    lines.append("# Caldera Therapeutics — Clinical Monitoring Triage Packet")
    lines.append(f"**System Status**: `{triage_output.system_status}`")
    lines.append(f"> *{triage_output.disclaimer}*\n")

    if triage_output.degradation_notices:
        lines.append("### ⚠️ Degradation & Resilience Notices")
        for note in triage_output.degradation_notices:
            lines.append(f"- {note}")
        lines.append("")

    if triage_output.exclusions:
        lines.append("### 🛑 Region-Restricted Document Exclusions (Pre-processing Gate)")
        for exc in triage_output.exclusions:
            lines.append(f"- **Doc ID**: `{exc.document_id}` | **Site**: `{exc.site_id}` ({exc.country}) | **Reason**: {exc.reason}")
        lines.append("")

    lines.append("## Surfaced Site Observations")
    for site in triage_output.processed_sites:
        lines.append(f"### Site: `{site.site_id}` ({site.country}) — Reports Analyzed: {site.total_reports_processed}")
        if not site.themes:
            lines.append("*(No candidate signals surfaced for this site)*")
        for theme in site.themes:
            lines.append(f"#### Theme: {theme.theme} *(Appeared across {theme.distinct_visit_count} distinct visits)*")
            for obs in theme.observations:
                citation = obs.citation
                lines.append(f"- **[{obs.visit_date}]** *\"{citation.verbatim_sentence}\"*")
                lines.append(f"  *(Source: Document `{citation.document_id}`, Page {citation.page_number})*")
        lines.append("---")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Caldera Clinical Monitoring Triage")
    parser.add_argument("--data", default="data/sample_reports/twenty_reports.json", help="Path to reports JSON")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format")
    parser.add_argument("--use-ai-studio", action="store_true", help="Invoke Google AI Studio (Gemini) for extraction")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: Sample data not found at {data_path}")
        return

    with open(data_path, "r") as f:
        raw_data = json.load(f)

    if args.use_ai_studio:
        from src.clients.ai_studio_client import GoogleAIStudioClient
        from src.pipeline.extractor import ClinicalObservationExtractor

        ai_client = GoogleAIStudioClient()
        if not ai_client.is_configured():
            print("Notice: GEMINI_API_KEY environment variable not set. Falling back to deterministic extraction.")
        extractor = ClinicalObservationExtractor(ai_studio_client=ai_client, prefer_ai_studio=True)
        pipeline = MonitoringTriagePipeline(extractor=extractor)
    else:
        pipeline = MonitoringTriagePipeline()

    output = pipeline.run(raw_data)

    if args.format == "json":
        print(output.model_dump_json(indent=2))
    else:
        print(format_markdown_packet(output))


if __name__ == "__main__":
    main()
