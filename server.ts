import express from 'express';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { createServer as createViteServer } from 'vite';
import {
  MonitoringTriagePipeline,
  ETMFClient,
  SiteRegistryClient,
  ClinicalObservationExtractor,
  validateMonitoringReport,
  validateCandidateObservation,
} from './src/server/pipeline.js';
import { TriageRequestPayload } from './src/types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json({ limit: '10mb' }));

  // Helper to get sample reports
  function getSampleReports() {
    const filePath = path.join(__dirname, 'data', 'sample_reports', 'twenty_reports.json');
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf-8');
      return JSON.parse(content);
    }
    return [];
  }

  // Health endpoint
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  // Sample reports endpoint
  app.get('/api/reports', (req, res) => {
    try {
      const reports = getSampleReports();
      res.json({ reports, count: reports.length });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      res.status(500).json({ error: msg });
    }
  });

  // Triage execution endpoint
  app.post('/api/triage', async (req, res) => {
    try {
      const body: TriageRequestPayload = req.body || {};
      const rawReports = body.reports && body.reports.length > 0 ? body.reports : getSampleReports();

      const etmfClient = new ETMFClient(
        Boolean(body.simulate_etmf_500),
        Boolean(body.simulate_partial_etmf_500),
        11
      );
      const registryClient = new SiteRegistryClient(Boolean(body.simulate_registry_500));

      const apiKey = body.gemini_key || process.env.GEMINI_API_KEY;
      const extractor = new ClinicalObservationExtractor(apiKey, Boolean(body.prefer_ai_studio));

      const pipeline = new MonitoringTriagePipeline({
        etmfClient,
        siteRegistry: registryClient,
        extractor,
      });

      const output = await pipeline.run(rawReports);
      res.json(output);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      res.status(500).json({ error: msg });
    }
  });

  // Governance validation tests (API verification)
  app.get('/api/governance-tests', async (req, res) => {
    const results: Array<{ test: string; status: 'PASSED' | 'FAILED'; details: string; iso_mapping: string }> = [];

    // Test 1: EDC Boundary Enforcement (ISO 42001 A.7)
    try {
      let threw = false;
      try {
        validateMonitoringReport({
          document_id: 'MVR-FAIL',
          site_id: 'SITE-101',
          visit_date: '2024-01-01',
          monitor_name: 'Auditor Test',
          pages: { 1: 'Clean' },
          subject_initials: 'J.D.',
        });
      } catch (e: unknown) {
        if (e instanceof Error && e.message.includes('EDC Boundary Violation')) {
          threw = true;
        }
      }
      results.push({
        test: 'EDC Boundary Enforcement',
        status: threw ? 'PASSED' : 'FAILED',
        details: threw
          ? 'Successfully blocked subject-level clinical data ingestion (rejected subject_initials).'
          : 'Failed: Did not reject EDC forbidden field.',
        iso_mapping: 'ISO 42001 A.7 (Data Control Boundary)',
      });
    } catch (err: unknown) {
      results.push({
        test: 'EDC Boundary Enforcement',
        status: 'FAILED',
        details: String(err),
        iso_mapping: 'ISO 42001 A.7',
      });
    }

    // Test 2: Zero Predictive Scoring & Ranking (ISO 42001 A.6)
    try {
      let threw = false;
      try {
        validateCandidateObservation({
          observation_id: 'OBS-FAIL',
          site_id: 'SITE-101',
          visit_date: '2024-01-01',
          theme: 'Informed Consent',
          citation: { document_id: 'DOC-1', page_number: 1, verbatim_sentence: 'Test' },
          risk_level: 'HIGH',
        });
      } catch (e: unknown) {
        if (e instanceof Error && e.message.includes('Governance Violation')) {
          threw = true;
        }
      }
      results.push({
        test: 'Zero Scoring & Ranking Governance',
        status: threw ? 'PASSED' : 'FAILED',
        details: threw
          ? 'Strictly rejected forbidden predictive field (risk_level), enforcing GxP CSV boundary.'
          : 'Failed to reject predictive score field.',
        iso_mapping: 'ISO 42001 A.6 (AI Life Cycle & Non-Predictive Boundary)',
      });
    } catch (err: unknown) {
      results.push({
        test: 'Zero Scoring & Ranking Governance',
        status: 'FAILED',
        details: String(err),
        iso_mapping: 'ISO 42001 A.6',
      });
    }

    // Test 3: Regional Compliance Pre-Processing Gating (ISO 42001 A.7)
    try {
      const sample = [
        {
          document_id: 'MVR-RESTRICTED-001',
          site_id: 'SITE-404',
          visit_date: '2024-01-01',
          monitor_name: 'Auditor',
          pages: { 1: 'Must not be parsed.' },
        },
      ];
      const pipeline = new MonitoringTriagePipeline();
      const out = await pipeline.run(sample);
      const passed =
        out.exclusions.length === 1 &&
        out.exclusions[0].site_id === 'SITE-404' &&
        out.exclusions[0].country === 'RESTRICTED_REGION_X' &&
        out.processed_sites.length === 0;

      results.push({
        test: 'Regional Compliance Pre-Processing Gate',
        status: passed ? 'PASSED' : 'FAILED',
        details: passed
          ? 'SITE-404 document dropped before extraction; recorded in auditable exclusion log.'
          : 'Failed: Restricted document was not excluded properly.',
        iso_mapping: 'ISO 42001 A.7 (Data Sovereignty & Cross-Border Controls)',
      });
    } catch (err: unknown) {
      results.push({
        test: 'Regional Compliance Pre-Processing Gate',
        status: 'FAILED',
        details: String(err),
        iso_mapping: 'ISO 42001 A.7',
      });
    }

    // Test 4: Verbatim Grounding & Provenance (ISO 42001 A.8)
    try {
      const sample = [
        {
          document_id: 'MVR-VERIFY-01',
          site_id: 'SITE-101',
          visit_date: '2024-03-01',
          monitor_name: 'Verifier CRA',
          pages: { 4: 'Fridge log indicated a temporary temperature excursion of +12C over the weekend.' },
        },
      ];
      const pipeline = new MonitoringTriagePipeline();
      const out = await pipeline.run(sample);
      const obs = out.processed_sites[0]?.themes[0]?.observations[0];
      const passed =
        obs &&
        obs.citation.document_id === 'MVR-VERIFY-01' &&
        obs.citation.page_number === 4 &&
        obs.citation.verbatim_sentence === 'Fridge log indicated a temporary temperature excursion of +12C over the weekend.';

      results.push({
        test: 'Verbatim Sentence & Page Provenance',
        status: passed ? 'PASSED' : 'FAILED',
        details: passed
          ? 'Exact citation retained with document ID, page 4, and verbatim sentence without hallucination.'
          : 'Failed: Provenance mismatch.',
        iso_mapping: 'ISO 42001 A.8 (Transparency & Audit Traceability)',
      });
    } catch (err: unknown) {
      results.push({
        test: 'Verbatim Sentence & Page Provenance',
        status: 'FAILED',
        details: String(err),
        iso_mapping: 'ISO 42001 A.8',
      });
    }

    // Test 5: Resilience & Graceful Degradation (ISO 42001 A.10 / Curveball 3)
    try {
      const pipeline500 = new MonitoringTriagePipeline({
        etmfClient: new ETMFClient(true),
      });
      const out500 = await pipeline500.run([{ document_id: '1', site_id: 'SITE-101', visit_date: '2024-01-01', monitor_name: 'CRA', pages: { 1: 'ok' } }]);
      const passed =
        out500.system_status === 'DEGRADED' &&
        out500.degradation_notices.length > 0 &&
        out500.degradation_notices[0].includes('UPSTREAM FAILURE');

      results.push({
        test: 'Upstream Dependency 500 Graceful Degradation',
        status: passed ? 'PASSED' : 'FAILED',
        details: passed
          ? 'System caught eTMF 500 safely, transitioned to DEGRADED, and surfaced transparent reviewer notice.'
          : 'Failed: Did not handle 500 gracefully.',
        iso_mapping: 'ISO 42001 A.10 (Resilience & Third-Party Failure Handling)',
      });
    } catch (err: unknown) {
      results.push({
        test: 'Upstream Dependency 500 Graceful Degradation',
        status: 'FAILED',
        details: String(err),
        iso_mapping: 'ISO 42001 A.10',
      });
    }

    res.json({
      summary: results.every((r) => r.status === 'PASSED') ? 'ALL_PASSED' : 'SOME_FAILED',
      tests: results,
    });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Caldera Triage Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
