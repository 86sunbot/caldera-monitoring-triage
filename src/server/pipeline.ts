/**
 * Caldera Therapeutics Clinical Monitoring Triage Pipeline
 * 
 * Ported from Python LangGraph pipeline with 100% fidelity to governance controls:
 * - ISO 42001 A.6: Zero predictive scores, zero ranking, unranked review packets.
 * - ISO 42001 A.7: EDC boundary enforcement & regional compliance pre-processing drop.
 * - ISO 42001 A.8: Immutable verbatim sentence and page number grounding.
 * - ISO 42001 A.10 / Curveball 3: Graceful degradation on upstream 500s.
 */

import crypto from 'crypto';
import { GoogleGenAI, Type } from '@google/genai';
import {
  MonitoringReport,
  CandidateObservation,
  SameThemeAcrossVisitsView,
  SiteReviewPacket,
  ExclusionRecord,
  TriageOutput,
} from '../types.js';

// EDC boundary forbidden fields
const EDC_FORBIDDEN_KEYS = [
  'edc_id',
  'subject_dob',
  'subject_initials',
  'randomization_code',
  'lab_results',
  'adverse_event_term',
  'concomitant_meds',
  'crf_data',
];

// Governance forbidden fields for observations
const SCORING_FORBIDDEN_KEYWORDS = [
  'score',
  'risk_level',
  'priority',
  'severity',
  'rank',
  'deviation_confirmed',
];

export function validateMonitoringReport(data: Record<string, unknown>): MonitoringReport {
  for (const key of Object.keys(data)) {
    if (EDC_FORBIDDEN_KEYS.some((forbidden) => key.toLowerCase().includes(forbidden))) {
      throw new Error(
        `EDC Boundary Violation: Ingestion of EDC field '${key}' is strictly forbidden. ` +
        'System only ingests eTMF monitoring visit reports, not subject-level clinical data.'
      );
    }
  }

  if (!data.document_id || !data.site_id || !data.visit_date || !data.pages) {
    throw new Error('Invalid report format: missing required fields');
  }

  return data as unknown as MonitoringReport;
}

export function validateCandidateObservation(data: Record<string, unknown>): CandidateObservation {
  for (const key of Object.keys(data)) {
    if (SCORING_FORBIDDEN_KEYWORDS.some((forbidden) => key.toLowerCase().includes(forbidden))) {
      throw new Error(
        `Governance Violation: Field '${key}' is forbidden. ` +
        'System must remain outside GxP CSV boundary (Surfacing, not predicting).'
      );
    }
  }
  return data as unknown as CandidateObservation;
}

export class SiteRegistryClient {
  private simulate500: boolean;
  private registry: Record<string, string> = {
    'SITE-101': 'UK',
    'SITE-102': 'DE',
    'SITE-103': 'FR',
    'SITE-404': 'RESTRICTED_REGION_X',
  };
  private restrictedRegions = new Set(['RESTRICTED_REGION_X', 'EMBARGOED_TERRITORY']);

  constructor(simulate500 = false) {
    this.simulate500 = simulate500;
  }

  getSiteCountry(siteId: string): string {
    if (this.simulate500) {
      throw new Error('HTTP 500: Site Registry Service Unavailable');
    }
    return this.registry[siteId] || 'UNKNOWN';
  }

  isRegionRestricted(siteId: string): { isRestricted: boolean; country: string; justification: string } {
    const country = this.getSiteCountry(siteId);
    if (this.restrictedRegions.has(country)) {
      return {
        isRestricted: true,
        country,
        justification: `Data sovereignty restriction: ${country} data cannot cross study processing boundary.`,
      };
    }
    return {
      isRestricted: false,
      country,
      justification: '',
    };
  }
}

export class ETMFClient {
  private simulate500: boolean;

  constructor(simulate500 = false) {
    this.simulate500 = simulate500;
  }

