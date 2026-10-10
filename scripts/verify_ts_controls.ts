/**
 * TypeScript Governance & Citation Grounding Regression Tests
 * Verifies src/server/pipeline.ts controls:
 * 1. Verbatim quote acceptance on exact attributed page.
 * 2. Rejection of fabricated/paraphrased or whitespace quotes.
 * 3. Rejection of verbatim quotes attributed to the wrong page number or non-existent page.
 * 4. Rejection of verbatim quotes attributed to the wrong document_id.
 * 5. Immutability of SourceCitation via Object.freeze.
 * 6. End-to-end MonitoringTriagePipeline filtering of unverified citations.
 */

import assert from 'node:assert/strict';
import {
  MonitoringTriagePipeline,
  ClinicalObservationExtractor,
  validateCandidateObservation,
  validateMonitoringReport,
  verifyCitationAgainstReport,
} from '../src/server/pipeline.js';
import { CandidateObservation, MonitoringReport } from '../src/types.js';

async function runTests(): Promise<void> {
  const report: MonitoringReport = validateMonitoringReport({
    document_id: 'MVR-TS-GROUND-01',
    site_id: 'SITE-101',
    visit_date: '2024-05-10',
    monitor_name: 'TS Verifier CRA',
    pages: {
      '1': 'Informed consent form was signed prior to any study procedures.',
      '2': 'Investigational product dispensing log was reviewed with the site pharmacist.',
    },
  });

  // 1. Valid quote on page 1
  assert.equal(
    verifyCitationAgainstReport(
      {
        document_id: 'MVR-TS-GROUND-01',
        page_number: 1,
        verbatim_sentence: 'Informed consent form was signed prior to any study procedures.',
      },
      report
    ),
    true,
    'Expected exact verbatim quote on page 1 to be accepted'
  );

  // 2. Fabricated / paraphrased quote on page 1
  assert.equal(
    verifyCitationAgainstReport(
      {
        document_id: 'MVR-TS-GROUND-01',
        page_number: 1,
        verbatim_sentence: 'Patient signed the consent form before procedures.',
      },
      report
    ),
    false,
    'Expected paraphrased quote to be rejected'
  );

  // 3. Empty / whitespace quote
  assert.equal(
    verifyCitationAgainstReport(
      {
        document_id: 'MVR-TS-GROUND-01',
        page_number: 1,
        verbatim_sentence: '   ',
      },
      report
    ),
    false,
    'Expected whitespace quote to be rejected'
  );

  // 4. Wrong page attribution (quote on page 1 attributed to page 2)
  assert.equal(
    verifyCitationAgainstReport(
      {
        document_id: 'MVR-TS-GROUND-01',
        page_number: 2,
        verbatim_sentence: 'Informed consent form was signed prior to any study procedures.',
      },
      report
    ),
    false,
    'Expected verbatim quote attributed to wrong page (page 2) to be rejected'
  );

  // 5. Non-existent page attribution (page 99)
  assert.equal(
    verifyCitationAgainstReport(
      {
        document_id: 'MVR-TS-GROUND-01',
        page_number: 99,
        verbatim_sentence: 'Informed consent form was signed prior to any study procedures.',
      },
      report
    ),
    false,
    'Expected verbatim quote attributed to non-existent page (page 99) to be rejected'
  );

  // 6. Wrong document_id attribution
  assert.equal(
    verifyCitationAgainstReport(
      {
        document_id: 'MVR-OTHER-99',
        page_number: 1,
        verbatim_sentence: 'Informed consent form was signed prior to any study procedures.',
      },
      report
    ),
    false,
    'Expected verbatim quote attributed to wrong document_id to be rejected'
  );

  // 7. Immutability of SourceCitation via validateCandidateObservation
  const obs = validateCandidateObservation({
    observation_id: 'OBS-TS-001',
    site_id: 'SITE-101',
    visit_date: '2024-05-10',
    theme: 'Informed Consent',
    citation: {
      document_id: 'MVR-TS-GROUND-01',
      page_number: 1,
      verbatim_sentence: 'Informed consent form was signed prior to any study procedures.',
    },
  });
  assert.equal(Object.isFrozen(obs.citation), true, 'Expected obs.citation to be frozen');
  assert.throws(() => {
    (obs.citation as { verbatim_sentence: string }).verbatim_sentence = 'Tampered';
  }, TypeError);

  // 8. Pipeline drops unverified citations from custom extractor
  class FaultyTSExtractor extends ClinicalObservationExtractor {
    override async extractFromReport(rep: MonitoringReport): Promise<CandidateObservation[]> {
      return [
        validateCandidateObservation({
          observation_id: 'OBS-TS-VALID',
          site_id: rep.site_id,
          visit_date: rep.visit_date,
          theme: 'Informed Consent',
          citation: {
            document_id: rep.document_id,
            page_number: 1,
            verbatim_sentence: 'Informed consent form was signed prior to any study procedures.',
          },
        }),
        validateCandidateObservation({
          observation_id: 'OBS-TS-WRONG-PAGE',
          site_id: rep.site_id,
          visit_date: rep.visit_date,
          theme: 'Informed Consent',
          citation: {
            document_id: rep.document_id,
            page_number: 2,
            verbatim_sentence: 'Informed consent form was signed prior to any study procedures.',
          },
        }),
        validateCandidateObservation({
          observation_id: 'OBS-TS-FABRICATED',
          site_id: rep.site_id,
          visit_date: rep.visit_date,
          theme: 'Informed Consent',
          citation: {
            document_id: rep.document_id,
            page_number: 1,
            verbatim_sentence: 'Fabricated quote not in report.',
          },
        }),
      ];
    }
  }

  const pipeline = new MonitoringTriagePipeline({ extractor: new FaultyTSExtractor() });
  const output = await pipeline.run([
    {
      document_id: 'MVR-TS-GROUND-01',
      site_id: 'SITE-101',
      visit_date: '2024-05-10',
      monitor_name: 'TS Verifier CRA',
      pages: {
        '1': 'Informed consent form was signed prior to any study procedures.',
        '2': 'Investigational product dispensing log was reviewed with the site pharmacist.',
      },
    },
  ]);

  assert.equal(output.processed_sites.length, 1);
  assert.equal(output.processed_sites[0].themes.length, 1);
  assert.equal(output.processed_sites[0].themes[0].observations.length, 1);
  assert.equal(output.processed_sites[0].themes[0].observations[0].observation_id, 'OBS-TS-VALID');

  console.log('TypeScript citation grounding & immutability regression tests passed (8/8 assertions).');
}

runTests().catch((err) => {
  console.error(err);
  process.exit(1);
});
