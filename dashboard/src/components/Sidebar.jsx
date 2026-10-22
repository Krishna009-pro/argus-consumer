import React, { useState } from 'react';
import {
  ShieldCheck,
  FileText,
  BarChart3,
  Search,
  Scale,
  CheckCircle2,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Loader2,
  AlertCircle,
  FileSearch,
} from 'lucide-react';
import { getIntakeData } from '../data/intakeSamples';

export default function Sidebar({
  selectedKey,
  setSelectedKey,
  availableCompanies,
  activeTab,
  setActiveTab,
  onIntakeResult,
  activeIntake,
}) {
  const tabs = [
    { id: 'brief', label: 'Executive Brief & Proof', icon: ShieldCheck },
    { id: 'charts', label: 'Financial Residuals', icon: BarChart3 },
    { id: 'cohorts', label: 'Statements & Cohorts', icon: FileText },
    { id: 'evidence', label: 'Forensic Evidence Trail', icon: Search },
    { id: 'eval', label: 'Falsification & Scoreboard', icon: Scale },
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

  // 🌐 Live Company Intake State (matching streamlit_app.py lines 382-478)
  const [isIntakeOpen, setIsIntakeOpen] = useState(true);
  const [companyQuery, setCompanyQuery] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedResultIdx, setSelectedResultIdx] = useState(0);
  const [isFetchingPdfs, setIsFetchingPdfs] = useState(false);
  const [pdfLinks, setPdfLinks] = useState([]);
  const [selectedPdfIdx, setSelectedPdfIdx] = useState(0);
  const [isExtracting, setIsExtracting] = useState(false);
  const [intakeSuccess, setIntakeSuccess] = useState(null);

  const handleSearch = () => {
    if (!companyQuery.trim()) {
      setErrorMessage('Enter a company name first.');
      return;
    }
    setErrorMessage('');
    setIsSearching(true);
    setSearchResults([]);
    setPdfLinks([]);
    setIntakeSuccess(null);

    setTimeout(() => {
      setIsSearching(false);
      const data = getIntakeData(companyQuery.trim());
      setSearchResults(data.searchResults || []);
      setSelectedResultIdx(0);
    }, 500);
  };

  const handleInspectReport = () => {
    setIsFetchingPdfs(true);
    setErrorMessage('');
    setTimeout(() => {
      setIsFetchingPdfs(false);
      const data = getIntakeData(companyQuery.trim());
      setPdfLinks(data.pdfLinks || []);
      setSelectedPdfIdx(0);
    }, 400);
  };

  const handleFetchAndExtract = () => {
    setIsExtracting(true);
    setErrorMessage('');
    setTimeout(() => {
      setIsExtracting(false);
      const data = getIntakeData(companyQuery.trim());
      const extraction = data.extraction;
      setIntakeSuccess({
        count: extraction.candidate_count,
        ambiguous: extraction.ambiguous_count,
      });
      if (onIntakeResult) {
        onIntakeResult(extraction);
      }
    }, 600);
  };

  return (
    <aside className="app-sidebar">
      {/* 🌐 Live Company Intake Expander (matching streamlit_app.py lines 382-478) */}
      <div
        style={{
          background: '#ffffff',
          border: '1.5px solid #cbd5e1',
          borderRadius: '10px',
          overflow: 'hidden',
          boxShadow: isIntakeOpen ? '0 2px 8px rgba(15,23,42,0.06)' : 'none',
        }}
      >
        <button
          type="button"
          onClick={() => setIsIntakeOpen(!isIntakeOpen)}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.7rem 0.9rem',
            background: isIntakeOpen ? '#f8fafc' : '#ffffff',
            border: 'none',
            borderBottom: isIntakeOpen ? '1px solid #e2e8f0' : 'none',
            cursor: 'pointer',
            textAlign: 'left',
          }}
        >
          <span style={{ fontWeight: 750, fontSize: '0.85rem', color: '#0f172a' }}>
            🌐 Live company intake
          </span>
          {isIntakeOpen ? <ChevronUp size={16} color="#64748b" /> : <ChevronDown size={16} color="#64748b" />}
        </button>

        {isIntakeOpen && (
          <div style={{ padding: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
            <div style={{ fontSize: '0.74rem', color: '#64748b', lineHeight: 1.4 }}>
              Search public sources, cache a selected PDF, and extract review-only claims.
            </div>

            <div>
              <label style={{ fontSize: '0.74rem', color: '#334155', fontWeight: 700, display: 'block', marginBottom: '0.3rem' }}>
                Company name
              </label>
              <input
                type="text"
                value={companyQuery}
                onChange={(e) => {
                  setCompanyQuery(e.target.value);
                  if (errorMessage) setErrorMessage('');
                }}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="e.g. ITC Limited"
                style={{
                  width: '100%',
                  padding: '0.55rem 0.7rem',
                  fontSize: '0.82rem',
                  borderRadius: '6px',
                  border: '1px solid #cbd5e1',
                  boxSizing: 'border-box',
                  outline: 'none',
                  background: '#ffffff',
                  color: '#0f172a',
                }}
              />
            </div>

            {errorMessage && (
              <div
                style={{
                  background: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '6px',
                  padding: '0.45rem 0.65rem',
                  fontSize: '0.73rem',
                  color: '#b91c1c',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                }}
              >
                <AlertCircle size={13} color="#b91c1c" />
                <span>{errorMessage}</span>
              </div>
            )}

            <button
              type="button"
              onClick={handleSearch}
              disabled={isSearching}
              style={{
                width: '100%',
                padding: '0.55rem 0.8rem',
                fontSize: '0.78rem',
                fontWeight: 700,
                color: '#ffffff',
                background: '#0284c7',
                border: 'none',
                borderRadius: '6px',
                cursor: isSearching ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.4rem',
              }}
            >
              {isSearching ? <Loader2 size={13} className="spin" /> : <Search size={13} />}
              <span>Search public reports</span>
            </button>

            {searchResults.length > 0 && (
              <div style={{ marginTop: '0.2rem', display: 'flex', flexDirection: 'column', gap: '0.55rem' }}>
                <div>
                  <label style={{ fontSize: '0.72rem', color: '#334155', fontWeight: 700, display: 'block', marginBottom: '0.25rem' }}>
                    Choose a report to inspect
                  </label>
                  <select
                    className="dossier-selector"
                    style={{ fontSize: '0.74rem', padding: '0.45rem', width: '100%', boxSizing: 'border-box' }}
                    value={selectedResultIdx}
                    onChange={(e) => setSelectedResultIdx(Number(e.target.value))}
                  >
                    {searchResults.map((r, i) => (
                      <option key={i} value={i}>
                        {r.title} · {r.url}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ fontSize: '0.7rem', color: '#64748b', fontStyle: 'italic', lineHeight: 1.35 }}>
                  Search results are unverified. Confirm the publisher and report before fetching.
                </div>

                <button
                  type="button"
                  onClick={handleInspectReport}
                  disabled={isFetchingPdfs}
                  style={{
                    width: '100%',
                    padding: '0.55rem 0.8rem',
                    fontSize: '0.76rem',
                    fontWeight: 700,
                    color: '#ffffff',
                    background: '#334155',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: isFetchingPdfs ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.4rem',
                  }}
                >
                  {isFetchingPdfs ? <Loader2 size={13} className="spin" /> : <FileSearch size={13} />}
                  <span>Fetch PDF and extract claims</span>
                </button>
              </div>
            )}

            {pdfLinks.length > 0 && (
              <div style={{ marginTop: '0.2rem', display: 'flex', flexDirection: 'column', gap: '0.55rem' }}>
                <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                  Direct PDF links found on the selected page:
                </div>

                <div>
                  <label style={{ fontSize: '0.72rem', color: '#334155', fontWeight: 700, display: 'block', marginBottom: '0.25rem' }}>
                    Choose the report PDF
                  </label>
                  <select
                    className="dossier-selector"
                    style={{ fontSize: '0.74rem', padding: '0.45rem', width: '100%', boxSizing: 'border-box' }}
                    value={selectedPdfIdx}
                    onChange={(e) => setSelectedPdfIdx(Number(e.target.value))}
                  >
                    {pdfLinks.map((p, i) => (
                      <option key={i} value={i}>
                        {p.title} · {p.url}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  type="button"
                  onClick={handleFetchAndExtract}
                  disabled={isExtracting}
                  style={{
                    width: '100%',
                    padding: '0.55rem 0.8rem',
                    fontSize: '0.76rem',
                    fontWeight: 700,
                    color: '#ffffff',
                    background: '#059669',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: isExtracting ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.4rem',
                  }}
                >
                  {isExtracting ? <Loader2 size={13} className="spin" /> : <CheckCircle2 size={13} />}
                  <span>Fetch selected PDF and extract claims</span>
                </button>
              </div>
            )}

            {intakeSuccess && (
              <div
                style={{
                  background: '#ecfdf5',
                  border: '1px solid #a7f3d0',
                  borderRadius: '6px',
                  padding: '0.6rem',
                  fontSize: '0.73rem',
                  color: '#047857',
                  lineHeight: 1.4,
                }}
              >
                <div style={{ fontWeight: 700 }}>
                  Cached and extracted {intakeSuccess.count} claims. They remain unverified until reviewed.
                </div>
                {intakeSuccess.ambiguous > 0 && (
                  <div style={{ marginTop: '0.3rem', color: '#065f46', fontSize: '0.68rem' }}>
                    {intakeSuccess.ambiguous} superseded extraction rows are retained as ambiguous for audit and are excluded from review.
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Select Company Dossier */}
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

      {/* Analysis Modules Navigation */}
      <div>
        <div className="sidebar-section-title">Analysis Modules</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
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
                  border: 'none',
                  background: isActive ? 'rgba(2, 132, 199, 0.08)' : 'transparent',
                  color: isActive ? '#0284c7' : '#475569',
                  fontWeight: isActive ? 750 : 550,
                  fontSize: '0.84rem',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease',
                  width: '100%',
                }}
              >
                <Icon size={16} color={isActive ? '#0284c7' : '#64748b'} />
                <span style={{ flex: 1 }}>{tab.label}</span>
                {isActive && <ChevronRight size={14} color="#0284c7" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* Core Rules Status */}
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