  fetchReports(rawReportsData: Array<Record<string, unknown>>): MonitoringReport[] {
    if (this.simulate500) {
      throw new Error('HTTP 500: eTMF Document Gateway Internal Server Error');
    }
    return rawReportsData.map((item) => validateMonitoringReport(item));
  }
}

// Standardized clinical monitoring observation themes
export const THEME_PATTERNS: Record<string, RegExp[]> = {
  'Informed Consent': [
    /\bconsent\b/i,
    /\bre-consent\b/i,
    /\bicf\b/i,
    /\bassent\b/i,
    /\bsigned prior to\b/i,
  ],
  'Investigational Product & Accountability': [
    /\bdrug accountability\b/i,
    /\binvestigational product\b/i,
    /\bdispensing log\b/i,
    /\breturned kits?\b/i,
    /\bexpiry date\b/i,
    /\bip storage\b/i,
  ],
  'Temperature Monitoring': [
    /\btemperature excursion\b/i,
    /\bfridge log\b/i,
    /\bthermometer calibration\b/i,
    /\btemperature out of range\b/i,
  ],
  'Staff Training & Delegation': [
    /\bdelegation of authority\b/i,
    /\bgcp certificate\b/i,
    /\bstaff turnover\b/i,
    /\btraining log missing\b/i,
  ],
  'Safety & Adverse Events': [
    /\bsae reconciliation\b/i,
    /\bsafety reporting timeline\b/i,
    /\bdelayed reporting\b/i,
  ],
};

const AI_STUDIO_SYSTEM_INSTRUCTION =
  'You are a clinical monitoring triage assistant for Caldera Therapeutics. ' +
  'Your duty is SURFACING candidate signals from monitoring reports, NOT PREDICTING or SCORING. ' +
  'CRITICAL GOVERNANCE MANDATES: ' +
  '1. NEVER output a risk score, priority, rating, or deviation confirmation. ' +
  '2. Every candidate observation MUST cite the exact page number and verbatim sentence from the report text. ' +
  '3. Classify each observation into one of these neutral themes: ' +
  "'Informed Consent', 'Investigational Product & Accountability', 'Temperature Monitoring', " +
  "'Staff Training & Delegation', 'Safety & Adverse Events'. " +
  '4. If no candidate observations exist in the report, return an empty list.';

export class ClinicalObservationExtractor {
  private apiKey?: string;
  private preferAiStudio: boolean;

  constructor(apiKey?: string, preferAiStudio = false) {
    this.apiKey = apiKey || process.env.GEMINI_API_KEY;
    this.preferAiStudio = preferAiStudio;
  }

  async extractFromReport(report: MonitoringReport): Promise<CandidateObservation[]> {
    // 1. Try Google AI Studio if enabled and configured
    if (this.preferAiStudio && this.apiKey && this.apiKey.trim().length > 0) {
      try {
        const aiResults = await this.extractWithGemini(report);
        if (aiResults && aiResults.length >= 0) {
          return aiResults;
        }
      } catch (err) {
        console.warn(`[AI Studio Degradation Warning] Falling back to deterministic extractor: ${err}`);
      }
    }

    // 2. Deterministic Regex Extraction (Default / Fallback)
    return this.extractWithRegex(report);
  }

  private extractWithRegex(report: MonitoringReport): CandidateObservation[] {
    const observations: CandidateObservation[] = [];

    const pageEntries = Object.entries(report.pages).sort(([a], [b]) => Number(a) - Number(b));

    for (const [pageNumStr, pageText] of pageEntries) {
      const pageNum = parseInt(pageNumStr, 10) || 1;
      // Split into sentences
      const sentences = pageText.split(/(?<=[.!?])\s+/);
      for (const rawSentence of sentences) {
        const sentenceClean = rawSentence.trim();
        if (!sentenceClean) continue;

        for (const [theme, patterns] of Object.entries(THEME_PATTERNS)) {
          if (patterns.some((pattern) => pattern.test(sentenceClean))) {
            const obs = validateCandidateObservation({
              observation_id: `OBS-${crypto.randomBytes(4).toString('hex').toUpperCase()}`,
              site_id: report.site_id,
              visit_date: report.visit_date,
              theme,
              citation: {
                document_id: report.document_id,
                page_number: pageNum,
                verbatim_sentence: sentenceClean,
              },
            });
            observations.push(obs);
            break; // theme matched
          }
        }
      }
    }

    return observations;
  }

