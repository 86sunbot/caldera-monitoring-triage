"""
Streamlit Web Application for Caldera Clinical Monitoring Triage.
Provides an interactive operational UI for Clinical Research Associates (CRAs),
demonstrating Google AI Studio integration, regional gating, and graceful degradation.
"""

import json
from pathlib import Path
import streamlit as st

from src.pipeline.triage_graph import MonitoringTriagePipeline
from src.clients.ai_studio_client import GoogleAIStudioClient
from src.clients.etmf_client import ETMFClient
from src.clients.site_registry import SiteRegistryClient
from src.pipeline.extractor import ClinicalObservationExtractor

st.set_page_config(
    page_title="Caldera Therapeutics · Monitoring Triage",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Caldera Therapeutics · Clinical Monitoring Triage")
st.caption("FDE Challenge Build Sprint · Team 2 (Health & Life Sciences Studio) · *Surfacing, Not Predicting*")

# Mandatory Governance Disclaimer
st.info(
    "**CALDERA CLINICAL OPS TRIAGE AID**: Informational surfacing only. Not a predictive score, "
    "not a regulatory deviation record. All clinical actions require human evaluation by an authorized monitor."
)

# Sidebar Controls
st.sidebar.header("⚙️ Execution Configuration")

# AI Studio Key Input
gemini_key = st.sidebar.text_input(
    "Google AI Studio API Key",
    type="password",
    help="Enter GEMINI_API_KEY to enable live Gemini extraction from Google AI Studio"
)

mode = st.sidebar.radio(
    "Extraction Engine",
    ["Deterministic Regex (Default / Fallback)", "Google AI Studio (Gemini 2.5 Flash)"],
    index=1 if gemini_key else 0
)

# Curveball 3 Simulator
st.sidebar.subheader("⚠️ Resilience & Curveball 3 Simulation")
simulate_etmf_500 = st.sidebar.checkbox("Simulate eTMF Document API (HTTP 500)")
simulate_registry_500 = st.sidebar.checkbox("Simulate Site Registry (HTTP 500)")

# Load sample data
sample_file = Path("data/sample_reports/twenty_reports.json")
if sample_file.exists():
    with open(sample_file, "r") as f:
        default_reports = json.load(f)
else:
    default_reports = []

# Pipeline Execution
if st.button("🚀 Run Clinical Monitoring Triage", type="primary"):
    # Build clients
    etmf_client = ETMFClient(simulate_500=simulate_etmf_500)
    registry_client = SiteRegistryClient(simulate_500=simulate_registry_500)

    use_ai_studio = mode.startswith("Google AI Studio") and bool(gemini_key)
    ai_client = GoogleAIStudioClient(api_key=gemini_key) if use_ai_studio else None
    extractor = ClinicalObservationExtractor(ai_studio_client=ai_client, prefer_ai_studio=use_ai_studio)

    pipeline = MonitoringTriagePipeline(
        etmf_client=etmf_client,
        site_registry=registry_client,
        extractor=extractor
    )

    with st.spinner("Executing triage pipeline across reports..."):
        output = pipeline.run(default_reports)

    # Status Banner
    if output.system_status == "DEGRADED":
        st.warning("### ⚠️ System Status: DEGRADED")
        for notice in output.degradation_notices:
            st.error(notice)
    else:
        st.success("### ✅ System Status: NORMAL")

    # Exclusions Tab / Expander
    if output.exclusions:
        with st.expander("🛑 Region-Restricted Document Exclusions (Pre-processing Gate)", expanded=True):
            st.write(
                "Documents originating from region-restricted jurisdictions are dropped **before** content extraction "
                "to enforce data sovereignty (ISO 42001 A.7)."
            )
            exc_data = [
                {
                    "Document ID": e.document_id,
                    "Site ID": e.site_id,
                    "Country": e.country,
                    "Reason": e.reason,
                    "Timestamp": e.timestamp
                }
                for e in output.exclusions
            ]
            st.table(exc_data)

    # Surfaced Observations by Site
    st.subheader("📋 Surfaced Site Review Packets")
    if not output.processed_sites:
        st.write("No eligible reports processed.")

    for site in output.processed_sites:
        with st.container():
            st.markdown(f"### Site: `{site.site_id}` ({site.country}) · Reports Analyzed: `{site.total_reports_processed}`")
            if not site.themes:
                st.write("*(No candidate signals surfaced for this site)*")
            for theme in site.themes:
                st.markdown(
                    f"**Theme: {theme.theme}** — *Appeared across {theme.distinct_visit_count} distinct visits*"
                )
                for obs in theme.observations:
                    cit = obs.citation
                    st.markdown(
                        f"- 📅 **[{obs.visit_date}]** *\"{cit.verbatim_sentence}\"*  \n"
                        f"  <small style='color:gray'>Source: Document <code>{cit.document_id}</code>, Page {cit.page_number}</small>",
                        unsafe_allow_html=True
                    )
            st.divider()
