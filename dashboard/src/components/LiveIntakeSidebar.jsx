import React, { useState } from 'react';
import { Globe, Search, FileDown, Loader2, CheckCircle2, ChevronDown, ChevronUp, AlertCircle, FileSearch, Sparkles } from 'lucide-react';
import { getIntakeData } from '../data/intakeSamples';

export default function LiveIntakeSidebar({ onIntakeResult, activeIntake, isOpen, setIsOpen }) {
  const [internalOpen, setInternalOpen] = useState(true);
  const open = isOpen !== undefined ? isOpen : internalOpen;
  const toggleOpen = () => {
    if (setIsOpen) setIsOpen(!open);
    else setInternalOpen(!internalOpen);
  };

  const [companyQuery, setCompanyQuery] = useState('Dabur India Limited');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedResultIdx, setSelectedResultIdx] = useState(0);
  const [isFetchingPdfs, setIsFetchingPdfs] = useState(false);
  const [pdfLinks, setPdfLinks] = useState([]);
  const [selectedPdfIdx, setSelectedPdfIdx] = useState(0);
  const [isExtracting, setIsExtracting] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  const handleSearch = () => {
    if (!companyQuery.trim()) return;
    setIsSearching(true);
    setStatusMessage(null);
    setPdfLinks([]);

    setTimeout(() => {
      setIsSearching(false);
      const data = getIntakeData(companyQuery);
      setSearchResults(data.searchResults);
      setSelectedResultIdx(0);
    }, 600);
  };

  const handleInspectReport = () => {
    setIsFetchingPdfs(true);
    setStatusMessage(null);
    setTimeout(() => {
      setIsFetchingPdfs(false);
      const data = getIntakeData(companyQuery);
      setPdfLinks(data.pdfLinks);
      setSelectedPdfIdx(0);
    }, 500);
  };

  const handleFetchAndExtract = () => {
    setIsExtracting(true);
    setStatusMessage(null);
    setTimeout(() => {
      setIsExtracting(false);
      const data = getIntakeData(companyQuery);
      const extraction = data.extraction;
      setStatusMessage({
        type: 'success',
        text: `Cached and extracted ${extraction.candidate_count} claims. They remain unverified until reviewed.`,
        ambiguous: extraction.ambiguous_count
          ? `${extraction.ambiguous_count} superseded extraction rows are retained as ambiguous for audit and are excluded from review.`
          : null,
      });
      onIntakeResult(extraction);
    }, 800);
  };

  return (
    <div
      style={{
        background: open ? '#ffffff' : '#f8fafc',
        border: '1.5px solid',
        borderColor: open ? '#0284c7' : '#cbd5e1',
        borderRadius: '12px',
        overflow: 'hidden',
        transition: 'all 0.2s ease',
        boxShadow: open ? '0 4px 16px rgba(2, 132, 199, 0.08)' : 'none',
      }}
    >
      {/* Accordion Header */}
      <button
        onClick={toggleOpen}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.8rem 1rem',
          background: open ? 'linear-gradient(to right, rgba(2, 132, 199, 0.04), transparent)' : 'transparent',
          border: 'none',
          cursor: 'pointer',
          fontFamily: 'var(--font-sans)',
          textAlign: 'left',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', fontWeight: 800, fontSize: '0.84rem', color: '#0f172a' }}>
          <div style={{ background: '#e0f2fe', padding: '4px', borderRadius: '6px', display: 'flex' }}>
            <Globe size={15} color="#0284c7" />
          </div>
          <span>🌐 Live company intake</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '2px 6px', borderRadius: '4px', background: '#e0f2fe', color: '#0284c7' }}>
            SERPER + PDF
          </span>
          {open ? <ChevronUp size={16} color="#64748b" /> : <ChevronDown size={16} color="#64748b" />}
        </div>
      </button>

      {/* Accordion Body */}
      {open && (
        <div style={{ padding: '0.6rem 1rem 1rem 1rem', borderTop: '1px solid #f1f5f9', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <p style={{ fontSize: '0.74rem', color: '#64748b', lineHeight: 1.4, margin: 0 }}>
            Search public sources, cache a selected PDF, and extract review-only candidate claims.
          </p>

          {/* Step 1: Company Name Input */}
          <div>
            <label style={{ fontSize: '0.72rem', fontWeight: 750, color: '#475569', textTransform: 'uppercase', marginBottom: '0.3rem', display: 'block' }}>
              Company Name
            </label>
            <input
              type="text"
              className="search-input"
              style={{ padding: '0.55rem 0.75rem', fontSize: '0.8rem', width: '100%', boxSizing: 'border-box' }}
              value={companyQuery}
              onChange={(e) => setCompanyQuery(e.target.value)}
              placeholder="e.g. Dabur India Limited or ITC Limited"
            />
          </div>

          {/* Search Button */}
          <button
            onClick={handleSearch}
            disabled={isSearching || !companyQuery.trim()}
            className="btn-primary"
            style={{ padding: '0.55rem', fontSize: '0.78rem', justifyContent: 'center' }}
          >
            {isSearching ? <Loader2 size={14} className="spin" /> : <Search size={14} />}
            <span>Search public reports</span>
          </button>

          {/* Step 2: Search Results Dropdown */}
          {searchResults.length > 0 && (
            <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
              <label style={{ fontSize: '0.72rem', fontWeight: 750, color: '#475569', textTransform: 'uppercase', marginBottom: '0.3rem', display: 'block' }}>
                Choose report to inspect
              </label>
              <select
                className="dossier-selector"
                style={{ fontSize: '0.74rem', padding: '0.45rem', width: '100%', boxSizing: 'border-box' }}
                value={selectedResultIdx}
                onChange={(e) => setSelectedResultIdx(Number(e.target.value))}
              >
                {searchResults.map((r, i) => (
                  <option key={i} value={i}>
                    {r.title}
                  </option>
                ))}
              </select>
              <span style={{ fontSize: '0.68rem', color: '#64748b', marginTop: '0.25rem', display: 'block', fontStyle: 'italic' }}>
                Search results are unverified. Confirm the publisher and report before fetching.
              </span>

              <button
                onClick={handleInspectReport}
                disabled={isFetchingPdfs}
                className="btn-primary"
                style={{ marginTop: '0.55rem', padding: '0.5rem', fontSize: '0.76rem', background: '#334155', justifyContent: 'center', width: '100%' }}
              >
                {isFetchingPdfs ? <Loader2 size={13} className="spin" /> : <FileSearch size={13} />}
                <span>Fetch PDF and extract claims</span>
              </button>
            </div>
          )}

          {/* Step 3: Discovered Direct PDF Links */}
          {pdfLinks.length > 0 && (
            <div style={{ background: '#f0fdf4', padding: '0.75rem', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
              <label style={{ fontSize: '0.72rem', fontWeight: 750, color: '#166534', textTransform: 'uppercase', marginBottom: '0.3rem', display: 'block' }}>
                Direct PDF links found ({pdfLinks.length}):
              </label>
              <select
                className="dossier-selector"
                style={{ fontSize: '0.74rem', padding: '0.45rem', width: '100%', boxSizing: 'border-box', borderColor: '#86efac' }}
                value={selectedPdfIdx}
                onChange={(e) => setSelectedPdfIdx(Number(e.target.value))}
              >
                {pdfLinks.map((p, i) => (
                  <option key={i} value={i}>
                    {p.title}
                  </option>
                ))}
              </select>

              <button
                onClick={handleFetchAndExtract}
                disabled={isExtracting}
                className="btn-primary"
                style={{ marginTop: '0.55rem', padding: '0.55rem', fontSize: '0.78rem', background: 'linear-gradient(135deg, #059669 0%, #047857 100%)', justifyContent: 'center', width: '100%' }}
              >
                {isExtracting ? <Loader2 size={14} className="spin" /> : <CheckCircle2 size={14} />}
                <span>Fetch selected PDF and extract claims</span>
              </button>
            </div>
          )}

          {/* Status Message */}
          {statusMessage && (
            <div
              style={{
                background: '#ecfdf5',
                border: '1px solid #a7f3d0',
                borderRadius: '8px',
                padding: '0.65rem 0.75rem',
                fontSize: '0.73rem',
                color: '#047857',
                lineHeight: 1.4,
              }}
            >
              <div style={{ fontWeight: 700 }}>✓ {statusMessage.text}</div>
              {statusMessage.ambiguous && (
                <div style={{ fontSize: '0.68rem', color: '#065f46', marginTop: '0.3rem' }}>
                  {statusMessage.ambiguous}
                </div>
              )}
            </div>
          )}

          {activeIntake && (
            <button
              onClick={() => onIntakeResult(null)}
              style={{
                background: 'transparent',
                border: '1px dashed #cbd5e1',
                borderRadius: '6px',
                padding: '0.4rem',
                fontSize: '0.72rem',
                color: '#64748b',
                cursor: 'pointer',
                marginTop: '0.2rem',
                textAlign: 'center',
              }}
            >
              ✕ Close Live Intake Workspace
            </button>
          )}
        </div>
      )}
    </div>
  );
}