  private async extractWithGemini(report: MonitoringReport): Promise<CandidateObservation[]> {
    const ai = new GoogleGenAI({ apiKey: this.apiKey });
    const formattedPages = Object.entries(report.pages)
      .sort(([a], [b]) => Number(a) - Number(b))
      .map(([p, text]) => `--- PAGE ${p} ---\n${text}`)
      .join('\n\n');

    const prompt =
      `Study Report ID: ${report.document_id}\n` +
      `Site ID: ${report.site_id}\n` +
      `Visit Date: ${report.visit_date}\n\n` +
      `Report Content:\n${formattedPages}\n\n` +
      'Extract all candidate observations strictly adhering to the schema. Do not summarize; use verbatim sentences.';

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        systemInstruction: AI_STUDIO_SYSTEM_INSTRUCTION,
        temperature: 0.1,
        responseMimeType: 'application/json',
        responseSchema: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              page_number: { type: Type.INTEGER },
              verbatim_sentence: { type: Type.STRING },
              theme: {
                type: Type.STRING,
                enum: [
                  'Informed Consent',
                  'Investigational Product & Accountability',
                  'Temperature Monitoring',
                  'Staff Training & Delegation',
                  'Safety & Adverse Events',
                ],
              },
            },
            required: ['page_number', 'verbatim_sentence', 'theme'],
          },
        },
      },
    });

    const text = response.text?.trim() || '[]';
    const parsed = JSON.parse(text) as Array<{
      page_number: number;
      verbatim_sentence: string;
      theme: string;
    }>;

    return parsed.map((item, idx) =>
      validateCandidateObservation({
        observation_id: `OBS-AI-${String(idx + 1).padStart(3, '0')}-${report.document_id}`,
        site_id: report.site_id,
        visit_date: report.visit_date,
        theme: item.theme,
        citation: {
          document_id: report.document_id,
          page_number: Number(item.page_number),
          verbatim_sentence: item.verbatim_sentence,
        },
      })
    );
  }
}

export class MonitoringTriagePipeline {
  private etmfClient: ETMFClient;
  private siteRegistry: SiteRegistryClient;
  private extractor: ClinicalObservationExtractor;

  constructor(options?: {
    etmfClient?: ETMFClient;
    siteRegistry?: SiteRegistryClient;
    extractor?: ClinicalObservationExtractor;
  }) {
    this.etmfClient = options?.etmfClient || new ETMFClient();
    this.siteRegistry = options?.siteRegistry || new SiteRegistryClient();
    this.extractor = options?.extractor || new ClinicalObservationExtractor();
  }

