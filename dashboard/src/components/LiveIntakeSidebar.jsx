import React, { useState } from 'react';
import { Globe, Search, Loader2, ChevronDown, ChevronUp, AlertCircle, FileSearch, CheckCircle2 } from 'lucide-react';
import { getIntakeData } from '../data/intakeSamples';

export default function LiveIntakeSidebar({ onIntakeResult, activeIntake }) {
  const [isOpen, setIsOpen] = useState(true);
  const [companyName, setCompanyName] = useState('');
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
    if (!companyName.trim()) {
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
      const data = getIntakeData(companyName.trim());
      setSearchResults(data.searchResults || []);
      setSelectedResultIdx(0);
    }, 600);
  };

  const handleInspectReport = () => {
    setIsFetchingPdfs(true);
    setErrorMessage('');
    setTimeout(() => {
      setIsFetchingPdfs(false);
      const data = getIntakeData(companyName.trim());
      setPdfLinks(data.pdfLinks || []);
      setSelectedPdfIdx(0);
    }, 500);
  };

  const handleFetchAndExtract = () => {
    setIsExtracting(true);
    setErrorMessage('');
    setTimeout(() => {
      setIsExtracting(false);
      const data = getIntakeData(companyName.trim());
      const extraction = data.extraction;
      setIntakeSuccess({
        count: extraction.candidate_count,
        ambiguous: extraction.ambiguous_count,
      });
      if (onIntakeResult) {
        onIntakeResult(extraction);
      }
    }, 700);
  };

  return (
    <div
      style={{
        background: '#ffffff',
        border: '1px solid #cbd5e1',
        borderRadius: '10px',
        overflow: 'hidden',
        boxShadow: isOpen ? '0 2px 8px rgba(15,23,42,0.05)' : 'none',
      }}
    >
      {/* Expander Header matching st.expander("🌐 Live company intake", expanded=False) */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0.65rem 0.85rem',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          fontFamily: 'var(--font-sans)',
          textAlign: 'left',
        }}
      >
        <span style={{ fontWeight: 700, fontSize: '0.84rem', color: '#0f172a' }}>
          🌐 Live company intake
        </span>
        {isOpen ? <ChevronUp size={16} color="#64748b" /> : <ChevronDown size={16} color="#64748b" />}
      </button>

      {/* Expander Content */}
      {isOpen && (
        <div style={{ padding: '0 0.85rem 0.85rem 0.85rem', borderTop: '1px solid #f1f5f9', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
          <div style={{ fontSize: '0.74rem', color: '#64748b', marginTop: '0.4rem', lineHeight: 1.4 }}>
            Search public sources, cache a selected PDF, and extract review-only claims.
          </div>

          {/* Company Name Input */}
          <div>
            <label style={{ fontSize: '0.74rem', color: '#334155', fontWeight: 600, display: 'block', marginBottom: '0.25rem' }}>
              Company name
            </label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => {
                setCompanyName(e.target.value);
                if (errorMessage) setErrorMessage('');
              }}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="e.g. ITC Limited"
              style={{
                width: '100%',
                padding: '0.5rem 0.65rem',
                fontSize: '0.8rem',
                borderRadius: '6px',
                border: '1px solid #cbd5e1',
                boxSizing: 'border-box',
                outline: 'none',
                background: '#ffffff',
              }}
            />
          </div>

          {/* Error Message */}
          {errorMessage && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', padding: '0.45rem 0.65rem', fontSize: '0.72rem', color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <AlertCircle size={13} color="#b91c1c" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Search Button */}
          <button
            type="button"
            onClick={handleSearch}
            disabled={isSearching}
            className="btn-primary"
            style={{ width: '100%', padding: '0.5rem', fontSize: '0.78rem', justifyContent: 'center' }}
          >
            {isSearching ? <Loader2 size={13} className="spin" /> : <Search size={13} />}
            <span>Search public reports</span>
          </button>

          {/* Search Results Dropdown */}
          {searchResults.length > 0 && (
            <div style={{ marginTop: '0.2rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div>
                <label style={{ fontSize: '0.72rem', color: '#334155', fontWeight: 600, display: 'block', marginBottom: '0.25rem' }}>
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
                className="btn-primary"
                style={{ width: '100%', padding: '0.5rem', fontSize: '0.76rem', background: '#334155', justifyContent: 'center' }}
              >
                {isFetchingPdfs ? <Loader2 size={13} className="spin" /> : <FileSearch size={13} />}
                <span>Fetch PDF and extract claims</span>
              </button>
            </div>
          )}

          {/* Direct PDF Links Dropdown */}
          {pdfLinks.length > 0 && (
            <div style={{ marginTop: '0.2rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                Direct PDF links found on the selected page:
              </div>

              <div>
                <label style={{ fontSize: '0.72rem', color: '#334155', fontWeight: 600, display: 'block', marginBottom: '0.25rem' }}>
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
                className="btn-primary"
                style={{ width: '100%', padding: '0.5rem', fontSize: '0.76rem', background: '#059669', justifyContent: 'center' }}
              >
                {isExtracting ? <Loader2 size={13} className="spin" /> : <CheckCircle2 size={13} />}
                <span>Fetch selected PDF and extract claims</span>
              </button>
            </div>
          )}

          {/* Success Status matching streamlit */}
          {intakeSuccess && (
            <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: '6px', padding: '0.6rem', fontSize: '0.72rem', color: '#047857', lineHeight: 1.4 }}>
              <div>Cached and extracted {intakeSuccess.count} claims. They remain unverified until reviewed.</div>
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
  );
}
