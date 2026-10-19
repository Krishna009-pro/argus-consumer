import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Globe,
  Search,
  FileText,
  FileDown,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Copy,
  Check,
  ExternalLink,
  Terminal,
  ShieldCheck,
  Database,
  ArrowRight,
  Sparkles,
  RefreshCw,
  FileSearch,
  Layers
} from 'lucide-react';
import { getIntakeData } from '../data/intakeSamples';

export default function LiveIntakeStudio({ onIntakeResult, activeIntake, currentDossierCompany }) {
  const showcasePresets = [
    'Dabur India Limited',
    'ITC Limited',
    'Tata Consumer Products',
    'Nestle India',
    'Britannia Industries',
    'Marico Limited',
  ];

  const [companyInput, setCompanyInput] = useState('Dabur India Limited');
  const [currentStep, setCurrentStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [copied, setCopied] = useState(false);

  // Intake workflow state
  const [intakeData, setIntakeData] = useState(() => getIntakeData('Dabur India Limited'));
  const [selectedResultIdx, setSelectedResultIdx] = useState(0);
  const [selectedPdfIdx, setSelectedPdfIdx] = useState(0);
  const [extractedResult, setExtractedResult] = useState(null);

  const handleSelectPreset = (name) => {
    setCompanyInput(name);
    const data = getIntakeData(name);
    setIntakeData(data);
    setSelectedResultIdx(0);
    setSelectedPdfIdx(0);
    setCurrentStep(1);
    setExtractedResult(null);
  };

  const handleSearch = () => {
    if (!companyInput.trim()) return;
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      const data = getIntakeData(companyInput);
      setIntakeData(data);
      setSelectedResultIdx(0);
      setCurrentStep(2);
    }, 550);
  };

  const handleInspectReport = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setSelectedPdfIdx(0);
      setCurrentStep(3);
    }, 500);
  };

  const handleFetchAndExtract = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      const res = intakeData.extraction;
      setExtractedResult(res);
      setCurrentStep(4);
      if (onIntakeResult) {
        onIntakeResult(res);
      }
    }, 700);
  };

  const handleRunFullShowcase = () => {
    setIsProcessing(true);
    setCurrentStep(1);
    setTimeout(() => {
      const data = getIntakeData(companyInput);
      setIntakeData(data);
      setCurrentStep(2);
      setTimeout(() => {
        setCurrentStep(3);
        setTimeout(() => {
          setIsProcessing(false);
          const res = data.extraction;
          setExtractedResult(res);
          setCurrentStep(4);
          if (onIntakeResult) {
            onIntakeResult(res);
          }
        }, 600);
      }, 500);
    }, 500);
  };

  const cliCommand = extractedResult
    ? `python scripts/argus.py verify-candidate "${extractedResult.candidate_file}" ${extractedResult.candidates[0]?.id || '<candidate-id>'} --verified-by "Reviewer name" --period FY2025 --unit INR_crore --period-type annual --currency INR --basis consolidated
python scripts/argus.py run --company "${extractedResult.company}"`
    : '';

  const copyToClipboard = () => {
    if (!cliCommand) return;
    navigator.clipboard.writeText(cliCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getColumnYear = (notes) => {
    if (!notes || !Array.isArray(notes)) return 'Unresolved';
    const match = notes.find((n) => typeof n === 'string' && n.startsWith('Dated column header year: '));
    if (!match) return 'Unresolved';
    return match.split(': ', 2)[1].replace(/\.$/, '');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Studio Header Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
          border: '1.5px solid #bae6fd',
          borderRadius: '16px',
          padding: '1.75rem 2rem',
          boxShadow: '0 4px 20px rgba(2, 132, 199, 0.06)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div style={{ background: '#0284c7', color: '#ffffff', padding: '10px', borderRadius: '12px', display: 'flex' }}>
              <Globe size={24} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 850, color: '#0f172a', margin: 0 }}>
                  🌐 Live Company Intake Studio
                </h2>
                <span className="tag-badge status-emerald">SHOWCASE ENGINE</span>
                <span className="tag-badge" style={{ background: '#f1f5f9', color: '#475569', border: '1px solid #cbd5e1' }}>
                  Rule R2 & R8 Grounded
                </span>
              </div>
              <p style={{ fontSize: '0.86rem', color: '#64748b', margin: '4px 0 0 0' }}>
                Enter any listed company name to discover public regulatory filings, cache verified PDFs with SHA-256 digests, and extract unverified candidate claims for human review.
              </p>
            </div>
          </div>

          <button
            onClick={handleRunFullShowcase}
            disabled={isProcessing}
            className="btn-primary"
            style={{
              padding: '0.65rem 1.25rem',
              fontSize: '0.84rem',
              fontWeight: 800,
              background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
              boxShadow: '0 4px 12px rgba(2, 132, 199, 0.25)',
            }}
          >
            {isProcessing ? <Loader2 size={16} className="spin" /> : <Sparkles size={16} />}
            <span>Auto-Run Intake Showcase</span>
          </button>
        </div>

        {/* Showcase Company Presets */}
        <div>
          <div style={{ fontSize: '0.74rem', fontWeight: 750, color: '#475569', textTransform: 'uppercase', marginBottom: '0.45rem', letterSpacing: '0.04em' }}>
            Instant Showcase Presets:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {showcasePresets.map((preset) => {
              const isSelected = companyInput.toLowerCase() === preset.toLowerCase();
              return (
                <button
                  key={preset}
                  onClick={() => handleSelectPreset(preset)}
                  style={{
                    background: isSelected ? '#0284c7' : '#ffffff',
                    color: isSelected ? '#ffffff' : '#334155',
                    border: '1px solid',
                    borderColor: isSelected ? '#0284c7' : '#cbd5e1',
                    borderRadius: '20px',
                    padding: '0.35rem 0.85rem',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    boxShadow: isSelected ? '0 2px 8px rgba(2, 132, 199, 0.2)' : 'none',
                  }}
                >
                  {preset}
                </button>
              );
            })}
          </div>
        </div>

        {/* Custom Company Search Input Bar */}
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <input
              type="text"
              value={companyInput}
              onChange={(e) => setCompanyInput(e.target.value)}
              placeholder="Enter company name (e.g. Godrej Consumer Products or ITC Limited)..."
              style={{
                width: '100%',
                padding: '0.75rem 1rem 0.75rem 2.5rem',
                borderRadius: '10px',
                border: '1.5px solid #cbd5e1',
                fontSize: '0.92rem',
                fontFamily: 'var(--font-sans)',
                background: '#ffffff',
                boxSizing: 'border-box',
                outline: 'none',
              }}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Search size={18} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
          </div>

          <button
            onClick={handleSearch}
            disabled={isProcessing || !companyInput.trim()}
            className="btn-primary"
            style={{ padding: '0.75rem 1.5rem', fontSize: '0.88rem', fontWeight: 800 }}
          >
            {isProcessing ? <Loader2 size={16} className="spin" /> : <Search size={16} />}
            <span>Search Public Reports</span>
          </button>
        </div>
      </div>

      {/* 4-Step Interactive Pipeline Stepper */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '1rem',
          background: '#ffffff',
          padding: '1.25rem',
          borderRadius: '14px',
          border: '1px solid #e2e8f0',
        }}
      >
        {[
          { num: 1, title: 'Public Discovery', desc: 'Serper web & BSE filings', icon: Search },
          { num: 2, title: 'PDF Inspection', desc: 'Detect direct PDF URLs', icon: FileSearch },
          { num: 3, title: 'SHA-256 Ingestion', desc: 'Tamper-proof file cache', icon: Database },
          { num: 4, title: 'Candidate Extract', desc: 'Unverified claims table', icon: FileText },
        ].map((s) => {
          const isDone = currentStep > s.num;
          const isCurrent = currentStep === s.num;
          const Icon = s.icon;
          return (
            <div
              key={s.num}
              style={{
                padding: '0.85rem 1rem',
                borderRadius: '10px',
                background: isCurrent ? 'rgba(2, 132, 199, 0.06)' : isDone ? '#f0fdf4' : '#f8fafc',
                border: '1.5px solid',
                borderColor: isCurrent ? '#0284c7' : isDone ? '#86efac' : '#e2e8f0',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                transition: 'all 0.2s ease',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: isCurrent ? '#0284c7' : isDone ? '#16a34a' : '#cbd5e1',
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: '0.85rem',
                  flexShrink: 0,
                }}
              >
                {isDone ? <CheckCircle2 size={18} /> : s.num}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.84rem', fontWeight: 750, color: isCurrent ? '#0284c7' : isDone ? '#166534' : '#334155' }}>
                  {s.title}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#64748b' }}>{s.desc}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Step Panels */}
      <AnimatePresence mode="wait">
        {/* Step 1: Search Public Sources */}
        {currentStep === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="analysis-card"
          >
            <div className="card-header">
              <div className="card-title">
                <Search size={18} color="#0284c7" />
                <span>Step 1: Public Source Discovery Query</span>
              </div>
              <span className="tag-badge tag-neutral">Serper Engine / BSE Public Filings</span>
            </div>

            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1rem 1.25rem', marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.74rem', fontWeight: 750, color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>
                Executed Search Query
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.88rem', color: '#0f172a', fontWeight: 700 }}>
                "{companyInput.trim()}" annual report financial statements PDF
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={handleSearch}
                disabled={isProcessing}
                className="btn-primary"
                style={{ padding: '0.65rem 1.5rem' }}
              >
                {isProcessing ? <Loader2 size={16} className="spin" /> : <ArrowRight size={16} />}
                <span>Execute Search & Proceed</span>
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 2: Search Results & Inspect Report */}
        {currentStep === 2 && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="analysis-card"
          >
            <div className="card-header">
              <div className="card-title">
                <FileSearch size={18} color="#0284c7" />
                <span>Step 2: Choose a Report to Inspect</span>
              </div>
              <span className="tag-badge status-amber">Unverified Search Results</span>
            </div>

            <p style={{ fontSize: '0.84rem', color: '#64748b', marginBottom: '1rem' }}>
              Found {intakeData.searchResults.length} public source candidates. Review the publisher and URL before inspecting the report:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
              {intakeData.searchResults.map((r, i) => {
                const isSelected = selectedResultIdx === i;
                return (
                  <div
                    key={i}
                    onClick={() => setSelectedResultIdx(i)}
                    style={{
                      padding: '1rem',
                      borderRadius: '10px',
                      border: '1.5px solid',
                      borderColor: isSelected ? '#0284c7' : '#e2e8f0',
                      background: isSelected ? 'rgba(2, 132, 199, 0.04)' : '#ffffff',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <div style={{ fontWeight: 750, fontSize: '0.9rem', color: '#0f172a' }}>
                        {r.title}
                      </div>
                      <span className="tag-badge tag-neutral">Hit #{i + 1}</span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#0284c7', fontFamily: 'var(--font-mono)', marginBottom: '4px' }}>
                      {r.url}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#64748b' }}>{r.snippet}</div>
                  </div>
                );
              })}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button
                onClick={() => setCurrentStep(1)}
                className="btn-neutral"
                style={{ padding: '0.6rem 1rem' }}
              >
                Back to Search
              </button>

              <button
                onClick={handleInspectReport}
                disabled={isProcessing}
                className="btn-primary"
                style={{ padding: '0.65rem 1.5rem', background: '#334155' }}
              >
                {isProcessing ? <Loader2 size={16} className="spin" /> : <FileDown size={16} />}
                <span>Inspect Selected Report & Extract PDFs</span>
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 3: Direct PDF Discovery & Cryptographic Caching */}
        {currentStep === 3 && (
          <motion.div
            key="step3"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="analysis-card"
          >
            <div className="card-header">
              <div className="card-title">
                <Database size={18} color="#059669" />
                <span>Step 3: Direct PDF Discovery & SHA-256 Ingestion</span>
              </div>
              <span className="tag-badge status-emerald">Rule R8 Content-Addressed Cache</span>
            </div>

            <p style={{ fontSize: '0.84rem', color: '#64748b', marginBottom: '1rem' }}>
              Extracted {intakeData.pdfLinks.length} direct PDF documents from the corporate filing portal. Select the audited statement PDF to fetch and cache:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
              {intakeData.pdfLinks.map((p, i) => {
                const isSelected = selectedPdfIdx === i;
                return (
                  <div
                    key={i}
                    onClick={() => setSelectedPdfIdx(i)}
                    style={{
                      padding: '1rem',
                      borderRadius: '10px',
                      border: '1.5px solid',
                      borderColor: isSelected ? '#059669' : '#e2e8f0',
                      background: isSelected ? 'rgba(5, 150, 105, 0.04)' : '#ffffff',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <div style={{ fontWeight: 750, fontSize: '0.9rem', color: '#0f172a' }}>
                        {p.title}
                      </div>
                      <span className="tag-badge status-emerald">PDF Document</span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#059669', fontFamily: 'var(--font-mono)' }}>
                      {p.url}
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button
                onClick={() => setCurrentStep(2)}
                className="btn-neutral"
                style={{ padding: '0.6rem 1rem' }}
              >
                Back to Reports
              </button>

              <button
                onClick={handleFetchAndExtract}
                disabled={isProcessing}
                className="btn-primary"
                style={{ padding: '0.65rem 1.5rem', background: 'linear-gradient(135deg, #059669 0%, #047857 100%)' }}
              >
                {isProcessing ? <Loader2 size={16} className="spin" /> : <CheckCircle2 size={16} />}
                <span>Fetch Selected PDF & Extract Candidate Claims</span>
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 4: Machine Extraction Results & Human Review Table */}
        {currentStep === 4 && extractedResult && (
          <motion.div
            key="step4"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="analysis-card"
          >
            <div className="card-header">
              <div className="card-title">
                <ShieldCheck size={18} color="#0284c7" />
                <span>Step 4: Machine-Extracted Financial Candidates ({extractedResult.candidate_count} rows)</span>
              </div>
              <span className="tag-badge status-amber">Review-Only Unverified Claims</span>
            </div>

            {/* Provenance Pills */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.85rem', marginBottom: '1.25rem' }}>
              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.65rem 0.9rem', fontSize: '0.76rem' }}>
                <div style={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Cached File Path</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.74rem', color: '#0f172a', wordBreak: 'break-all' }}>
                  {extractedResult.cache_path}
                </div>
              </div>

              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.65rem 0.9rem', fontSize: '0.76rem' }}>
                <div style={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>SHA-256 Digest</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#0f172a', wordBreak: 'break-all' }}>
                  {extractedResult.sha256}
                </div>
              </div>

              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.65rem 0.9rem', fontSize: '0.76rem' }}>
                <div style={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Cache Delivery</div>
                <div style={{ fontWeight: 700, color: extractedResult.cache_reused ? '#059669' : '#0284c7' }}>
                  {extractedResult.cache_reused ? '✓ Reused from local content-addressed cache' : 'Fetched fresh online'}
                </div>
              </div>
            </div>

            {/* Rule R2 Warning Guard Banner */}
            <div
              style={{
                background: '#fffbeb',
                border: '1px solid #fde68a',
                borderLeft: '4px solid #d97706',
                borderRadius: '8px',
                padding: '0.85rem 1.1rem',
                marginBottom: '1.25rem',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.6rem',
              }}
            >
              <AlertTriangle size={18} color="#d97706" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div style={{ fontSize: '0.82rem', color: '#92400e', lineHeight: 1.45 }}>
                <strong>Rule R2 Enforcement:</strong> These are extraction candidates, not verified observations. Review each cited PDF page and approve only values whose period, unit, statement basis, and scope are clear.
              </div>
            </div>

            {/* Candidate Claims Table */}
            <div className="data-table-container" style={{ marginBottom: '1.25rem' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Candidate ID</th>
                    <th>Metric</th>
                    <th>Extracted Value</th>
                    <th>Unit</th>
                    <th>Period</th>
                    <th>Column Year</th>
                    <th>PDF Page</th>
                    <th>Status</th>
                    <th>Source Verbatim Snippet</th>
                  </tr>
                </thead>
                <tbody>
                  {extractedResult.candidates.map((c) => {
                    const colYear = getColumnYear(c.notes);
                    return (
                      <tr key={c.id}>
                        <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 750, color: '#0284c7' }}>
                          {c.id}
                        </td>
                        <td style={{ fontWeight: 650, color: '#0f172a' }}>
                          {(c.metric || '').replace(/_/g, ' ').toUpperCase()}
                        </td>
                        <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#0f172a' }}>
                          {c.value !== null && c.value !== undefined ? Number(c.value).toLocaleString() : '—'}
                        </td>
                        <td style={{ color: c.unit ? '#0f172a' : '#94a3b8', fontStyle: c.unit ? 'normal' : 'italic' }}>
                          {c.unit || 'Unresolved'}
                        </td>
                        <td style={{ color: c.period ? '#0f172a' : '#94a3b8', fontStyle: c.period ? 'normal' : 'italic' }}>
                          {c.period || 'Unresolved'}
                        </td>
                        <td style={{ fontFamily: 'var(--font-mono)', color: colYear !== 'Unresolved' ? '#0284c7' : '#94a3b8' }}>
                          {colYear}
                        </td>
                        <td style={{ fontFamily: 'var(--font-mono)' }}>Page {c.doc_page || 'N/A'}</td>
                        <td>
                          <span className="tag-badge status-amber">UNVERIFIED</span>
                        </td>
                        <td style={{ fontSize: '0.76rem', color: '#475569', maxWidth: '300px', fontFamily: 'var(--font-mono)' }}>
                          "{c.snippet}"
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* CLI Verification Command Box */}
            <div style={{ background: '#0f172a', borderRadius: '10px', padding: '1.1rem 1.35rem', color: '#f8fafc', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', fontWeight: 700, color: '#38bdf8' }}>
                  <Terminal size={14} color="#38bdf8" />
                  <span>After review, approve a candidate with verify-candidate and rerun the deterministic analysis:</span>
                </div>
                <button
                  onClick={copyToClipboard}
                  style={{
                    background: copied ? '#059669' : '#334155',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '0.35rem 0.75rem',
                    color: '#ffffff',
                    fontSize: '0.74rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    transition: 'background 0.2s',
                  }}
                >
                  {copied ? <Check size={12} /> : <Copy size={12} />}
                  <span>{copied ? 'Copied' : 'Copy PowerShell'}</span>
                </button>
              </div>
              <pre
                style={{
                  margin: 0,
                  fontSize: '0.78rem',
                  color: '#7dd3fc',
                  fontFamily: 'var(--font-mono)',
                  overflowX: 'auto',
                  lineHeight: 1.6,
                  background: 'rgba(15, 23, 42, 0.6)',
                  padding: '0.75rem',
                  borderRadius: '6px',
                  border: '1px solid #1e293b',
                }}
              >
                {cliCommand}
              </pre>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button
                onClick={() => setCurrentStep(1)}
                className="btn-neutral"
                style={{ padding: '0.6rem 1.25rem' }}
              >
                Intake Another Company
              </button>

              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button
                  onClick={() => {
                    if (onIntakeResult) onIntakeResult(extractedResult);
                  }}
                  className="btn-primary"
                  style={{ padding: '0.65rem 1.5rem', background: '#0284c7' }}
                >
                  <CheckCircle2 size={16} />
                  <span>Pinned to Top of Active Dossier</span>
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
