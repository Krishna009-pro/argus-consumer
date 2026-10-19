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
import LiveIntakeStudio from './components/LiveIntakeStudio';
import { ShieldCheck, BarChart3, FileText, Search, Scale, Globe } from 'lucide-react';

export default function App() {
  const reports = bundledData.reports || {};
  const ledger = bundledData.ledger || [];

  // Available companies list (prioritize rich reports)
  const availableCompanies = Object.keys(reports)
    .filter((k) => k === 'hindustan-unilever-limited' || k === 'itc-limited')
    .map((k) => {
      const rep = reports[k];
      const d = rep?.dossier || {};
      return {
        key: k,
        name: d.company || k.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        obsCount: (d.evidence || []).length,
      };
    });

  const [selectedKey, setSelectedKey] = useState(
    availableCompanies.length ? availableCompanies[0].key : Object.keys(reports)[0]
  );
  const [activeTab, setActiveTab] = useState('brief');
  const [activeIntake, setActiveIntake] = useState(null);
  const [isLiveIntakeOpen, setIsLiveIntakeOpen] = useState(false);

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
    window.print();
  };

  const tabs = [
    { id: 'brief', label: 'Executive Brief & Proof', icon: ShieldCheck },
    { id: 'charts', label: 'Financial Residuals', icon: BarChart3 },
    { id: 'cohorts', label: 'Statements & Cohorts', icon: FileText },
    { id: 'evidence', label: 'Forensic Evidence Trail', icon: Search },
    { id: 'eval', label: 'Falsification & Scoreboard', icon: Scale },
    { id: 'intake', label: '🌐 Live Company Intake', icon: Globe },
  ];

  return (
    <div className="app-container">
      <Header
        onOpenLiveIntake={() => setActiveTab('intake')}
        isIntakeActive={activeTab === 'intake'}
      />

      <div className="main-layout">
        <Sidebar
          selectedKey={selectedKey}
          setSelectedKey={setSelectedKey}
          availableCompanies={availableCompanies}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onIntakeResult={setActiveIntake}
          activeIntake={activeIntake}
          isLiveIntakeOpen={isLiveIntakeOpen}
          setIsLiveIntakeOpen={setIsLiveIntakeOpen}
        />

        <main className="content-area">
          {/* Active Online Source Intake Workspace (pinned when in other analysis tabs) */}
          {activeIntake && activeTab !== 'intake' && (
            <IntakeWorkspace
              intake={activeIntake}
              onClose={() => setActiveIntake(null)}
              currentDossierCompany={company}
            />
          )}

          {/* Dedicated Full Live Intake Studio View */}
          {activeTab === 'intake' && (
            <LiveIntakeStudio
              onIntakeResult={setActiveIntake}
              activeIntake={activeIntake}
              currentDossierCompany={company}
            />
          )}

          {/* Standard Company Dossier Views */}
          {activeTab !== 'intake' && (
            <>
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

              {/* Interactive Navigation Tabs */}
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
            </>
          )}
        </main>
      </div>
    </div>
  );
}
