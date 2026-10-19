import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Globe, AlertTriangle, ExternalLink, Copy, Check, X, Terminal, ShieldAlert, FileText, Info } from 'lucide-react';

export default function IntakeWorkspace({ intake, onClose, currentDossierCompany }) {
  const [copied, setCopied] = useState(false);

  if (!intake) return null;

  const candidates = intake.candidates || [];
  const candidateFile = intake.candidate_file || 'data/candidates/...';
  const company = intake.company || 'Company';
  const firstCandId = candidates[0]?.id || '<candidate-id>';

  const cliCommand = `python scripts/argus.py verify-candidate "${candidateFile}" ${firstCandId} --verified-by "Reviewer name" --period FY2025 --unit INR_crore --period-type annual --currency INR --basis consolidated
python scripts/argus.py run --company "${company}"`;

  const copyToClipboard = () => {
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
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      style={{
        background: '#ffffff',
        border: '1.5px solid #0284c7',
        borderRadius: '16px',
        padding: '1.75rem',
        marginBottom: '2rem',
        boxShadow: '0 8px 30px rgba(2, 132, 199, 0.08)',
      }}
    >
      {/* Top Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.25rem',
          borderBottom: '1px solid #f1f5f9',
          paddingBottom: '1rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: '#e0f2fe', padding: '8px', borderRadius: '10px', display: 'flex' }}>
            <Globe size={22} color="#0284c7" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                Online source intake
              </h2>
              <span className="tag-badge status-amber">
                Unverified Extraction Candidates
              </span>
            </div>
            <div style={{ fontSize: '0.84rem', color: '#475569', marginTop: '0.2rem' }}>
              <strong>Company:</strong> {company} &nbsp;·&nbsp;
              <strong>Source:</strong>{' '}
              <a
                href={intake.url}
                target="_blank"
                rel="noreferrer"
                style={{ color: '#0284c7', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '3px' }}
              >
                <span>{intake.title}</span>
                <ExternalLink size={12} />
              </a>
            </div>
          </div>
        </div>

        <button
          onClick={onClose}
          style={{
            background: '#f8fafc',
            border: '1px solid #cbd5e1',
            borderRadius: '8px',
            padding: '0.45rem 0.85rem',
            fontSize: '0.78rem',
            fontWeight: 700,
            color: '#475569',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            transition: 'all 0.15s ease',
          }}
        >
          <X size={14} />
          <span>Dismiss Intake</span>
        </button>
      </div>

      {/* Cross-Company Disclaimer if viewing different saved dossier */}
      {currentDossierCompany && currentDossierCompany.toLowerCase() !== company.toLowerCase() && (
        <div
          style={{
            background: '#eff6ff',
            border: '1px solid #bfdbfe',
            borderRadius: '8px',
            padding: '0.65rem 0.9rem',
            marginBottom: '1rem',
            fontSize: '0.78rem',
            color: '#1e40af',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <Info size={15} color="#2563eb" style={{ flexShrink: 0 }} />
          <span>
            Live intake is for <strong>{company}</strong>; the saved dossier below is for <strong>{currentDossierCompany}</strong>. Importing a source does not replace or generate a company dossier until human verification is complete.
          </span>
        </div>
      )}

      {/* Provenance Metadata Pills */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.85rem', marginBottom: '1.25rem' }}>
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.65rem 0.9rem', fontSize: '0.76rem' }}>
          <div style={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Cached File</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.74rem', color: '#0f172a', wordBreak: 'break-all' }}>
            {intake.cache_path}
          </div>
        </div>

        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.65rem 0.9rem', fontSize: '0.76rem' }}>
          <div style={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>SHA-256 Digest</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#0f172a', wordBreak: 'break-all' }}>
            {intake.sha256}
          </div>
        </div>

        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.65rem 0.9rem', fontSize: '0.76rem' }}>
          <div style={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Cache Delivery</div>
          <div style={{ fontWeight: 700, color: intake.cache_reused ? '#059669' : '#0284c7' }}>
            {intake.cache_reused ? '✓ Reused from local content-addressed cache' : 'Fetched online'}
          </div>
        </div>
      </div>

      {/* Warning Guard Banner (Matching Rule R2 & Streamlit) */}
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
          <strong>Rule R2 Warning:</strong> These are extraction candidates, not verified observations. Review each cited PDF page and approve only values whose period, unit, statement basis, and scope are clear.
        </div>
      </div>

      {/* Candidate Claims Table */}
      <div style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <h4 style={{ fontSize: '0.92rem', fontWeight: 750, color: '#0f172a', margin: 0 }}>
            Extracted Candidate Claims ({candidates.length} reviewable rows)
          </h4>
          {intake.ambiguous_count > 0 && (
            <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
              {intake.ambiguous_count} superseded extraction rows retained as ambiguous for audit
            </span>
          )}
        </div>

        <div className="data-table-container">
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
                <th>Source Snippet</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => {
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
                    <td style={{ fontFamily: 'var(--font-mono)' }}>
                      Page {c.doc_page || 'N/A'}
                    </td>
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
      </div>

      {/* Review & Approval Command Box */}
      <div style={{ background: '#0f172a', borderRadius: '10px', padding: '1.1rem 1.35rem', color: '#f8fafc' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', fontWeight: 700, color: '#38bdf8' }}>
              <Terminal size={14} color="#38bdf8" />
              <span>After review, approve a candidate with verify-candidate and rerun the deterministic analysis:</span>
            </div>
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
    </motion.div>
  );
}
