import React, { useState, useEffect } from 'react';
import {
  FlaskConical,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  FileText,
  ChevronDown,
  ChevronRight,
  Play,
  Key,
  RefreshCw,
  Sliders,
  Database,
  Copy,
  Check,
  Building2,
  Globe2,
  Calendar,
  Layers,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { TriageOutput, MonitoringReport } from './types';

export default function App() {
  const [reports, setReports] = useState<MonitoringReport[]>([]);
  const [loadingReports, setLoadingReports] = useState(true);
  const [running, setRunning] = useState(false);
  const [output, setOutput] = useState<TriageOutput | null>(null);
  const [copiedMd, setCopiedMd] = useState(false);

  // Configuration
  const [geminiKey, setGeminiKey] = useState('');
  const [extractionMode, setExtractionMode] = useState<'regex' | 'gemini'>('regex');
  const [simulateEtmf500, setSimulateEtmf500] = useState(false);
  const [simulatePartialEtmf500, setSimulatePartialEtmf500] = useState(false);
  const [simulateRegistry500, setSimulateRegistry500] = useState(false);

  // Accordions / Tabs
  const [exclusionsExpanded, setExclusionsExpanded] = useState(true);
  const [showReportsViewer, setShowReportsViewer] = useState(false);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);

  // Governance Verification Tests
  const [verifyingGovernance, setVerifyingGovernance] = useState(false);
  const [governanceResults, setGovernanceResults] = useState<{
    summary: string;
    tests: Array<{ test: string; status: 'PASSED' | 'FAILED'; details: string; iso_mapping: string }>;
  } | null>(null);

  // Load sample reports on mount
  useEffect(() => {
    fetch('/api/reports')
      .then((res) => res.json())
      .then((data) => {
        if (data.reports) {
          setReports(data.reports);
          if (data.reports.length > 0) {
            setSelectedReportId(data.reports[0].document_id);
          }
        }
      })
      .catch((err) => console.error('Failed to load reports:', err))
      .finally(() => setLoadingReports(false));
  }, []);

  // Run Triage Pipeline
  const runTriage = async () => {
    setRunning(true);
    try {
      const response = await fetch('/api/triage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reports,
          simulate_etmf_500: simulateEtmf500,
          simulate_partial_etmf_500: simulatePartialEtmf500,
          simulate_registry_500: simulateRegistry500,
          prefer_ai_studio: extractionMode === 'gemini',
          gemini_key: geminiKey || undefined,
        }),
      });
      const data: TriageOutput = await response.json();
      setOutput(data);
    } catch (err) {
      console.error('Triage execution failed:', err);
    } finally {
      setRunning(false);
    }
  };

  // Run Governance Verification Test Suite
  const runGovernanceTests = async () => {
    setVerifyingGovernance(true);
    try {
      const response = await fetch('/api/governance-tests');
      const data = await response.json();
      setGovernanceResults(data);
    } catch (err) {
      console.error('Governance test failed:', err);
    } finally {
      setVerifyingGovernance(false);
    }
  };

  // Format Reviewer Packet as Markdown
  const generateMarkdownPacket = (res: TriageOutput) => {
    const lines: string[] = [];
    lines.push('# Caldera Therapeutics — Clinical Monitoring Triage Packet');
    lines.push(`**System Status**: \`${res.system_status}\``);
    lines.push(`> *${res.disclaimer}*\n`);

    if (res.degradation_notices && res.degradation_notices.length > 0) {
      lines.push('### ⚠️ Degradation & Resilience Notices');
      for (const note of res.degradation_notices) {
        lines.push(`- ${note}`);
      }
      lines.push('');
    }

    if (res.exclusions && res.exclusions.length > 0) {
      lines.push('### 🛑 Region-Restricted Document Exclusions (Pre-processing Gate)');
      for (const exc of res.exclusions) {
        lines.push(`- **Doc ID**: \`${exc.document_id}\` | **Site**: \`${exc.site_id}\` (${exc.country}) | **Reason**: ${exc.reason}`);
      }
      lines.push('');
    }

    lines.push('## Surfaced Site Observations');
    for (const site of res.processed_sites) {
      lines.push(`### Site: \`${site.site_id}\` (${site.country}) — Reports Analyzed: ${site.total_reports_processed}`);
      if (!site.themes || site.themes.length === 0) {
        lines.push('*(No candidate signals surfaced for this site)*');
      }
      for (const theme of site.themes) {
        lines.push(`#### Theme: ${theme.theme} *(Appeared across ${theme.distinct_visit_count} distinct visits)*`);
        for (const obs of theme.observations) {
          const cit = obs.citation;
          lines.push(`- **[${obs.visit_date}]** *"${cit.verbatim_sentence}"*`);
          lines.push(`  *(Source: Document \`${cit.document_id}\`, Page ${cit.page_number})*`);
        }
      }
      lines.push('---');
    }
    return lines.join('\n');
  };

  const handleCopyMarkdown = () => {
    if (!output) return;
    const md = generateMarkdownPacket(output);
    navigator.clipboard.writeText(md);
    setCopiedMd(true);
    setTimeout(() => setCopiedMd(false), 2000);
  };

  const selectedReport = reports.find((r) => r.document_id === selectedReportId);

  return (
    <div className="min-h-screen bg-stone-100 text-stone-900 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-30 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-teal-900 text-teal-100 flex items-center justify-center font-bold">
              <FlaskConical className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-lg tracking-tight text-stone-900">
                  Caldera Therapeutics
                </span>
                <span className="text-xs bg-teal-50 text-teal-800 border border-teal-200 px-2 py-0.5 rounded-full font-medium">
                  Clinical Ops Triage
                </span>
              </div>
              <p className="text-xs text-stone-500">
                FDE Challenge Build Sprint · Team 2 (Health & Life Sciences Studio) · <em>Surfacing, Not Predicting</em>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <a
              id="ai-studio-quick-link"
              href="https://aistudio.google.com/apps/cc4ffde2-8a28-4c34-92e3-09e9b1bb805a?showAssistant=true&project=metal-contact-364103&showPreview=true"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-teal-900 bg-teal-50 hover:bg-teal-100 border border-teal-200 rounded-md transition-colors"
              title="Open applet in Google AI Studio"
            >
              <ExternalLink className="w-3.5 h-3.5 text-teal-700" />
              AI Studio Applet
            </a>
            <button
              id="view-corpus-btn"
              onClick={() => setShowReportsViewer(!showReportsViewer)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-stone-700 bg-stone-100 hover:bg-stone-200 rounded-md transition-colors"
            >
              <Database className="w-3.5 h-3.5 text-stone-500" />
              {showReportsViewer ? 'Hide eTMF Corpus' : `Corpus (${reports.length} Reports)`}
            </button>
            <button
              id="run-governance-btn"
              onClick={runGovernanceTests}
              disabled={verifyingGovernance}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-amber-900 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-md transition-colors"
            >
              <ShieldAlert className="w-3.5 h-3.5 text-amber-700" />
              {verifyingGovernance ? 'Verifying Controls...' : 'Verify Governance Controls'}
            </button>
          </div>
        </div>
      </header>

      {/* Mandatory Governance Disclaimer */}
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-2.5 sm:px-6">
        <div className="max-w-7xl mx-auto flex items-start gap-2.5 text-xs text-amber-950">
          <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold uppercase tracking-wider">Caldera Clinical Ops Triage Aid:</strong> Informational surfacing only. Not a predictive score, not a regulatory deviation record. All clinical actions require human evaluation by an authorized clinical monitor.
          </div>
        </div>
      </div>

      {/* Governance Tests Modal / Drawer */}
      {governanceResults && (
        <div className="bg-white border-b border-stone-200 px-4 py-4 sm:px-6 shadow-inner">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm text-stone-900">Governance Control Verification (Empirical Evidence)</span>
                <span className={`text-xs px-2 py-0.5 rounded font-medium ${governanceResults.summary === 'ALL_PASSED' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                  {governanceResults.summary === 'ALL_PASSED' ? 'ALL 5 CONTROLS PASSED' : 'DEGRADATION DETECTED'}
                </span>
              </div>
              <button
                id="close-gov-btn"
                onClick={() => setGovernanceResults(null)}
                className="text-xs text-stone-500 hover:text-stone-800 font-medium"
              >
                Dismiss
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {governanceResults.tests.map((t, idx) => (
                <div key={idx} className="border border-stone-200 rounded-lg p-3 bg-stone-50 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-stone-900">{t.test}</span>
                    <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                      {t.status}
                    </span>
                  </div>
                  <p className="text-stone-600 mb-2">{t.details}</p>
                  <div className="text-[11px] text-stone-400 font-mono">{t.iso_mapping}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Corpus Viewer Drawer */}
      {showReportsViewer && (
        <div className="bg-stone-50 border-b border-stone-200 px-4 py-4 sm:px-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-stone-700" />
                <h3 className="font-semibold text-sm text-stone-900">
                  eTMF Document Corpus ({reports.length} Monitoring Visit Reports)
                </h3>
              </div>
              <span className="text-xs text-stone-500">
                Sample corpus ingested from study CAL-301 eTMF
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Document List */}
              <div className="h-64 overflow-y-auto border border-stone-200 bg-white rounded-md divide-y divide-stone-100 text-xs">
                {reports.map((r) => (
                  <button
                    key={r.document_id}
                    onClick={() => setSelectedReportId(r.document_id)}
                    className={`w-full text-left p-2.5 transition-colors flex items-center justify-between ${
                      selectedReportId === r.document_id
                        ? 'bg-teal-50 text-teal-900 font-medium'
                        : 'hover:bg-stone-50 text-stone-700'
                    }`}
                  >
                    <div>
                      <div className="font-mono font-medium">{r.document_id}</div>
                      <div className="text-[11px] text-stone-500">
                        {r.site_id} · {r.visit_date}
                      </div>
                    </div>
                    {r.site_id === 'SITE-404' && (
                      <span className="text-[10px] bg-red-100 text-red-700 px-1.5 py-0.5 rounded font-mono">
                        Restricted
                      </span>
                    )}
                  </button>
                ))}
              </div>

              {/* Document Detail Preview */}
              <div className="md:col-span-2 h-64 overflow-y-auto border border-stone-200 bg-white rounded-md p-3 text-xs">
                {selectedReport ? (
                  <div>
                    <div className="flex items-center justify-between pb-2 mb-2 border-b border-stone-100">
                      <div>
                        <span className="font-bold text-stone-900 text-sm">{selectedReport.document_id}</span>
                        <span className="ml-2 font-mono text-stone-600">Site: {selectedReport.site_id}</span>
                      </div>
                      <div className="text-stone-500">
                        Date: {selectedReport.visit_date} | Monitor: {selectedReport.monitor_name}
                      </div>
                    </div>
                    <div className="space-y-3">
                      {Object.entries(selectedReport.pages)
                        .sort(([a], [b]) => Number(a) - Number(b))
                        .map(([pNum, text]) => (
                          <div key={pNum} className="bg-stone-50 p-2.5 rounded border border-stone-100">
                            <span className="text-[10px] uppercase tracking-wider font-semibold text-stone-400 block mb-1">
                              Page {pNum}
                            </span>
                            <p className="text-stone-700 leading-relaxed font-sans">{text}</p>
                          </div>
                        ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-stone-400 italic">Select a report to preview content.</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Workspace Layout */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full flex-1">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
          {/* Left Sidebar: Controls & Resilience Simulator */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-xs">
              <div className="flex items-center gap-2 pb-3 mb-3 border-b border-stone-100">
                <Sliders className="w-4 h-4 text-stone-700" />
                <h2 className="font-semibold text-sm text-stone-900">Execution Configuration</h2>
              </div>

              {/* Extraction Engine */}
              <div className="mb-4">
                <label className="block text-xs font-medium text-stone-700 mb-1.5">
                  Extraction Engine
                </label>
                <div className="space-y-1.5">
                  <label className="flex items-center gap-2 text-xs text-stone-800 p-2 rounded-lg border border-stone-200 cursor-pointer hover:bg-stone-50">
                    <input
                      type="radio"
                      name="engine"
                      value="regex"
                      checked={extractionMode === 'regex'}
                      onChange={() => setExtractionMode('regex')}
                      className="text-teal-600 focus:ring-teal-500"
                    />
                    <div>
                      <div className="font-medium">Deterministic Regex</div>
                      <div className="text-[11px] text-stone-500">Default / Immutable Fallback</div>
                    </div>
                  </label>

                  <label className="flex items-center gap-2 text-xs text-stone-800 p-2 rounded-lg border border-stone-200 cursor-pointer hover:bg-stone-50">
                    <input
                      type="radio"
                      name="engine"
                      value="gemini"
                      checked={extractionMode === 'gemini'}
                      onChange={() => setExtractionMode('gemini')}
                      className="text-teal-600 focus:ring-teal-500"
                    />
                    <div>
                      <div className="font-medium flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-amber-500" />
                        Google AI Studio
                      </div>
                      <div className="text-[11px] text-stone-500">Gemini 2.5 Flash Structured JSON</div>
                    </div>
                  </label>
                </div>
              </div>

              {/* Gemini Key Input */}
              {extractionMode === 'gemini' && (
                <div className="mb-4 bg-teal-50/50 p-2.5 rounded-lg border border-teal-100">
                  <label className="flex items-center gap-1 text-xs font-medium text-teal-900 mb-1">
                    <Key className="w-3 h-3" />
                    Google AI Studio API Key
                  </label>
                  <input
                    id="gemini-key-input"
                    type="password"
                    placeholder="Enter GEMINI_API_KEY (optional if env set)"
                    value={geminiKey}
                    onChange={(e) => setGeminiKey(e.target.value)}
                    className="w-full text-xs bg-white border border-stone-300 rounded px-2.5 py-1.5 text-stone-900 focus:outline-none focus:ring-1 focus:ring-teal-500"
                  />
                  <p className="text-[10px] text-teal-700 mt-1">
                    Falls back safely to Deterministic Regex if key is omitted or invalid.
                  </p>
                </div>
              )}

              {/* Resilience & Curveball 3 Simulator */}
              <div className="pt-3 border-t border-stone-100 mb-4">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-stone-800 mb-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  Resilience & Curveball 3 Simulator
                </div>
                <div className="space-y-2">
                  <label className="flex items-start gap-2 text-xs text-stone-700 cursor-pointer">
                    <input
                      id="sim-etmf-check"
                      type="checkbox"
                      checked={simulateEtmf500}
                      onChange={(e) => {
                        setSimulateEtmf500(e.target.checked);
                        if (e.target.checked) setSimulatePartialEtmf500(false);
                      }}
                      className="mt-0.5 rounded text-teal-600 focus:ring-teal-500"
                    />
                    <span>Simulate Complete eTMF Outage (HTTP 500)</span>
                  </label>

                  <label className="flex items-start gap-2 text-xs text-stone-700 cursor-pointer bg-amber-50/60 p-1.5 rounded border border-amber-200/70">
                    <input
                      id="sim-partial-etmf-check"
                      type="checkbox"
                      checked={simulatePartialEtmf500}
                      onChange={(e) => {
                        setSimulatePartialEtmf500(e.target.checked);
                        if (e.target.checked) setSimulateEtmf500(false);
                      }}
                      className="mt-0.5 rounded text-amber-600 focus:ring-amber-500"
                    />
                    <div>
                      <span className="font-semibold text-amber-950">Partial eTMF Outage (15:00 Curveball)</span>
                      <p className="text-[10px] text-amber-800">11 of 20 reports retrieved; 9 fail with 500s</p>
                    </div>
                  </label>

                  <label className="flex items-start gap-2 text-xs text-stone-700 cursor-pointer">
                    <input
                      id="sim-reg-check"
                      type="checkbox"
                      checked={simulateRegistry500}
                      onChange={(e) => setSimulateRegistry500(e.target.checked)}
                      className="mt-0.5 rounded text-teal-600 focus:ring-teal-500"
                    />
                    <span>Simulate Site Registry (HTTP 500)</span>
                  </label>
                </div>
              </div>

              {/* Run Primary Action Button */}
              <button
                id="run-triage-btn"
                onClick={runTriage}
                disabled={running || loadingReports}
                className="w-full py-2.5 px-4 bg-teal-800 hover:bg-teal-900 text-white font-medium text-xs rounded-lg shadow-xs flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                {running ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    Executing Triage Pipeline...
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    Run Clinical Monitoring Triage
                  </>
                )}
              </button>
            </div>

            {/* Architecture Highlights Card */}
            <div className="bg-stone-50 border border-stone-200 rounded-xl p-3.5 text-xs text-stone-600 space-y-2">
              <div className="font-semibold text-stone-800 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-teal-700" />
                Pipeline Governance Controls
              </div>
              <ul className="space-y-1.5 text-[11px]">
                <li className="flex items-start gap-1.5">
                  <Check className="w-3 h-3 text-teal-600 shrink-0 mt-0.5" />
                  <span><strong>ISO 42001 A.6:</strong> Zero predictive scores or severity ranks (GxP CSV protection).</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <Check className="w-3 h-3 text-teal-600 shrink-0 mt-0.5" />
                  <span><strong>ISO 42001 A.7:</strong> EDC clinical boundary + region-restriction gate.</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <Check className="w-3 h-3 text-teal-600 shrink-0 mt-0.5" />
                  <span><strong>ISO 42001 A.8:</strong> Verbatim sentence provenance & page citations.</span>
                </li>
                <li className="flex items-start gap-1.5">
                  <Check className="w-3 h-3 text-teal-600 shrink-0 mt-0.5" />
                  <span><strong>ISO 42001 A.10:</strong> Transparent fail-closed graceful degradation on 500s.</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Right Main Panel: Results & Reviewer Packets */}
          <div className="lg:col-span-3 space-y-4">
            {!output && !running && (
              <div className="bg-white border border-stone-200 rounded-xl p-12 text-center shadow-xs">
                <div className="w-12 h-12 rounded-full bg-stone-100 text-stone-400 flex items-center justify-center mx-auto mb-3">
                  <FlaskConical className="w-6 h-6 text-stone-500" />
                </div>
                <h3 className="font-semibold text-stone-800 text-base mb-1">
                  Ready to Execute Clinical Monitoring Triage
                </h3>
                <p className="text-stone-500 text-xs max-w-md mx-auto mb-5 leading-relaxed">
                  Click <strong>Run Clinical Monitoring Triage</strong> to ingest the 20-report eTMF corpus, apply regional compliance gating, extract candidate observations with verbatim source attribution, and generate structured reviewer packets.
                </p>
                <button
                  id="initial-run-btn"
                  onClick={runTriage}
                  disabled={loadingReports}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-teal-800 hover:bg-teal-900 text-white text-xs font-medium rounded-lg transition-colors"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  Run Pipeline Now
                </button>
              </div>
            )}

            {running && (
              <div className="bg-white border border-stone-200 rounded-xl p-12 text-center shadow-xs animate-pulse">
                <RefreshCw className="w-8 h-8 text-teal-700 animate-spin mx-auto mb-3" />
                <h3 className="font-medium text-stone-800 text-sm">
                  Executing Triage Pipeline Across Reports...
                </h3>
                <p className="text-stone-500 text-xs mt-1">
                  Applying regional sovereignty checks, extracting verbatim citations, and assembling packets.
                </p>
              </div>
            )}

            {output && !running && (
              <div className="space-y-4">
                {/* Status Banner */}
                <div
                  className={`p-4 rounded-xl border flex items-start justify-between shadow-xs ${
                    output.system_status === 'DEGRADED'
                      ? 'bg-amber-50 border-amber-300 text-amber-950'
                      : 'bg-emerald-50 border-emerald-300 text-emerald-950'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {output.system_status === 'DEGRADED' ? (
                      <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <div className="font-bold text-sm">
                        System Status: {output.system_status}
                      </div>
                      {output.degradation_notices && output.degradation_notices.length > 0 ? (
                        <div className="mt-1 space-y-1 text-xs">
                          {output.degradation_notices.map((notice, idx) => (
                            <p key={idx} className="font-medium text-amber-800 bg-amber-100/70 px-2 py-1 rounded">
                              {notice}
                            </p>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-emerald-800 mt-0.5">
                          Pipeline executed normally. All eligible documents processed with verbatim grounding.
                        </p>
                      )}
                    </div>
                  </div>

                  <button
                    id="copy-markdown-btn"
                    onClick={handleCopyMarkdown}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-stone-200 hover:bg-stone-50 text-stone-700 text-xs font-medium rounded-md shadow-2xs transition-colors shrink-0"
                  >
                    {copiedMd ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                        Copied Packet!
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 text-stone-500" />
                        Copy Markdown Packet
                      </>
                    )}
                  </button>
                </div>

                {/* Critical Data Completeness Warning (15:00 Curveball) */}
                {output.data_completeness_warning && (
                  <div className="bg-amber-50 border border-amber-300 text-amber-950 p-4 rounded-xl text-xs flex items-start gap-3 shadow-xs">
                    <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
                    <div>
                      <div className="font-bold text-sm text-amber-900 mb-0.5">⚠️ Data Completeness & Denominator Disclosure (15:00 Curveball Defense)</div>
                      <p className="leading-relaxed text-amber-900 font-medium">{output.data_completeness_warning}</p>
                    </div>
                  </div>
                )}

                {/* Exclusions Expander (Pre-processing Gate) */}
                {output.exclusions && output.exclusions.length > 0 && (
                  <div className="bg-white border border-stone-200 rounded-xl overflow-hidden shadow-xs">
                    <button
                      id="toggle-exclusions-btn"
                      onClick={() => setExclusionsExpanded(!exclusionsExpanded)}
                      className="w-full px-4 py-3 bg-red-50/50 hover:bg-red-50 flex items-center justify-between border-b border-red-100 text-left transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <ShieldAlert className="w-4 h-4 text-red-600" />
                        <span className="font-semibold text-xs text-red-950">
                          🛑 Region-Restricted Document Exclusions ({output.exclusions.length} Documents Dropped at Gate)
                        </span>
                      </div>
                      {exclusionsExpanded ? (
                        <ChevronDown className="w-4 h-4 text-stone-500" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-stone-500" />
                      )}
                    </button>

                    {exclusionsExpanded && (
                      <div className="p-4 bg-white text-xs">
                        <p className="text-stone-600 text-xs mb-3">
                          Documents originating from region-restricted jurisdictions are dropped <strong>before</strong> content extraction to enforce data sovereignty (ISO 42001 A.7). The model and extractor are never invoked for these files.
                        </p>
                        <div className="overflow-x-auto border border-stone-200 rounded-md">
                          <table className="w-full text-left text-xs">
                            <thead className="bg-stone-50 text-stone-700 border-b border-stone-200">
                              <tr>
                                <th className="p-2.5 font-semibold">Document ID</th>
                                <th className="p-2.5 font-semibold">Site ID</th>
                                <th className="p-2.5 font-semibold">Country</th>
                                <th className="p-2.5 font-semibold">Reason / Audit Trail</th>
                                <th className="p-2.5 font-semibold">Timestamp</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-stone-100 text-stone-600">
                              {output.exclusions.map((e, idx) => (
                                <tr key={idx} className="hover:bg-stone-50/70">
                                  <td className="p-2.5 font-mono font-medium text-stone-900">{e.document_id}</td>
                                  <td className="p-2.5 font-medium">{e.site_id}</td>
                                  <td className="p-2.5">
                                    <span className="bg-red-50 text-red-700 px-1.5 py-0.5 rounded font-mono text-[11px]">
                                      {e.country}
                                    </span>
                                  </td>
                                  <td className="p-2.5 text-stone-700">{e.reason}</td>
                                  <td className="p-2.5 text-stone-400 font-mono text-[11px]">
                                    {new Date(e.timestamp).toLocaleTimeString()}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Surfaced Site Review Packets */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-sm text-stone-900 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-teal-800" />
                      Surfaced Site Review Packets ({output.processed_sites.length} Sites Processed)
                    </h3>
                    <span className="text-xs text-stone-500 font-medium">
                      Unranked Human Review · Grouped by Site & Recurring Theme
                    </span>
                  </div>

                  {output.processed_sites.length === 0 ? (
                    <div className="p-8 text-center bg-white border border-stone-200 rounded-xl text-xs text-stone-500 italic">
                      No eligible reports processed (or all held/degraded).
                    </div>
                  ) : (
                    output.processed_sites.map((site) => (
                      <div
                        key={site.site_id}
                        className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs space-y-4"
                      >
                        {/* Site Header */}
                        <div className="flex flex-wrap items-center justify-between pb-3 border-b border-stone-100 gap-2">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-md bg-stone-100 text-stone-700 flex items-center justify-center font-bold text-xs">
                              <Building2 className="w-4 h-4 text-stone-600" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-sm text-stone-900 font-mono">
                                  Site: {site.site_id}
                                </span>
                                <span className="text-xs text-stone-600 bg-stone-100 px-2 py-0.5 rounded font-medium flex items-center gap-1">
                                  <Globe2 className="w-3 h-3 text-stone-500" />
                                  {site.country}
                                </span>
                              </div>
                              <div className="text-xs text-stone-500 mt-0.5">
                                Analyzed across <strong>{site.total_reports_processed}</strong> monitoring visit reports
                              </div>
                            </div>
                          </div>

                          <div className="text-xs text-stone-500 bg-stone-50 px-2.5 py-1 rounded-md border border-stone-100">
                            {site.themes.length} Recurring Themes Surfaced
                          </div>
                        </div>

                        {/* Themes for this site */}
                        {site.themes.length === 0 ? (
                          <p className="text-xs text-stone-400 italic">
                            *(No candidate signals surfaced for this site)*
                          </p>
                        ) : (
                          <div className="space-y-4">
                            {site.themes.map((theme, tIdx) => (
                              <div
                                key={tIdx}
                                className="bg-stone-50/70 border border-stone-200/80 rounded-lg p-3.5 space-y-2.5"
                              >
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-teal-600"></span>
                                    <h4 className="font-semibold text-xs text-stone-900">
                                      Theme: {theme.theme}
                                    </h4>
                                  </div>
                                  <span className="text-[11px] font-medium text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 flex items-center gap-1">
                                    <Calendar className="w-3 h-3 text-teal-600" />
                                    Appeared across {theme.distinct_visit_count} distinct visits ({theme.observations.length} observations)
                                  </span>
                                </div>

                                <div className="space-y-2 pl-3 border-l-2 border-teal-200">
                                  {theme.observations.map((obs, oIdx) => {
                                    const cit = obs.citation;
                                    return (
                                      <div key={oIdx} className="text-xs space-y-0.5">
                                        <div className="flex items-baseline gap-2">
                                          <span className="font-semibold text-stone-700 font-mono text-[11px] shrink-0">
                                            [{obs.visit_date}]
                                          </span>
                                          <p className="text-stone-800 italic leading-relaxed">
                                            "{cit.verbatim_sentence}"
                                          </p>
                                        </div>
                                        <div className="text-[11px] text-stone-500 font-mono pl-1">
                                          Source: Document <code className="bg-stone-200/70 px-1 py-0.2 rounded text-stone-800">{cit.document_id}</code>, Page {cit.page_number}
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
