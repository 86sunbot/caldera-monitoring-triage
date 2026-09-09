/**
 * Data models for Caldera Therapeutics Monitoring Report Triage System.
 * 
 * CRITICAL GOVERNANCE CONSTRAINT (Team 2 Brief):
 * Surfacing, not predicting.
 * 1. Verbatim source provenance (document ID, page, and sentence).
 * 2. Zero predictive scores, tiers, or automated deviation assertions.
 */

export interface MonitoringReport {
  document_id: string;
  site_id: string;
  visit_date: string;
  monitor_name: string;
  pages: Record<string, string>;
  [key: string]: unknown;
}

export interface SourceCitation {
  document_id: string;
  page_number: number;
  verbatim_sentence: string;
}

export interface CandidateObservation {
  observation_id: string;
  site_id: string;
  visit_date: string;
  theme: string;
  citation: SourceCitation;
}

export interface SameThemeAcrossVisitsView {
  theme: string;
  observations: CandidateObservation[];
  distinct_visit_count: number;
}

export interface SiteReviewPacket {
  site_id: string;
  country: string;
  total_reports_processed: number;
  total_reports_expected?: number;
  coverage_ratio?: string;
  is_partial_coverage?: boolean;
  themes: SameThemeAcrossVisitsView[];
}

export interface ExclusionRecord {
  document_id: string;
  site_id: string;
  country: string;
  reason: string;
  timestamp: string;
}

export interface TriageOutput {
  system_status: 'NORMAL' | 'DEGRADED';
  disclaimer: string;
  reports_expected: number;
  reports_retrieved: number;
  is_partial_dataset: boolean;
  data_completeness_warning?: string | null;
  processed_sites: SiteReviewPacket[];
  exclusions: ExclusionRecord[];
  degradation_notices: string[];
}

export interface TriageRequestPayload {
  reports?: MonitoringReport[];
  simulate_etmf_500?: boolean;
  simulate_partial_etmf_500?: boolean;
  simulate_registry_500?: boolean;
  prefer_ai_studio?: boolean;
  gemini_key?: string;
}
