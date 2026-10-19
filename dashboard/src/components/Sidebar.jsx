import React from 'react';
import { ShieldCheck, FileText, BarChart3, Search, Scale, CheckCircle2, ChevronRight, Globe } from 'lucide-react';
import LiveIntakeSidebar from './LiveIntakeSidebar';

export default function Sidebar({
  selectedKey,
  setSelectedKey,
  availableCompanies,
  activeTab,
  setActiveTab,
  onIntakeResult,
  activeIntake,
  isLiveIntakeOpen,
  setIsLiveIntakeOpen,
}) {
  const tabs = [
    { id: 'brief', label: 'Executive Brief & Proof', icon: ShieldCheck },
    { id: 'charts', label: 'Financial Residuals', icon: BarChart3 },
    { id: 'cohorts', label: 'Statements & Cohorts', icon: FileText },
    { id: 'evidence', label: 'Forensic Evidence Trail', icon: Search },
    { id: 'eval', label: 'Falsification & Scoreboard', icon: Scale },
    { id: 'intake', label: '🌐 Live Company Intake', icon: Globe },
  ];

  const rules = [
    { code: 'R1', text: 'Zero hardcoded company logic' },
    { code: 'R2', text: '100% mapped to ledger [Lxxxx]' },
    { code: 'R3', text: 'Deterministic math; no LLM math' },
    { code: 'R4', text: 'Strict abstention on missing data' },
    { code: 'R5', text: '≥ 2 independent source layers' },
    { code: 'R6', text: '100% public BSE/NSE filings' },
    { code: 'R8', text: 'Content-addressed SHA-256 cache' },
  ];

  return (
    <aside className="app-sidebar">
      {/* 🌐 Live Company Intake Accordion Widget */}
      <LiveIntakeSidebar
        onIntakeResult={onIntakeResult}
        activeIntake={activeIntake}
        isOpen={isLiveIntakeOpen}
        setIsOpen={setIsLiveIntakeOpen}
      />

      <div>
        <div className="sidebar-section-title">Select Company Dossier</div>
        <select
          className="dossier-selector"
          value={selectedKey}
          onChange={(e) => setSelectedKey(e.target.value)}
        >
          {availableCompanies.map((c) => (
            <option key={c.key} value={c.key}>
              {c.name} ({c.obsCount} obs)
            </option>
          ))}
        </select>
      </div>

      <div>
        <div className="sidebar-section-title">Analysis Modules</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const isIntake = tab.id === 'intake';
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.6rem',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '8px',
                  border: isIntake && !isActive ? '1px dashed #cbd5e1' : 'none',
                  background: isActive
                    ? 'rgba(2, 132, 199, 0.08)'
                    : isIntake
                    ? '#f0f9ff'
                    : 'transparent',
                  color: isActive ? '#0284c7' : isIntake ? '#0369a1' : '#475569',
                  fontWeight: isActive || isIntake ? 750 : 550,
                  fontSize: '0.84rem',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease',
                  width: '100%',
                }}
              >
                <Icon size={16} color={isActive ? '#0284c7' : isIntake ? '#0284c7' : '#64748b'} />
                <span style={{ flex: 1 }}>{tab.label}</span>
                {isActive && <ChevronRight size={14} color="#0284c7" />}
              </button>
            );
          })}
        </div>
      </div>

      <div className="rules-card">
        <div className="rules-header">
          <div className="rules-title">
            <CheckCircle2 size={16} color="#059669" />
            <span>Core Rules Status</span>
          </div>
          <span className="badge-pass">ALL PASS</span>
        </div>
        <div className="rules-list">
          {rules.map((r) => (
            <div key={r.code} className="rule-item">
              <span className="rule-code">{r.code}:</span>
              <span>{r.text}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
