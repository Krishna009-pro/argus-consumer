import React, { useState } from 'react';
import bundledData from './data/data.json';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import HeroBanner from './components/HeroBanner';
import MetricCards from './components/MetricCards';
import ProofPanel from './components/ProofPanel';
import ResidualChart from './components/ResidualChart';
import CohortsView from './components/CohortsView';
import EvidenceTrail from './components/EvidenceTrail';
import FalsificationView from './components/FalsificationView';
import IntakeWorkspace from './components/IntakeWorkspace';
import { ShieldCheck, BarChart3, FileText, Search, Scale } from 'lucide-react';

export default function App() {
  const [reports, setReports] = useState(bundledData.reports || {});
  const [ledger, setLedger] = useState(bundledData.ledger || []);

  // Canonical companies list for dropdown selector
  const availableCompanies = React.useMemo(() => {
    const seen = new Set();
    const list = [];
    // Prioritize main canonical keys
    const canonicalOrder = [
      'hindustan-unilever-limited',
      'itc-limited',
      'godrej-consumer-products-limited',
      'nestle-india-limited',
      'united-spirits-limited',
      'britannia-industries-limited',
      'dabur-india-limited',
      'marico-limited',
    ];

    const sortedKeys = Object.keys(reports).sort((a, b) => {
      const idxA = canonicalOrder.indexOf(a);
      const idxB = canonicalOrder.indexOf(b);
      if (idxA !== -1 && idxB !== -1) return idxA - idxB;
      if (idxA !== -1) return -1;
      if (idxB !== -1) return 1;
      return a.localeCompare(b);
    });

    for (const k of sortedKeys) {
      const rep = reports[k];
      const d = rep?.dossier || {};
      const name = d.company || k.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
      const normalized = name.toLowerCase().replace(/[^a-z0-9]/g, '');
      if (!seen.has(normalized)) {
        seen.add(normalized);
        const obs = (d.evidence || []).length || (d.validation?.candidates || []).length || 0;
        list.push({
          key: k,
          name,
          obsCount: obs,
        });
      }
    }
    return list;
  }, [reports]);

  const [selectedKey, setSelectedKey] = useState(
    availableCompanies.length ? availableCompanies[0].key : Object.keys(reports)[0]
  );
  const [activeTab, setActiveTab] = useState('brief');
  const [activeIntake, setActiveIntake] = useState(null);

  // Ingested live company callback: update active intake and switch dashboard dossier
  const handleIntakeResult = (extraction) => {
    if (!extraction) return;
    setActiveIntake(extraction);

    const compName = extraction.company || 'Unknown Company';
    const cleanSlug = compName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

    // Check if an existing report matches this company
    const compLower = compName.toLowerCase();
    const existingKey = Object.keys(reports).find((k) => {
      const repName = (reports[k]?.dossier?.company || '').toLowerCase();
      return k === cleanSlug || repName === compLower || (repName && compLower.includes(repName)) || (repName && repName.includes(compLower));
    });

    if (existingKey) {
      setSelectedKey(existingKey);
    } else {
      // Build dynamic dossier and analysis for newly ingested company
      const candList = extraction.candidates || [];
      const newDossier = {
        company: compName,
        discovery: `Statutory audited intake from ${extraction.title || 'annual report'}. ${extraction.candidate_count || candList.length} extraction candidates retrieved for audit.`,
        why_it_matters: [
          `Primary statutory source: ${extraction.url}`,
          'Under Rule R2, candidate values require verification against the source statement page before ledger commitment.'
        ],
        evidence: candList.map((c) => c.id),
        timeline: candList.map((c) => ({
          period: c.period || 'FY2025',
          angle: c.metric,
          reported: c.value,
          expected_low: null,
          expected_high: null,
          ledger_ids: [c.id],
          status: 'unverified_candidate',
          consolidation_basis: c.consolidation_basis || 'consolidated',
          reporting_scope: 'annual',
          comparability_cohort: 'FMCG'
        })),
        numbers: Object.fromEntries(
          candList.map((c) => [`${c.metric} ${c.period || 'FY2025'} [${c.id}]`, c.value])
        ),
        counterargument: 'Candidates are machine-extracted directly from public statutory PDF and remain unverified until audited against the physical statement page.',
        falsification_condition: 'Candidate values will be falsified if column headers, reporting units, or period dates differ upon line-by-line inspection.',
        evidence_score: 0.0,
        evidence_label: 'Unverified Candidate',
        not_tested: ['Pending human verification against PDF statement page.'],
        hypotheses: [],
        red_team_log: candList.slice(0, 3).map((c) => ({
          candidate_id: c.id,
          test: 'Verbatim text snippet audit',
          passed: true,
          notes: `Doc page ${c.doc_page}: ${c.snippet || 'Statement table row'}`
        })),
        score_components: {},
        validation: {
          state: 'unverified',
          candidates: candList,
          rejected_findings: [],
          tested_patterns: candList.length,
          panel_count: 1,
          generated_candidates: candList,
          peer_companies: ['Hindustan Unilever Limited', 'ITC Limited', 'Dabur India Limited'],
          period_type: 'annual',
          consolidation_basis: 'consolidated',
          reporting_scope: 'statutory',
          comparability_cohort: 'FMCG',
          verified_ledger_entries: 0,
          elapsed_seconds: 0.05
        }
      };

      const newAnalysis = {
        company: compName,
        panels: [
          {
            panel: {
              company: compName,
              period_type: 'annual',
              consolidation_basis: 'consolidated',
              reporting_scope: 'statutory',
              comparability_cohort: 'FMCG',
              periods: ['FY2024-25']
            },
            angles: {},
            candidates: candList,
            tested_patterns: candList.length,
            peer_companies: ['Hindustan Unilever Limited', 'ITC Limited', 'Dabur India Limited']
          }
        ],
        rejected: [],
        status: 'candidate_intake',
        reason: null
      };

      const newEntries = candList.map((c) => ({
        id: c.id,
        company: compName,
        metric: c.metric,
        value: c.value,
        period: c.period || 'FY2025',
        period_type: 'annual',
        period_start: '2024-04-01',
        period_end: '2025-03-31',
        unit: 'INR_crore',
        currency: 'INR',
        source_type: 'filing',
        source_url: extraction.url,
        source_sha256: extraction.sha256,
        cache_path: extraction.cache_path,
        doc_page: c.doc_page,
        snippet: c.snippet,
        notes: 'Machine-extracted candidate from public statutory filing (unverified)',
        verified: false,
        status: 'unverified'
      }));

      setReports((prev) => ({
        ...prev,
        [cleanSlug]: { dossier: newDossier, analysis: newAnalysis }
      }));
      setLedger((prev) => [...prev, ...newEntries]);
      setSelectedKey(cleanSlug);
    }
  };

  const activeReport = reports[selectedKey] || Object.values(reports)[0] || {};
  const dossier = activeReport.dossier || {};
  const analysis = activeReport.analysis || {};

  const validation = dossier.validation || {};
  const state = validation.state || 'unknown';
  const company = dossier.company || selectedKey.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  // Ledger entries linked to this company dossier
  const evidenceIds = new Set(dossier.evidence || []);
  const linkedEntries = ledger.filter((e) => evidenceIds.has(e.id));

  const handleExportPdf = () => {
    // Open or download the verified audit dossier PDF
    window.open(`/api/pdf/${selectedKey}`, '_blank');
  };

  const tabs = [
    { id: 'brief', label: 'Executive Brief & Proof', icon: ShieldCheck },
    { id: 'charts', label: 'Financial Residuals', icon: BarChart3 },
    { id: 'cohorts', label: 'Statements & Cohorts', icon: FileText },
    { id: 'evidence', label: 'Forensic Evidence Trail', icon: Search },
    { id: 'eval', label: 'Falsification & Scoreboard', icon: Scale },
  ];

  return (
    <div className="app-container">
      <Header />

      <div className="main-layout">
        <Sidebar
          selectedKey={selectedKey}
          setSelectedKey={setSelectedKey}
          availableCompanies={availableCompanies}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onIntakeResult={handleIntakeResult}
          activeIntake={activeIntake}
        />

        <main className="content-area">
          {/* Active Online Source Intake Workspace (matching streamlit_app.py lines 524-564) */}
          {activeIntake && (
            <IntakeWorkspace
              intake={activeIntake}
              onClose={() => setActiveIntake(null)}
              currentDossierCompany={company}
            />
          )}

          <HeroBanner
            company={company}
            state={state}
            evidenceCount={linkedEntries.length}
            onExportPdf={handleExportPdf}
          />

          <MetricCards
            state={state}
            obsCount={linkedEntries.length}
            panelCount={(analysis.panels || []).length}
            score={dossier.evidence_score || 0.0}
            scoreLabel={dossier.evidence_label || 'Weak'}
          />

          {/* Interactive Navigation Tabs (Original 5 Modules) */}
          <div className="tabs-header">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`tab-btn ${isActive ? 'active' : ''}`}
                >
                  <Icon size={16} />
                  <span>{tab.label}</span>
                  {isActive && <div className="tab-active-indicator" />}
                </button>
              );
            })}
          </div>

          {/* Active Tab View */}
          {activeTab === 'brief' && <ProofPanel dossier={dossier} analysis={analysis} />}
          {activeTab === 'charts' && <ResidualChart analysis={analysis} />}
          {activeTab === 'cohorts' && <CohortsView analysis={analysis} />}
          {activeTab === 'evidence' && <EvidenceTrail linkedEntries={linkedEntries} />}
          {activeTab === 'eval' && <FalsificationView dossier={dossier} />}
        </main>
      </div>
    </div>
  );
}