  async run(rawReportsData: Array<Record<string, unknown>>): Promise<TriageOutput> {
    let systemStatus: 'NORMAL' | 'DEGRADED' = 'NORMAL';
    const degradationNotices: string[] = [];
    const exclusions: ExclusionRecord[] = [];
    let reports: MonitoringReport[] = [];

    // 1. Ingress via eTMF (Resilience Gate)
    try {
      reports = this.etmfClient.fetchReports(rawReportsData);
    } catch (err: unknown) {
      systemStatus = 'DEGRADED';
      const errMsg = err instanceof Error ? err.message : String(err);
      degradationNotices.push(
        `UPSTREAM FAILURE: eTMF Document API encountered error: ${errMsg}. ` +
        'Processing degraded; unable to retrieve newly published reports.'
      );
      return {
        system_status: systemStatus,
        disclaimer:
          'CALDERA CLINICAL OPS TRIAGE AID: Informational surfacing only. Not a predictive score, not a regulatory deviation record. All clinical actions require human evaluation by an authorized clinical monitor.',
        processed_sites: [],
        exclusions: [],
        degradation_notices: degradationNotices,
      };
    }

    // 2. Regional Compliance Gate (ISO 42001 A.7 Data Control)
    const eligibleReports: MonitoringReport[] = [];
    for (const report of reports) {
      try {
        const { isRestricted, country, justification } = this.siteRegistry.isRegionRestricted(report.site_id);
        if (isRestricted) {
          // Pre-processing drop: document text is NEVER parsed
          exclusions.push({
            document_id: report.document_id,
            site_id: report.site_id,
            country,
            reason: justification,
            timestamp: new Date().toISOString(),
          });
        } else {
          eligibleReports.push(report);
        }
      } catch (err: unknown) {
        // Curveball 3: Upstream Site Registry 500 error
        systemStatus = 'DEGRADED';
        const errMsg = err instanceof Error ? err.message : String(err);
        degradationNotices.push(
          `COMPLIANCE GATE DEGRADED: Site Registry lookup failed for ${report.site_id} (${errMsg}). ` +
          'Fail-closed policy activated: document held in staging pending regional compliance verification.'
        );
        exclusions.push({
          document_id: report.document_id,
          site_id: report.site_id,
          country: 'UNKNOWN',
          reason: `Fail-closed hold: Site Registry service returned 500 (${errMsg})`,
          timestamp: new Date().toISOString(),
        });
      }
    }

    // 3. Candidate Observation Extraction (Verbatim citations)
    const observationsBySite = new Map<string, CandidateObservation[]>();
    const siteReportsCount = new Map<string, Set<string>>();

    for (const report of eligibleReports) {
      if (!siteReportsCount.has(report.site_id)) {
        siteReportsCount.set(report.site_id, new Set());
      }
      siteReportsCount.get(report.site_id)!.add(report.document_id);

      const extracted = await this.extractor.extractFromReport(report);
      if (!observationsBySite.has(report.site_id)) {
        observationsBySite.set(report.site_id, []);
      }
      observationsBySite.get(report.site_id)!.push(...extracted);
    }

    // 4. Grouping: By site & theme, generating same-theme-across-visits view
    const processedSites: SiteReviewPacket[] = [];
    for (const [siteId, observations] of observationsBySite.entries()) {
      const country = this.siteRegistry.getSiteCountry(siteId);
      const themeMap = new Map<string, CandidateObservation[]>();

      for (const obs of observations) {
        if (!themeMap.has(obs.theme)) {
          themeMap.set(obs.theme, []);
        }
        themeMap.get(obs.theme)!.push(obs);
      }

      const themeViews: SameThemeAcrossVisitsView[] = [];
      for (const [themeName, obsList] of themeMap.entries()) {
        const distinctVisits = new Set(obsList.map((o) => o.visit_date)).size;
        themeViews.push({
          theme: themeName,
          observations: obsList,
          distinct_visit_count: distinctVisits,
        });
      }

      // Sort themes alphabetically (STRICTLY NO RANKING OR SCORES)
      themeViews.sort((a, b) => a.theme.localeCompare(b.theme));

      processedSites.push({
        site_id: siteId,
        country,
        total_reports_processed: siteReportsCount.get(siteId)?.size || 0,
        themes: themeViews,
      });
    }

    // Sort sites deterministically by site_id
    processedSites.sort((a, b) => a.site_id.localeCompare(b.site_id));

    // 5. Assemble and return Reviewer Packet
    return {
      system_status: systemStatus,
      disclaimer:
        'CALDERA CLINICAL OPS TRIAGE AID: Informational surfacing only. Not a predictive score, not a regulatory deviation record. All clinical actions require human evaluation by an authorized clinical monitor.',
      processed_sites: processedSites,
      exclusions,
      degradation_notices: degradationNotices,
    };
  }
}
