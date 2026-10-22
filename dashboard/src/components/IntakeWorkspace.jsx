import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Globe,
  AlertTriangle,
  ExternalLink,
  Copy,
  Check,
  X,
  Terminal,
  FileText,
  Info,
  CheckCircle2,
  Loader2,
  ChevronDown,
  ChevronUp,
  FileSearch,
} from 'lucide-react';

export default function IntakeWorkspace({
  intake,
  onClose,
  currentDossierCompany,
  onCandidateVerified,
}) {
  const [copied, setCopied] = useState(false);
  const [showCli, setShowCli] = useState(false);
  const [verifyingId, setVerifyingId] = useState(null);
  const [verifySuccess, setVerifySuccess] = useState('');
  const [verifyError, setVerifyError] = useState('');

  if (!intake) return null;

  const candidates = intake.candidates || [];
  const candidateFile = intake.candidate_file || 'data/candidates/...';
  const company = intake.company || 'Company';
  const firstCandId = candidates[0]?.id || '<candidate-id>';
  const unverifiedCandidates = candidates.filter((c) => c.status === 'unverified');

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

  // Direct 1-Click Verification Handler for single candidate
  const handleVerifyCandidate = async (cand) => {
    setVerifyingId(cand.id);
    setVerifyError('');
    setVerifySuccess('');

    try {
      const res = await fetch('/api/candidate/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_file: candidateFile,
          candidate_id: cand.id,
          company: company,
          verified_by: 'Audit Reviewer',
          period: cand.period || 'FY2025',
          unit: cand.unit || 'INR_crore',
          period_type: 'annual',
          currency: 'INR',
          basis: 'consolidated',
          run_analysis: true,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Verification request failed');
      }

      const result = await res.json();
      setVerifySuccess(`✓ Verified ${cand.metric || 'claim'} [${cand.id}] into official audit ledger!`);
      if (onCandidateVerified) {
        onCandidateVerified(result);
      }
    } catch (err) {
      setVerifyError(err.message || 'Verification failed');
    } finally {
      setVerifyingId(null);
    }
  };

  // Direct 1-Click Batch Verification Handler for all unverified candidates
  const handleVerifyAll = async () => {
    const unverifiedIds = unverifiedCandidates.map((c) => c.id);
    if (unverifiedIds.length === 0) return;

    setVerifyingId('all');
    setVerifyError('');
    setVerifySuccess('');

    try {
      const res = await fetch('/api/candidate/verify-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_file: candidateFile,
          candidate_ids: unverifiedIds,
          company: company,
          verified_by: 'Audit Reviewer',
          run_analysis: true,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Batch verification request failed');
      }

      const result = await res.json();
      setVerifySuccess(`✓ Approved and committed ${result.verified_count} candidates into audit ledger!`);
      if (onCandidateVerified) {
        onCandidateVerified(result);
      }
    } catch (err) {
      setVerifyError(err.message || 'Batch verification failed');
    } finally {
      setVerifyingId(null);
    }
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
        maxWidth: '100%',
        width: '100%',
        boxSizing: 'border-box',
        overflow: 'hidden',
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', minWidth: 0, flex: 1 }}>
          <div style={{ background: '#e0f2fe', padding: '8px', borderRadius: '10px', display: 'flex', flexShrink: 0 }}>
            <Globe size={22} color="#0284c7" />
          </div>
          <div style={{ minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                Online source intake
              </h2>
              <span className="tag-badge status-amber">
                Unverified Extraction Candidates
              </span>
            </div>
            <div style={{ fontSize: '0.84rem', color: '#475569', marginTop: '0.2rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              <strong>Company:</strong> {company} &nbsp;·&nbsp;
              <strong>Source:</strong>{' '}
              <a
                href={intake.url}
                target="_blank"
                rel="noreferrer"
                style={{ color: '#0284c7', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '3px' }}
              >
                <span style={{ textDecoration: 'underline' }}>{intake.title}</span>
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
            flexShrink: 0,
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
            Live intake is for <strong>{company}</strong>; the saved dossier below is for <strong>{currentDossierCompany}</strong>. Approving candidates below will commit them to the ledger and execute the deterministic analysis for <strong>{company}</strong>.
          </span>
        </div>
      )}

      {/* Provenance Metadata Pills */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.85rem', marginBottom: '1.25rem', width: '100%' }}>
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.65rem 0.9rem', fontSize: '0.76rem', minWidth: 0 }}>
          <div style={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Cached File</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.74rem', color: '#0f172a', wordBreak: 'break-all' }}>
            {intake.cache_path}
          </div>
        </div>

        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.65rem 0.9rem', fontSize: '0.76rem', minWidth: 0 }}>
          <div style={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>SHA-256 Digest</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#0f172a', wordBreak: 'break-all' }}>
            {intake.sha256}
          </div>
        </div>

        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.65rem 0.9rem', fontSize: '0.76rem', minWidth: 0 }}>
          <div style={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Cache Delivery</div>
          <div style={{ fontWeight: 700, color: intake.cache_reused ? '#059669' : '#0284c7' }}>
            {intake.cache_reused ? '✓ Reused from local content-addressed cache' : 'Fetched online'}
          </div>
        </div>
      </div>

      {/* Warning Guard Banner (Rule R2) */}
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
          <strong>Rule R2 Verification Gate:</strong> Extraction candidates are retrieved directly from official statutory PDF statements. Review each item and approve only values whose period, unit, and basis are verified.
        </div>
      </div>

      {/* In-UI Status Alerts */}
      {verifySuccess && (
        <div
          style={{
            background: '#ecfdf5',
            border: '1px solid #a7f3d0',
            borderRadius: '8px',
            padding: '0.75rem 1rem',
            marginBottom: '1rem',
            color: '#065f46',
            fontSize: '0.82rem',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <CheckCircle2 size={16} color="#059669" />
          <span>{verifySuccess}</span>
        </div>
      )}

      {verifyError && (
        <div
          style={{
            background: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '0.75rem 1rem',
            marginBottom: '1rem',
            color: '#b91c1c',
            fontSize: '0.82rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <AlertTriangle size={16} color="#b91c1c" />
          <span>{verifyError}</span>
        </div>
      )}

      {/* Candidate Claims Section */}
      {candidates.length === 0 ? (
        /* Empty-state when 0 claims are extracted */
        <div
          style={{
            background: '#f8fafc',
            border: '1px dashed #cbd5e1',
            borderRadius: '12px',
            padding: '1.75rem 1.25rem',
            textAlign: 'center',
            margin: '1rem 0',
          }}
        >
          <FileSearch size={34} color="#64748b" style={{ margin: '0 auto 0.6rem', display: 'block' }} />
          <h4 style={{ fontSize: '0.98rem', fontWeight: 750, color: '#0f172a', marginBottom: '0.35rem' }}>
            0 Candidate Claims Extracted from this PDF
          </h4>
          <p style={{ fontSize: '0.82rem', color: '#64748b', maxWidth: '560px', margin: '0 auto 1.25rem', lineHeight: 1.45 }}>
            The automated PDF table parser did not identify standard financial statement line items on the scanned filing pages. Under Rule R2, ARGUS abstains from fabricating numbers without clear tabular evidence.
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <a
              href={intake.url}
              target="_blank"
              rel="noreferrer"
              style={{
                background: '#0284c7',
                color: '#ffffff',
                textDecoration: 'none',
                padding: '0.55rem 1.1rem',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: 700,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
              }}
            >
              <span>View Source PDF</span>
              <ExternalLink size={13} />
            </a>
            <button
              onClick={onClose}
              style={{
                background: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '8px',
                padding: '0.55rem 1.1rem',
                fontSize: '0.8rem',
                fontWeight: 650,
                color: '#475569',
                cursor: 'pointer',
              }}
            >
              Dismiss Intake
            </button>
          </div>
        </div>
      ) : (
        /* Candidates Table with 1-Click Interactive In-UI Actions */
        <div style={{ marginBottom: '1.25rem', maxWidth: '100%' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '0.65rem',
              flexWrap: 'wrap',
              gap: '0.75rem',
            }}
          >
            <div>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                Extracted Candidate Claims ({candidates.length} rows)
              </h4>
              {intake.ambiguous_count > 0 && (
                <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '2px' }}>
                  {intake.ambiguous_count} superseded extraction rows retained as ambiguous for audit
                </div>
              )}
            </div>

            {unverifiedCandidates.length > 0 && (
              <button
                type="button"
                onClick={handleVerifyAll}
                disabled={verifyingId !== null}
                style={{
                  background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0.5rem 0.95rem',
                  fontSize: '0.78rem',
                  fontWeight: 750,
                  cursor: verifyingId !== null ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  boxShadow: '0 2px 6px rgba(5, 150, 105, 0.25)',
                  transition: 'all 0.2s ease',
                }}
              >
                {verifyingId === 'all' ? <Loader2 size={13} className="spin" /> : <CheckCircle2 size={13} />}
                <span>Approve All ({unverifiedCandidates.length}) & Run Analysis</span>
              </button>
            )}
          </div>

          <div className="data-table-container">
            <table className="data-table" style={{ minWidth: '820px' }}>
              <thead>
                <tr>
                  <th>Action</th>
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
                  const isVerified = c.status === 'verified';
                  const isProcessing = verifyingId === c.id || verifyingId === 'all';

                  return (
                    <tr key={c.id}>
                      <td style={{ whiteSpace: 'nowrap' }}>
                        {isVerified ? (
                          <span
                            className="tag-badge status-emerald"
                            style={{ display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                          >
                            <Check size={11} /> Verified
                          </span>
                        ) : (
                          <button
                            type="button"
                            onClick={() => handleVerifyCandidate(c)}
                            disabled={verifyingId !== null}
                            style={{
                              background: '#0284c7',
                              color: '#ffffff',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '0.35rem 0.75rem',
                              fontSize: '0.73rem',
                              fontWeight: 750,
                              cursor: verifyingId !== null ? 'not-allowed' : 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              transition: 'background 0.15s ease',
                            }}
                          >
                            {isProcessing ? <Loader2 size={11} className="spin" /> : <CheckCircle2 size={11} />}
                            <span>Approve & Run</span>
                          </button>
                        )}
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 750, color: '#0284c7', whiteSpace: 'nowrap' }}>
                        {c.id}
                      </td>
                      <td style={{ fontWeight: 650, color: '#0f172a', whiteSpace: 'nowrap' }}>
                        {(c.metric || '').replace(/_/g, ' ').toUpperCase()}
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#0f172a', whiteSpace: 'nowrap' }}>
                        {c.value !== null && c.value !== undefined ? Number(c.value).toLocaleString() : '—'}
                      </td>
                      <td style={{ color: c.unit ? '#0f172a' : '#94a3b8', fontStyle: c.unit ? 'normal' : 'italic', whiteSpace: 'nowrap' }}>
                        {c.unit || 'INR_crore'}
                      </td>
                      <td style={{ color: c.period ? '#0f172a' : '#94a3b8', fontStyle: c.period ? 'normal' : 'italic', whiteSpace: 'nowrap' }}>
                        {c.period || 'FY2025'}
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', color: colYear !== 'Unresolved' ? '#0284c7' : '#94a3b8', whiteSpace: 'nowrap' }}>
                        {colYear}
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap' }}>
                        Page {c.doc_page || 'N/A'}
                      </td>
                      <td style={{ whiteSpace: 'nowrap' }}>
                        <span className={`tag-badge ${isVerified ? 'status-emerald' : 'status-amber'}`}>
                          {isVerified ? 'VERIFIED' : 'UNVERIFIED'}
                        </span>
                      </td>
                      <td
                        style={{
                          fontSize: '0.74rem',
                          color: '#475569',
                          maxWidth: '240px',
                          fontFamily: 'var(--font-mono)',
                          overflowWrap: 'anywhere',
                          wordBreak: 'break-word',
                          whiteSpace: 'normal',
                          lineHeight: 1.35,
                        }}
                      >
                        "{c.snippet}"
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Collapsible CLI Reproduction Command (Only if candidate claims exist) */}
      {candidates.length > 0 && (
        <div style={{ marginTop: '1.25rem', borderTop: '1px solid #f1f5f9', paddingTop: '0.85rem' }}>
          <button
            type="button"
            onClick={() => setShowCli(!showCli)}
            style={{
              background: 'none',
              border: 'none',
              color: '#64748b',
              fontSize: '0.76rem',
              fontWeight: 650,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '0.2rem 0',
            }}
          >
            <Terminal size={13} color="#0284c7" />
            <span>{showCli ? 'Hide CLI audit reproduction command' : 'View CLI reproduction command (PowerShell / Terminal)'}</span>
            {showCli ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>

          {showCli && (
            <div
              style={{
                background: '#0f172a',
                borderRadius: '10px',
                padding: '1rem 1.25rem',
                color: '#f8fafc',
                marginTop: '0.65rem',
                maxWidth: '100%',
                boxSizing: 'border-box',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                <div style={{ fontSize: '0.76rem', color: '#94a3b8' }}>
                  Run this command in terminal to verify via deterministic CLI:
                </div>
                <button
                  type="button"
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
                  fontSize: '0.76rem',
                  color: '#7dd3fc',
                  fontFamily: 'var(--font-mono)',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-all',
                  maxWidth: '100%',
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
          )}
        </div>
      )}
    </motion.div>
  );
}
